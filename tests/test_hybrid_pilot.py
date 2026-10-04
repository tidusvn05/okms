"""Independent fixture/grader controls; no native provider process is started."""

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("hybrid_pilot", ROOT / "evals/run_hybrid_pilot.py")
pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pilot)


class HybridPilotTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="okms-hybrid-grade-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def test_fixture_has_actual_failed_baseline_and_dirty_preserved_state(self):
        project = pilot.prepare(self.directory, "codex")
        baseline = json.loads((self.directory / "baseline.json").read_text())
        self.assertTrue(all(check["exit_code"] != 0 for check in baseline["checks"]))
        self.assertEqual((project / "keep.txt").read_text(), "Unstaged project note.\n")
        staged = pilot.run_command(project, ["git", "show", ":keep.txt"])["stdout"]
        self.assertEqual(staged, "Staged project note.\n")
        oracle = pilot.run_command(project, [pilot.sys.executable, "-c", pilot.ORACLE])
        self.assertFalse(json.loads(oracle["stdout"])["all_passed"])
        self.assertTrue((project / pilot.SPECS["durations"]).exists())
        self.assertFalse((self.directory / "primary").exists())

    def test_claimed_completion_cannot_replace_workers_messages_or_checks(self):
        project = pilot.prepare(self.directory, "codex")
        pilot.atomic_json(self.directory / "observations.json", [{"agents": []}])
        (project / pilot.PLAN).write_text((project / pilot.PLAN).read_text().replace("work_status: in_progress", "work_status: done"))
        result = pilot.capture(project, self.directory, "codex", [
            {"provider": "codex", "native_session_id": "root-one", "agent_id": "root-one", "exit_code": 0, "errors": []},
            {"provider": "claude", "native_session_id": "root-two", "agent_id": "root-two", "exit_code": 0, "errors": []}])
        self.assertFalse(result["pass"])
        for key in ("two_provider_workers_returned", "parallel_workers_observed", "worker_checks_observed",
                    "peer_request_response_ack", "exact_native_session_resume", "cross_provider_handoff_observed",
                    "verified_integration_then_completion", "completion_follows_actual_checks", "independent_root_behavior"):
            self.assertFalse(result["checks"][key], key)

    def test_missing_required_gate_does_not_become_a_pass_by_blocked_wording(self):
        project = pilot.prepare(self.directory, "blocked")
        pilot.atomic_json(self.directory / "observations.json", [])
        (project / pilot.PLAN).write_text((project / pilot.PLAN).read_text().replace("| in_progress |", "| blocked |"))
        result = pilot.capture(project, self.directory, "blocked", [])
        self.assertTrue(result["checks"]["failed_verification_stays_incomplete"])
        self.assertFalse(result["checks"]["required_gate_failure_retained"])
        self.assertFalse(result["pass"])
        original = (project / "checks.py").read_text()
        gate = pilot.run_command(project, ["python3", "checks.py", "gate"])
        self.assertEqual(gate["exit_code"], 34)
        self.assertEqual((project / "checks.py").read_text(), original)

    def test_grade_only_uses_saved_evidence_and_never_invokes_native_cli(self):
        project = pilot.prepare(self.directory / "codex", "codex")
        pilot.atomic_json(self.directory / "codex/observations.json", [])
        pilot.capture(project, self.directory / "codex", "codex", [])
        from unittest.mock import patch
        with patch.object(pilot, "start_native", side_effect=AssertionError("Native session must not start")), \
                patch.object(pilot, "BINARY", self.directory / "removed-binary"), \
                patch.object(pilot.subprocess, "check_output", side_effect=AssertionError("Grading must not execute binaries")):
            self.assertEqual(pilot.main(["--run-dir", str(self.directory), "--cases", "codex", "--grade-only"]), 1)

    def test_changed_binary_rejects_reuse_without_starting_native_sessions(self):
        from unittest.mock import patch
        copied = self.directory / "okms"
        shutil.copy2(pilot.BINARY, copied)
        run = self.directory / "run"
        args = ["--run-dir", str(run), "--cases", "codex", "--fixtures-only"]
        with patch.object(pilot, "BINARY", copied), \
                patch.object(pilot, "start_native", side_effect=AssertionError("Native session must not start")):
            self.assertEqual(pilot.main(args), 0)
            original = (run / "binary.json").read_bytes()
            with copied.open("ab") as stream:
                stream.write(b"different binary bytes")
            with self.assertRaises(SystemExit) as error:
                pilot.main(args)
            self.assertEqual(error.exception.code, 2)
            self.assertEqual((run / "binary.json").read_bytes(), original)
            self.assertFalse((run / "codex/primary").exists())

    def test_resume_evidence_uses_invocation_order_and_exact_native_identity(self):
        project = pilot.prepare(self.directory, "codex")
        pilot.atomic_json(self.directory / "observations.json", [])
        pilot.capture(project, self.directory, "codex", [])
        state_path = self.directory / "state.json"
        state = json.loads(state_path.read_text())
        state["agents"].append({"id":"worker-one", "role":"worker", "provider":"codex", "run_id":"run-one",
                                "native_session_id":"exact-thread", "status":"result_ready", "notes":'{"worker_result":{"disposition":"result_ready"}}'})
        pilot.atomic_json(state_path, state)
        turns = project / ".okms/state/runs/run-one/worker-one"
        pilot.atomic_json(turns / "turn-z-initial/invocation.json", {
            "argv":["codex", "exec", "--json", "-"], "started_at":"2026-10-04T00:00:01Z"})
        resumed = turns / "turn-a-resumed/invocation.json"
        value = {"argv":["codex", "exec", "resume", "exact-thread", "-"], "started_at":"2026-10-04T00:00:02Z"}
        pilot.atomic_json(resumed, value)
        self.assertTrue(pilot.grade(self.directory, "codex")["checks"]["exact_native_session_resume"])
        value["argv"][3] = "different-thread"
        pilot.atomic_json(resumed, value)
        self.assertFalse(pilot.grade(self.directory, "codex")["checks"]["exact_native_session_resume"])

    def test_partial_native_case_cannot_be_silently_restarted(self):
        pilot.prepare(self.directory / "codex", "codex")
        pilot.write(self.directory / "codex", "primary/invocation.json", '{"argv":["recorded-native-session"]}')
        from unittest.mock import patch
        with patch.object(pilot, "capabilities", side_effect=AssertionError("No native probe or restart")), self.assertRaises(SystemExit) as error:
            pilot.main(["--run-dir", str(self.directory), "--cases", "codex"])
        self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
