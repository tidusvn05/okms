"""Negative trace and fixture checks do not invoke coding agents."""

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evals"))
SPEC = importlib.util.spec_from_file_location("review_pilot", ROOT / "evals/run_review_pilot.py")
pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pilot)


class ReviewPilotTests(unittest.TestCase):
    def test_requested_or_unreturned_workers_are_not_observed_results(self):
        for provider in pilot.PROVIDERS:
            self.assertEqual(pilot.delegation_evidence({}, {}, provider)["reader_returns"], 0)
        calls = {"a": {"name": "Agent", "input": {"subagent_type": "okms-reviewer"}},
                 "b": {"name": "Agent", "input": {"subagent_type": "okms-reviewer"}}}
        self.assertEqual(pilot.delegation_evidence(calls, {}, "claude")["reader_returns"], 0)
        returns = {"a": {"is_error": False, "content": "Scoped findings returned."},
                   "b": {"is_error": True, "content": "Worker failed."}}
        self.assertEqual(pilot.delegation_evidence(calls, returns, "claude")["reader_returns"], 1)
        calls["a"]["input"]["run_in_background"] = True
        self.assertEqual(pilot.delegation_evidence(calls, returns, "claude")["reader_returns"], 0)

    def test_background_launch_and_progress_are_not_completed_results(self):
        with tempfile.TemporaryDirectory(prefix="okms-review-trace-") as directory:
            destination = Path(directory)
            entries = [
                {"seconds": 1, "event": {"type": "assistant", "message": {"content": [
                    {"type": "tool_use", "id": "reader", "name": "Agent", "input": {
                        "subagent_type": "okms-reviewer"}}]}}},
                {"seconds": 2, "event": {"type": "system", "subtype": "task_started",
                    "tool_use_id": "reader", "is_backgrounded": True}},
                {"seconds": 3, "event": {"type": "user", "message": {"content": [
                    {"type": "tool_result", "tool_use_id": "reader", "content": "Async agent launched."}]}}},
                {"seconds": 4, "event": {"type": "system", "subtype": "task_updated",
                    "task_id": "child", "patch": {"status": "completed"}}},
                {"seconds": 5, "event": {"type": "system", "subtype": "task_notification",
                    "tool_use_id": "unrelated", "status": "completed", "summary": "Other work."}},
            ]
            trace = destination / "timed-events.json"
            trace.write_text(json.dumps(entries))
            calls, returns = pilot.tools(destination, "claude")
            self.assertEqual(pilot.delegation_evidence(calls, returns, "claude")["reader_returns"], 0)
            for status, summary, expected in (("failed", "Unavailable.", 0), ("completed", "", 0),
                                              ("completed", "Scoped finding at api.py:4.", 1)):
                with self.subTest(status=status, summary=summary):
                    notification = {"seconds": 6, "event": {"type": "system", "subtype": "task_notification",
                        "tool_use_id": "reader", "status": status, "summary": summary}}
                    trace.write_text(json.dumps(entries + [notification]))
                    calls, returns = pilot.tools(destination, "claude")
                    result = pilot.delegation_evidence(calls, returns, "claude")
                    self.assertEqual(result["reader_returns"], expected)
                    if expected:
                        self.assertEqual(result["return_seconds"], [6])

    def test_grade_only_reuses_saved_invocation_without_launching_an_agent(self):
        with tempfile.TemporaryDirectory(prefix="okms-review-grade-") as directory:
            root = Path(directory)
            workspace, run = root / "workspace", root / "run"
            (workspace / "codex/finding").mkdir(parents=True)
            destination = run / "codex/finding/finding"
            destination.mkdir(parents=True)
            invocation = {"thread_id": "saved-session", "exit_code": 0}
            result = {"checks": {"fixture": True}, "invocation": invocation, "passed": True}
            (destination / "invocation.json").write_text(json.dumps(invocation))
            (destination / "grade.json").write_text(json.dumps(result))
            manifest = {"workspace_root": str(workspace), "template_version": "0.4.0",
                "clis": {"codex": {"path": "unused-cli"}}, "sessions": [
                    {"provider": "codex", "case": "finding", "label": "finding", **invocation}]}
            (run / "manifest.json").write_text(json.dumps(manifest))
            arguments = ["review-pilot", "--providers", "codex", "--cases", "finding",
                         "--run-dir", str(run), "--grade-only"]
            with patch.object(sys, "argv", arguments), patch.object(pilot, "source_record", return_value={}), \
                    patch.object(pilot, "grade", return_value=result), patch.object(pilot.observer, "invoke") as invoke:
                self.assertEqual(pilot.main(), 0)
                invoke.assert_not_called()

    def test_codex_started_workers_are_not_completed_workers(self):
        calls = {"a": {"name": "spawn_agent", "input": {"agent_type": "okms-reviewer", "receiver_thread_ids": ["reader1"]}},
                 "c": {"name": "spawn_agent", "input": {"agent_type": "okms-reviewer", "receiver_thread_ids": ["reader2"]}},
                 "b": {"name": "wait", "input": {"agents_states": {
                     "reader1": {"status": "running"}, "reader2": {"status": "completed", "message": "Scoped finding."},
                     "unrelated": {"status": "completed", "message": "Other work."}}}}}
        result = pilot.delegation_evidence(calls, {}, "codex")
        self.assertEqual(result["reader_returns"], 1)
        self.assertTrue(result["role_visible"])

    def test_role_name_in_a_prompt_does_not_prove_native_role_selection(self):
        calls = {"a": {"name": "spawn_agent", "input": {"prompt": "Use okms-reviewer", "receiver_thread_ids": ["reader"]}},
                 "b": {"name": "wait", "input": {"agents_states": {"reader": {"status": "completed"}}}}}
        result = pilot.delegation_evidence(calls, {}, "codex")
        self.assertFalse(result["role_visible"])
        self.assertEqual(result["reader_returns"], 0)

    def test_bounded_no_findings_is_a_findings_section_claim(self):
        report = "## Findings\nNo actionable violations of the two contracts were identified within the reviewed scope.\n"
        self.assertTrue(pilot.no_findings(report))
        self.assertFalse(pilot.no_findings("## Scope\nNo findings.\n\n## Findings\nAuthorization bypass at api.py:4.\n"))
        self.assertFalse(pilot.no_findings("## Findings\nNo evidence of violations because the required review could not run.\n"))

    def test_continuation_requires_and_preserves_saved_reader_records(self):
        with tempfile.TemporaryDirectory(prefix="okms-review-handoff-") as directory:
            root = Path(directory)
            previous, project, artifacts = root / "previous", root / "project", root / "artifacts"
            before = previous / "final-project"
            (before / "docs/_templates").mkdir(parents=True)
            with self.assertRaisesRegex(RuntimeError, "all four saved reader records"):
                pilot.prepare_continuation(previous, project, artifacts)
            (before / "pagination.py").write_text(pilot.PARSER_BAD)
            (before / "api.py").write_text(pilot.API_BAD)
            (before / "tests").mkdir()
            (before / "tests/test_existing.py").write_text(pilot.TESTS)
            (previous / "invocation.json").write_text('{"thread_id":"previous-session"}\n')
            records = ("parser-brief.md", "auth-brief.md", "parser-result.md", "auth-result.md")
            for name in records:
                (before / "docs" / name).write_text("Saved fixture reader record: " + name + "\n")
            pilot.prepare_continuation(previous, project, artifacts)
            for name in records:
                self.assertEqual((project / "docs" / name).read_bytes(), (before / "docs" / name).read_bytes())
            self.assertEqual((project / "api.py").read_bytes(), (before / "api.py").read_bytes())
            self.assertTrue((artifacts / "handoff.json").exists())

    def test_scope_mentions_do_not_count_as_supported_findings(self):
        self.assertFalse(pilot.known_findings("## Scope\npagination.py zero and api.py unauthorized paths\n\n## Findings\nNone.\n"))
        self.assertTrue(pilot.known_findings("## Findings\npagination.py accepts zero; api.py leaks records to unauthorized callers.\n"))

    def test_fixture_oracle_exposes_application_changes(self):
        with tempfile.TemporaryDirectory(prefix="okms-review-test-") as directory:
            root = Path(directory)
            project, artifacts = root / "project", root / "artifacts"
            project.mkdir()
            artifacts.mkdir()
            (project / "pagination.py").write_text(pilot.PARSER_GOOD)
            (project / "api.py").write_text(pilot.API_GOOD)
            self.assertEqual(pilot.fixture_oracle(project, "no-findings", artifacts)["exit_code"], 0)
            (project / "api.py").write_text(pilot.API_BAD)
            self.assertNotEqual(pilot.fixture_oracle(project, "no-findings", artifacts)["exit_code"], 0)

    def test_dispatch_uses_start_time_instead_of_completion_time(self):
        with tempfile.TemporaryDirectory(prefix="okms-review-trace-") as directory:
            destination = Path(directory)
            entries = [{"seconds": second, "event": {"type": event_type, "item": {
                "id": "spawn1", "type": "collab_tool_call", "tool": "spawn_agent"}}}
                for second, event_type in ((1, "item.started"), (5, "item.completed"))]
            (destination / "timed-events.json").write_text(json.dumps(entries))
            calls, _ = pilot.tools(destination, "codex")
            self.assertEqual(calls["spawn1"]["seconds"], 1)


if __name__ == "__main__":
    unittest.main()
