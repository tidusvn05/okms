use crate::{state::Store, util};
use anyhow::{Context, Result, ensure};
use regex::Regex;
use serde_json::{Value, json};
use std::collections::BTreeMap;
use std::fs;
use std::path::{Component, Path};

include!(concat!(env!("OUT_DIR"), "/payload.rs"));

fn body(name: &str) -> Result<&'static [u8]> {
    PAYLOAD
        .iter()
        .find(|(path, _)| *path == name)
        .map(|(_, bytes)| *bytes)
        .context(format!("Missing embedded asset: {name}"))
}

fn existing_json(path: &Path) -> Result<Value> {
    let value = if path.exists() {
        util::json(path)?
    } else {
        json!({})
    };
    ensure!(
        value.is_object(),
        "Expected an existing JSON object; unchanged: {}",
        path.display()
    );
    Ok(value)
}

fn occupied(path: &Path) -> Result<bool> {
    if !path.exists() {
        return Ok(false);
    }
    ensure!(
        path.is_dir(),
        "Documentation destination is not a directory; unchanged."
    );
    Ok(fs::read_dir(path)?.next().is_some())
}

fn hooks(path: &Path, provider: &str) -> Result<Vec<u8>> {
    let original = existing_json(path)?;
    let mut value = original.clone();
    let object = value
        .as_object_mut()
        .unwrap()
        .entry("hooks")
        .or_insert(json!({}))
        .as_object_mut()
        .context("Existing hooks must be an object; unchanged.")?;
    let command =
        format!("\"$(git rev-parse --show-toplevel)/.okms/okms\" hook --provider {provider}");
    for event in [
        "SessionStart",
        "UserPromptSubmit",
        "PostToolUse",
        "SessionEnd",
    ] {
        let groups = object
            .entry(event)
            .or_insert(json!([]))
            .as_array_mut()
            .context("Existing hook groups must be arrays; unchanged.")?;
        ensure!(
            groups
                .iter()
                .all(|group| group.is_object() && group.get("hooks").is_none_or(Value::is_array)),
            "Existing hook groups need review; unchanged."
        );
        let matching = groups.iter().any(|group| {
            group["hooks"]
                .as_array()
                .is_some_and(|items| items.iter().any(|item| item["command"] == command))
        });
        if !matching {
            groups.push(json!({"hooks":[{"type":"command","command":command,"timeout":5}]}));
        }
    }
    if path.exists() && value == original {
        return Ok(fs::read(path)?);
    }
    Ok([serde_json::to_vec_pretty(&value)?.as_slice(), b"\n"].concat())
}

pub fn install(project: &Path, docs: Option<&str>, dry_run: bool) -> Result<Value> {
    let project = project.canonicalize()?;
    ensure!(
        project.is_dir(),
        "The destination project must already exist."
    );
    let manifest_path = util::project_path(&project, ".okms/install.json")?;
    let manifest = existing_json(&manifest_path)?;
    let installed = !manifest.as_object().unwrap().is_empty();
    if installed {
        ensure!(
            manifest["profile"] == "hybrid-team",
            "Existing .okms installation is not Hybrid Team; preserve it and resolve the namespace explicitly."
        );
        ensure!(
            manifest["version"] == crate::VERSION,
            "Repeated setup does not upgrade an existing profile (installed {}, requested {}). Review the version change explicitly.",
            manifest["version"],
            crate::VERSION
        );
    }
    let selected = if installed {
        let selected = util::string(&manifest, "docs_path")?;
        ensure!(
            docs.is_none_or(|path| path == selected),
            "Repeated setup preserves the installed documentation path."
        );
        selected.to_string()
    } else if let Some(docs) = docs {
        docs.to_string()
    } else {
        let mut selected = "docs".to_string();
        if occupied(&util::project_path(&project, &selected)?)? {
            selected = "docs/okms".to_string();
            if occupied(&util::project_path(&project, &selected)?)? {
                selected = "docs/okms-hybrid".to_string();
                let mut number = 2;
                while occupied(&util::project_path(&project, &selected)?)? {
                    selected = format!("docs/okms-hybrid-{number}");
                    number += 1;
                }
            }
        }
        selected
    };
    let selected_path = Path::new(&selected);
    ensure!(
        !selected.is_empty()
            && !selected.contains('\\')
            && !selected_path.is_absolute()
            && selected
                .split('/')
                .all(|part| !part.is_empty() && part != "." && part != "..")
            && selected_path
                .components()
                .all(|part| matches!(part, Component::Normal(_)))
            && ![".git", ".okms", ".codex", ".claude", ".agents"]
                .contains(&selected.split('/').next().unwrap()),
        "Documentation path must be a project-relative documentation directory."
    );
    let destination = util::project_path(&project, &selected)?;
    if !installed && occupied(&destination)? {
        let workflow = destination.join("workflow.md");
        ensure!(
            workflow.is_file()
                && Regex::new(r"(?m)^template:\s*hybrid-team\s*$")?
                    .is_match(&fs::read_to_string(&workflow)?)
                && fs::read_to_string(&workflow)?
                    .contains(&format!("template_version: \"{}\"", crate::VERSION)),
            "Explicit documentation destination is occupied; unchanged."
        );
    }
    let mut assets = BTreeMap::new();
    assets.insert(
        ".okms/okms".to_string(),
        fs::read(std::env::current_exe()?)?,
    );
    assets.insert(
        ".okms/LICENSE-MIT".to_string(),
        include_bytes!("../LICENSE-MIT").to_vec(),
    );
    assets.insert(
        ".okms/LICENSE-APACHE".to_string(),
        include_bytes!("../LICENSE-APACHE").to_vec(),
    );
    for (path, bytes) in PAYLOAD.iter().filter(|(path, _)| path.starts_with("docs/")) {
        assets.insert(
            format!("{selected}/{}", path.strip_prefix("docs/").unwrap()),
            bytes.to_vec(),
        );
    }
    let mut roles = manifest.get("native_roles").cloned().unwrap_or(json!({}));
    ensure!(
        roles.is_object(),
        "Installed native_roles must be an object."
    );
    let mut skills = manifest.get("skills").cloned().unwrap_or(json!({}));
    ensure!(skills.is_object(), "Installed skills must be an object.");
    let managed = manifest.get("files").cloned().unwrap_or(json!({}));
    ensure!(managed.is_object(), "Installed files must be an object.");
    for provider in ["codex", "claude"] {
        for role in ["worker", "reviewer"] {
            let key = format!("{provider}_{role}");
            let extension = if provider == "codex" { "toml" } else { "md" };
            let source =
                std::str::from_utf8(body(&format!("native/{provider}/okms-{role}.{extension}"))?)?;
            let mut name = roles[&key]
                .as_str()
                .unwrap_or(&format!("okms-{role}"))
                .to_string();
            ensure!(
                !name.contains(['/', '\\']) && !name.is_empty(),
                "Installed role name needs review."
            );
            let mut number = 2;
            let (relative, rendered) = loop {
                let relative = format!(".{provider}/agents/{name}.{extension}");
                let target = util::project_path(&project, &relative)?;
                let rendered = source.replace(&format!("okms-{role}"), &name);
                if managed.get(&relative).is_some()
                    || !target.exists()
                    || fs::read_to_string(target)? == rendered
                {
                    break (relative, rendered);
                }
                name = format!("okms-team-{role}-{number}");
                number += 1;
            };
            roles[&key] = json!(name);
            assets.insert(relative, rendered.into_bytes());
        }
    }
    for skill in ["okms-coordinate", "okms-work"] {
        let source = std::str::from_utf8(body(&format!("skills/{skill}/SKILL.md"))?)?;
        for native in [".agents", ".claude"] {
            let key = format!("{native}/{skill}");
            let mut name = skills[&key].as_str().unwrap_or(skill).to_string();
            ensure!(
                !name.contains(['/', '\\']) && !name.is_empty(),
                "Installed skill name needs review."
            );
            let mut number = 2;
            let (relative, rendered) = loop {
                let relative = format!("{native}/skills/{name}/SKILL.md");
                let target = util::project_path(&project, &relative)?;
                let rendered =
                    source.replacen(&format!("name: {skill}"), &format!("name: {name}"), 1);
                if managed.get(&relative).is_some()
                    || !target.exists()
                    || fs::read_to_string(target)? == rendered
                {
                    break (relative, rendered);
                }
                name = format!("{skill}-{number}");
                number += 1;
            };
            skills[&key] = json!(name);
            assets.insert(relative, rendered.into_bytes());
        }
    }
    let config_path = util::project_path(&project, ".okms/team.json")?;
    if !config_path.exists() {
        let config = json!({"schema_version":1,"profile":"hybrid-team","template_version":crate::VERSION,"runtime":"rust",
            "docs_path":selected,"max_workers":2,"assignment_timeout_seconds":1800,"checks":[],
            "providers":{"codex":{"command":["codex"],"args":[],"worker_role":roles["codex_worker"],"reviewer_role":roles["codex_reviewer"]},
                "claude":{"command":["claude"],"args":[],"worker_role":roles["claude_worker"],"reviewer_role":roles["claude_reviewer"]}}});
        assets.insert(
            ".okms/team.json".to_string(),
            [serde_json::to_vec_pretty(&config)?.as_slice(), b"\n"].concat(),
        );
    } else {
        let config = existing_json(&config_path)?;
        ensure!(
            config["profile"] == "hybrid-team"
                && config["docs_path"] == selected
                && (installed || config["template_version"] == crate::VERSION),
            "Existing team config is owned by another installation; unchanged."
        );
    }
    let mut changes = BTreeMap::new();
    let mut drift = Vec::new();
    for (relative, bytes) in &assets {
        let target = util::project_path(&project, relative)?;
        if target.exists() {
            if fs::read(&target)? != *bytes {
                ensure!(
                    relative.starts_with(&format!("{selected}/"))
                        || managed.get(relative).is_some(),
                    "Unmanaged runtime file collision; unchanged: {relative}"
                );
                drift.push(relative.clone());
            }
        } else {
            changes.insert(relative.clone(), bytes.clone());
        }
    }
    for (relative, provider) in [
        (".codex/hooks.json", "codex"),
        (".claude/settings.json", "claude"),
    ] {
        let target = util::project_path(&project, relative)?;
        let bytes = hooks(&target, provider)?;
        if !target.exists() || fs::read(&target)? != bytes {
            changes.insert(relative.to_string(), bytes);
        }
    }
    if !util::project_path(&project, ".codex/config.toml")?.exists() {
        changes.insert(".codex/config.toml".to_string(),b"# Project-owned Codex configuration; Hybrid Team hooks and roles are alongside this file.\n".to_vec());
    }
    for relative in ["AGENTS.md", "CLAUDE.md"] {
        let target = util::project_path(&project, relative)?;
        let current = if target.exists() {
            fs::read_to_string(&target)?
        } else {
            String::new()
        };
        let pointer = format!(
            "Hybrid Team is the explicitly selected team profile. For runtime-coordinated work, follow [its workflow]({selected}/workflow.md), starting with [its index]({selected}/index.md). Existing project instructions and work records remain applicable."
        );
        if !current.contains(&pointer) {
            changes.insert(
                relative.to_string(),
                format!(
                    "{current}{}{pointer}\n",
                    if current.is_empty() { "" } else { "\n" }
                )
                .into_bytes(),
            );
        }
    }
    let ignored = util::project_path(&project, ".gitignore")?;
    let current = if ignored.exists() {
        fs::read_to_string(&ignored)?
    } else {
        String::new()
    };
    let mut updated = current.clone();
    for line in ["/.okms/state/", "/.okms/okms"] {
        if !current.lines().any(|saved| saved == line) {
            if !updated.is_empty() && !updated.ends_with('\n') {
                updated.push('\n');
            }
            updated += &format!("{line}\n");
        }
    }
    if updated != current {
        changes.insert(".gitignore".to_string(), updated.into_bytes());
    }
    let mut records = managed.as_object().unwrap().clone();
    for (relative, bytes) in assets.iter().chain(changes.iter()) {
        records
            .entry(relative.clone())
            .or_insert_with(|| json!(util::digest(bytes)));
    }
    let updated = json!({"profile":"hybrid-team","version":crate::VERSION,"runtime":"rust","docs_path":selected,
        "native_roles":roles,"skills":skills,"files":records});
    if !installed || manifest != updated {
        changes.insert(
            ".okms/install.json".to_string(),
            [serde_json::to_vec_pretty(&updated)?.as_slice(), b"\n"].concat(),
        );
    }
    let database = util::project_path(&project, ".okms/state/team.sqlite3")?;
    let create_database = !database.exists();
    if database.exists() {
        ensure!(
            database.is_file(),
            "Operational state path is not a file; unchanged."
        );
    }
    let mut originals = BTreeMap::new();
    for relative in changes
        .keys()
        .map(String::as_str)
        .chain(std::iter::once(".okms/state/team.sqlite3"))
    {
        let target = util::project_path(&project, relative)?;
        let pending = target.with_file_name(format!(
            "{}.okms-new",
            target.file_name().unwrap().to_string_lossy()
        ));
        ensure!(
            fs::symlink_metadata(&pending).is_err(),
            "Temporary setup path is occupied; preserve it: {}",
            pending.display()
        );
        for parent in target.ancestors().skip(1) {
            if parent == project {
                break;
            }
            ensure!(
                !parent.exists() || parent.is_dir(),
                "Installation parent is not a directory; unchanged: {}",
                parent.display()
            );
        }
        originals.insert(
            relative.to_string(),
            if target.exists() {
                Some(fs::read(&target)?)
            } else {
                None
            },
        );
    }
    let mut changed = changes.keys().cloned().collect::<Vec<_>>();
    if create_database {
        changed.push(".okms/state/team.sqlite3".to_string());
        changed.sort();
    }
    if !dry_run {
        for (relative, original) in originals {
            let target = util::project_path(&project, &relative)?;
            let current = if target.exists() {
                Some(fs::read(&target)?)
            } else {
                None
            };
            ensure!(
                current == original,
                "Project changed during setup; review before continuing: {relative}"
            );
        }
        for (relative, bytes) in changes {
            let target = util::project_path(&project, &relative)?;
            util::atomic_write(&target, &bytes, false)?;
            if relative == ".okms/okms" {
                #[cfg(unix)]
                {
                    use std::os::unix::fs::PermissionsExt;
                    fs::set_permissions(&target, fs::Permissions::from_mode(0o755))?;
                }
            }
        }
        if create_database {
            Store::new(&project)?;
        }
    }
    Ok(
        json!({"profile":"hybrid-team","version":crate::VERSION,"runtime":"rust","docs_path":selected,"dry_run":dry_run,
        "changed":changed,"preserved_project_edits":drift,"native_roles":roles,
        "next":"Fill actual context/check argv arrays, run doctor, and review native hook trust/loading. Setup launches no agent."}),
    )
}
