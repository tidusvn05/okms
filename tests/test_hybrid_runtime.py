"""Operational invariants in disposable projects; no real agent is launched."""

from __future__ import annotations

import concurrent.futures
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
from hybrid_legacy import SOURCE as LEGACY_SOURCE
SOURCE = LEGACY_SOURCE / "runtime"
sys.path.insert(0, str(SOURCE))
from okms_team import gitops, providers, worker
from okms_team.runtime import CHILDREN, Runtime
from okms_team.state import Store, TeamError, atomic_json


FAKE = '''import json, os, pathlib, subprocess, sys, time
provider = sys.argv[1]
prompt = sys.stdin.read()
assignment = json.loads(prompt.split("Assignment:\\n", 1)[1].splitlines()[0])
mode = assignment.get("context", [])
session = "native-" + os.environ["OKMS_AGENT_ID"]
def emit(value):
    print(json.dumps(value), flush=True)
def helper(command, value):
    result = subprocess.run([sys.executable, os.environ["OKMS_PROJECT"] + "/.okms/team.py", command,
                             "--input-json", json.dumps(value)], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return json.loads(result.stdout)
emit({"type":"thread.started", "thread_id":session} if provider == "codex"
     else {"type":"system", "subtype":"init", "session_id":session})
if "sleep" in mode:
    time.sleep(10)
if "early-message" in mode and "resume" not in sys.argv:
    time.sleep(0.4)
if "fail" in mode:
    emit({"type":"error", "message":"fixture transport failure"})
    sys.exit(3)
if "outside" in mode:
    pathlib.Path("unowned.txt").write_text("unauthorized fixture change")
resume = "resume" in sys.argv or "--resume" in sys.argv
if not any(value in mode for value in ("wait", "early-message")) or resume:
    for path in assignment["owns"]:
        target = pathlib.Path(path)
        if target.is_dir():
            target = target / "fixture.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        original = target.read_text() if target.exists() else ""
        target.write_text(original + "\\n# fixture change " + provider + "\\n")
    messages = helper("inbox", {})["messages"]
    for message in messages:
        helper("ack", {"id": message["id"]})
    if assignment["checks"]:
        helper("verify", {})
result = {"summary":"fixture result", "evidence":["Fixture transport; not a real agent"],
          "remaining":[], "next":"Coordinator verifies combined acceptance",
          "disposition":"waiting_input" if ("wait" in mode or "early-message" in mode) and not resume else "result_ready"}
if "malformed" in mode:
    result = {"summary":"missing required fields"}
if provider == "codex":
    emit({"type":"item.completed", "item":{"type":"agent_message", "text":json.dumps(result)}})
    emit({"type":"turn.completed"})
else:
    emit({"type":"result", "session_id":session, "structured_output":result,
          "permission_denials":[{"tool_name":"Bash"}] if "denied" in mode else []})
'''


def git(project, *args):
    result = subprocess.run(["git", "-C", str(project), *args], capture_output=True)
    if result.returncode:
        raise AssertionError(result.stderr.decode())
    return result.stdout


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="okms-runtime-")
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / "project with spaces $literal"
        self.project.mkdir()
        git(self.project, "init", "-q")
        git(self.project, "config", "user.name", "Fixture")
        git(self.project, "config", "user.email", "fixture@example.invalid")
        (self.project / ".gitignore").write_text(".okms/state/\n__pycache__/\n*.pyc\nignored.txt\n")
        for name in ("a.py", "b.py", "c.py"):
            (self.project / name).write_text("VALUE = 1\n")
        git(self.project, "add", ".")
        git(self.project, "commit", "-qm", "Fixture baseline")
        shutil.copytree(SOURCE, self.project / ".okms")
        shutil.copytree(ROOT / "templates/plan-first/docs", self.project / "docs")
        self.fake = Path(self.temp.name) / "fake.py"
        self.fake.write_text(FAKE)
        self.checks = [[sys.executable, "-c", "import pathlib; [compile(p.read_text(), str(p), 'exec') for p in pathlib.Path('.').glob('*.py')]"]]
        atomic_json(self.project / ".okms/team.json", {
            "schema_version": 1, "docs_path": "docs", "max_workers": 2, "assignment_timeout_seconds": 30,
            "checks": self.checks, "providers": {name: {"command": [sys.executable, str(self.fake), name], "args": []}
                                                    for name in ("codex", "claude")}})
        directory = self.project / "docs/work/P001-fixture"
        directory.mkdir()
        self.plan = "docs/work/P001-fixture/plan.md"
        (directory / "plan.md").write_text(
            "---\ntype: Plan\nwork_status: in_progress\n---\n# Fixture plan\n\n## Goal\n\nFixture.\n\n## Approach\n\nFixture.\n\n"
            "## Work\n\n| Spec | Depends on | State | Evidence |\n| --- | --- | --- | --- |\n"
            "| [P001-MS01](P001-MS01-fixture.md) | — | in_progress | Pending. |\n"
            "| [P001-MS02](P001-MS02-fixture.md) | — | planned | Pending. |\n\n"
            "## Resume\n\n- Current: P001-MS01.\n- Next: verify.\n- Blocker: none.\n\n## Result\n\nPending.\n")
        for number in (1, 2):
            (directory / f"P001-MS0{number}-fixture.md").write_text(
                "---\ntype: MicroSpec\nkind: implementation\n---\n# Fixture\n\n## Intent\n\nFixture.\n\n"
                "## Constraints\n\nPreserve staging.\n\n## Acceptance\n\nFixture checks pass.\n\n## Verify\n\nFixture command.\n")
        self.runtime = Runtime(self.project)
        self.owner = self.runtime.store.join("codex", "root-codex")

    def tearDown(self):
        if hasattr(self, "runtime"):
            for agent in self.runtime.store.status()["agents"]:
                if agent["role"] == "worker" and agent["status"] in {"queued", "starting", "running", "waiting_input"}:
                    try:
                        self.runtime.stop(self.owner, {"agent_id": agent["id"]})
                    except TeamError:
                        pass
            for process in CHILDREN:
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    worker.stop_process(process)
            CHILDREN.clear()

    def assign(self, provider="codex", path="a.py", context=None, launch=True, number=1):
        return self.runtime.dispatch(self.owner, {"provider": provider, "plan": self.plan,
                "spec": f"docs/work/P001-fixture/P001-MS0{number}-fixture.md", "intent": "Fixture scoped change",
                "owns": [path] if path else [], "checks": self.checks, "context": context or [], "launch": launch})

    def wait(self, result, state=None, timeout=10):
        limit = time.monotonic() + timeout
        while time.monotonic() < limit:
            with self.runtime.store.connection() as db:
                row = dict(db.execute("SELECT * FROM agents WHERE id=?", (result["agent_id"],)).fetchone())
            if (state and row["status"] == state) or (not state and row["status"] not in {"queued", "starting", "running"}):
                return row
            time.sleep(0.05)
        self.fail("Fixture driver did not finish: " + json.dumps(self.runtime.store.status()))

    def identity(self, result):
        with self.runtime.store.connection() as db:
            row = db.execute("SELECT * FROM agents WHERE id=?", (result["agent_id"],)).fetchone()
        return {"agent_id": row["id"], "token": row["token"]}

    def checkpoint(self, state="done", number=1):
        return self.runtime.checkpoint(self.owner, {"plan": self.plan, "spec_id": f"P001-MS0{number}", "state": state,
            "evidence": "Fixture checks passed in retained logs.", "acceptance_review": "Fixture acceptance reviewed.",
            "resume": {"current": "fixture", "next": "fixture next action", "blocker": "none"}, "result": "Fixture plan verified."})

    def test_concurrent_join_selects_one_owner_and_handoff_fences_old_token(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            values = list(pool.map(lambda n: Store(self.project).join("claude", "session-" + str(n)), range(6)))
        self.assertTrue(all(value["role"] == "standby" for value in values))
        promoted = self.runtime.store.handoff(self.owner, values[0]["agent_id"])
        with self.assertRaises(TeamError):
            self.runtime.actor(self.owner, coordinator=True)
        previous = json.loads(Path(self.owner["identity_file"]).read_text())
        self.assertEqual(self.runtime.actor(previous)["role"], "standby")
        with self.assertRaises(TeamError):
            self.runtime.actor(previous, coordinator=True)
        notice = self.runtime.send(previous, {"to": "coordinator", "payload": {"note": "Handoff complete"}})
        self.assertEqual(self.runtime.store.inbox(promoted)[0]["id"], notice["id"])
        self.runtime.actor(promoted, coordinator=True)
        self.owner = promoted

    def test_peer_messages_ack_deduplicate_and_survive_new_runtime(self):
        a, b = self.assign(launch=False), self.assign("claude", "b.py", launch=False)
        message = {"id": "stable-request", "to": b["agent_id"], "type": "request", "payload": {"question": "fixture question"}}
        saved = self.runtime.send(self.identity(a), message)
        self.assertEqual(saved, self.runtime.send(self.identity(a), message))
        fresh = Runtime(self.project)
        self.assertEqual(fresh.store.inbox(self.identity(b))[0]["id"], "stable-request")
        with self.assertRaises(TeamError):
            fresh.store.ack(self.identity(a), "stable-request")
        fresh.store.ack(self.identity(b), "stable-request")
        self.assertFalse(fresh.store.inbox(self.identity(b)))
        with self.assertRaises(TeamError):
            fresh.send(self.identity(a), {**message, "payload": {"question": "changed content"}})

    def test_coordinator_alias_survives_provider_handoff(self):
        a = self.assign(launch=False)
        self.runtime.send(self.identity(a), {"to": "coordinator", "payload": {"question": "handoff fixture"}})
        standby = self.runtime.store.join("claude", "root-claude")
        self.owner = self.runtime.store.handoff(self.owner, standby["agent_id"])
        self.assertEqual(len(self.runtime.store.inbox(self.owner)), 1)

    def test_snapshot_contains_dirty_and_untracked_files_preserving_index_and_head(self):
        (self.project / "a.py").write_text("VALUE = 2\n")
        git(self.project, "add", "a.py")
        (self.project / "a.py").write_text("VALUE = 3\n")
        (self.project / "new.py").write_text("NEW = True\n")
        (self.project / "ignored.txt").write_text("not in snapshot")
        head, index = git(self.project, "rev-parse", "HEAD"), (self.project / ".git/index").read_bytes()
        result = self.assign(launch=False)
        fork = Path(result["worktree"])
        self.assertEqual((fork / "a.py").read_text(), "VALUE = 3\n")
        self.assertTrue((fork / "new.py").exists())
        self.assertFalse((fork / "ignored.txt").exists())
        self.assertFalse((fork / ".okms/state/team.sqlite3").exists())
        self.assertEqual(head, git(self.project, "rev-parse", "HEAD"))
        self.assertEqual(index, (self.project / ".git/index").read_bytes())

    def test_overlap_scope_worker_limit_and_unready_dependencies_are_rejected(self):
        self.assign(launch=False)
        with self.assertRaises(TeamError):
            self.assign(launch=False)
        self.assign("claude", "b.py", launch=False)
        with self.assertRaises(TeamError):
            self.assign("codex", "c.py", launch=False)
        path = self.project / self.plan
        path.write_text(path.read_text().replace("[P001-MS02](P001-MS02-fixture.md) | —", "[P001-MS02](P001-MS02-fixture.md) | P001-MS01"))
        with self.assertRaises(TeamError):
            self.assign("codex", "c.py", number=2)
        for forbidden in ("../escape", "/absolute", ".okms", "AGENTS.md", "docs/work"):
            with self.subTest(scope=forbidden), self.assertRaises(TeamError):
                self.assign(path=forbidden, launch=False)

    def test_real_processes_return_results_then_combined_checks_preserve_staging(self):
        (self.project / "a.py").write_text("VALUE = 2\n")
        git(self.project, "add", "a.py")
        (self.project / "a.py").write_text("VALUE = 3\n")
        before_index = (self.project / ".git/index").read_bytes()
        before_head = git(self.project, "rev-parse", "HEAD")
        a, b = self.assign(), self.assign("claude", "b.py", number=2)
        self.assertEqual(a["baseline"], b["baseline"])
        for result in (a, b):
            self.assertEqual(self.wait(result)["status"], "result_ready")
        with self.assertRaises(TeamError):
            self.checkpoint()
        integrated = self.runtime.integrate(self.owner, {"run_id": a["run_id"], "acceptance_review": "Review fixture changes and combined checks."})
        self.assertTrue(integrated["verified"])
        self.assertIn("fixture change codex", (self.project / "a.py").read_text())
        self.assertIn("fixture change claude", (self.project / "b.py").read_text())
        self.assertEqual(before_index, (self.project / ".git/index").read_bytes())
        self.assertEqual(before_head, git(self.project, "rev-parse", "HEAD"))
        self.assertEqual(self.checkpoint()["work_status"], "in_progress")
        self.assertEqual(self.checkpoint(number=2)["work_status"], "done")

    def test_changed_root_and_failed_combined_checks_keep_parent_incomplete(self):
        a = self.assign()
        self.assertEqual(self.wait(a)["status"], "result_ready")
        (self.project / "a.py").write_text("USER_NEW = True\n")
        with self.assertRaisesRegex(TeamError, "Root changed"):
            self.runtime.integrate(self.owner, {"run_id": a["run_id"], "acceptance_review": "Fixture review"})
        self.assertEqual((self.project / "a.py").read_text(), "USER_NEW = True\n")
        with self.assertRaisesRegex(TeamError, "Combined checks failed"):
            self.runtime.integrate(self.owner, {"run_id": a["run_id"], "acceptance_review": "Fixture review", "checks": [[sys.executable, "-c", "raise SystemExit(1)"]]})
        with self.assertRaises(TeamError):
            self.checkpoint()
        self.assertTrue(any(e["type"] == "integration_failed" for e in self.runtime.store.status()["events"]))

    def test_idle_worker_resumes_exact_session_on_peer_message_and_acks(self):
        a = self.assign(context=["wait"])
        row = self.wait(a, "waiting_input")
        self.assertEqual(row["native_session_id"], "native-" + a["agent_id"])
        self.runtime.send(self.owner, {"to": a["agent_id"], "type": "response", "payload": {"answer": "continue"}})
        self.assertEqual(self.wait(a, "result_ready")["native_session_id"], row["native_session_id"])
        self.assertFalse(self.runtime.store.inbox(self.identity(a)))
        result = json.loads(self.wait(a)["notes"])
        invocation = json.loads((Path(result["artifact"]) / "invocation.json").read_text())
        self.assertIn(row["native_session_id"], invocation["argv"])
        self.assertNotIn("--last", invocation["argv"])

    def test_duplicate_driver_does_not_launch_a_second_process(self):
        a = self.assign(context=["sleep"])
        with self.assertRaises(TeamError):
            self.runtime.launch(a["agent_id"])
        self.runtime.stop(self.owner, {"agent_id": a["agent_id"]})
        self.assertEqual(self.wait(a, "cancelled")["status"], "cancelled")

    def test_configured_gate_cannot_be_replaced_by_passing_integration_checks(self):
        original = (self.project / "a.py").read_text()
        assignment = self.assign()
        self.wait(assignment, "result_ready")
        self.runtime.config["checks"] = [[sys.executable, "-c", "raise SystemExit(23)"]]
        with self.assertRaisesRegex(TeamError, "Combined checks failed"):
            self.runtime.integrate(self.owner, {"run_id": assignment["run_id"], "acceptance_review": "Fixture review",
                                              "checks": [[sys.executable, "-c", "pass"]]})
        self.assertEqual((self.project / "a.py").read_text(), original)

    def test_worker_cannot_dispatch_checkpoint_integrate_or_choose_checks(self):
        a = self.assign(launch=False)
        identity = self.identity(a)
        with self.assertRaises(TeamError):
            self.runtime.dispatch(identity, {})
        with self.assertRaises(TeamError):
            self.runtime.integrate(identity, {})
        with self.assertRaises(TeamError):
            self.runtime.checkpoint(identity, {})
        verification = self.runtime.verify(identity, {"checks": [["nonexistent-command"]]})
        self.assertTrue(verification["passed"])

    def test_errors_denials_missing_results_and_scope_violations_are_failed(self):
        for mode, provider in (("fail", "codex"), ("denied", "claude"), ("malformed", "codex"), ("outside", "claude")):
            with self.subTest(mode=mode):
                result = self.assign(provider, context=[mode])
                row = self.wait(result)
                self.assertEqual(row["status"], "failed", row)
                self.assertTrue(json.loads(row["notes"])["error"])
                with self.assertRaises(TeamError):
                    self.checkpoint()

    def test_timeout_preserves_worktree_and_requires_explicit_extension(self):
        self.runtime.config["assignment_timeout_seconds"] = 0.7
        atomic_json(self.project / ".okms/team.json", self.runtime.config)
        result = self.assign(context=["sleep"])
        row = self.wait(result)
        self.assertEqual(row["status"], "failed")
        self.assertIn("deadline", json.loads(row["notes"])["error"])
        self.assertTrue(Path(row["worktree"]).is_dir())
        with self.assertRaisesRegex(TeamError, "extend_seconds"):
            self.runtime.resume(self.owner, {"agent_id": result["agent_id"]})

    def test_crashed_coordinator_recovery_fences_old_owner(self):
        standby = self.runtime.store.join("claude", "recovery")
        self.owner = self.runtime.store.handoff(standby, recover=True)
        self.runtime.actor(self.owner, coordinator=True)
        original = json.loads((self.runtime.store.directory / "identities" / (self.runtime.store.status()["agents"][0]["id"] + ".json")).read_text())
        with self.assertRaises(TeamError):
            self.runtime.actor(original, coordinator=True)

    def test_hook_context_binds_worker_without_claiming_coordinator(self):
        a = self.assign(launch=False)
        identity = self.identity(a)
        original = os.environ.copy()
        try:
            os.environ.update(OKMS_AGENT_ID=identity["agent_id"], OKMS_AGENT_TOKEN=identity["token"])
            output = self.runtime.hook("claude", {"session_id": "native-worker", "hook_event_name": "SessionStart"})
            self.assertIn("role: worker", output["hookSpecificOutput"]["additionalContext"])
            self.assertEqual(self.runtime.store.status()["owner"]["agent_id"], self.owner["agent_id"])
        finally:
            os.environ.clear()
            os.environ.update(original)

    def test_resume_commands_preserve_native_configuration_and_environment(self):
        agent = {"id": "fixture", "token": "fixture-token", "worktree": str(self.project), "native_session_id": "explicit-native-id"}
        for provider in ("codex", "claude"):
            command = providers.command(provider, self.runtime.config, self.project, agent, Path(self.temp.name))
            self.assertIn("explicit-native-id", command)
            self.assertFalse(any("bypass" in flag or flag == "--last" for flag in command))
        self.assertNotIn("CLAUDECODE", providers.environment(self.project, agent))

    def test_native_plan_mode_blocks_implementation_operations(self):
        self.runtime.hook("codex", {"session_id": "root-codex", "hook_event_name": "SessionStart", "permission_mode": "plan"})
        with self.assertRaisesRegex(TeamError, "plan mode"):
            self.assign(launch=False)
        self.assertEqual(len(self.runtime.store.status()["agents"]), 1)

    def test_message_arriving_during_turn_wakes_worker_after_it_begins_waiting(self):
        a = self.assign(context=["early-message"])
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            with self.runtime.store.connection() as db:
                native = db.execute("SELECT native_session_id FROM agents WHERE id=?", (a["agent_id"],)).fetchone()[0]
            if native:
                break
            time.sleep(0.01)
        self.assertTrue(native)
        message = self.runtime.send(self.owner, {"to": a["agent_id"], "type": "response", "payload": {"answer": "early fixture response"}})
        row = self.wait(a, "result_ready")
        self.assertEqual(row["native_session_id"], "native-" + a["agent_id"])
        self.assertFalse(self.runtime.store.inbox(self.identity(a)))
        self.assertTrue(any(event["type"] == "message_acknowledged" and event["payload"]["message_id"] == message["id"]
                            for event in self.runtime.store.status()["events"]))

    def test_handoff_during_combined_check_prevents_stale_root_application(self):
        a = self.assign()
        self.wait(a, "result_ready")
        marker = Path(self.temp.name) / "check-started"
        checks = [[sys.executable, "-c", "import pathlib,time; pathlib.Path(" + repr(str(marker)) + ").write_text('started'); time.sleep(0.5)"]]
        standby = self.runtime.store.join("claude", "handoff-target")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.runtime.integrate, self.owner, {"run_id": a["run_id"], "checks": checks, "acceptance_review": "Fixture acceptance"})
            deadline = time.monotonic() + 3
            while not marker.exists() and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertTrue(marker.exists())
            self.owner = self.runtime.store.handoff(self.owner, standby["agent_id"])
            with self.assertRaises(TeamError):
                future.result()
        self.assertNotIn("fixture change", (self.project / "a.py").read_text())

    def test_failed_root_check_requires_explicit_reverification_before_checkpoint(self):
        a = self.assign()
        self.wait(a, "result_ready")
        root = str(self.project)
        checks = [[sys.executable, "-c", "import os; raise SystemExit(1 if os.getcwd()==" + repr(root) + " else 0)"]]
        value = self.runtime.integrate(self.owner, {"run_id": a["run_id"], "checks": checks, "acceptance_review": "Fixture acceptance"})
        self.assertTrue(value["applied"])
        self.assertFalse(value["verified"])
        with self.assertRaises(TeamError):
            self.checkpoint()
        self.assertTrue(self.runtime.verify(self.owner, {"run_id": a["run_id"]})["passed"])
        self.assertEqual(self.checkpoint()["state"], "done")

    def test_empty_and_nonfinite_limits_and_bypass_arguments_are_rejected(self):
        original = self.runtime.config.copy()
        for value in (True, 0, -1, float('inf'), float('nan')):
            with self.subTest(value=value):
                atomic_json(self.project / ".okms/team.json", {**original, "assignment_timeout_seconds": value})
                with self.assertRaises(TeamError):
                    Runtime(self.project)
        self.runtime.config["providers"]["codex"]["args"] = ["--dangerously-bypass-hook-trust"]
        with self.assertRaises(TeamError):
            self.assign(launch=False)


if __name__ == "__main__":
    unittest.main()
