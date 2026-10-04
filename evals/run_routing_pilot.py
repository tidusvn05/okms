#!/usr/bin/env python3
"""Opt-in fresh-session task routing and portable Goal pilots."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

import run_agent_pilot as observer


ROOT = observer.ROOT
CASES = ("investigate-fix", "design", "research", "runbook", "general", "goal", "goal-blocked")
PROFILES = {"investigate-fix": "plan-first", "design": "plan-first", "research": "lite",
            "runbook": "lite", "general": "lite", "goal": "plan-first", "goal-blocked": "plan-first"}
EXPECTED = {"diagnosis": "investigation", "repair": "bugfix", "design": "design", "research": "research",
            "runbook": "runbook", "general": "general", "goal-limit": "implementation",
            "goal-resume": "implementation", "goal-blocked": "bugfix"}
SERVICE = '''import argparse, json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("action", choices=("status", "recover", "rollback"))
parser.add_argument("--dry-run", action="store_true")
args = parser.parse_args()
path = Path("service-state.json")
state = json.loads(path.read_text())
if args.action == "status":
    print("STATUS " + state["status"])
elif args.dry_run:
    print("DRY_RUN " + args.action + ": state unchanged; current=" + state["status"])
else:
    state["status"] = "healthy" if args.action == "recover" else "degraded"
    path.write_text(json.dumps(state) + "\\n")
    print("STATUS " + state["status"])
'''


def read_document(path: Path):
    text = path.read_text()
    if text.startswith("---\n"):
        _, raw, body = text.split("---", 2)
        metadata = yaml.safe_load(raw)
        return metadata if isinstance(metadata, dict) else {}, body
    return {}, text


def documents(project: Path, document_type: str) -> dict:
    return {str(path.relative_to(project)): (metadata, body)
            for path in (project / "docs").rglob("*.md")
            for metadata, body in [read_document(path)] if metadata.get("type") == document_type
            and "history" not in path.parts}


def source_record(run_dir: Path) -> dict:
    """Fingerprint the observed draft separately from later report edits."""
    payload = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
               for path in sorted((ROOT / "templates").glob("*/docs/**/*.md"))}
    record = {"files": payload,
              "combined_sha256": hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()}
    path = run_dir / "source-record.json"
    if path.exists():
        return json.loads(path.read_text())
    observer.json_write(path, record)
    snapshot = run_dir / "source-snapshot"
    shutil.copytree(ROOT / "templates", snapshot / "templates")
    shutil.copy2(Path(__file__), snapshot / "run_routing_pilot.py")
    shutil.copy2(ROOT / "scripts/check_docs.py", snapshot / "check_docs.py")
    return record


def prepare(case: str, project: Path, destination: Path):
    old_case = "blocked" if case == "goal-blocked" else "existing-system" if case == "design" else PROFILES[case]
    observer.prepare(old_case, project, destination)
    agents = project / "AGENTS.md"
    agents.write_text(agents.read_text().replace("For implementation tasks,", "For substantive project tasks,") +
                      "\nEvery new Markdown document under docs/ follows concept frontmatter and directory-index rules.\n")
    if case == "research":
        source_dir = project / "docs/sources"
        source_dir.mkdir()
        reports = {
            "harbor.md": ("Harbor", "2026-09-30", "4 ms", "Atomic multi-row commits are not supported. The fixture measurement used in-memory data; hardware is unspecified."),
            "quarry.md": ("Quarry", "2026-10-01", "12 ms", "Atomic multi-row commits are supported. The fixture measurement used durable writes; hardware is unspecified."),
        }
        for name, (title, date, latency, detail) in reports.items():
            observer.write(source_dir / name, f"---\ntype: Evidence\ntitle: {title} source report\n"
                           "description: Provide controlled synthetic source facts for the routing pilot's research comparison.\n---\n\n"
                           f"# {title}\n\nReport date: {date}. Observed p99 read latency: {latency} at 200 requests/second. {detail}\n\n"
                           "These are synthetic fixture reports, not measurements of actual vendors.\n")
        observer.write(source_dir / "index.md", "# Controlled source reports\n\n"
                       "- [Harbor](harbor.md) - Fixture latency and transaction evidence.\n"
                       "- [Quarry](quarry.md) - Fixture durability and transaction evidence.\n")
        with (project / "docs/index.md").open("a") as handle:
            handle.write("\n- [Controlled sources](sources/index.md) - Use these supplied reports for the bounded comparison.\n")
    if case == "runbook":
        observer.write(project / "fixture_service.py", SERVICE)
        observer.write(project / "service-state.json", '{"status": "degraded"}\n')
        with agents.open("a") as handle:
            handle.write("The operating fixture may be observed with status or rehearsed with --dry-run only. Preserve its source and state.\n")
    if case == "general":
        observer.write(project / "note_es.txt", "Tiempo limite: 10 segundos. Intentos maximos: 3.\n"
                       "Conservar el comando: python3 fixture_service.py --dry-run recover\n")
    observer.json_write(destination / "initial.json", {name: observer.digest(value) for name, value in observer.files(project).items()})


def prompts(case: str):
    if case == "investigate-fix":
        return [
            ("diagnosis", "Our article endpoint crashes for page_size='bad' and accepts invalid values. "
             "Find the cause and repair pagination to this contract: " + observer.VALIDATION_TASK + " " + observer.ENDPOINT_TASK +
             " For this session, reproduce at least one crashing request, explain the confirmed cause in a separate findings document, "
             "and stop before repairing application code. Save the remaining repair scope and checkpoint for another session."),
            ("repair", "Continue the pagination repair from the saved project files. Complete the remaining repair and regression checks."),
        ]
    if case == "design":
        return [("design", "Decide where the existing duplicated endpoint page_size validation should live. "
                 "Save a decision document comparing viable alternatives, consequences, and compatibility with article responses "
                 "and device authorization. This task produces the decision only; preserve application code and tests.")]
    if case == "research":
        return [("research", "Compare the supplied Harbor and Quarry source reports in docs/sources/ for read latency, "
                 "atomic multi-row commits, dates, and measurement limitations. Save a separate source-backed comparison report. "
                 "Treat these fixture reports as the complete source scope; identify what cannot be inferred. "
                 "This task is the comparison, with no architecture decision or application changes.")]
    if case == "runbook":
        return [("runbook", "Write an operator runbook for recovering the degraded fixture service with fixture_service.py. "
                 "Include trigger, prerequisites, actual commands, expected output, success/failure checks, and rollback. "
                 "Rehearse relevant steps with --dry-run only; preserve the application, service source, and service-state.json. "
                 "Record the rehearsal limits honestly.")]
    if case == "general":
        return [("general", "Translate note_es.txt into English and save a separate docs/translation.md. "
                 "Preserve the timeout, attempt count, and command exactly. Do not execute the translated command or change application code.")]
    if case == "goal":
        feature = observer.VALIDATION_TASK.replace("Fix parse_page_size", "Implement strict parse_page_size") + " " + observer.ENDPOINT_TASK
        return [
            ("goal-limit", "Build new strict pagination support using a portable Goal loop. " + feature +
             " The parser and endpoint are two dependent outcomes. The Goal's completion requires both. "
             "Set a maximum of one attempt for this session; stop at that limit with the remaining scope and checkpoint saved."),
            ("goal-resume", "Continue the saved portable Goal from project files. I explicitly extend its maximum "
             "from one attempt to two total attempts. Preserve already consumed attempts and complete the remaining scope and checks."),
        ]
    return [("goal-blocked", "Use a portable Goal loop with at most three attempts to repair this parser violation: " + observer.VALIDATION_TASK +
             " Complete the required project checks and record the actual result.")]


def grade(case: str, label: str, destination: Path, previous: Path | None) -> dict:
    invocation = json.loads((destination / "invocation.json").read_text())
    project = destination / "final-project"
    snapshots = json.loads((destination / "observations.json").read_text())
    commands = observer.command_events(destination)
    initial = json.loads((destination.parent / "initial.json").read_text())
    current_files = observer.files(project)
    specs, plans, goals = documents(project, "MicroSpec"), documents(project, "Plan"), documents(project, "Goal")
    expected = EXPECTED[label]
    seen_kinds = set()
    for command in commands:
        seen_kinds.update(re.findall(r"type: Template\s*\nkind: ([a-z]+)", command.get("aggregated_output", "")))
    checks = {"fresh_session_completed": invocation["exit_code"] == 0 and invocation["turn_completed"] and not invocation["timed_out"],
              "chosen_kind_present": any(info.get("kind") == expected for info, _ in specs.values()),
              "selected_blueprint_read": expected in seen_kinds,
              "only_current_kind_blueprints_read": seen_kinds <= {expected},
              "required_unit_check_passed": any("unittest" in c.get("command", "") and c.get("exit_code") == 0 and
                                                re.search(r"Ran [1-9]\d* tests?", c.get("aggregated_output", "")) for c in commands),
              "history_bodies_not_emitted": not re.search(r"HISTORY_BODY_CANARY_\d+", (destination / "events.jsonl").read_text())}
    existing = set(c["path"] for c in snapshots if c["tick"] == 0)
    artifacts = {}
    for path in (project / "docs").rglob("*.md"):
        relative = str(path.relative_to(project))
        info, body = read_document(path)
        if relative not in initial and path.name != "index.md" and info.get("type") not in {"MicroSpec", "Plan", "Goal", "Template"}:
            artifacts[relative] = body
    changes = [c for c in snapshots if c["tick"] > 0 and c["path"] in {"pagination.py", "api.py", *artifacts}]
    new_specs = [c for c in snapshots if c["path"] in specs and c["path"] not in existing]
    first_output = min((c["tick"] for c in changes), default=None)
    first_spec = min((c["tick"] for c in new_specs), default=None)
    checks["spec_saved_before_output"] = first_output is not None and first_spec is not None and first_spec < first_output
    timed_events = json.loads((destination / "timed-events.json").read_text())
    selected_reads = [event["tick"] for event in timed_events
                      if event["event"].get("type") == "item.completed"
                      and event["event"].get("item", {}).get("type") == "command_execution"
                      and expected in re.findall(r"type: Template\s*\nkind: ([a-z]+)",
                                                 event["event"]["item"].get("aggregated_output", ""))]
    checks["blueprint_read_before_output"] = first_output is not None and any(tick < first_output for tick in selected_reads)
    checks["all_kinds_match_scoped_outcomes"] = all(info.get("kind") in ({"investigation", "bugfix"} if case == "investigate-fix" else {expected}) for info, _ in specs.values())
    app_names = ("pagination.py", "api.py", "tests/test_existing.py")
    if label in {"diagnosis", "design", "research", "runbook", "general"}:
        checks["application_unchanged"] = all(observer.digest(current_files[name]) == initial[name] for name in app_names)
        checks["separate_deliverable_saved"] = bool(artifacts)
    body = "\n".join(artifacts.values()).lower()
    if label == "diagnosis":
        rows = observer.work_rows(next((text for _, text in plans.values()), ""))
        checks["investigation_checkpoint_and_deferred_repair"] = len(rows) >= 2 and rows[0][2] == "done" and all(row[2] == "planned" for row in rows[1:]) and len(specs) == 1
        checks["cause_supported_by_observed_failure"] = "int(" in body and "valueerror" in body and any("ValueError" in c.get("aggregated_output", "") for c in commands)
    if label == "repair":
        before = observer.files(previous / "final-project")
        prior_artifacts = [name for name in before if name not in initial and name.endswith(".md") and
                           read_document(previous / "final-project" / name)[0].get("type") not in {"MicroSpec", "Plan", "Goal", "Template"} and not name.endswith("index.md")]
        checks["completed_findings_preserved"] = bool(prior_artifacts) and all(current_files.get(name) == before[name] for name in prior_artifacts)
        checks["fresh_file_only_handoff"] = invocation["thread_id"] != json.loads((previous / "invocation.json").read_text())["thread_id"]
        checks["repair_plan_closed"] = len(plans) == 1 and next(iter(plans.values()))[0].get("work_status") == "done" and len(specs) >= 2
    if label == "design":
        checks["decision_and_compatibility_evidence"] = all(re.search(pattern, body) for pattern in (r"alternativ|option", r"decision|recommend", r"consequence|trade.?off", r"invalid_page_size", r"forbidden"))
        checks["existing_system_baseline_recorded"] = any("## Baseline" in text and "## Compatibility" in text and observer.CHECK in text for _, text in plans.values())
    if label == "research":
        checks["source_facts_dates_and_limits"] = all(token in body for token in ("harbor", "quarry", "2026-09-30", "2026-10-01", "atomic")) and all(re.search(pattern, body) for pattern in (r"\b4\s*ms", r"\b12\s*ms", r"limit|unknown|unspecified|comparab"))
        checks["source_references_present"] = "harbor.md" in body and "quarry.md" in body
    if label == "runbook":
        checks["operator_steps_and_failure_handling"] = all(re.search(pattern, body) for pattern in (r"prerequis|precondition", r"rollback", r"--dry-run", r"fixture_service.py", r"verif|success", r"fail|stop"))
        checks["dry_run_observed"] = any(re.search(r"^DRY_RUN (?:recover|rollback): state unchanged; current=degraded$",
                                                   c.get("aggregated_output", ""), re.M)
                                         and "python3 fixture_service.py" in c.get("command", "")
                                         and "--dry-run" in c.get("command", "") and c.get("exit_code") == 0 for c in commands)
        checks["service_source_and_state_preserved"] = all(observer.digest(current_files[name]) == initial[name] for name in ("fixture_service.py", "service-state.json"))
    if label == "general":
        checks["translation_retains_values_and_command"] = "10" in body and "seconds" in body and "3" in body and "python3 fixture_service.py --dry-run recover" in body
        checks["translated_command_not_executed"] = not any("fixture_service.py" in c.get("command", "") and "python3 fixture_service.py" in c.get("command", "") and c.get("exit_code") != 0 for c in commands)
    behavior = None
    if label in {"repair", "goal-limit", "goal-resume", "goal-blocked"}:
        behavior = observer.oracle(project, "plan-first" if label in {"repair", "goal-resume"} else "lite", destination)
        observer.json_write(destination / "behavior.json", behavior)
        checks["independent_behavior_passed"] = behavior["exit_code"] == 0
    if case.startswith("goal"):
        checks["one_persistent_goal"] = len(goals) == 1
        info, goal_body = next(iter(goals.values()), ({}, ""))
        checks["portable_mode_honest"] = info.get("execution") == "portable" and not info.get("native_id")
        rows = observer.work_rows(next((text for _, text in plans.values()), ""))
        goal_versions = [(c, read_document(destination / c["snapshot"])[0]) for c in snapshots if c["path"] in goals and c["snapshot"]]
        source_changes = [c for c in snapshots if c["tick"] > 0 and c["path"] in {"pagination.py", "api.py"}]
        first_source = min((c["tick"] for c in source_changes), default=None)
        required_count = 2 if label == "goal-resume" else 1
        checks["attempt_reserved_before_code"] = first_source is not None and any(c["tick"] < first_source and version.get("iterations_used") == required_count for c, version in goal_versions)
        if label == "goal-limit":
            checks["limit_preserves_incomplete_goal"] = info.get("max_iterations") == info.get("iterations_used") == 1 and info.get("work_status") == "in_progress" and info.get("stop_reason") == "iteration_limit"
            checks["one_outcome_and_spec_at_limit"] = len(specs) == 1 and len(rows) == 2 and rows[0][2] == "done" and rows[1][2] == "planned" and observer.digest(current_files["api.py"]) == initial["api.py"]
        elif label == "goal-resume":
            before_goals = documents(previous / "final-project", "Goal")
            checks["same_goal_and_new_conversation"] = set(goals) == set(before_goals) and invocation["thread_id"] != json.loads((previous / "invocation.json").read_text())["thread_id"]
            checks["explicit_extension_preserves_attempts"] = info.get("max_iterations") == info.get("iterations_used") == 2 and all(version.get("iterations_used", 0) >= 1 for _, version in goal_versions)
            checks["goal_completed_with_plan"] = info.get("work_status") == "done" and info.get("stop_reason") == "complete" and len(rows) == 2 and all(row[2] == "done" for row in rows)
            checks["completed_parser_not_rewritten"] = current_files["pagination.py"] == observer.files(previous / "final-project")["pagination.py"] and not any(c["tick"] > 0 and c["path"] == "pagination.py" for c in snapshots)
        else:
            checks["required_gate_failed_without_repairing_it"] = current_files["verify_required.py"].decode() == observer.REQUIRED_GATE and any("verify_required.py" in c.get("command", "") and c.get("exit_code") == 2 for c in commands)
            checks["blocked_goal_preserves_incomplete_verification"] = info.get("work_status") == "blocked" and info.get("stop_reason") == "blocked" and info.get("max_iterations") == 3 and info.get("iterations_used") == 1 and "verify_required.py" in goal_body
    if PROFILES[case] == "lite":
        checks["standalone_lite_progress"] = len(specs) == 1 and not plans and not goals and next(iter(specs.values()))[0].get("work_status") == "done"
    spec = importlib.util.spec_from_file_location("routing_docs_checker", ROOT / "scripts/check_docs.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    checker = module.Checker(project / "docs")
    checker.load()
    checker.check_links()
    checker.check_bundle(project / "docs", link_root=project)
    checks["document_contracts"] = not checker.errors
    observer.write(destination / "original-tests/test_original.py", (destination.parent / "original_tests.py").read_text())
    original_script = "import sys,unittest; sys.path.insert(0,sys.argv[1]); suite=unittest.defaultTestLoader.discover(sys.argv[2]); result=unittest.TextTestRunner(verbosity=2).run(suite); sys.exit(not result.wasSuccessful())"
    original_checks = observer.run_check([sys.executable, "-I", "-c", original_script, str(project), str(destination / "original-tests")], destination)
    checks["independent_original_tests_passed"] = original_checks["exit_code"] == 0
    observer.json_write(destination / "original-checks.json", original_checks)
    result = {"scenario": label, "profile": PROFILES[case], "expected_kind": expected,
              "selected_blueprints_observed": sorted(seen_kinds), "invocation": invocation,
              "checks": checks, "passed": all(checks.values()), "document_errors": checker.errors,
              "specs": list(specs), "plans": list(plans), "goals": {name: info for name, (info, _) in goals.items()},
              "deliverables": list(artifacts), "behavior": behavior, "original_checks": original_checks,
              "prompt_sha256": hashlib.sha256((destination / "prompt.txt").read_bytes()).hexdigest(),
              "trace_sha256": hashlib.sha256((destination / "events.jsonl").read_bytes()).hexdigest()}
    observer.json_write(destination / "grade.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", nargs="+", choices=CASES, default=list(CASES))
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--fixtures-only", action="store_true")
    parser.add_argument("--grade-only", action="store_true")
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()
    run_dir = (args.run_dir or ROOT / ".pilot-runs" / ("routing-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = run_dir / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
    else:
        cli = shutil.which("codex")
        if not cli or observer.run_check([cli, "login", "status"], ROOT)["exit_code"]:
            parser.error("Codex must already be installed and logged in; credentials are never created or copied")
        manifest = {"started_utc": datetime.now(timezone.utc).isoformat(), "cli": cli,
                    "cli_version": observer.run_check([cli, "--version"], ROOT)["stdout"].strip(),
                    "model": "existing default; no override", "template_version": observer.template_version(),
                    "workspace_root": tempfile.mkdtemp(prefix="okms-routing-pilot."), "sessions": []}
        observer.json_write(manifest_path, manifest)
    workspace_root = Path(manifest["workspace_root"])
    recorded_source = source_record(run_dir)
    print(f"Artifacts: {run_dir}\nProjects: {workspace_root}", flush=True)
    for case in args.cases:
        project, base = workspace_root / case, run_dir / case
        if not project.exists():
            if args.grade_only:
                raise RuntimeError(f"Missing observed project for {case}")
            for name, fingerprint in recorded_source["files"].items():
                if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != fingerprint:
                    raise RuntimeError("Payload changed since this run started; preserve evidence and use a new run directory")
            base.mkdir(parents=True, exist_ok=True)
            prepare(case, project, base)
            print(f"{case}: original baseline passed", flush=True)
        if args.fixtures_only:
            continue
        previous = None
        for label, prompt in prompts(case):
            destination = base / label
            if not (destination / "invocation.json").exists():
                if args.grade_only or destination.exists():
                    raise RuntimeError(f"Missing or incomplete session {label}; preserve artifacts and use a fresh run directory")
                print(f"{label}: starting fresh session", flush=True)
                invocation = observer.invoke(manifest["cli"], project, destination, prompt, args.timeout)
                manifest["sessions"].append({"case": case, "label": label, **invocation})
                observer.json_write(manifest_path, manifest)
                print(f"{label}: CLI exit {invocation['exit_code']}, {invocation['duration_seconds']:.1f}s", flush=True)
            result = grade(case, label, destination, previous)
            failed = [name for name, passed in result["checks"].items() if not passed]
            print(f"{label}: {'PASS' if result['passed'] else 'FAIL ' + ', '.join(failed)}", flush=True)
            previous = destination
    grades = {entry["label"]: json.loads((run_dir / entry["case"] / entry["label"] / "grade.json").read_text())
              for entry in manifest["sessions"] if (run_dir / entry["case"] / entry["label"] / "grade.json").exists()}
    observer.json_write(run_dir / "results.json", {"template_version": manifest["template_version"], "sessions": grades,
                                                    "passed": all(value["passed"] for value in grades.values()) if grades else None})
    return 0 if args.fixtures_only or grades and all(value["passed"] for value in grades.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
