"""Detached, bounded CLI driver with persistent session IDs and raw artifacts."""

from __future__ import annotations

import json
import os
import queue
import signal
import subprocess
import threading
import time
from pathlib import Path

from . import gitops, providers
from .state import Store, TeamError, atomic_json, dump, now


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


def execute_checks(directory, checks, output, timeout=1800):
    evidence = []
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    for number, argv in enumerate(checks):
        if not isinstance(argv, list) or not argv or not all(isinstance(part, str) and part for part in argv):
            raise TeamError("Checks must be nonempty argument arrays, without a shell.")
        path = output / f"check-{number + 1}.log"
        start = time.monotonic()
        with path.open("wb") as stream:
            try:
                process = subprocess.Popen(argv, cwd=directory, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
                try:
                    code = process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    stop_process(process)
                    code = None
            except OSError as error:
                stream.write(str(error).encode())
                code = None
        evidence.append({"argv": argv, "exit_code": code, "artifact": str(path),
                         "elapsed_seconds": round(time.monotonic() - start, 3)})
    atomic_json(output / "checks.json", evidence)
    return evidence


def run(project, agent_id, reason="Initial assignment", nonce=None):
    store = Store(project)
    config = json.loads((Path(project) / ".okms/team.json").read_text())
    with store.transaction() as db:
        row = db.execute("SELECT * FROM agents WHERE id=?", (agent_id,)).fetchone()
        if not row or row["role"] != "worker" or row["status"] != "starting" or row["driver_nonce"] != nonce:
            raise TeamError("Worker is not queued; refusing a duplicate driver.")
        agent = dict(row)
        db.execute("UPDATE agents SET status='running',pid=? WHERE id=?", (os.getpid(), agent_id))
        store.event(db, "worker_started", agent_id, agent["run_id"], agent["spec_id"], {"driver_pid": os.getpid()})
    directory = store.directory / "runs" / agent["run_id"] / agent_id
    directory.mkdir(parents=True, exist_ok=True)
    turn = directory / ("turn-" + str(time.time_ns()))
    turn.mkdir()
    assignment = json.loads(agent["assignment"])
    atomic_json(turn / "result-schema.json", providers.RESULT_SCHEMA)
    tool_guidance = (
        "For Bash, invoke ONLY the helper using --input-json with shell-quoted JSON, or --input FILE. "
        "Prepare input files with Write under your worktree's ignored .okms/state directory. "
        "Pure inbox/verify calls need no input. Read files and logs with Read, not Bash cat. "
        "Use separate tool calls for polling; heredocs, compound commands, loops, wrappers, redirects and parsing pipelines can require native approval.\n"
        if agent["provider"] == "claude" else
        "Use your available file/shell tools for project reads and owned edits under the workspace sandbox. "
        "Codex may expose shell reads rather than a tool named Read; ordinary scoped shell commands are permitted. "
        "Use the runtime helper for messaging/status/assigned verification, not as a replacement for file reads.\n")
    prompt = ("You are an okms Hybrid Team worker, not the coordinator. Do not dispatch workers or edit shared progress.\n"
              "Follow project instructions and the assignment below. Work only in your worktree and owned paths.\n"
              "Use python3 .okms/team.py COMMAND --input - with JSON stdin. Its identity/project are in your OKMS environment.\n"
              "Worker commands are status/send/inbox/ack/verify.\n"
              + tool_guidance +
              "Verify executes only the checks already assigned by the coordinator. Poll and acknowledge peer messages.\n"
              "If input is needed, send a request and return disposition waiting_input. Do not fabricate evidence.\n"
              "Return exactly the WorkerResult object below, without prose, Markdown, extra keys or nested evidence objects. "
              "Use StructuredOutput when supplied by the CLI; otherwise return the same raw JSON object. "
              "remaining lists every missing check or coverage gap.\nWorkerResult schema:\n"
              + dump(providers.RESULT_SCHEMA) + "\n"
              + reason + "\nAssignment:\n" + dump(assignment) + "\n")
    pending = store.inbox({"agent_id": agent_id, "token": agent["token"]})
    if pending:
        prompt += "Unacknowledged inbox:\n" + dump(pending) + "\n"
    (turn / "prompt.txt").write_text(prompt, encoding="utf-8")
    command = providers.command(agent["provider"], config, project, agent, turn)
    atomic_json(turn / "invocation.json", {"argv": command, "cwd": agent["worktree"], "started_at": now()})
    observed, failure, process = None, None, None
    try:
        with (turn / "stderr.log").open("wb") as errors, (turn / "stdout.jsonl").open("wb") as raw:
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=errors, cwd=agent["worktree"],
                                       env=providers.environment(project, agent), start_new_session=True)
            messages = queue.Queue()

            def read():
                for line in process.stdout:
                    raw.write(line)
                    raw.flush()
                    messages.put(line)
                messages.put(None)

            reader = threading.Thread(target=read, daemon=True)
            reader.start()
            process.stdin.write(prompt.encode())
            process.stdin.close()
            ended = False
            while not ended:
                with store.connection() as db:
                    status = db.execute("SELECT status FROM agents WHERE id=?", (agent_id,)).fetchone()[0]
                if status == "cancelled":
                    failure = "Worker stopped by coordinator."
                    stop_process(process)
                if time.time() >= agent["deadline"]:
                    failure = "Assignment deadline expired; no automatic retry."
                    stop_process(process)
                try:
                    line = messages.get(timeout=0.25)
                except queue.Empty:
                    if process.poll() is not None and not reader.is_alive():
                        break
                    continue
                if line is None:
                    ended = True
                    continue
                try:
                    record = json.loads(line)
                    if not isinstance(record, dict):
                        continue
                except ValueError:
                    continue
                observation = providers.observation(agent["provider"], record)
                with store.transaction() as db:
                    if observation["native_session_id"]:
                        db.execute("UPDATE agents SET native_session_id=? WHERE id=?", (observation["native_session_id"], agent_id))
                if observation["result"]:
                    observed = observation["result"]
                if observation["error"]:
                    failure = dump(observation["error"])
            code = process.wait(timeout=10)
            reader.join(timeout=5)
            if code != 0:
                failure = failure or f"Provider exited with code {code}; inspect stderr.log."
            if observed is None:
                failure = failure or "Provider returned no schema-valid WorkerResult."
    except (OSError, subprocess.SubprocessError, TeamError) as error:
        failure = str(error)
    finally:
        if process is not None:
            stop_process(process)
    revision, paths = None, []
    try:
        revision = gitops.snapshot(agent["worktree"])
        with store.connection() as db:
            baseline = db.execute("SELECT baseline FROM runs WHERE id=?", (agent["run_id"],)).fetchone()[0]
        paths = gitops.paths_changed(project, baseline, revision)
        forbidden = [path for path in paths if not gitops.within(path, assignment["owns"])]
        if forbidden:
            failure = "Out-of-scope changes retained but rejected: " + ", ".join(forbidden)
    except TeamError as error:
        failure = failure or str(error)
    result = {"worker_result": observed, "error": failure, "revision": revision, "changed_paths": paths,
              "artifact": str(turn), "finished_at": now()}
    atomic_json(directory / "result.json", result)
    with store.transaction() as db:
        current = db.execute("SELECT status FROM agents WHERE id=?", (agent_id,)).fetchone()[0]
        state = "cancelled" if current == "cancelled" else "failed" if failure else observed["disposition"]
        db.execute("UPDATE agents SET status=?,pid=NULL,notes=? WHERE id=?", (state, dump(result), agent_id))
        store.event(db, "worker_failed" if failure else state, agent_id, agent["run_id"], agent["spec_id"], result)
        initial_ids = {message["id"] for message in pending}
        newer = any(row["id"] not in initial_ids for row in db.execute(
            "SELECT id FROM messages WHERE recipient=? AND acked=0", (agent_id,)))
        saved_session = db.execute("SELECT native_session_id FROM agents WHERE id=?", (agent_id,)).fetchone()[0]
        wake = state == "waiting_input" and newer and saved_session and time.time() < agent["deadline"]
        if wake:
            db.execute("UPDATE agents SET status='queued' WHERE id=?", (agent_id,))
            store.event(db, "resume_requested", agent_id, agent["run_id"], agent["spec_id"], {"reason": "Message arrived during the previous turn"})
    if wake:
        from .runtime import Runtime
        Runtime(project).launch(agent_id, "A message arrived before you began waiting; process and acknowledge your inbox.")
    return result
