use crate::{
    gitops, process, providers,
    state::{Store, first, rows},
    util, worker,
};
use anyhow::{Context, Result, bail, ensure};
use regex::Regex;
use rusqlite::params;
use serde_json::{Value, json};
use std::collections::BTreeSet;
use std::fs::{self, OpenOptions};
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

#[derive(Clone)]
pub struct Runtime {
    pub project: PathBuf,
    pub config: Value,
    pub store: Store,
    pub docs: PathBuf,
}

#[derive(Clone)]
struct WorkRow {
    id: String,
    path: Option<String>,
    depends: Vec<String>,
    state: String,
    line: String,
}

fn work_rows(text: &str) -> Result<Vec<WorkRow>> {
    let section = Regex::new(r"(?ms)^## Work\s*\n(.*?)(?:^## |\z)")?;
    let body = section
        .captures(text)
        .context("Plan needs its canonical Work table.")?
        .get(1)
        .unwrap()
        .as_str();
    let spec = Regex::new(r"\bP\d+-MS\d+\b")?;
    let link = Regex::new(r"\]\(([^)]+)\)")?;
    let mut result = Vec::new();
    for line in body.lines() {
        let cells = line
            .trim()
            .trim_matches('|')
            .split('|')
            .map(str::trim)
            .collect::<Vec<_>>();
        if cells.len() != 4 || cells[0] == "Spec" {
            continue;
        }
        if let Some(id) = spec.find(cells[0]) {
            result.push(WorkRow {
                id: id.as_str().to_string(),
                path: link.captures(cells[0]).map(|m| m[1].to_string()),
                depends: spec
                    .find_iter(cells[1])
                    .map(|m| m.as_str().to_string())
                    .collect(),
                state: cells[2].to_string(),
                line: line.to_string(),
            });
        }
    }
    Ok(result)
}

pub fn overlay(project: &Path, destination: &Path) -> Result<()> {
    let manifest = if project.join(".okms/install.json").is_file() {
        util::json(&project.join(".okms/install.json"))?
    } else {
        json!({})
    };
    let mut paths = manifest["files"]
        .as_object()
        .map(|v| v.keys().cloned().collect::<BTreeSet<_>>())
        .unwrap_or_default();
    paths.extend(
        [
            ".okms/okms",
            ".okms/team.json",
            ".okms/install.json",
            ".codex/config.toml",
            ".codex/hooks.json",
            ".claude/settings.json",
            ".claude/settings.local.json",
            "AGENTS.md",
            "CLAUDE.md",
        ]
        .map(str::to_string),
    );
    let docs = manifest["docs_path"].as_str().unwrap_or("docs");
    for relative in paths {
        if ![".okms/", ".codex/", ".claude/", ".agents/"]
            .iter()
            .any(|prefix| relative.starts_with(prefix))
            && !relative.starts_with(&format!("{docs}/"))
            && !["AGENTS.md", "CLAUDE.md"].contains(&relative.as_str())
        {
            continue;
        }
        let source = util::project_path(project, &relative)?;
        let target = util::project_path(destination, &relative)?;
        if source.is_file() && !target.exists() {
            fs::create_dir_all(target.parent().context("Overlay needs a parent.")?)?;
            fs::copy(source, target)?;
        }
    }
    Ok(())
}

impl Runtime {
    pub fn new(project: &Path) -> Result<Self> {
        let project = project.canonicalize()?;
        let config_path = util::project_path(&project, ".okms/team.json")?;
        ensure!(
            config_path.is_file(),
            "Hybrid Team is not installed here; run okms init first."
        );
        let config = util::json(&config_path)?;
        ensure!(
            config.is_object() && config["schema_version"] == 1,
            "Unsupported team configuration schema_version."
        );
        let max_workers = config["max_workers"]
            .as_u64()
            .context("max_workers must be a positive integer.")?;
        ensure!(
            max_workers > 0 && max_workers < 10_000_000,
            "max_workers must be a positive integer below 10000000."
        );
        let timeout = config["assignment_timeout_seconds"]
            .as_f64()
            .context("Team configuration needs finite positive assignment_timeout_seconds.")?;
        ensure!(
            timeout.is_finite() && timeout > 0. && timeout < 10_000_000.,
            "Team configuration needs finite positive assignment_timeout_seconds."
        );
        let docs = util::project_path(&project, util::string(&config, "docs_path")?)?;
        let store = Store::new(&project)?;
        Ok(Self {
            project,
            config,
            store,
            docs,
        })
    }

    pub fn path(&self, relative: &str) -> Result<PathBuf> {
        util::project_path(&self.project, relative)
    }

    pub fn actor(&self, identity: &Value, coordinator: bool) -> Result<Value> {
        self.store
            .authenticate(&self.store.connection()?, identity, coordinator)
    }

    pub fn timeout(&self) -> f64 {
        self.config["assignment_timeout_seconds"].as_f64().unwrap()
    }

    pub fn doctor(&self) -> Result<Value> {
        let status = self.store.status()?;
        let available = providers::capabilities(&self.config, &self.project);
        let git_baseline = gitops::git(
            &self.project,
            &["rev-parse", "--verify", "HEAD"],
            None,
            None,
            false,
        )
        .is_ok_and(|r| r.status.success());
        let checks_configured = self.config["checks"]
            .as_array()
            .is_some_and(|v| !v.is_empty())
            && process::validate_checks(&self.config["checks"]).is_ok();
        let mut hooks = status["events"]
            .as_array()
            .unwrap()
            .iter()
            .filter(|e| e["type"] == "hook_received")
            .cloned()
            .collect::<Vec<_>>();
        if hooks.len() > 10 {
            hooks.drain(..hooks.len() - 10);
        }
        let ready = cfg!(unix)
            && git_baseline
            && checks_configured
            && ["codex", "claude"].iter().all(|p| {
                let info = &available[*p];
                info["available"] == true
                    && info["structured_output"] == true
                    && info["authenticated"] == true
            });
        Ok(
            json!({"runtime_version":crate::VERSION,"runtime":"rust","python_required":false,"platform_supported":cfg!(unix),
            "docs_path":self.docs,"git_baseline":git_baseline,"providers":available,"checks_configured":checks_configured,
            "hooks":"configured; native trust and loading require confirmation in each CLI","last_hook_receipts":hooks,"ready":ready}),
        )
    }

    fn validate_contract(&self, plan: &str, spec: &str) -> Result<String> {
        let plan_path = self.path(plan)?;
        let spec_path = self.path(spec)?;
        ensure!(
            plan_path.is_file() && spec_path.is_file(),
            "Save the plan and selected micro spec before dispatch."
        );
        let text = fs::read_to_string(&plan_path)?;
        ensure!(
            Regex::new(r"(?m)^type:\s*Plan\s*$")?.is_match(&text),
            "Assignment plan must be a saved Plan."
        );
        ensure!(
            Regex::new(r"(?m)^type:\s*MicroSpec\s*$")?.is_match(&fs::read_to_string(&spec_path)?),
            "Assignment spec must be a saved MicroSpec."
        );
        let work = work_rows(&text)?;
        let selected = work
            .iter()
            .find(|row| {
                row.path.as_ref().is_some_and(|link| {
                    plan_path
                        .parent()
                        .unwrap()
                        .join(link)
                        .canonicalize()
                        .ok()
                        .as_ref()
                        == Some(&spec_path)
                })
            })
            .context("Spec must be an open linked row of the assignment plan.")?;
        ensure!(
            ["planned", "in_progress", "blocked"].contains(&selected.state.as_str()),
            "Spec must be an open linked row of the assignment plan."
        );
        ensure!(
            selected.depends.iter().all(|dependency| work
                .iter()
                .any(|row| row.id == *dependency && row.state == "done")),
            "Assignment dependencies are not done."
        );
        Ok(selected.id.clone())
    }

    pub fn dispatch(&self, identity: &Value, data: &Value) -> Result<Value> {
        self.actor(identity, true)?;
        let provider = util::string(data, "provider")?;
        ensure!(
            ["codex", "claude"].contains(&provider),
            "Assignment provider must be codex or claude."
        );
        let plan = util::string(data, "plan")?;
        let spec = util::string(data, "spec")?;
        let spec_id = self.validate_contract(plan, spec)?;
        let scope = data
            .get("owns")
            .unwrap_or(&json!([]))
            .as_array()
            .context("owns must be an array of explicit paths, or [] for a reader.")?
            .iter()
            .map(|v| gitops::scope_path(v.as_str().context("Write scopes need string paths.")?))
            .collect::<Result<Vec<_>>>()?;
        for path in &scope {
            self.path(path)?;
        }
        let docs = self.docs.strip_prefix(&self.project)?.to_string_lossy();
        let mut shared = [
            "index.md",
            "workflow.md",
            "context.md",
            "team.md",
            "team-policy.md",
            "delegation.md",
            "_templates",
            "roles",
        ]
        .iter()
        .map(|name| format!("{docs}/{name}"))
        .collect::<Vec<_>>();
        shared.extend([plan.to_string(), spec.to_string()]);
        ensure!(
            !gitops::overlap(&scope, &shared),
            "Workers cannot own shared contracts, progress, or role instructions."
        );
        let checks_value = data
            .get("checks")
            .or_else(|| self.config.get("checks"))
            .cloned()
            .unwrap_or(json!([]));
        let checks = process::validate_checks(&checks_value)?;
        let intent = util::string(data, "intent")?;
        ensure!(
            !intent.trim().is_empty(),
            "Assignment needs a bounded intent."
        );
        providers::command(
            provider,
            &self.config,
            &self.project,
            &json!({"worktree":self.project}),
            &self.store.directory,
        )?;
        let mut result = self.store.transact(|db| {
            let actor = self.store.authenticate(db,identity,true)?;
            let active: i64 = db.query_row("SELECT COUNT(*) FROM agents WHERE role='worker' AND status IN ('queued','starting','running','waiting_input')",[],|r|r.get(0))?;
            ensure!(active < self.config["max_workers"].as_i64().unwrap(),"Worker limit reached; finish or stop an assignment first.");
            let open = rows(db,"SELECT * FROM runs WHERE status IN ('active','integrating','applied_unverified')",[])?;
            if let Some(run) = open.first() {
                ensure!(run["plan"] == plan && run["status"] == "active","Finish or recover the existing run before starting this batch.");
            }
            let run = if let Some(id) = data["run_id"].as_str() {
                let run = first(db,"SELECT * FROM runs WHERE id=?",[id])?.context("Requested run is not an active batch of this plan.")?;
                ensure!(run["plan"] == plan && run["status"] == "active","Requested run is not an active batch of this plan.");
                Some(run)
            } else { open.first().cloned() };
            let (run_id,baseline) = if let Some(run) = run {
                (util::string(&run,"id")?.to_string(),util::string(&run,"baseline")?.to_string())
            } else {
                let run_id = util::identifier("run");
                let baseline = gitops::snapshot(&self.project,Some(&format!("refs/okms/runs/{run_id}/base")))?;
                db.execute("INSERT INTO runs VALUES(?,?,?,'active',?)",params![run_id,baseline,plan,json!({"created_at":util::now()}).to_string()])?;
                self.store.event(db,"run_started",actor["id"].as_str(),Some(&run_id),None,json!({"baseline":baseline,"plan":plan}))?;
                (run_id,baseline)
            };
            for row in rows(db,"SELECT assignment FROM agents WHERE run_id=? AND status NOT IN ('failed','cancelled')",[&run_id])? {
                let assignment: Value = serde_json::from_str(util::string(&row,"assignment")?)?;
                let owns = assignment["owns"].as_array().context("Invalid saved scope.")?.iter()
                    .map(|s|s.as_str().context("Invalid saved scope.").map(str::to_string)).collect::<Result<Vec<_>>>()?;
                ensure!(!gitops::overlap(&scope,&owns),"Write scopes overlap; serialize or split the assignments.");
            }
            let agent_id = util::identifier("worker");
            let location = gitops::worktree(&self.project,&agent_id,&baseline)?;
            overlay(&self.project,&location)?;
            let assignment = json!({"plan":plan,"spec":spec,"spec_id":spec_id,"provider":provider,"intent":intent,"owns":scope,
                "checks":checks,"baseline":baseline,"context":data.get("context").cloned().unwrap_or(json!([])),
                "role":"worker","run_id":run_id,"worker_id":agent_id,"worktree":location,"contract":fs::read_to_string(self.path(spec)?)?});
            providers::command(provider,&self.config,&self.project,&json!({"id":agent_id,"worktree":location}),&self.store.directory)?;
            db.execute("INSERT INTO agents(id,provider,role,token,status,run_id,spec_id,worktree,assignment,deadline) VALUES(?,?,'worker',?,'queued',?,?,?,?,?)",
                params![agent_id,provider,util::token(),run_id,spec_id,location.to_str(),assignment.to_string(),util::seconds()+self.timeout()])?;
            self.store.event(db,"assignment_queued",actor["id"].as_str(),Some(&run_id),Some(&spec_id),assignment)?;
            Ok(json!({"agent_id":agent_id,"run_id":run_id,"worktree":location,"baseline":baseline,"status":"queued"}))
        })?;
        if data.get("launch").and_then(Value::as_bool).unwrap_or(true) {
            result["driver_pid"] =
                json!(self.launch(util::string(&result, "agent_id")?, "Initial assignment")?);
        }
        Ok(result)
    }

    pub fn launch(&self, agent_id: &str, reason: &str) -> Result<u32> {
        let nonce = util::identifier("driver");
        self.store.transact(|db| {
            ensure!(db.execute("UPDATE agents SET status='starting',driver_nonce=? WHERE id=? AND status='queued'",params![nonce,agent_id])? == 1,
                "Worker already has a driver or is not queued.");
            Ok(())
        })?;
        let log_path = self.path(&format!(".okms/state/drivers/{agent_id}.log"))?;
        fs::create_dir_all(log_path.parent().unwrap())?;
        let helper = self.project.join(".okms/okms");
        let executable = if helper.is_file() {
            helper
        } else {
            std::env::current_exe()?
        };
        let spawn = (|| -> Result<std::process::Child> {
            let log = OpenOptions::new()
                .create(true)
                .append(true)
                .open(log_path)?;
            let mut command = Command::new(executable);
            command
                .args(["_run", "--project"])
                .arg(&self.project)
                .args([
                    "--input-json",
                    &json!({"agent_id":agent_id,"reason":reason,"nonce":nonce}).to_string(),
                ])
                .current_dir(&self.project)
                .stdin(Stdio::null())
                .stdout(log.try_clone()?)
                .stderr(log);
            process::isolate(&mut command);
            Ok(command.spawn()?)
        })();
        let child = match spawn {
            Ok(child) => child,
            Err(error) => {
                self.store.transact(|db| {
                    db.execute(
                        "UPDATE agents SET status='failed',notes=? WHERE id=? AND driver_nonce=?",
                        params![
                            json!({"error":error.to_string()}).to_string(),
                            agent_id,
                            nonce
                        ],
                    )?;
                    Ok(())
                })?;
                bail!("Driver launch failed: {error}");
            }
        };
        let pid = child.id();
        self.store.transact(|db| {
            db.execute(
                "UPDATE agents SET pid=? WHERE id=? AND status='starting' AND driver_nonce=?",
                params![pid, agent_id, nonce],
            )?;
            Ok(())
        })?;
        // A separate driver owns the provider process and persists completion. Reap
        // it here when this library is hosted by a long-lived process.
        std::thread::spawn(move || {
            let mut child = child;
            let _ = child.wait();
        });
        Ok(pid)
    }

    pub fn resume(&self, identity: &Value, data: &Value) -> Result<Value> {
        let target = self.store.transact(|db| {
            let actor = self.store.authenticate(db,identity,true)?;
            let target = first(db,"SELECT * FROM agents WHERE id=?",[util::string(data,"agent_id")?])?.context("Resume needs a registered worker.")?;
            ensure!(target["role"] == "worker","Resume needs a registered worker.");
            if target["status"] == "running" {
                ensure!(!target["pid"].as_i64().is_some_and(process::alive),"The worker driver is still running.");
            } else {
                ensure!(matches!(target["status"].as_str(),Some("queued"|"waiting_input"|"failed"|"cancelled")),
                    "Worker is not resumable; its result has already been returned or integrated.");
            }
            if util::seconds() >= target["deadline"].as_f64().context("Worker has no deadline.")? {
                let extension = data["extend_seconds"].as_f64().context("Deadline expired; an explicit positive extend_seconds is required.")?;
                ensure!(extension.is_finite() && extension > 0. && extension < 10_000_000.,"Deadline expired; an explicit positive extend_seconds is required.");
                db.execute("UPDATE agents SET deadline=? WHERE id=?",params![util::seconds()+extension,target["id"].as_str()])?;
            }
            ensure!(target["status"] == "queued" || target["native_session_id"].is_string(),
                "No saved provider session ID; preserve this worktree and dispatch a new assignment explicitly.");
            db.execute("UPDATE agents SET status='queued',pid=NULL WHERE id=?",[util::string(&target,"id")?])?;
            self.store.event(db,"resume_requested",actor["id"].as_str(),target["run_id"].as_str(),target["spec_id"].as_str(),json!({"worker":target["id"]}))?;
            Ok(target)
        })?;
        let id = util::string(&target, "id")?;
        Ok(
            json!({"agent_id":id,"driver_pid":self.launch(id,data["reason"].as_str().unwrap_or("Explicit resume; inspect saved changes first."))?}),
        )
    }

    pub fn send(&self, identity: &Value, data: &Value) -> Result<Value> {
        let message = self.store.send(identity, data)?;
        if message["to"] != "coordinator" {
            let wake = self.store.transact(|db| {
                let target = first(
                    db,
                    "SELECT * FROM agents WHERE id=?",
                    [util::string(&message, "to")?],
                )?
                .context("Message recipient disappeared.")?;
                let pending = first(
                    db,
                    "SELECT id FROM messages WHERE id=? AND acked=0",
                    [util::string(&message, "id")?],
                )?
                .is_some();
                let wake = pending
                    && target["status"] == "waiting_input"
                    && target["native_session_id"].is_string()
                    && util::seconds() < target["deadline"].as_f64().unwrap_or(0.);
                if wake {
                    db.execute(
                        "UPDATE agents SET status='queued' WHERE id=?",
                        [util::string(&target, "id")?],
                    )?;
                    self.store.event(
                        db,
                        "resume_requested",
                        message["from"].as_str(),
                        target["run_id"].as_str(),
                        target["spec_id"].as_str(),
                        json!({"worker":target["id"],"message_id":message["id"]}),
                    )?;
                }
                Ok(wake)
            })?;
            if wake {
                self.launch(
                    util::string(&message, "to")?,
                    "A peer message is queued; process and acknowledge your inbox.",
                )?;
            }
        }
        Ok(message)
    }

    pub fn verify(&self, identity: &Value, data: &Value) -> Result<Value> {
        let actor = self.actor(identity, false)?;
        let (checks, directory) = match actor["role"].as_str() {
            Some("worker") => {
                let assignment: Value = serde_json::from_str(util::string(&actor, "assignment")?)?;
                (
                    process::validate_checks(&assignment["checks"])?,
                    PathBuf::from(util::string(&actor, "worktree")?),
                )
            }
            Some("coordinator") => {
                self.actor(identity, true)?;
                (
                    process::validate_checks(self.config.get("checks").unwrap_or(&json!([])))?,
                    self.project.clone(),
                )
            }
            _ => bail!("Standby sessions cannot execute verification commands."),
        };
        ensure!(
            !checks.is_empty(),
            "Verification commands are unknown; fill actual checks in the team config or assignment."
        );
        let output = self
            .store
            .directory
            .join("verification")
            .join(util::identifier("verify"));
        let evidence = process::checks(&directory, &checks, &output, self.timeout().min(1800.))?;
        let passed = evidence.iter().all(|item| item["exit_code"] == 0);
        self.store.transact(|db| {
            self.store
                .authenticate(db, identity, actor["role"] == "coordinator")?;
            self.store.event(
                db,
                "verification_finished",
                actor["id"].as_str(),
                actor["run_id"].as_str(),
                actor["spec_id"].as_str(),
                json!({"passed":passed,"evidence":evidence}),
            )?;
            if actor["role"] == "coordinator"
                && let Some(run_id) = data["run_id"].as_str()
                && let Some(run) = first(db, "SELECT * FROM runs WHERE id=?", [run_id])?
                && run["status"] == "applied_unverified"
                && passed
            {
                let mut metadata: Value = serde_json::from_str(util::string(&run, "metadata")?)?;
                metadata["root_checks"] = json!(evidence);
                db.execute(
                    "UPDATE runs SET status='applied',metadata=? WHERE id=?",
                    params![metadata.to_string(), run_id],
                )?;
            }
            Ok(())
        })?;
        Ok(json!({"passed":passed,"evidence":evidence}))
    }

    pub fn integrate(&self, identity: &Value, data: &Value) -> Result<Value> {
        let review = util::string(data, "acceptance_review")?;
        ensure!(
            !review.trim().is_empty(),
            "Coordinator acceptance_review is required, including how reported gaps are covered."
        );
        let required = process::validate_checks(self.config.get("checks").unwrap_or(&json!([])))?;
        ensure!(
            !required.is_empty(),
            "Required integration checks are unknown; configure actual commands first."
        );
        let extra = process::validate_checks(data.get("checks").unwrap_or(&json!([])))?;
        let mut checks = required;
        for argv in extra {
            if !checks.contains(&argv) {
                checks.push(argv);
            }
        }
        let (actor, run, agents) = self.store.transact(|db| {
            let actor = self.store.authenticate(db, identity, true)?;
            let run = first(
                db,
                "SELECT * FROM runs WHERE id=?",
                [util::string(data, "run_id")?],
            )?
            .context("Integrate needs an active run with returned results.")?;
            ensure!(
                run["status"] == "active",
                "Integrate needs an active run with returned results."
            );
            let agents = rows(
                db,
                "SELECT * FROM agents WHERE run_id=? AND status!='cancelled' ORDER BY spec_id,id",
                [util::string(&run, "id")?],
            )?;
            ensure!(
                !agents.is_empty() && agents.iter().all(|a| a["status"] == "result_ready"),
                "Every noncancelled worker must return a valid result before integration."
            );
            db.execute(
                "UPDATE runs SET status='integrating' WHERE id=?",
                [util::string(&run, "id")?],
            )?;
            Ok((actor, run, agents))
        })?;
        let run_id = util::string(&run, "id")?;
        let baseline = util::string(&run, "baseline")?;
        let operation = (|| -> Result<Value> {
            let commits = agents
                .iter()
                .map(|agent| {
                    let result: Value = serde_json::from_str(util::string(agent, "notes")?)?;
                    Ok(util::string(&result, "revision")?.to_string())
                })
                .collect::<Result<Vec<_>>>()?;
            let integration = gitops::combine(&self.project, baseline, &commits)?;
            overlay(&self.project, &integration)?;
            let artifacts = self
                .store
                .directory
                .join("runs")
                .join(run_id)
                .join(util::identifier("integration-checks"));
            let checked = process::checks(&integration, &checks, &artifacts, self.timeout())?;
            ensure!(
                checked.iter().all(|r| r["exit_code"] == 0),
                "Combined checks failed; retained evidence: {}",
                artifacts.display()
            );
            let integrated = gitops::snapshot(
                &integration,
                Some(&format!("refs/okms/runs/{run_id}/integrated")),
            )?;
            let changed = gitops::paths_changed(&self.project, baseline, &integrated)?;
            let mut scopes = Vec::new();
            for agent in &agents {
                let assignment: Value = serde_json::from_str(util::string(agent, "assignment")?)?;
                scopes.extend(
                    assignment["owns"]
                        .as_array()
                        .context("Invalid assignment scope.")?
                        .iter()
                        .map(|s| {
                            s.as_str()
                                .context("Invalid assignment scope.")
                                .map(str::to_string)
                        })
                        .collect::<Result<Vec<_>>>()?,
                );
            }
            ensure!(
                changed.iter().all(|p| gitops::within(p, &scopes)),
                "Integration checks changed an unowned path; reconcile the retained worktree."
            );
            let mut metadata = self.store.transact(|db| {
                self.store.authenticate(db, identity, true)?;
                let paths = gitops::apply_to_root(&self.project, baseline, &integrated)?;
                let mut metadata: Value = serde_json::from_str(util::string(&run, "metadata")?)?;
                metadata["integration_worktree"] = json!(integration);
                metadata["revision"] = json!(integrated);
                metadata["combined_checks"] = json!(checked);
                metadata["acceptance_review"] = json!(review);
                metadata["changed_paths"] = json!(paths);
                db.execute(
                    "UPDATE runs SET status='applied_unverified',metadata=? WHERE id=?",
                    params![metadata.to_string(), run_id],
                )?;
                for agent in &agents {
                    db.execute(
                        "UPDATE agents SET status='integrated' WHERE id=?",
                        [util::string(agent, "id")?],
                    )?;
                }
                self.store.event(
                    db,
                    "integration_applied",
                    actor["id"].as_str(),
                    Some(run_id),
                    None,
                    metadata.clone(),
                )?;
                Ok(metadata)
            })?;
            let root_checks = process::checks(
                &self.project,
                &checks,
                &artifacts.join("root"),
                self.timeout(),
            )?;
            let passed = root_checks.iter().all(|r| r["exit_code"] == 0);
            metadata["root_checks"] = json!(root_checks);
            self.store.transact(|db| {
                db.execute(
                    "UPDATE runs SET status=?,metadata=? WHERE id=?",
                    params![
                        if passed {
                            "applied"
                        } else {
                            "applied_unverified"
                        },
                        metadata.to_string(),
                        run_id
                    ],
                )?;
                self.store.event(
                    db,
                    "root_verification_finished",
                    actor["id"].as_str(),
                    Some(run_id),
                    None,
                    json!({"passed":passed,"evidence":root_checks}),
                )?;
                Ok(())
            })?;
            metadata["run_id"] = json!(run_id);
            metadata["applied"] = json!(true);
            metadata["verified"] = json!(passed);
            Ok(metadata)
        })();
        if let Err(error) = &operation {
            self.store.transact(|db| {
                db.execute(
                    "UPDATE runs SET status='active' WHERE id=? AND status='integrating'",
                    [run_id],
                )?;
                self.store.event(
                    db,
                    "integration_failed",
                    actor["id"].as_str(),
                    Some(run_id),
                    None,
                    json!({"error":error.to_string()}),
                )?;
                Ok(())
            })?;
        }
        operation
    }

    pub fn checkpoint(&self, identity: &Value, data: &Value) -> Result<Value> {
        let relative = util::string(data, "plan")?;
        let plan = self.path(relative)?;
        self.store.transact(|db| {
            let actor = self.store.authenticate(db,identity,true)?;
            let mut text = fs::read_to_string(&plan)?;
            let work = work_rows(&text)?;
            let selected = work.iter().find(|row| Some(row.id.as_str()) == data["spec_id"].as_str()).context("Checkpoint needs an existing spec_id.")?;
            let state = util::string(data,"state")?;
            ensure!(["planned","in_progress","blocked","done","cancelled"].contains(&state),"Checkpoint needs a valid work state.");
            let evidence = data.get("evidence").map(|v|v.as_str().context("Evidence must fit one Work table cell.")).transpose()?.unwrap_or("Pending.");
            ensure!(!evidence.contains(['|','\n','\r']),"Evidence must fit one Work table cell.");
            if state == "done" {
                ensure!(data["acceptance_review"].as_str().is_some_and(|s|!s.trim().is_empty())
                    && !Regex::new(r"(?i)^(pending|not run|not verified)\b")?.is_match(evidence),
                    "Completion needs coordinator acceptance review and actual evidence.");
                let pending = first(db,"SELECT agents.id FROM agents JOIN runs ON agents.run_id=runs.id WHERE agents.spec_id=? AND runs.plan=? AND agents.status IN ('queued','starting','running','waiting_input','failed')",
                    params![selected.id,relative])?.is_some();
                let unverified = first(db,"SELECT 1 FROM runs WHERE plan=? AND status IN ('integrating','applied_unverified')",[relative])?.is_some();
                let candidates = rows(db,"SELECT assignment FROM agents JOIN runs ON agents.run_id=runs.id WHERE spec_id=? AND runs.plan=? AND agents.status='result_ready'",
                    params![selected.id,relative])?;
                let mut writers = false;
                for candidate in candidates {
                    let assignment: Value = serde_json::from_str(util::string(&candidate,"assignment")?)?;
                    writers |= assignment["owns"].as_array().is_some_and(|a|!a.is_empty());
                }
                ensure!(!pending && !unverified && !writers,"Necessary worker execution, integration, or root verification remains incomplete.");
            }
            let cells = selected.line.trim().trim_matches('|').split('|').map(str::trim).collect::<Vec<_>>();
            let replacement = format!("| {} | {} | {state} | {evidence} |",cells[0],cells[1]);
            text = text.replacen(&selected.line,&replacement,1);
            let resume = data["resume"].as_object().context("Checkpoint needs resume.current, resume.next, and resume.blocker.")?;
            for (key,title) in [("current","Current"),("next","Next"),("blocker","Blocker")] {
                let value = resume.get(key).and_then(Value::as_str).context("Checkpoint needs resume.current, resume.next, and resume.blocker.")?;
                ensure!(!value.contains(['\n','\r']),"Resume values must fit one line.");
                let pattern = Regex::new(&format!(r"(?m)^- {title}:.*$"))?;
                ensure!(pattern.is_match(&text),"Plan is missing its {title} Resume field.");
                text = pattern.replace_all(&text,regex::NoExpand(&format!("- {title}: {value}"))).into_owned();
            }
            let complete = work_rows(&text)?.iter().all(|row| ["done","cancelled"].contains(&row.state.as_str()));
            let plan_state = if complete {"done"}else{"in_progress"};
            text = Regex::new(r"(?m)^work_status:.*$")?.replace(&text,format!("work_status: {plan_state}")).into_owned();
            if complete {
                let result = util::string(data,"result")?;
                ensure!(!result.trim().is_empty() && !result.starts_with("Pending"),"A completed plan needs an actual Result.");
                let pattern = Regex::new(r"(?ms)(^## Result\s*\n).*\z")?;
                ensure!(pattern.is_match(&text),"Plan is missing its Result.");
                text = pattern.replace(&text,|caps: &regex::Captures|format!("{}\n{result}\n",&caps[1])).into_owned();
            }
            let index = self.docs.join("index.md");
            let index_text = fs::read_to_string(&index)?;
            let link = plan.strip_prefix(&self.docs)?.to_string_lossy();
            let active = Regex::new(r"(?s)(# Active work\s*\n)(.*?)(\n# |\z)")?;
            let updated_index = if let Some(section) = active.captures(&index_text) {
                let mut lines = section[2].lines().filter(|line| !line.contains(&format!("({link})"))
                    && !line.starts_with("No open work.") && *line != "None.").filter(|line|!line.trim().is_empty()).map(str::to_string).collect::<Vec<_>>();
                if !complete { lines.push(format!("- [Current plan]({link}) - Runtime-managed progress and recovery checkpoint.")); }
                let content = if lines.is_empty() {"No open work.".to_string()}else{lines.join("\n")};
                active.replacen(&index_text,1,|caps: &regex::Captures|format!("{}\n{content}\n{}",&caps[1],&caps[3])).into_owned()
            } else { index_text };
            util::atomic_write(&plan,text.as_bytes(),false)?;
            util::atomic_write(&index,updated_index.as_bytes(),false)?;
            self.store.event(db,"checkpoint_saved",actor["id"].as_str(),None,Some(&selected.id),
                json!({"plan":relative,"state":state,"evidence":evidence,"acceptance_review":data.get("acceptance_review")}))?;
            Ok(json!({"plan":relative,"work_status":plan_state,"spec_id":selected.id,"state":state}))
        })
    }

    pub fn stop(&self, identity: &Value, data: &Value) -> Result<Value> {
        self.store.transact(|db| {
            let actor = self.store.authenticate(db,identity,true)?;
            let target = first(db,"SELECT * FROM agents WHERE id=?",[util::string(data,"agent_id")?])?.context("Stop needs an unintegrated worker.")?;
            ensure!(target["role"] == "worker" && target["status"] != "integrated","Stop needs an unintegrated worker.");
            db.execute("UPDATE agents SET status='cancelled' WHERE id=?",[util::string(&target,"id")?])?;
            self.store.event(db,"worker_stop_requested",actor["id"].as_str(),target["run_id"].as_str(),target["spec_id"].as_str(),
                json!({"worker":target["id"],"reason":data.get("reason").cloned().unwrap_or(json!("Explicit stop"))}))?;
            Ok(json!({"agent_id":target["id"],"status":"cancelled","worktree_retained":target["worktree"]}))
        })
    }

    pub fn hook(&self, provider: &str, data: &Value) -> Result<Value> {
        ensure!(
            ["codex", "claude"].contains(&provider),
            "Hook requires a supported provider."
        );
        let event = data["hook_event_name"].as_str().unwrap_or("SessionStart");
        let bound = std::env::var("OKMS_AGENT_ID").ok();
        let (identity, identity_path) = if let Some(bound) = bound {
            if event == "SessionEnd" {
                return Ok(json!({}));
            }
            (
                json!({"agent_id":bound,"token":std::env::var("OKMS_AGENT_TOKEN").ok()}),
                None,
            )
        } else {
            let settings = &self.config["providers"][provider];
            let kind = data["agent_type"].as_str();
            if kind.is_some()
                && [
                    settings["worker_role"].as_str().unwrap_or("okms-worker"),
                    settings["reviewer_role"]
                        .as_str()
                        .unwrap_or("okms-reviewer"),
                ]
                .contains(&kind.unwrap())
            {
                return Ok(
                    json!({"hookSpecificOutput":{"hookEventName":event,"additionalContext":"You are a native helper. Return to your parent; do not claim coordination or alter shared progress."}}),
                );
            }
            let session = util::string(data, "session_id")?;
            if event == "SessionEnd" {
                self.store.transact(|db| {
                    if let Some(actor) = first(db,"SELECT * FROM agents WHERE provider=? AND session_id=?",params![provider,session])? {
                        db.execute("UPDATE agents SET status='ended' WHERE id=?",[util::string(&actor,"id")?])?;
                        db.execute("UPDATE owner SET agent_id=NULL,generation=generation+1 WHERE agent_id=?",[util::string(&actor,"id")?])?;
                        self.store.event(db,"session_ended",actor["id"].as_str(),None,None,json!({}))?;
                    }
                    Ok(())
                })?;
                return Ok(json!({}));
            }
            let joined = self.store.join(provider, session)?;
            let identity_path = joined["identity_file"].as_str().map(str::to_string);
            (joined, identity_path)
        };
        let actor = self.actor(&identity, false)?;
        self.store.transact(|db| {
            if data.get("permission_mode").is_some() {
                db.execute(
                    "UPDATE agents SET native_permission_mode=? WHERE id=?",
                    params![data["permission_mode"].as_str(), actor["id"].as_str()],
                )?;
            }
            self.store.event(
                db,
                "hook_received",
                actor["id"].as_str(),
                actor["run_id"].as_str(),
                actor["spec_id"].as_str(),
                json!({"provider":provider,"event":event}),
            )?;
            Ok(())
        })?;
        let inbox = self.store.inbox(&identity)?;
        let mut context = format!(
            "Hybrid Team role: {}. Read {}. ",
            util::string(&actor, "role")?,
            self.docs.join("workflow.md").display()
        );
        if let Some(path) = identity_path {
            context += &format!(
                "Runtime identity file: {path}. Use {} COMMAND --identity {} --input - with JSON stdin. ",
                util::shell_quote(&self.project.join(".okms/okms").to_string_lossy()),
                util::shell_quote(&path)
            );
        } else {
            context +=
                "Use .okms/okms COMMAND --input -; worker identity is already in the environment. ";
        }
        if actor["role"] == "standby" {
            context += "A coordinator is active. Observe or perform an explicit handoff/recovery; do not write shared progress. ";
        }
        context += &format!(
            "Acknowledge processed messages; returned worker results require coordinator acceptance. Inbox: {}",
            json!(inbox)
        );
        Ok(json!({"hookSpecificOutput":{"hookEventName":event,"additionalContext":context}}))
    }

    pub fn run(&self, data: &Value) -> Result<Value> {
        let agent_id = util::string(data, "agent_id")?;
        let nonce = util::string(data, "nonce")?;
        let result = worker::run(
            self,
            agent_id,
            data["reason"].as_str().unwrap_or("Initial assignment"),
            nonce,
        );
        if let Err(error) = &result {
            self.store.transact(|db| {
                let changed = db.execute("UPDATE agents SET status='failed',pid=NULL,notes=? WHERE id=? AND status='starting' AND driver_nonce=?",
                    params![json!({"error":error.to_string()}).to_string(),agent_id,nonce])?;
                if changed > 0 { self.store.event(db,"worker_failed",Some(agent_id),None,None,json!({"error":error.to_string()}))?; }
                Ok(())
            })?;
        }
        result
    }
}
