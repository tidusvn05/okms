#!/usr/bin/env python3
"""Opt-in Codex/Claude review, native-reader, and saved-recovery pilots."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

import run_agent_pilot as observer


ROOT = observer.ROOT
GRADING_SOURCE_SHA256 = observer.digest(Path(__file__).read_bytes())
CASES = ("finding", "no-findings", "delegation", "child-missing", "integration-failure")
PROVIDERS = ("codex", "claude")
PARSER_BAD = "def parse_size(raw):\n    return int(raw)\n"
PARSER_GOOD = '''def parse_size(raw):
    if isinstance(raw, bool):
        raise ValueError("positive integer required")
    value = int(raw)
    if value < 1:
        raise ValueError("positive integer required")
    return value
'''
API_BAD = '''def list_records(is_admin):
    records = [{"private": "fixture-secret"}]
    if records:
        return records
    if not is_admin:
        raise PermissionError("admin required")
    return records
'''
API_GOOD = '''def list_records(is_admin):
    if not is_admin:
        raise PermissionError("admin required")
    return [{"private": "fixture-secret"}]
'''
TESTS = '''import unittest
from pagination import parse_size
from api import list_records

class ExistingTests(unittest.TestCase):
    def test_positive_size(self):
        self.assertEqual(parse_size("5"), 5)
    def test_authorized_records(self):
        self.assertEqual(list_records(True), [{"private": "fixture-secret"}])
'''
PROBE = '''import sys
print("READER_PROBE_UNAVAILABLE: fixture external dataset offline")
sys.exit(2)
'''
COMBINED = '''import sys
from api import list_records
try:
    records = list_records(False)
except PermissionError:
    print("COMBINED_CHECK_OK: unauthorized request denied")
else:
    print("COMBINED_CHECK_FAILED: unauthorized request received records")
    sys.exit(1)
'''
PROTECTED = ("pagination.py", "api.py", "tests/test_existing.py", "AGENTS.md", "CLAUDE.md",
             "reader_probe.py", "verify_combined.py", ".codex/agents/okms-reviewer.toml",
             ".claude/agents/okms-reviewer.md")


def read_document(path):
    text = path.read_text()
    if text.startswith("---\n"):
        _, raw, body = text.split("---", 2)
        return yaml.safe_load(raw) or {}, body
    return {}, text


def source_record(run_dir):
    paths = list((ROOT / "templates").glob("*/docs/**/*.md"))
    paths += [ROOT / "adapters/codex/okms-reviewer.toml", ROOT / "adapters/claude/okms-reviewer.md",
              Path(__file__), ROOT / "evals/run_agent_pilot.py", ROOT / "scripts/check_docs.py"]
    fingerprints = {str(path.relative_to(ROOT)): observer.digest(path.read_bytes()) for path in sorted(paths)}
    path = run_dir / "source-record.json"
    if path.exists():
        return json.loads(path.read_text())
    record = {"files": fingerprints,
              "combined_sha256": observer.digest(json.dumps(fingerprints, sort_keys=True).encode())}
    observer.json_write(path, record)
    for name in fingerprints:
        target = run_dir / "source-snapshot" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
    return record


def verify_source(record):
    if any(observer.digest((ROOT / name).read_bytes()) != fingerprint
           for name, fingerprint in record["files"].items()):
        raise RuntimeError("Observed source changed; preserve artifacts and use a new run directory")


def prepare(provider, case, project, destination):
    project.mkdir(parents=True)
    destination.mkdir(parents=True, exist_ok=True)
    profile = "lite" if case in {"finding", "no-findings"} else "plan-first"
    shutil.copytree(ROOT / "templates" / profile / "docs", project / "docs")
    good = case == "no-findings"
    observer.write(project / "pagination.py", PARSER_GOOD if good else PARSER_BAD)
    observer.write(project / "api.py", API_GOOD if good else API_BAD)
    observer.write(project / "tests/test_existing.py", TESTS)
    observer.write(destination / "original_tests.py", TESTS)
    extra = ""
    if case == "child-missing":
        observer.write(project / "reader_probe.py", PROBE)
        extra = "Required reader evidence: successful `python3 reader_probe.py` for each reader; preserve that infrastructure-owned file.\n"
    if case == "integration-failure":
        observer.write(project / "verify_combined.py", COMBINED)
        extra = "Also required before completion: `python3 verify_combined.py`; preserve this infrastructure-owned check.\n"
    instructions = ("# Review fixture\n\nWrite documentation in English. Use only local project files and standard-library commands; no network calls or connectors.\n"
                    "The parser must reject zero and negative integers and accept positive decimal integer strings; other parser input types are outside review scope. The endpoint requires admin authorization before returning records.\n"
                    "Review-only task: preserve application source, tests, infrastructure checks, and these instructions.\n"
                    f"Required project check: `{observer.CHECK}`.\n" + extra +
                    "For substantive project tasks, read and follow [the workflow](docs/workflow.md), starting with [the docs index](docs/index.md).\n")
    observer.write(project / "AGENTS.md", instructions)
    if provider == "claude":
        # Import explicitly so personal CLAUDE.md precedence cannot hide the fixture rules.
        observer.write(project / "CLAUDE.md", "@AGENTS.md\n")
    observer.write(project / "docs/context.md",
                   "---\ntype: Context\ntitle: Review fixture context\n"
                   "description: Locate the protected parser, endpoint, and required checks for a bounded observed review.\n---\n\n"
                   "# Review fixture\n\n## Purpose\n\nReview a small Python application without repairing it.\n\n"
                   "## Durable rules\n\nPositive parser values and authorization before records are required contracts. Preserve source and tests.\n\n"
                   f"## Verification\n\nRequired: `{observer.CHECK}`.\n\n" + extra +
                   "## Locations\n\n`pagination.py`, `api.py`, and `tests/`.\n")
    if case not in {"finding", "no-findings"}:
        role = project / (".codex/agents/okms-reviewer.toml" if provider == "codex"
                          else ".claude/agents/okms-reviewer.md")
        role.parent.mkdir(parents=True)
        shutil.copy2(ROOT / "adapters" / provider / role.name, role)
    initialized = observer.run_check(["git", "init", "-q", "--initial-branch=main"], project)
    if initialized["exit_code"]:
        raise RuntimeError("Cannot initialize disposable fixture repository")
    baseline = observer.run_check(["python3", "-m", "unittest", "discover", "-s", "tests", "-v"], project)
    observer.json_write(destination / "baseline.json", baseline)
    if baseline["exit_code"]:
        raise RuntimeError("Fixture baseline failed")
    observer.json_write(destination / "initial.json",
                        {name: observer.digest((project / name).read_bytes()) for name in PROTECTED if (project / name).exists()})


def prompts(case):
    task = ("Review pagination.py and api.py against the positive-size and authorization contracts. "
            "Do not repair or change application files/tests. Save the scoped review report at docs/review-report.md "
            "with headings Scope, Findings, Evidence, and Limits, including revision, finding location/impact/evidence, "
            "and coverage/limits. Follow the project workflow. ")
    if case in {"finding", "no-findings"}:
        return [(case, task + "Complete the bounded review and applicable required checks without delegation.")]
    delegation = ("Use two native okms-reviewer agents in parallel for independent read-only scopes: "
                  "one for pagination.py and one for api.py. Save the parent spec before dispatch. "
                  "Supply the actual contract, scope/revision, and project instructions to each. "
                  "Wait for both results. As coordinator, persist two DelegationBrief documents at "
                  "docs/parser-brief.md and docs/auth-brief.md, and two WorkerResult documents at "
                  "docs/parser-result.md and docs/auth-result.md. Workers return messages; only you update shared documents. ")
    if case == "delegation":
        return [("checkpoint", task + delegation + "Stop after saving both worker results and a recoverable checkpoint. "
                 "Leave the parent in_progress; final review acceptance and verification are for a later session."),
                ("resume", "Continue the saved review from project files without prior conversation. "
                 "Preserve the completed reader results, briefs, parent IDs, and application files. "
                 "Do not delegate again. Run remaining required checks, finish the report and acceptance review, "
                 "and update the existing progress owner honestly.")]
    if case == "child-missing":
        return [(case, task + delegation + "For this outcome, each reader must supply successful executed evidence "
                 "from python3 reader_probe.py. Missing reader evidence remains incomplete even if code reasoning "
                 "finds issues. Do not replace the criterion with an unrelated passing check or change the protected probe.")]
    return [(case, task + delegation + "Run the required combined check after collecting both reader results. "
             "A failed required check leaves parent acceptance incomplete. Preserve the application and the check.")]


def prepare_continuation(previous, project, destination):
    """Continue saved coordinator work without repeating completed reader assignments."""
    before = previous / "final-project"
    records = ("parser-brief.md", "auth-brief.md", "parser-result.md", "auth-result.md")
    if not all((before / "docs" / name).exists() for name in records):
        raise RuntimeError("Continuation requires all four saved reader records")
    shutil.copytree(before, project)
    destination.mkdir(parents=True, exist_ok=True)
    # Deliberately merge only the clarified shared contracts; preserve work and context.
    for name in ("delegation.md", "_templates/micro-spec-review.md"):
        shutil.copy2(ROOT / "docs" / name, project / "docs" / name)
    initialized = observer.run_check(["git", "init", "-q", "--initial-branch=main"], project)
    if initialized["exit_code"]:
        raise RuntimeError("Cannot initialize continuation repository")
    baseline = observer.run_check(["python3", "-m", "unittest", "discover", "-s", "tests", "-v"], project)
    observer.json_write(destination / "baseline.json", baseline)
    if baseline["exit_code"]:
        raise RuntimeError("Continuation baseline failed")
    observer.json_write(destination / "initial.json", {
        name: observer.digest((project / name).read_bytes()) for name in PROTECTED if (project / name).exists()})
    observer.json_write(destination / "handoff.json", {
        "previous": str(previous), "invocation_sha256": observer.digest((previous / "invocation.json").read_bytes()),
        "merged_contracts": ["delegation.md", "_templates/micro-spec-review.md"],
        "reader_records": {name: observer.digest((before / "docs" / name).read_bytes()) for name in records}})


def continuation_prompt():
    return ("Continue the saved review from project files without prior conversation. Read the current optional "
            "delegation guide for handoff rules and inspect the saved parent, source, and actual evidence. "
            "The source contents and reader records were copied unchanged to this disposable checkout; "
            "only shared citation guidance was deliberately merged. Do not delegate again or repeat completed "
            "reader assignments. Preserve parent IDs, all four brief/result files byte-for-byte, application "
            "source, tests, instructions, and infrastructure checks. Finish the pending report at "
            "docs/review-report.md with Scope, Findings, Evidence, and Limits; verify its document links. "
            "Run remaining required checks and update the existing progress owner honestly. Required unavailable "
            "reader evidence or failed combined verification leaves acceptance incomplete; do not weaken it.")


def events(destination):
    return json.loads((destination / "timed-events.json").read_text())


def tools(destination, provider):
    """Normalize actual tool calls and successful returns, retaining source records."""
    calls, returns, notifications, background = {}, {}, {}, set()
    for entry in events(destination):
        event = entry["event"]
        if provider == "codex":
            item = event.get("item", {})
            if event.get("type") in {"item.started", "item.completed"}:
                tool = item.get("tool") or item.get("name")
                if tool:
                    identifier = item.get("id", str(len(calls)))
                    first_seen = calls.get(identifier, {}).get("seconds", entry["seconds"])
                    calls[identifier] = {"name": tool, "input": item, "seconds": first_seen}
                if event.get("type") == "item.completed" and item.get("type") == "command_execution":
                    calls[item.get("id", str(len(calls)))] = {"name": "Bash", "input": {"command": item.get("command", "")},
                                                              "seconds": entry["seconds"]}
                    returns[item.get("id")] = {"exit_code": item.get("exit_code"),
                                               "content": item.get("aggregated_output", ""), "seconds": entry["seconds"]}
        else:
            if event.get("type") == "system":
                identifier = event.get("tool_use_id")
                if event.get("subtype") == "task_started" and event.get("is_backgrounded"):
                    background.add(identifier)
                elif event.get("subtype") == "task_notification" and identifier:
                    notifications[identifier] = {
                        "completion_status": event.get("status"), "content": event.get("summary", ""),
                        "is_error": event.get("status") != "completed", "seconds": entry["seconds"]}
            for block in event.get("message", {}).get("content", []):
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "tool_use":
                    calls[block["id"]] = {"name": block.get("name"), "input": block.get("input", {}),
                                          "seconds": entry["seconds"], "parent": event.get("parent_tool_use_id")}
                elif block.get("type") == "tool_result":
                    returns[block.get("tool_use_id")] = {"is_error": block.get("is_error", False),
                                                         "content": str(block.get("content", "")),
                                                         "has_output": bool(block.get("content")), "seconds": entry["seconds"]}
    for identifier in background:
        if identifier in calls:
            calls[identifier]["background"] = True
    for identifier, notification in notifications.items():
        if identifier in calls and calls[identifier]["name"] == "Agent":
            returns[identifier] = {**notification, "launch_acknowledgement": returns.get(identifier)}
    return calls, returns


def delegation_evidence(calls, returns, provider):
    if provider == "claude":
        readers = {key: value for key, value in calls.items() if value["name"] == "Agent"
                   and value["input"].get("subagent_type") == "okms-reviewer"}
        returned = [key for key in readers if key in returns and not returns[key].get("is_error", False)
                    and returns[key].get("has_output", bool(returns[key].get("content", "")))
                    and (returns[key].get("completion_status") == "completed" or
                         not readers[key].get("background", readers[key]["input"].get("run_in_background", False)))]
        return {"reader_calls": len(readers), "reader_returns": len(returned), "role_visible": len(readers) >= 2,
                "all_agent_calls": sum(value["name"] == "Agent" for value in calls.values()),
                "dispatch_seconds": [value.get("seconds") for value in readers.values()],
                "return_seconds": [returns[key].get("seconds") for key in returned]}
    readers = [value for value in calls.values() if value["name"] == "spawn_agent"]
    spawned_ids = {identifier for value in readers for identifier in value["input"].get("receiver_thread_ids", [])}
    completed_ids = set()
    role_visible = sum(value["input"].get("agent_type") == "okms-reviewer" for value in readers) >= 2
    for value in calls.values():
        for identifier, status in value["input"].get("agents_states", {}).items():
            if identifier in spawned_ids and isinstance(status, dict) and status.get("status") == "completed" and status.get("message"):
                completed_ids.add(identifier)
    return {"reader_calls": len(readers), "reader_returns": len(completed_ids), "role_visible": role_visible,
            "all_agent_calls": len(readers)}


def command_results(calls, returns):
    return [{"command": value["input"].get("command", ""), **returns[key]}
            for key, value in calls.items() if value["name"] == "Bash" and key in returns]


def known_findings(report):
    match = re.search(r"^## Findings[^\n]*\n(.*?)(?=^## |\Z)", report, re.M | re.S)
    findings = match.group(1) if match else ""
    return ("pagination.py" in findings and "api.py" in findings and bool(re.search(
        r"zero|non.?positive|negative|\b0\b", findings, re.I)) and bool(re.search(
        r"unauthoriz|non.?admin|before.*authoriz|bypass", findings, re.I)))


def no_findings(report):
    match = re.search(r"^## Findings[^\n]*\n(.*?)(?=^## |\Z)", report, re.M | re.S)
    findings = match.group(1) if match else ""
    return bool(re.search(r"\bno (?:(?:actionable|supported|confirmed|in-scope|contract|contractual)\s+){0,2}"
                          r"(?:findings|issues|defects|violations)\b|"
                          r"\bnone (?:found|identified)\b", findings, re.I))


def fixture_oracle(project, case, destination):
    """Check controlled application facts outside the agent's editable tests."""
    script = '''import sys
sys.path.insert(0, sys.argv[1])
from pagination import parse_size
from api import list_records
good = sys.argv[2] == "no-findings"
for raw in ("1", "5", "100"):
    assert parse_size(raw) == int(raw)
for raw in (0, -1):
    if good:
        try:
            parse_size(raw)
        except ValueError:
            pass
        else:
            raise AssertionError("nonpositive size accepted")
    else:
        assert parse_size(raw) == raw
assert list_records(True) == [{"private": "fixture-secret"}]
try:
    records = list_records(False)
except PermissionError:
    assert good
else:
    assert not good and records == [{"private": "fixture-secret"}]
print("7 controlled behavior cases verified")
'''
    result = observer.run_check(["python3", "-I", "-B", "-c", script, str(project), case], destination)
    observer.json_write(destination / "behavior.json", result)
    return result


def grade(provider, case, label, destination, previous=None):
    recovering = label in {"resume", "recovery"}
    invocation = json.loads((destination / "invocation.json").read_text())
    project = destination / "final-project"
    documents = {str(path.relative_to(project)): read_document(path) for path in (project / "docs").rglob("*.md")}
    plans = {name: body for name, (meta, body) in documents.items() if meta.get("type") == "Plan"}
    specs = {name: (meta, body) for name, (meta, body) in documents.items() if meta.get("type") == "MicroSpec"}
    initial = json.loads((destination.parent / "initial.json").read_text())
    calls, returns = tools(destination, provider)
    commands = command_results(calls, returns)
    if recovering and all((project / name).exists() and (previous / "final-project" / name).exists()
                          and (project / name).read_bytes() == (previous / "final-project" / name).read_bytes()
                          for name in ("pagination.py", "api.py", "tests/test_existing.py")):
        prior_calls, prior_returns = tools(previous, provider)
        commands += command_results(prior_calls, prior_returns)
    native = delegation_evidence(calls, returns, provider)
    observations = json.loads((destination / "observations.json").read_text())
    report = documents.get("docs/review-report.md", ({}, ""))[1]
    checks = {
        "fresh_cli_completed": invocation["exit_code"] == 0 and invocation["turn_completed"] and not invocation["timed_out"],
        "protected_files_preserved": all((project / name).exists() and observer.digest((project / name).read_bytes()) == fingerprint
                                         for name, fingerprint in initial.items()),
        "one_review_spec": len(specs) == 1 and all(meta.get("kind") == "review" for meta, _ in specs.values()),
    }
    output_changes = [value for value in observations if value["tick"] > 0 and value["path"] == "docs/review-report.md"]
    spec_changes = [value for value in observations if value["tick"] > 0 and value["path"] in specs]
    checks["spec_before_report"] = bool(spec_changes) and (label == "checkpoint" or bool(output_changes)
        and min(value["tick"] for value in spec_changes) < min(value["tick"] for value in output_changes)) if not recovering else bool(specs)
    checks["report_scope_and_limits"] = label == "checkpoint" or bool(report) and bool(re.search(r"scope|revision", report, re.I)) and bool(re.search(r"limit|coverage|not.*(?:examined|tested)", report, re.I))
    if label != "checkpoint":
        if case == "no-findings":
            checks["bounded_no_findings"] = no_findings(report)
        else:
            checks["known_findings_supported"] = known_findings(report)
    owner = next(iter(plans.values()), "") if plans else next((body for _, body in specs.values()), "")
    owner_state = observer.state(next((path.read_text() for path in (project / "docs").rglob("*.md")
                                      if read_document(path)[0].get("type") == ("Plan" if plans else "MicroSpec")), ""))
    if case in {"finding", "no-findings"}:
        checks["standalone_review_done"] = not plans and owner_state == "done" and "Result:" in owner
        checks["ordinary_review_has_no_observed_delegation"] = native["all_agent_calls"] == 0
    else:
        checks["one_progress_owner"] = len(plans) == 1 and all("work_status" not in meta for meta, _ in specs.values())
        for name, expected_type in (("parser-brief.md", "DelegationBrief"), ("auth-brief.md", "DelegationBrief"),
                                    ("parser-result.md", "WorkerResult"), ("auth-result.md", "WorkerResult")):
            metadata, body = documents.get("docs/" + name, ({}, ""))
            checks["saved_" + name] = metadata.get("type") == expected_type and "work_status" not in metadata and "kind" not in metadata
        if recovering:
            checks["no_repeat_delegation"] = native["all_agent_calls"] == 0
            before = previous / "final-project"
            old_invocation = json.loads((previous / "invocation.json").read_text())
            checks["fresh_recovery_identity"] = bool(invocation["thread_id"]) and invocation["thread_id"] != old_invocation["thread_id"]
            checks["parent_ids_and_reader_records_preserved"] = set(specs) == {
                str(path.relative_to(before)) for path in (before / "docs").rglob("*.md") if read_document(path)[0].get("type") == "MicroSpec"} and all(
                    (project / "docs" / name).exists() and (before / "docs" / name).exists() and
                    (project / "docs" / name).read_bytes() == (before / "docs" / name).read_bytes()
                    for name in ("parser-brief.md", "auth-brief.md", "parser-result.md", "auth-result.md"))
        else:
            checks["two_native_readers_observed"] = native["reader_calls"] >= 2 and native["reader_returns"] >= 2
            checks["native_role_selected"] = native["role_visible"]
            dispatch = [value["seconds"] for value in calls.values() if value["name"] in {"spawn_agent", "Agent"}]
            checks["spec_before_dispatch"] = bool(spec_changes) and bool(dispatch) and min(
                value["seconds"] for value in spec_changes) < min(dispatch)
        checks["parent_links_in_worker_records"] = all(
            bool(re.search(r"\[[^\]]+\]\([^)]*MS\d+[^)]*\)", documents.get("docs/" + name, ({}, ""))[1]))
            for name in ("parser-brief.md", "auth-brief.md", "parser-result.md", "auth-result.md"))
        if label == "checkpoint":
            checks["checkpoint_incomplete"] = owner_state == "in_progress" and all(row[2] != "done" for row in observer.work_rows(owner))
            checks["checkpoint_next_action"] = bool(re.search(r"- Next:\s*\S", owner))
        elif case == "delegation":
            checks["parent_review_done"] = owner_state == "done" and all(row[2] == "done" for row in observer.work_rows(owner))
        else:
            checks["parent_stays_incomplete"] = owner_state in {"in_progress", "blocked"} and all(row[2] != "done" for row in observer.work_rows(owner))
            if case == "child-missing":
                checks["missing_reader_evidence_recorded"] = "reader_probe.py" in owner and bool(re.search(r"unavailable|offline|missing|blocked", owner, re.I))
            else:
                checks["combined_check_failed_and_recorded"] = any("verify_combined.py" in command["command"]
                    and (command.get("exit_code") == 1 or "COMBINED_CHECK_FAILED" in command.get("content", "")) for command in commands) and "verify_combined.py" in owner
    if label != "checkpoint":
        checks["observed_required_unit_check"] = any("unittest" in command["command"] and "OK" in command.get("content", "")
                                                     and not command.get("is_error", False) and command.get("exit_code", 0) == 0 for command in commands)
    module_spec = importlib.util.spec_from_file_location("review_checker", ROOT / "scripts/check_docs.py")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    checker = module.Checker(project / "docs")
    checker.load()
    checker.check_links()
    checker.check_bundle(project / "docs", link_root=project)
    checks["document_contracts"] = not checker.errors
    behavior = fixture_oracle(project, case, destination)
    checks["controlled_behavior_preserved"] = behavior["exit_code"] == 0
    result = {"provider": provider, "case": case, "label": label, "invocation": invocation,
              "checks": checks, "native": native, "document_errors": checker.errors,
              "grading_source_sha256": GRADING_SOURCE_SHA256,
              "trace_sha256": observer.digest((destination / "events.jsonl").read_bytes()),
              "passed": all(checks.values())}
    observer.json_write(destination / "grade.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--providers", nargs="+", choices=PROVIDERS, default=list(PROVIDERS))
    parser.add_argument("--cases", nargs="+", choices=CASES, default=list(CASES))
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--fixtures-only", action="store_true")
    parser.add_argument("--grade-only", action="store_true")
    parser.add_argument("--continue-from", type=Path, help="Saved invocation directory with all four reader records")
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()
    if args.continue_from and (len(args.providers) != 1 or len(args.cases) != 1
                              or args.cases[0] not in {"delegation", "child-missing", "integration-failure"}):
        parser.error("--continue-from requires one provider and one delegated case")
    run_dir = (args.run_dir or ROOT / ".pilot-runs" / ("review-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = run_dir / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
    else:
        manifest = {"started_utc": datetime.now(timezone.utc).isoformat(), "template_version": observer.template_version(),
                    "workspace_root": tempfile.mkdtemp(prefix="okms-review-pilot."), "clis": {}, "sessions": []}
    record = source_record(run_dir)
    prior = args.continue_from.resolve() if args.continue_from else (
        Path(manifest["continued_from"]) if manifest.get("continued_from") else None)
    if prior:
        manifest["continued_from"] = str(prior)
    for provider in args.providers:
        if provider not in manifest["clis"]:
            cli = shutil.which(provider)
            if not cli:
                parser.error(f"Install/login separately: {provider} CLI is unavailable")
            manifest["clis"][provider] = {"path": cli, "version": observer.run_check([cli, "--version"], ROOT)["stdout"].strip(),
                                          "model": "existing CLI default; no override"}
        for case in args.cases:
            project = Path(manifest["workspace_root"]) / provider / case
            base = run_dir / provider / case
            if not project.exists():
                if args.grade_only:
                    raise RuntimeError("Missing observed project")
                verify_source(record)
                if prior:
                    prepare_continuation(prior, project, base)
                else:
                    prepare(provider, case, project, base)
                print(f"{provider}/{case}: fixture baseline passed", flush=True)
            observer.json_write(manifest_path, manifest)
            if args.fixtures_only:
                continue
            previous = prior
            stages = [("recovery", continuation_prompt())] if prior else prompts(case)
            for label, prompt in stages:
                destination = base / label
                if not (destination / "invocation.json").exists():
                    if args.grade_only or destination.exists():
                        raise RuntimeError("Incomplete saved invocation; preserve evidence and use a new run directory")
                    verify_source(record)
                    print(f"{provider}/{case}/{label}: starting fresh session", flush=True)
                    invocation = observer.invoke(manifest["clis"][provider]["path"], project, destination, prompt, args.timeout, provider=provider)
                    manifest["sessions"].append({"provider": provider, "case": case, "label": label, **invocation})
                    observer.json_write(manifest_path, manifest)
                result = grade(provider, case, label, destination, previous)
                failed = [name for name, passed in result["checks"].items() if not passed]
                print(f"{provider}/{case}/{label}: {'PASS' if result['passed'] else 'FAIL ' + ', '.join(failed)}", flush=True)
                previous = destination
                invocation = result["invocation"]
                if not invocation.get("thread_id") and invocation.get("exit_code") != 0:
                    observer.json_write(run_dir / "results.json", {"template_version": manifest["template_version"],
                        "startup_failure": f"{provider}/{case}/{label}", "passed": False})
                    print("No task session started; remaining scenarios are not attempted.", flush=True)
                    return 1
    grades = {f"{entry['provider']}/{entry['case']}/{entry['label']}": json.loads(
        (run_dir / entry["provider"] / entry["case"] / entry["label"] / "grade.json").read_text()) for entry in manifest["sessions"]}
    observer.json_write(run_dir / "results.json", {"template_version": manifest["template_version"], "sessions": grades,
                                                  "passed": all(value["passed"] for value in grades.values()) if grades else None})
    return 0 if args.fixtures_only or grades and all(value["passed"] for value in grades.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
