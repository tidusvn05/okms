#!/usr/bin/env python3
"""Opt-in live mixed-CLI evaluation; fixture/grader checks start no agent."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "templates/hybrid-team"
sys.path.insert(0, str(ROOT / "evals"))
from hybrid_support import BINARY, install, capabilities, observation, Runtime, atomic_json, stop_process

CASES = ("codex", "claude", "blocked")
PLAN = "docs/work/P001-feature/plan.md"
SPECS = {"labels": "docs/work/P001-feature/P001-MS01-labels.md",
         "durations": "docs/work/P001-feature/P001-MS02-durations.md"}
CHECK_SOURCE = '''import sys
from labels import normalize_label
from durations import duration_label
mode = sys.argv[1]
if mode == "gate":
    print("Required external fixture gate is unavailable; do not remove it.")
    raise SystemExit(34)
if mode in {"labels", "all"}:
    assert normalize_label("  HELLO   World ") == "hello world"
    assert normalize_label("A\\tB") == "a b"
    for bad in ("", "  ", None, 3):
        try:
            normalize_label(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("label must reject invalid input")
if mode in {"durations", "all"}:
    assert duration_label(90) == "1m30s"
    assert duration_label(0) == "0m00s"
    for bad in (-1, True, 1.5, "90"):
        try:
            duration_label(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("duration must reject invalid input")
print("Assigned fixture checks passed:", mode)
'''
ORACLE = '''import json
from labels import normalize_label
from durations import duration_label
checks = []
for value, expected in (("  MiXeD\\tLabel  ", "mixed label"), ("one\\nTWO", "one two"), ("éÉ", "éé")):
    try: checks.append(normalize_label(value) == expected)
    except Exception: checks.append(False)
for value in ("", "\\t", 0, None):
    try: normalize_label(value); checks.append(False)
    except ValueError: checks.append(True)
    except Exception: checks.append(False)
for value, expected in ((0, "0m00s"), (59, "0m59s"), (60, "1m00s"), (3671, "61m11s")):
    try: checks.append(duration_label(value) == expected)
    except Exception: checks.append(False)
for value in (-1, True, 2.5, "60"):
    try: duration_label(value); checks.append(False)
    except ValueError: checks.append(True)
    except Exception: checks.append(False)
print(json.dumps({"passed": sum(checks), "total": len(checks), "all_passed": all(checks)}))
'''
WAIT_SOURCE = '''import json, pathlib, sqlite3, time
root = pathlib.Path(__file__).resolve().parents[2]
until = time.monotonic() + 850
while time.monotonic() < until:
    meta = json.loads((root / ".okms/state/pilot-standby.json").read_text())
    with sqlite3.connect(root / ".okms/state/team.sqlite3") as db:
        role = db.execute("SELECT role FROM agents WHERE id=?", (meta["agent_id"],)).fetchone()[0]
    if role == "coordinator":
        print(json.dumps(meta)); break
    time.sleep(.5)
else:
    raise SystemExit("No handoff observed before the fixture wait limit")
'''


def run_command(project, argv):
    value = subprocess.run(argv, cwd=project, capture_output=True, text=True, timeout=30)
    return {"argv": argv, "exit_code": value.returncode, "stdout": value.stdout, "stderr": value.stderr}


def write(project, relative, content):
    path = project / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fingerprint():
    paths = [path for path in SOURCE.rglob("*") if path.is_file() and "__pycache__" not in path.parts]
    paths += list((ROOT / "src").glob("*.rs"))
    paths += [ROOT / name for name in ("Cargo.toml", "Cargo.lock", "build.rs", "LICENSE-MIT", "LICENSE-APACHE", "evals/hybrid_support.py")]
    paths += [Path(__file__), ROOT / "scripts/check_docs.py"]
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(paths)}


def prepare(directory, case, source=SOURCE):
    project = directory / "project"
    project.mkdir(parents=True)
    write(project, "labels.py", "def normalize_label(value):\n    return value\n")
    write(project, "durations.py", 'def duration_label(seconds):\n    return str(seconds) + "s"\n')
    write(project, "checks.py", CHECK_SOURCE)
    write(project, "keep.txt", "Original tracked note.\n")
    write(project, ".gitignore", "__pycache__/\n")
    write(project, "AGENTS.md", "Work only on this fixture. Preserve keep.txt, notes.txt, tests, staging and HEAD.\n")
    for argv in (["git", "init", "-q"], ["git", "add", "."],
                 ["git", "-c", "user.name=Pilot", "-c", "user.email=pilot@example.invalid", "commit", "-qm", "Fixture baseline"]):
        result = run_command(project, argv)
        if result["exit_code"]:
            raise RuntimeError(result["stderr"])
    install(source, project)
    write(project, "keep.txt", "Staged project note.\n")
    run_command(project, ["git", "add", "keep.txt"])
    write(project, "keep.txt", "Unstaged project note.\n")
    write(project, "notes.txt", "Nonignored untracked context.\n")
    write(project, ".okms/state/wait_handoff.py", WAIT_SOURCE)
    config = json.loads((project / ".okms/team.json").read_text())
    config["checks"] = [["python3", "checks.py", "gate" if case == "blocked" else "all"]]
    atomic_json(project / ".okms/team.json", config)
    write(project, "docs/context.md", "---\ntype: Context\ntitle: Hybrid pilot fixture\ndescription: Scope and actual checks for disposable CLI coordination.\n---\n\n# Context\n\nTwo independent modules. Required checks are argv arrays in .okms/team.json.\nKeep user notes, staging, HEAD, instructions and test source intact.\nWorker checks: python3 checks.py labels or durations. Root checks: python3 checks.py " + ("gate" if case == "blocked" else "all") + ".\n")
    write(project, PLAN, "---\ntype: Plan\ntitle: P001 · Hybrid fixture\ndescription: Deliver two scoped modules with mixed-provider workers.\nwork_status: in_progress\n---\n\n# P001 · Hybrid fixture\n\n## Goal\n\nImplement label normalization and duration formatting.\n\n## Baseline\n\nThe original implementations do not satisfy new outputs; recorded baseline checks fail.\n\n## Compatibility\n\nPreserve user notes, staging, HEAD and test source.\n\n## Approach\n\nTwo ready disjoint workers; review, integrate and verify before completion.\n\n## Work\n\n| Spec | Depends on | State | Evidence |\n| --- | --- | --- | --- |\n| [P001-MS01 · Labels](P001-MS01-labels.md) | — | in_progress | Pending. |\n| [P001-MS02 · Durations](P001-MS02-durations.md) | — | in_progress | Pending. |\n\n## Resume\n\n- Current: both saved assignments.\n- Next: dispatch ready workers.\n- Blocker: none.\n\n## Result\n\nPending.\n")
    definitions = {"labels": "normalize_label accepts nonempty strings, collapses all whitespace and casefolds; empty or non-string input raises ValueError.",
                   "durations": 'duration_label accepts nonnegative integers excluding bool and renders minutes plus two-digit seconds (90 becomes "1m30s"); invalid input raises ValueError.'}
    for name, path in SPECS.items():
        write(project, path, "---\ntype: MicroSpec\nkind: implementation\ntitle: Hybrid fixture " + name + "\ndescription: Implement an independently scoped fixture module with actual evidence.\n---\n\n# " + name.title() + "\n\n## Intent\n\n" + definitions[name] + "\n\n## Constraints\n\n- Always: edit only " + name + ".py; preserve tests, user notes and shared contracts.\n- Never: claim parent completion or weaken required checks.\n\n## Acceptance\n\n- The named function satisfies valid/invalid inputs above.\n- Assigned checks produce actual evidence; missing verification stays visible.\n\n## Verify\n\nRun python3 checks.py " + name + "; expect exit zero. Coordinator additionally runs configured combined/root checks.\n")
    write(project, "docs/work/P001-feature/index.md", "# Fixture\n\n- [Plan](plan.md) - Shared progress.\n- [Labels](P001-MS01-labels.md) - Label contract.\n- [Durations](P001-MS02-durations.md) - Duration contract.\n")
    with (project / "docs/work/index.md").open("a") as stream:
        stream.write("\n- [Fixture](P001-feature/index.md) - Saved hybrid work.\n")
    index = (project / "docs/index.md").read_text().replace("No open work. Add the current plan or standalone spec here when starting work, and remove its pointer when it closes.", "- [Fixture](work/P001-feature/plan.md) - Current work.")
    write(project, "docs/index.md", index)
    baseline = {"head": run_command(project, ["git", "rev-parse", "HEAD"])["stdout"].strip(),
                "index_sha256": hashlib.sha256((project / ".git/index").read_bytes()).hexdigest(),
                "preserved": {name: (project / name).read_text() for name in ("keep.txt", "notes.txt", "checks.py", "AGENTS.md", "CLAUDE.md")},
                "checks": [run_command(project, ["python3", "checks.py", name]) for name in ("labels", "durations")]}
    atomic_json(directory / "baseline.json", baseline)
    return project


def primary_prompt(case):
    peer = "" if case == "blocked" else """
The Codex labels assignment must first send a request to the registered durations worker (find its ID through status), asking it to confirm the saved label normalization contract. If no response is available, return waiting_input WITHOUT editing yet. On the resumed turn, read/ack the response, implement and verify.
The Claude durations assignment implements its module, polls inbox for that request, acknowledges it, and waits until the labels worker is waiting_input before sending a response with reply_to. Use status wait_seconds:2 for bounded polling. Confirm the saved label contract without changing scope; verify and return result_ready.
Put these coordination requirements in each assignment intent/context. Prepare BOTH dispatches with launch:false, then resume each queued worker, so both know the peer ID. Do not send the peer response yourself.
"""
    finish = """
Attempt integration using the configured required gate. It is deliberately unavailable and must stay configured. After failure, checkpoint BOTH rows blocked with real failure and a concrete next action. Never report done or remove the gate. Stop after preserving this incomplete result.
""" if case == "blocked" else """
Integrate using configured checks after inspecting actual results/diffs/gaps. Checkpoint P001-MS01 done with real evidence, leaving P001-MS02 open for the other root session. Read .okms/state/pilot-standby.json and handoff to its agent_id. Send a notice to coordinator describing the verified batch and remaining checkpoint; then stop, leaving final completion to the new owner. Do not overwrite its identity file.
"""
    return """You are the primary coordinator in an authorized disposable Hybrid Team pilot. Read project instructions, workflow, context and saved plan/specs. The external evaluation harness registers YOUR ACTUAL native session ID; read .okms/state/pilot-primary.json for identity_file. Use that file on every runtime command. This explicit bootstrap evaluates the runtime, not automatic Codex hook trust.
Execute autonomously through .okms/okms COMMAND --identity IDENTITY_FILE --input - and JSON stdin. Never launch provider CLIs directly or use native subagents. Preserve notes, staging, HEAD, tests and required gates. Do not rewrite specs or team configuration.
Dispatch Codex for labels.py/P001-MS01 and Claude for durations.py/P001-MS02 under docs/work/P001-feature/plan.md. Both contracts are saved and ready with no dependencies. Assign only the respective module, and checks [["python3","checks.py","labels"]] or [["python3","checks.py","durations"]]. Use status wait_seconds up to 30 while workers run. A result_ready is not completion. Read actual worker artifact results and diffs before acceptance_review.
""" + peer + finish


STANDBY_PROMPT = """You are the other root session in an authorized disposable Hybrid Team pilot. Read project instructions, workflow and saved plan. The external harness registers your ACTUAL native session ID; .okms/state/pilot-standby.json gives your identity_file. You start as standby. Do not dispatch, change files, or checkpoint before handoff.
Run python3 .okms/state/wait_handoff.py using Bash. It reads local state and waits up to 850 seconds for explicit handoff, then prints your identity_file. Read the actual identity file after handoff because its token changes.
Inspect the plan, runtime status, actual integrated diffs, run metadata/results, configured checks and inbox. Acknowledge the coordinator notice if present. Run verify with the existing configured root checks. If acceptance/evidence passes, checkpoint P001-MS02 done through the runtime with actual evidence, acceptance_review, an actual plan result and Resume current:none/next:none/blocker:none. Do not weaken checks. Report observations and native startup limits truthfully.
"""


def start_native(provider, project, directory, label, prompt):
    directory.mkdir(parents=True, exist_ok=True)
    argv = ["codex", "--no-daemon", "exec", "--json", "-"] if provider == "codex" else [
        "claude", "-p", "--verbose", "--output-format", "stream-json", "--permission-mode", "acceptEdits",
        "--permission-prompts", "none", "--tools", "Read,Glob,Grep,Edit,Write,Bash", "--allowedTools",
        "Read,Glob,Grep,Edit,Write,Bash"]
    (directory / "prompt.txt").write_text(prompt)
    atomic_json(directory / "invocation.json", {"argv": argv, "cwd": str(project), "started_at": datetime.now(timezone.utc).isoformat(),
                                                "permission_policy": "Existing Codex settings; Claude acceptEdits with local Bash/Read/Edit/Write explicitly allowed in this disposable fixture. Native deny rules remain. No bypass."})
    env = os.environ.copy()
    env.pop("CLAUDECODE", None)
    # Keep background Git reads from refreshing the root index during observation.
    env["GIT_OPTIONAL_LOCKS"] = "0"
    errors = (directory / "stderr.log").open("wb")
    process = subprocess.Popen(argv, cwd=project, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=errors, env=env, start_new_session=True)
    record = {"provider": provider, "label": label, "native_session_id": None, "exit_code": None,
              "artifact": str(directory), "bootstrap": "external join with actual streamed session ID", "errors": []}

    def read():
        with (directory / "stdout.jsonl").open("wb") as raw:
            for line in process.stdout:
                raw.write(line)
                raw.flush()
                try:
                    item = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(item, dict):
                    continue
                value = observation(provider, item)
                if value["native_session_id"] and record["native_session_id"] is None:
                    record["native_session_id"] = value["native_session_id"]
                    joined = Runtime(project).store.join(provider, value["native_session_id"])
                    atomic_json(project / (".okms/state/pilot-" + label + ".json"),
                                {key: joined[key] for key in ("agent_id", "identity_file", "role")})
                    record["agent_id"] = joined["agent_id"]
                if value["error"]:
                    record["errors"].append(value["error"])
        record["exit_code"] = process.wait()
        errors.close()
        atomic_json(directory / "result.json", record)

    thread = threading.Thread(target=read, daemon=True)
    thread.start()
    process.stdin.write(prompt.encode())
    process.stdin.close()
    return process, thread, record


def capture(project, directory, case, native):
    state = Runtime(project).store.status()
    atomic_json(directory / "state.json", state)
    with Runtime(project).store.connection() as db:
        messages = [{**json.loads(row["envelope"]), "acked": bool(row["acked"]), "deliveries": row["deliveries"]}
                    for row in db.execute("SELECT * FROM messages ORDER BY rowid")]
    atomic_json(directory / "messages.json", messages)
    atomic_json(directory / "oracle.json", run_command(project, [sys.executable, "-c", ORACLE]))
    current = {"head": run_command(project, ["git", "rev-parse", "HEAD"])["stdout"].strip(),
               "index_sha256": hashlib.sha256((project / ".git/index").read_bytes()).hexdigest(),
               "preserved": {name: (project / name).read_text() for name in ("keep.txt", "notes.txt", "checks.py", "AGENTS.md", "CLAUDE.md")}}
    atomic_json(directory / "current.json", current)
    (directory / "final-plan.md").write_text((project / PLAN).read_text())
    atomic_json(directory / "native.json", native)
    return grade(directory, case)


def grade(directory, case):
    read = lambda name: json.loads((directory / name).read_text())
    state, messages, native = read("state.json"), read("messages.json"), read("native.json")
    baseline, current = read("baseline.json"), read("current.json")
    plan = (directory / "final-plan.md").read_text()
    events = state["events"]
    workers = [agent for agent in state["agents"] if agent["role"] == "worker"]
    observations = read("observations.json")
    checks = {
        "native_roots_observed": bool(native) and all(value["native_session_id"] and value["exit_code"] == 0 and not value["errors"] for value in native),
        "two_provider_workers_returned": len(workers) == 2 and {agent["provider"] for agent in workers} == {"codex", "claude"}
            and all(agent["native_session_id"] and agent["status"] in {"result_ready", "integrated"} and json.loads(agent["notes"])["worker_result"] for agent in workers),
        "head_and_staging_preserved": current["head"] == baseline["head"] and current["index_sha256"] == baseline["index_sha256"],
        "notes_tests_instructions_preserved": current["preserved"] == baseline["preserved"],
        "one_coordinator_at_observed_checkpoints": bool(observations) and all(sum(agent["role"] == "coordinator" and agent["status"] == "active" for agent in item["agents"]) <= 1 for item in observations),
    }
    started = [event["sequence"] for event in events if event["type"] == "worker_started"]
    returned = [event["sequence"] for event in events if event["type"] in {"result_ready", "waiting_input", "worker_failed"}]
    checks["parallel_workers_observed"] = len(started) >= 2 and bool(returned) and started[1] < min(returned)
    checks["worker_checks_observed"] = len(workers) == 2 and all(any(event["type"] == "verification_finished" and
        event["from"] == agent["id"] and event["payload"].get("passed") and event["payload"].get("evidence")
        for event in events) for agent in workers)
    if case == "blocked":
        checks["required_gate_failure_retained"] = any(event["type"] == "integration_failed" and "Combined checks failed" in event["payload"].get("error", "") for event in events)
        checks["failed_verification_stays_incomplete"] = "work_status: done" not in plan and "| done |" not in plan and plan.count("| blocked |") == 2
        checks["no_unverified_root_application"] = not any(event["type"] == "integration_applied" for event in events)
    else:
        oracle = read("oracle.json")
        try:
            checks["independent_root_behavior"] = oracle["exit_code"] == 0 and json.loads(oracle["stdout"])["all_passed"]
        except ValueError:
            checks["independent_root_behavior"] = False
        checks["peer_request_response_ack"] = any(request["type"] == "request" and request["acked"] and
            request["from"].startswith("worker-") and request["to"].startswith("worker-") and
            any(response["type"] == "response" and response["reply_to"] == request["id"] and response["acked"] and
                response["from"] == request["to"] and response["to"] == request["from"] for response in messages) for request in messages)
        resumes = []
        for agent in workers:
            turns = list((directory / "project/.okms/state/runs" / agent["run_id"] / agent["id"]).glob("turn-*/invocation.json"))
            try:
                turns.sort(key=lambda path: datetime.fromisoformat(json.loads(path.read_text())["started_at"].replace("Z", "+00:00")))
            except (KeyError, TypeError, ValueError):
                resumes.append(False)
                continue
            for path in turns[1:]:
                argv = json.loads(path.read_text())["argv"]
                flag = "resume" if agent["provider"] == "codex" else "--resume"
                resumes.append(flag in argv and argv[argv.index(flag) + 1] == agent["native_session_id"])
        checks["exact_native_session_resume"] = bool(resumes) and all(resumes)
        checks["cross_provider_handoff_observed"] = len(native) == 2 and native[0]["provider"] != native[1]["provider"] and any(
            event["type"] == "coordinator_changed" and event["payload"].get("previous") == native[0].get("agent_id") and
            event["payload"].get("current") == native[1].get("agent_id") for event in events)
        checks["verified_integration_then_completion"] = bool(state["runs"]) and all(run["status"] == "applied" for run in state["runs"]) and "work_status: done" in plan
        integration = [event["sequence"] for event in events if event["type"] == "root_verification_finished" and event["payload"].get("passed")]
        done = [event["sequence"] for event in events if event["type"] == "checkpoint_saved" and event["payload"].get("state") == "done"]
        checks["completion_follows_actual_checks"] = bool(integration) and len(done) == 2 and min(done) > min(integration)
    receipts = [event["payload"] for event in events if event["type"] == "hook_received" and event["from"] in {value.get("agent_id") for value in native}]
    result = {"case": case, "pass": all(checks.values()), "checks": checks, "native_startup_receipts": receipts,
              "startup_limit": "External bootstrap joins actual IDs; untrusted Codex hooks are not activated by the runner."}
    atomic_json(directory / "grade.json", result)
    return result


def execute(directory, case, timeout):
    project = directory / "project"
    primary = "claude" if case == "blocked" else case
    handles = [start_native(primary, project, directory / "primary", "primary", primary_prompt(case))]
    until, last, observations, standby_started = time.monotonic() + timeout, None, [], case == "blocked"
    try:
        while any(process.poll() is None for process, _, _ in handles):
            if time.monotonic() >= until:
                for _, _, record in handles:
                    record["errors"].append("Pilot timeout; partial evidence retained.")
                break
            if not standby_started and (project / ".okms/state/pilot-primary.json").exists():
                other = "claude" if primary == "codex" else "codex"
                handles.append(start_native(other, project, directory / "standby", "standby", STANDBY_PROMPT))
                standby_started = True
            state = Runtime(project).store.status()
            signature = [(agent["id"], agent["status"], agent["role"]) for agent in state["agents"]]
            if signature != last:
                observations.append({"created_at": datetime.now(timezone.utc).isoformat(), "agents": state["agents"],
                                     "plan": (project / PLAN).read_text(),
                                     "event_sequence": state["events"][-1]["sequence"] if state["events"] else 0})
                print(case + ": " + ", ".join(agent["provider"] + "/" + agent["role"] + "=" + agent["status"] for agent in state["agents"]), flush=True)
                last = signature
            time.sleep(.5)
    finally:
        for process, thread, record in handles:
            if process.poll() is None:
                stop_process(process)
            thread.join(timeout=10)
            record["exit_code"] = process.poll()
        with Runtime(project).store.transaction() as db:
            db.execute("UPDATE agents SET status='cancelled' WHERE role='worker' AND status IN ('queued','starting','running','waiting_input')")
        atomic_json(directory / "observations.json", observations)
    return capture(project, directory, case, [record for _, _, record in handles])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--cases", nargs="+", choices=CASES, default=list(CASES))
    parser.add_argument("--fixtures-only", action="store_true")
    parser.add_argument("--grade-only", action="store_true")
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args(argv)
    directory = args.run_dir.resolve()
    directory.mkdir(parents=True, exist_ok=True)
    if args.grade_only:
        results = [grade(directory / case, case) for case in args.cases]
    else:
        signature = fingerprint()
        saved = directory / "source.json"
        if saved.exists() and json.loads(saved.read_text()) != signature:
            parser.error("Source changed; use a new run directory and retain previous observations.")
        binary_metadata = directory / "binary.json"
        digest = hashlib.sha256(BINARY.read_bytes()).hexdigest()
        if saved.exists():
            if not binary_metadata.is_file() or not (directory / "source/okms").is_file():
                parser.error("Partial binary snapshot exists; preserve/review it and use explicit recovery or a new directory.")
            recorded = json.loads(binary_metadata.read_text())["sha256"]
            if recorded != digest or recorded != hashlib.sha256((directory / "source/okms").read_bytes()).hexdigest():
                parser.error("Binary changed; use a new run directory and retain previous observations.")
        if not saved.exists():
            atomic_json(saved, signature)
            shutil.copytree(SOURCE, directory / "source/hybrid-team", ignore=shutil.ignore_patterns("__pycache__"))
            shutil.copy2(__file__, directory / "source/run_hybrid_pilot.py")
            shutil.copy2(ROOT / "scripts/check_docs.py", directory / "source/check_docs.py")
            shutil.copy2(ROOT / "evals/hybrid_support.py", directory / "source/hybrid_support.py")
            shutil.copy2(BINARY, directory / "source/okms")
            atomic_json(directory / "binary.json", {"path": str(BINARY),
                "sha256": hashlib.sha256(BINARY.read_bytes()).hexdigest(),
                "version": subprocess.check_output([str(BINARY), "--version"], text=True).strip()})
            for path in [ROOT / "Cargo.toml", ROOT / "Cargo.lock", ROOT / "build.rs", ROOT / "LICENSE-MIT", ROOT / "LICENSE-APACHE", *(ROOT / "src").glob("*.rs")]:
                target = directory / "source" / path.relative_to(ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
        results = []
        for case in args.cases:
            target = directory / case
            if not (target / "project").exists():
                prepare(target, case, directory / "source/hybrid-team")
            if args.fixtures_only:
                print(case + ": fixture prepared; no provider session launched.", flush=True)
                continue
            if (target / "grade.json").exists():
                results.append(grade(target, case))
                continue
            if (target / "primary/invocation.json").exists():
                parser.error("Partial native execution exists; preserve/review its artifacts and use explicit recovery or a new run directory. It is never silently restarted.")
            providers = capabilities(Runtime(target / "project").config, target / "project")
            atomic_json(target / "capabilities.json", providers)
            if not all(value["available"] and value["authenticated"] and value.get("structured_output") for value in providers.values()):
                parser.error("Both CLIs must support structured output and be logged in; setup/auth is not performed.")
            results.append(execute(target, case, args.timeout))
    if args.fixtures_only:
        return 0
    binary_metadata = directory / "binary.json"
    if binary_metadata.is_file():
        version = json.loads(binary_metadata.read_text())["version"].split()[-1]
    else:
        installed = directory / args.cases[0] / "project/.okms/install.json"
        version = json.loads(installed.read_text())["version"] if installed.is_file() else "unknown"
    atomic_json(directory / "results.json", {"profile": "hybrid-team", "runtime": "rust", "version": version, "results": results})
    for result in results:
        print(result["case"] + ": " + ("PASS" if result["pass"] else "FAIL") + " " + json.dumps(result["checks"]), flush=True)
    return 0 if all(result["pass"] for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
