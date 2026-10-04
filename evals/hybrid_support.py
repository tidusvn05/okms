"""Evaluation-only Rust command transport and independent SQLite observations."""

from contextlib import contextmanager
import json
import os
from pathlib import Path
import signal
import sqlite3
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[1]
BINARY = Path(os.environ.get("OKMS_TEST_BINARY", ROOT / "target/debug/okms")).resolve()


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        temporary.write_text(json.dumps(value, indent=2) + "\n")
        temporary.chmod(0o600)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def command(project, operation, data=None, provider=None):
    helper = Path(project) / ".okms/okms"
    argv = [str(helper), operation, "--project", str(project), "--input-json", json.dumps(data or {})]
    if provider:
        argv.extend(["--provider", provider])
    result = subprocess.run(argv, capture_output=True, text=True, timeout=45)
    value = json.loads(result.stdout)
    if result.returncode:
        raise RuntimeError(value.get("error", result.stdout) + result.stderr)
    return value


def install(source, project):
    frozen = Path(source).parent / "okms"
    binary = frozen if frozen.is_file() else BINARY
    result = subprocess.run([str(binary), "init", "--project", str(project)], capture_output=True, text=True, timeout=45)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return json.loads(result.stdout)


class Store:
    """Observe persisted schema without reimplementing coordination operations."""

    def __init__(self, project):
        self.project = Path(project)
        self.path = self.project / ".okms/state/team.sqlite3"

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=30, isolation_level=None)
        db.row_factory = sqlite3.Row
        try:
            yield db
        finally:
            db.close()

    @contextmanager
    def transaction(self):
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                yield db
                db.execute("COMMIT")
            except BaseException:
                db.execute("ROLLBACK")
                raise

    def join(self, provider, session_id):
        return command(self.project, "join", {"session_id": session_id}, provider)

    def status(self):
        with self.connection() as db:
            agents = [dict(row) for row in db.execute("SELECT * FROM agents ORDER BY rowid")]
            for agent in agents:
                agent.pop("token", None)
                agent.pop("driver_nonce", None)
                agent["assignment"] = json.loads(agent["assignment"]) if agent["assignment"] else None
            return {"owner": dict(db.execute("SELECT * FROM owner").fetchone()), "agents": agents,
                    "runs": [dict(row) for row in db.execute("SELECT id,baseline,plan,status FROM runs")],
                    "events": [{**json.loads(row["envelope"]), "sequence": row["sequence"]}
                               for row in db.execute("SELECT * FROM events ORDER BY sequence")]}


class Runtime:
    def __init__(self, project):
        self.project = Path(project)
        self.config = json.loads((self.project / ".okms/team.json").read_text())
        self.store = Store(project)


def capabilities(config, project):
    return command(project, "doctor")["providers"]


def observation(provider, record):
    value = {"native_session_id": None, "error": None}
    if provider == "codex":
        if record.get("type") == "thread.started":
            value["native_session_id"] = record.get("thread_id")
        elif record.get("type") in {"turn.failed", "error"}:
            value["error"] = record.get("error") or record.get("message") or "Provider reported failure."
    else:
        value["native_session_id"] = record.get("session_id")
        if record.get("type") == "result" and (record.get("is_error") or record.get("permission_denials")):
            value["error"] = record.get("permission_denials") or record.get("result") or "Provider reported failure."
        elif record.get("type") == "system" and record.get("subtype") == "permission_denied":
            value["error"] = record
    return value


def stop_process(process):
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    if process.poll() is None:
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=5)
