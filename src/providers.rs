use crate::process;
use anyhow::{Context, Result, bail, ensure};
use serde_json::{Value, json};
use std::path::Path;

pub fn result_schema() -> Value {
    json!({"type":"object","additionalProperties":false,
        "properties":{"summary":{"type":"string"},"evidence":{"type":"array","items":{"type":"string"}},
        "remaining":{"type":"array","items":{"type":"string"}},"next":{"type":"string"},
        "disposition":{"type":"string","enum":["result_ready","waiting_input"]}},
        "required":["summary","evidence","remaining","next","disposition"]})
}

pub fn parse_result(value: &Value) -> Option<Value> {
    let value = if let Some(text) = value.as_str() {
        serde_json::from_str(text.trim()).ok()?
    } else {
        value.clone()
    };
    let object = value.as_object()?;
    let required = ["summary", "evidence", "remaining", "next", "disposition"];
    if object.len() != required.len()
        || !required.iter().all(|key| object.contains_key(*key))
        || !["summary", "next"]
            .iter()
            .all(|key| value[*key].is_string())
        || !["evidence", "remaining"].iter().all(|key| {
            value[*key]
                .as_array()
                .is_some_and(|a| a.iter().all(Value::is_string))
        })
        || !matches!(
            value["disposition"].as_str(),
            Some("result_ready" | "waiting_input")
        )
    {
        return None;
    }
    Some(value)
}

fn arguments(value: &Value, label: &str) -> Result<Vec<String>> {
    value
        .as_array()
        .context(format!("{label} must be an argument array."))?
        .iter()
        .map(|s| {
            s.as_str()
                .filter(|s| !s.is_empty())
                .map(str::to_string)
                .context(format!("{label} needs nonempty string arguments."))
        })
        .collect()
}

pub fn prefix(config: &Value, provider: &str) -> Result<Vec<String>> {
    let settings = &config["providers"][provider];
    let argv = arguments(
        settings.get("command").unwrap_or(&json!([provider])),
        "Provider command",
    )?;
    ensure!(!argv.is_empty(), "Provider command needs an executable.");
    Ok(argv)
}

pub fn command(
    provider: &str,
    config: &Value,
    project: &Path,
    agent: &Value,
    artifact: &Path,
) -> Result<Vec<String>> {
    let settings = &config["providers"][provider];
    let mut argv = prefix(config, provider)?;
    let extra = arguments(settings.get("args").unwrap_or(&json!([])), "Provider args")?;
    let forbidden = [
        "--dangerously-skip-permissions",
        "--dangerously-bypass-approvals-and-sandbox",
        "--dangerously-bypass-hook-trust",
        "bypassPermissions",
        "--ephemeral",
        "--no-session-persistence",
        "--last",
        "--continue",
        "--ignore-rules",
    ];
    ensure!(
        !extra.iter().any(|arg| forbidden
            .iter()
            .any(|flag| arg == flag || arg.starts_with(&format!("{flag}=")))),
        "Worker arguments cannot bypass native trust/permissions or discard session identity."
    );
    let state = project.join(".okms/state").to_string_lossy().to_string();
    let session = agent["native_session_id"].as_str();
    match provider {
        "codex" => {
            argv.extend(
                ["--no-daemon", "--sandbox", "workspace-write", "--add-dir"].map(str::to_string),
            );
            argv.push(state);
            argv.extend(extra);
            argv.push("exec".to_string());
            if let Some(session) = session {
                argv.extend(["resume".to_string(), session.to_string()]);
            }
            argv.extend([
                "--json".to_string(),
                "--output-schema".to_string(),
                artifact
                    .join("result-schema.json")
                    .to_string_lossy()
                    .to_string(),
                "-".to_string(),
            ]);
        }
        "claude" => {
            argv.extend([
                "-p".to_string(),
                "--verbose".to_string(),
                "--output-format".to_string(),
                "stream-json".to_string(),
                "--json-schema".to_string(),
                result_schema().to_string(),
                "--permission-mode".to_string(),
                "acceptEdits".to_string(),
                "--permission-prompts".to_string(),
                "none".to_string(),
                "--add-dir".to_string(),
                state,
                "--tools".to_string(),
                "Read,Glob,Grep,Edit,Write,Bash,StructuredOutput".to_string(),
                "--allowedTools".to_string(),
                "Read,Glob,Grep,Edit,Write,StructuredOutput".to_string(),
                "Bash(.okms/okms *)".to_string(),
            ]);
            let role = settings["worker_role"].as_str().unwrap_or("okms-worker");
            ensure!(
                !role.contains(['/', '\\']) && !role.is_empty(),
                "Worker role must be a native role name."
            );
            if let Some(worktree) = agent["worktree"].as_str()
                && Path::new(worktree)
                    .join(format!(".claude/agents/{role}.md"))
                    .is_file()
            {
                argv.extend(["--agent".to_string(), role.to_string()]);
            }
            if let Some(session) = session {
                argv.extend(["--resume".to_string(), session.to_string()]);
            }
            argv.extend(extra);
        }
        _ => bail!("Unsupported provider: {provider}"),
    }
    Ok(argv)
}

pub struct Observation {
    pub native_session_id: Option<String>,
    pub result: Option<Value>,
    pub error: Option<Value>,
}

pub fn observation(provider: &str, record: &Value) -> Observation {
    let mut value = Observation {
        native_session_id: None,
        result: None,
        error: None,
    };
    match provider {
        "codex" => match record["type"].as_str() {
            Some("thread.started") => {
                value.native_session_id = record["thread_id"]
                    .as_str()
                    .filter(|s| !s.is_empty())
                    .map(str::to_string)
            }
            Some("item.completed") if record["item"]["type"] == "agent_message" => {
                value.result = parse_result(&record["item"]["text"])
            }
            Some("turn.failed" | "error") => {
                value.error = Some(
                    record
                        .get("error")
                        .or_else(|| record.get("message"))
                        .cloned()
                        .unwrap_or(json!("Provider reported failure.")),
                )
            }
            _ => {}
        },
        "claude" => {
            value.native_session_id = record["session_id"]
                .as_str()
                .filter(|s| !s.is_empty())
                .map(str::to_string);
            if record["type"] == "result" {
                value.result = parse_result(&record["structured_output"])
                    .or_else(|| parse_result(&record["result"]));
                if record["is_error"] == true
                    || record["permission_denials"]
                        .as_array()
                        .is_some_and(|v| !v.is_empty())
                {
                    value.error = Some(
                        if record["permission_denials"]
                            .as_array()
                            .is_some_and(|v| !v.is_empty())
                        {
                            record["permission_denials"].clone()
                        } else {
                            record
                                .get("result")
                                .cloned()
                                .unwrap_or(json!("Provider reported failure."))
                        },
                    );
                }
            } else if record["type"] == "system" && record["subtype"] == "permission_denied" {
                value.error = Some(record.clone());
            }
        }
        _ => value.error = Some(json!("Unsupported provider.")),
    }
    value
}

pub fn capabilities(config: &Value, project: &Path) -> Value {
    let mut result = json!({});
    for provider in ["codex", "claude"] {
        let mut record = json!({"available":false,"version":null,"authenticated":null});
        let observed = (|| -> Result<()> {
            let prefix = prefix(config, provider)?;
            let run = |args: &[&str]| {
                let argv = prefix
                    .iter()
                    .cloned()
                    .chain(args.iter().map(|s| (*s).to_string()))
                    .collect::<Vec<_>>();
                process::capture(project, &argv, 10.)
            };
            let (_, out, err) = run(&["--version"])?;
            record["available"] = json!(true);
            record["version"] = json!(
                if out.is_empty() { err } else { out }
                    .trim()
                    .chars()
                    .take(200)
                    .collect::<String>()
            );
            let (code, out, err) = run(if provider == "codex" {
                &["exec", "--help"]
            } else {
                &["--help"]
            })?;
            let help = out + &err;
            let flags: &[&str] = if provider == "codex" {
                &["--json", "--output-schema"]
            } else {
                &["--json-schema", "--output-format", "--resume"]
            };
            record["structured_output"] =
                json!(code == Some(0) && flags.iter().all(|f| help.contains(f)));
            let (code, out, _) = run(if provider == "codex" {
                &["login", "status"]
            } else {
                &["auth", "status", "--json"]
            })?;
            record["authenticated"] = json!(
                code == Some(0)
                    && (provider == "codex"
                        || serde_json::from_str::<Value>(&out)?["loggedIn"] == true)
            );
            Ok(())
        })();
        if observed.is_err() {
            record["probe_incomplete"] = json!(true);
        }
        result[provider] = record;
    }
    result
}
