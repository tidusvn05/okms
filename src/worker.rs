use crate::{gitops, process, providers, runtime::Runtime, state::first, util};
use anyhow::{Context, Result, ensure};
use rusqlite::params;
use serde_json::{Value, json};
use std::collections::BTreeSet;
use std::fs::{self, File};
use std::io::{BufRead, BufReader, Write};
use std::path::PathBuf;
use std::process::{Child, Command, Stdio};
use std::sync::mpsc;
use std::time::Duration;

pub fn run(runtime: &Runtime, agent_id: &str, reason: &str, nonce: &str) -> Result<Value> {
    let agent = runtime.store.transact(|db| {
        let row = first(db, "SELECT * FROM agents WHERE id=?", [agent_id])?
            .context("Worker is not queued; refusing a duplicate driver.")?;
        ensure!(
            row["role"] == "worker" && row["status"] == "starting" && row["driver_nonce"] == nonce,
            "Worker is not queued; refusing a duplicate driver."
        );
        db.execute(
            "UPDATE agents SET status='running',pid=? WHERE id=?",
            params![std::process::id(), agent_id],
        )?;
        runtime.store.event(
            db,
            "worker_started",
            Some(agent_id),
            row["run_id"].as_str(),
            row["spec_id"].as_str(),
            json!({"driver_pid":std::process::id()}),
        )?;
        Ok(row)
    })?;
    let run_id = util::string(&agent, "run_id")?;
    let directory = runtime.path(&format!(".okms/state/runs/{run_id}/{agent_id}"))?;
    let turn = directory.join(util::identifier("turn"));
    fs::create_dir_all(&turn)?;
    let assignment: Value = serde_json::from_str(util::string(&agent, "assignment")?)?;
    util::atomic_json(
        &turn.join("result-schema.json"),
        &providers::result_schema(),
    )?;
    let guidance = if agent["provider"] == "claude" {
        "For Bash, invoke ONLY .okms/okms using --input-json with shell-quoted JSON, or --input FILE. Prepare input files with Write under your worktree's ignored .okms/state directory. Pure inbox/verify calls need no input. Read files/logs with Read, not Bash cat. Use separate tool calls for polling; compound commands, wrappers, redirects and pipelines can require native approval.\n"
    } else {
        "Use your available file/shell tools for project reads and owned edits under the workspace sandbox. Codex may expose shell reads rather than a tool named Read; ordinary scoped shell commands are permitted. Use .okms/okms for messaging/status/assigned verification, not as a replacement for file reads.\n"
    };
    let identity = json!({"agent_id":agent_id,"token":agent["token"]});
    let pending = runtime.store.inbox(&identity)?;
    let mut prompt = format!(
        "You are an okms Hybrid Team worker, not the coordinator. Do not dispatch workers or edit shared progress.\n\
        Follow project instructions and the assignment below. Work only in your worktree and owned paths.\n\
        Use .okms/okms COMMAND --input - with JSON stdin. Its identity/project are in your OKMS environment.\n\
        Worker commands are status/send/inbox/ack/verify.\n{guidance}\
        Verify executes only the checks already assigned by the coordinator. Poll and acknowledge peer messages.\n\
        If input is needed, send a request and return disposition waiting_input. Do not fabricate evidence.\n\
        Return exactly the WorkerResult object below, without prose, Markdown, extra keys or nested evidence objects. \
        Use StructuredOutput when supplied by the CLI; otherwise return the same raw JSON object. \
        remaining lists every missing check or coverage gap.\nWorkerResult schema:\n{}\n{reason}\nAssignment:\n{assignment}\n",
        providers::result_schema()
    );
    if !pending.is_empty() {
        prompt += &format!("Unacknowledged inbox:\n{}\n", json!(pending));
    }
    fs::write(turn.join("prompt.txt"), &prompt)?;
    let provider = util::string(&agent, "provider")?;
    let argv = providers::command(provider, &runtime.config, &runtime.project, &agent, &turn)?;
    util::atomic_json(
        &turn.join("invocation.json"),
        &json!({"argv":argv,"cwd":agent["worktree"],"started_at":util::now()}),
    )?;
    let worktree = PathBuf::from(util::string(&agent, "worktree")?);
    let mut observed = None;
    let mut failure = None;
    let mut child: Option<Child> = None;
    let execution = (|| -> Result<()> {
        let errors = File::create(turn.join("stderr.log"))?;
        let mut command = Command::new(&argv[0]);
        command
            .args(&argv[1..])
            .current_dir(&worktree)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(errors)
            .env_remove("CLAUDECODE")
            .env("OKMS_PROJECT", &runtime.project)
            .env("OKMS_AGENT_ID", agent_id)
            .env("OKMS_AGENT_TOKEN", util::string(&agent, "token")?);
        process::isolate(&mut command);
        let process = child.insert(command.spawn()?);
        let stdout = process.stdout.take().context("Provider has no stdout.")?;
        let mut raw = File::create(turn.join("stdout.jsonl"))?;
        let (sender, receiver) = mpsc::channel::<Option<Vec<u8>>>();
        let reader = std::thread::spawn(move || {
            let mut stream = BufReader::new(stdout);
            loop {
                let mut line = Vec::new();
                match stream.read_until(b'\n', &mut line) {
                    Ok(0) | Err(_) => break,
                    Ok(_) => {
                        if raw.write_all(&line).and_then(|_| raw.flush()).is_err() {
                            break;
                        }
                        if sender.send(Some(line)).is_err() {
                            break;
                        }
                    }
                }
            }
            let _ = sender.send(None);
        });
        process
            .stdin
            .take()
            .context("Provider has no stdin.")?
            .write_all(prompt.as_bytes())?;
        loop {
            let status = first(
                &runtime.store.connection()?,
                "SELECT status FROM agents WHERE id=?",
                [agent_id],
            )?
            .context("Worker disappeared.")?;
            if status["status"] == "cancelled" {
                failure = Some("Worker stopped by coordinator.".to_string());
                process::stop(process);
            }
            if util::seconds()
                >= agent["deadline"]
                    .as_f64()
                    .context("Worker has no deadline.")?
            {
                failure = Some("Assignment deadline expired; no automatic retry.".to_string());
                process::stop(process);
            }
            match receiver.recv_timeout(Duration::from_millis(250)) {
                Ok(Some(line)) => {
                    let Ok(record) = serde_json::from_slice::<Value>(&line) else {
                        continue;
                    };
                    if !record.is_object() {
                        continue;
                    }
                    let observation = providers::observation(provider, &record);
                    if let Some(session) = observation.native_session_id {
                        runtime.store.transact(|db| {
                            db.execute(
                                "UPDATE agents SET native_session_id=? WHERE id=?",
                                params![session, agent_id],
                            )?;
                            Ok(())
                        })?;
                    }
                    if let Some(result) = observation.result {
                        observed = Some(result);
                    }
                    if let Some(error) = observation.error {
                        failure = Some(error.to_string());
                    }
                }
                Ok(None) | Err(mpsc::RecvTimeoutError::Disconnected) => break,
                Err(mpsc::RecvTimeoutError::Timeout) => {
                    if process.try_wait()?.is_some() && reader.is_finished() {
                        break;
                    }
                }
            }
        }
        let code = process::wait(process, 10.)?;
        if code != Some(0) && failure.is_none() {
            failure = Some(format!(
                "Provider exited with code {code:?}; inspect stderr.log."
            ));
        }
        if observed.is_none() && failure.is_none() {
            failure = Some("Provider returned no schema-valid WorkerResult.".to_string());
        }
        process::stop(process);
        if reader.is_finished() {
            let _ = reader.join();
        }
        Ok(())
    })();
    if let Err(error) = execution {
        failure = Some(format!("{error:#}"));
    }
    if let Some(mut child) = child {
        process::stop(&mut child);
    }
    let revision = match gitops::snapshot(&worktree, None) {
        Ok(revision) => Some(revision),
        Err(error) => {
            if failure.is_none() {
                failure = Some(error.to_string());
            }
            None
        }
    };
    let mut paths = Vec::new();
    if let Some(revision) = &revision {
        let scope = assignment["owns"]
            .as_array()
            .context("Saved assignment has no scopes.")?
            .iter()
            .map(|v| {
                v.as_str()
                    .context("Invalid saved scope.")
                    .map(str::to_string)
            })
            .collect::<Result<Vec<_>>>()?;
        let run = first(
            &runtime.store.connection()?,
            "SELECT baseline FROM runs WHERE id=?",
            [run_id],
        )?
        .context("Worker run disappeared.")?;
        paths = gitops::paths_changed(&runtime.project, util::string(&run, "baseline")?, revision)?;
        let forbidden = paths
            .iter()
            .filter(|path| !gitops::within(path, &scope))
            .cloned()
            .collect::<Vec<_>>();
        if !forbidden.is_empty() {
            failure = Some(format!(
                "Out-of-scope changes retained but rejected: {}",
                forbidden.join(", ")
            ));
        }
    }
    let result = json!({"worker_result":observed,"error":failure,"revision":revision,"changed_paths":paths,
        "artifact":turn,"finished_at":util::now()});
    util::atomic_json(&directory.join("result.json"), &result)?;
    let initial_ids = pending
        .iter()
        .filter_map(|v| v["id"].as_str())
        .collect::<BTreeSet<_>>();
    let wake = runtime.store.transact(|db| {
        let current = first(db, "SELECT status FROM agents WHERE id=?", [agent_id])?
            .context("Worker disappeared.")?;
        let state = if current["status"] == "cancelled" {
            "cancelled"
        } else if failure.is_some() {
            "failed"
        } else {
            observed
                .as_ref()
                .and_then(|v| v["disposition"].as_str())
                .context("Worker result is missing.")?
        };
        db.execute(
            "UPDATE agents SET status=?,pid=NULL,notes=? WHERE id=?",
            params![state, result.to_string(), agent_id],
        )?;
        runtime.store.event(
            db,
            if failure.is_some() {
                "worker_failed"
            } else {
                state
            },
            Some(agent_id),
            Some(run_id),
            agent["spec_id"].as_str(),
            result.clone(),
        )?;
        let newer = crate::state::rows(
            db,
            "SELECT id FROM messages WHERE recipient=? AND acked=0",
            [agent_id],
        )?
        .iter()
        .any(|v| v["id"].as_str().is_some_and(|id| !initial_ids.contains(id)));
        let row = first(
            db,
            "SELECT native_session_id FROM agents WHERE id=?",
            [agent_id],
        )?
        .context("Worker disappeared.")?;
        let wake = state == "waiting_input"
            && newer
            && row["native_session_id"].is_string()
            && util::seconds() < agent["deadline"].as_f64().unwrap_or(0.);
        if wake {
            db.execute("UPDATE agents SET status='queued' WHERE id=?", [agent_id])?;
            runtime.store.event(
                db,
                "resume_requested",
                Some(agent_id),
                Some(run_id),
                agent["spec_id"].as_str(),
                json!({"reason":"Message arrived during the previous turn"}),
            )?;
        }
        Ok(wake)
    })?;
    if wake {
        runtime.launch(
            agent_id,
            "A message arrived before you began waiting; process and acknowledge your inbox.",
        )?;
    }
    Ok(result)
}
