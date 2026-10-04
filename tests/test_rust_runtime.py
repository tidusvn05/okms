"""Run the retained operational contracts through the native Rust binary."""

import json
import os
import shutil
import subprocess
import time
from pathlib import Path

import test_hybrid_runtime as baseline

ROOT = Path(__file__).resolve().parents[1]
BINARY = Path(os.environ.get("OKMS_TEST_BINARY", ROOT / "target/debug/okms"))


class RustRuntime:
    """CLI transport and SQLite observer; Python does not implement operations."""

    def __init__(self, project):
        self.project = Path(project)
        self.config = json.loads((self.project / ".okms/team.json").read_text())
        self.store = baseline.Store(project)
        self.docs = self.project / self.config["docs_path"]
        self.driver_pids = set()
        self.owner = None

    def actor(self, identity, coordinator=False):
        with self.store.connection() as db:
            return self.store.authenticate(db, identity, coordinator=coordinator)

    def command(self, command, identity, data):
        baseline.atomic_json(self.project / ".okms/team.json", self.config)
        argv = [str(self.project / ".okms/okms"), command, "--project", str(self.project),
                "--input-json", json.dumps(data)]
        env = {**os.environ, "OKMS_AGENT_ID": identity["agent_id"], "OKMS_AGENT_TOKEN": identity["token"]}
        result = subprocess.run(argv, capture_output=True, text=True, env=env, timeout=45)
        try:
            value = json.loads(result.stdout)
        except ValueError as error:
            raise AssertionError(result.stdout + result.stderr) from error
        if result.returncode:
            raise baseline.TeamError(value.get("error", result.stderr))
        if value.get("driver_pid"):
            self.driver_pids.add(value["driver_pid"])
        self.driver_pids.update(agent["pid"] for agent in self.store.status()["agents"] if agent["pid"])
        return value

    def launch(self, agent_id):
        return self.resume(self.owner, {"agent_id": agent_id})["driver_pid"]

    def hook(self, provider, data):
        baseline.atomic_json(self.project / ".okms/team.json", self.config)
        result = subprocess.run([str(self.project / ".okms/okms"), "hook", "--provider", provider,
                                 "--project", str(self.project), "--input-json", json.dumps(data)],
                                capture_output=True, text=True, timeout=15)
        value = json.loads(result.stdout)
        if result.returncode:
            raise baseline.TeamError(value.get("systemMessage", result.stderr))
        return value

    def __getattr__(self, name):
        if name in {"dispatch", "resume", "send", "verify", "integrate", "checkpoint", "stop"}:
            return lambda identity, data: self.command(name, identity, data)
        raise AttributeError(name)


class RustRuntimeTests(baseline.RuntimeTests):
    def setUp(self):
        super().setUp()
        if not BINARY.is_file():
            self.fail("Build Rust with cargo build before running the native regression suite.")
        shutil.copy2(BINARY, self.project / ".okms/okms")
        self.fake.write_text(baseline.FAKE.replace(
            'sys.executable, os.environ["OKMS_PROJECT"] + "/.okms/team.py"',
            'os.environ["OKMS_PROJECT"] + "/.okms/okms"'))
        self.runtime = RustRuntime(self.project)
        self.runtime.owner = self.owner

    def tearDown(self):
        super().tearDown()
        if hasattr(self, "runtime"):
            deadline = time.monotonic() + 6
            while time.monotonic() < deadline:
                running = [agent for agent in self.runtime.store.status()["agents"]
                           if agent["role"] == "worker" and agent["pid"]]
                if not running:
                    break
                time.sleep(0.05)
