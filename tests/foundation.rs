use okms::state::Store;
use serde_json::{Value, json};
use std::fs;
use std::path::Path;
use std::process::{Command, Output};

fn project() -> tempfile::TempDir {
    let temporary = tempfile::tempdir().unwrap();
    fs::create_dir(temporary.path().join(".okms")).unwrap();
    fs::write(
        temporary.path().join(".okms/team.json"),
        json!({
            "schema_version":1,"docs_path":"docs","max_workers":2,"assignment_timeout_seconds":30,
            "checks":[],"providers":{}
        })
        .to_string(),
    )
    .unwrap();
    fs::write(
        temporary.path().join("notes.txt"),
        "Keep project-owned notes.\n",
    )
    .unwrap();
    temporary
}

fn invoke(project: &Path, args: &[&str]) -> Output {
    Command::new(env!("CARGO_BIN_EXE_okms"))
        .args(args)
        .arg("--project")
        .arg(project)
        .env_remove("OKMS_PROJECT")
        .env_remove("OKMS_AGENT_ID")
        .env_remove("OKMS_AGENT_TOKEN")
        .output()
        .unwrap()
}

fn success(output: Output) -> Value {
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stdout)
    );
    serde_json::from_slice(&output.stdout).unwrap()
}

fn join(project: &Path, session: &str) -> Value {
    success(invoke(
        project,
        &[
            "join",
            "--provider",
            "codex",
            "--input-json",
            &json!({"session_id":session}).to_string(),
        ],
    ))
}

#[test]
fn concurrent_native_processes_elect_one_owner_and_fence_handoff() {
    let fixture = project();
    let threads = (0..6)
        .map(|n| {
            let path = fixture.path().to_path_buf();
            std::thread::spawn(move || join(&path, &format!("root-{n}")))
        })
        .collect::<Vec<_>>();
    let values = threads
        .into_iter()
        .map(|t| t.join().unwrap())
        .collect::<Vec<_>>();
    let owner = values.iter().find(|v| v["role"] == "coordinator").unwrap();
    assert_eq!(
        values.iter().filter(|v| v["role"] == "coordinator").count(),
        1
    );
    let standby = values.iter().find(|v| v["role"] == "standby").unwrap();
    let previous = owner.clone();
    let promoted = success(invoke(
        fixture.path(),
        &[
            "handoff",
            "--identity",
            owner["identity_file"].as_str().unwrap(),
            "--input-json",
            &json!({"to":standby["agent_id"]}).to_string(),
        ],
    ));
    let store = Store::new(fixture.path()).unwrap();
    assert!(
        store
            .authenticate(&store.connection().unwrap(), &previous, true)
            .is_err()
    );
    store
        .authenticate(&store.connection().unwrap(), &promoted, true)
        .unwrap();
    let old_file: Value =
        serde_json::from_slice(&fs::read(owner["identity_file"].as_str().unwrap()).unwrap())
            .unwrap();
    assert_eq!(
        store
            .authenticate(&store.connection().unwrap(), &old_file, false)
            .unwrap()["role"],
        "standby"
    );
    assert!(
        store
            .authenticate(&store.connection().unwrap(), &old_file, true)
            .is_err()
    );
    let recovered = store.handoff(&old_file, None, true).unwrap();
    assert!(
        store
            .authenticate(&store.connection().unwrap(), &promoted, true)
            .is_err()
    );
    store
        .authenticate(&store.connection().unwrap(), &recovered, true)
        .unwrap();
    assert_eq!(
        fs::read_to_string(fixture.path().join("notes.txt")).unwrap(),
        "Keep project-owned notes.\n"
    );
}

#[test]
fn message_delivery_is_persistent_idempotent_and_recipient_owned() {
    let fixture = project();
    let owner = join(fixture.path(), "owner");
    let peer = join(fixture.path(), "peer");
    let store = Store::new(fixture.path()).unwrap();
    let request = json!({"id":"stable-request","to":peer["agent_id"],"type":"request","payload":{"question":"Read the saved contract."}});
    let saved = store.send(&owner, &request).unwrap();
    assert_eq!(
        saved,
        Store::new(fixture.path())
            .unwrap()
            .send(&owner, &request)
            .unwrap()
    );
    let identity = peer["identity_file"].as_str().unwrap();
    let fresh = success(invoke(fixture.path(), &["inbox", "--identity", identity]));
    assert_eq!(fresh["messages"][0]["id"], "stable-request");
    assert!(store.ack(&owner, "stable-request").is_err());
    assert!(!invoke(fixture.path(), &["send","--identity",owner["identity_file"].as_str().unwrap(),
        "--input-json",&json!({"id":"stable-request","to":peer["agent_id"],"payload":{"question":"Changed"}}).to_string()]).status.success());
    success(invoke(
        fixture.path(),
        &[
            "ack",
            "--identity",
            identity,
            "--input-json",
            r#"{"id":"stable-request"}"#,
        ],
    ));
    success(invoke(
        fixture.path(),
        &[
            "ack",
            "--identity",
            identity,
            "--input-json",
            r#"{"id":"stable-request"}"#,
        ],
    ));
    assert!(store.inbox(&peer).unwrap().is_empty());
    let events = store.status().unwrap()["events"]
        .as_array()
        .unwrap()
        .clone();
    assert_eq!(
        events
            .iter()
            .filter(|v| v["type"] == "message_acknowledged")
            .count(),
        1
    );
    assert!(
        events
            .windows(2)
            .all(|v| v[0]["sequence"].as_i64().unwrap() < v[1]["sequence"].as_i64().unwrap())
    );
}

#[test]
fn coordinator_alias_survives_handoff_and_worker_scope_is_enforced() {
    let fixture = project();
    let store = Store::new(fixture.path()).unwrap();
    let owner = store.join("codex", "owner").unwrap();
    let receiver = store.join("claude", "standby").unwrap();
    store.transact(|db| {
        db.execute("INSERT INTO agents(id,provider,role,token,status,run_id) VALUES('worker-a','codex','worker','secret-a','queued','run-a')",[])?;
        db.execute("INSERT INTO agents(id,provider,role,token,status,run_id) VALUES('worker-b','claude','worker','secret-b','queued','run-b')",[])?;
        Ok(())
    }).unwrap();
    let worker = json!({"agent_id":"worker-a","token":"secret-a"});
    let message = store
        .send(
            &worker,
            &json!({"to":"coordinator","payload":{"question":"Continue after handoff"}}),
        )
        .unwrap();
    assert!(
        store
            .send(&worker, &json!({"to":"worker-b","payload":{}}))
            .is_err()
    );
    let promoted = store
        .handoff(&owner, receiver["agent_id"].as_str(), false)
        .unwrap();
    assert_eq!(store.inbox(&promoted).unwrap()[0]["id"], message["id"]);
    store
        .ack(&promoted, message["id"].as_str().unwrap())
        .unwrap();
    let status = success(invoke(
        fixture.path(),
        &[
            "status",
            "--identity",
            promoted["identity_file"].as_str().unwrap(),
        ],
    ));
    assert!(
        status["agents"]
            .as_array()
            .unwrap()
            .iter()
            .all(|a| a.get("token").is_none() && a.get("driver_nonce").is_none())
    );
}

#[test]
fn native_binary_rejects_invalid_input_and_reads_file_or_stdin() {
    use std::io::Write;
    use std::process::Stdio;
    let fixture = project();
    for value in ["[]", "null", "not JSON"] {
        let result = invoke(
            fixture.path(),
            &["join", "--provider", "codex", "--input-json", value],
        );
        assert!(!result.status.success());
        let error: Value = serde_json::from_slice(&result.stdout).unwrap();
        assert_eq!(error["incomplete"], true);
    }
    fs::write(
        fixture.path().join("input.json"),
        r#"{"session_id":"from-file"}"#,
    )
    .unwrap();
    success(invoke(
        fixture.path(),
        &[
            "join",
            "--provider",
            "codex",
            "--input",
            fixture.path().join("input.json").to_str().unwrap(),
        ],
    ));
    let mut process = Command::new(env!("CARGO_BIN_EXE_okms"))
        .args(["join", "--provider", "claude", "--input", "-", "--project"])
        .arg(fixture.path())
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .unwrap();
    process
        .stdin
        .take()
        .unwrap()
        .write_all(br#"{"session_id":"from-stdin"}"#)
        .unwrap();
    success(process.wait_with_output().unwrap());
    let denied = invoke(fixture.path(), &["status", "--input-json", "{}"]);
    assert!(!denied.status.success());
    assert!(String::from_utf8_lossy(&denied.stdout).contains("stale identity"));
    let help = Command::new(env!("CARGO_BIN_EXE_okms"))
        .arg("--help")
        .output()
        .unwrap();
    assert!(help.status.success());
    assert!(String::from_utf8_lossy(&help.stdout).contains("dispatch"));
    let version = Command::new(env!("CARGO_BIN_EXE_okms"))
        .arg("--version")
        .output()
        .unwrap();
    assert_eq!(
        String::from_utf8(version.stdout).unwrap().trim(),
        format!("okms {}", okms::VERSION)
    );
}

#[cfg(unix)]
#[test]
fn state_paths_cannot_follow_links_outside_the_project() {
    use std::os::unix::fs::symlink;
    let fixture = project();
    let outside = tempfile::tempdir().unwrap();
    fs::write(
        outside.path().join("keep.sqlite3"),
        b"Preserve external bytes",
    )
    .unwrap();
    fs::create_dir(fixture.path().join(".okms/state")).unwrap();
    symlink(
        outside.path().join("keep.sqlite3"),
        fixture.path().join(".okms/state/team.sqlite3"),
    )
    .unwrap();
    let result = invoke(
        fixture.path(),
        &[
            "join",
            "--provider",
            "codex",
            "--input-json",
            r#"{"session_id":"root"}"#,
        ],
    );
    assert!(!result.status.success());
    assert_eq!(
        fs::read(outside.path().join("keep.sqlite3")).unwrap(),
        b"Preserve external bytes"
    );
}
