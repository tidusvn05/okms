"""Scoped orchestration operations shared by the CLI and lifecycle hooks."""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

from . import gitops, providers, worker
from .state import Store, TeamError, atomic_json, dump, identifier, now


CHILDREN = []


def write_text(path, text):
    path = Path(path)
    temporary = path.with_name(path.name + "." + identifier("write") + ".tmp")
    try:
        temporary.write_text(text, encoding="utf-8")
        if path.exists():
            temporary.chmod(path.stat().st_mode & 0o777)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def work_rows(text):
    match = re.search(r"^## Work\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not match:
        raise TeamError("Plan needs its canonical Work table.")
    result = []
    for line in match[1].splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 4 or cells[0] == "Spec" or not re.search(r"\bP\d+-MS\d+\b", cells[0]):
            continue
        spec_id = re.search(r"\bP\d+-MS\d+\b", cells[0]).group()
        link = re.search(r"\]\(([^)]+)\)", cells[0])
        result.append({"id": spec_id, "path": link.group(1) if link else None,
                       "depends": re.findall(r"\bP\d+-MS\d+\b", cells[1]),
                       "state": cells[2], "evidence": cells[3], "line": line})
    return result


class Runtime:
    def __init__(self, project):
        self.project = Path(project).resolve()
        path = self.project / ".okms/team.json"
        if not path.is_file():
            raise TeamError("Hybrid Team is not installed here; run its project setup first.")
        try:
            self.config = json.loads(path.read_text())
        except ValueError as error:
            raise TeamError("Invalid .okms/team.json: " + str(error)) from error
        if not isinstance(self.config, dict) or self.config.get("schema_version") != 1:
            raise TeamError("Unsupported team configuration schema_version.")
        for field in ("max_workers", "assignment_timeout_seconds"):
            value = self.config.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 < value < 10**7:
                raise TeamError("Team configuration needs a finite positive " + field)
        if not isinstance(self.config["max_workers"], int):
            raise TeamError("max_workers must be an integer.")
        self.store = Store(self.project)
        self.docs = self.path(self.config["docs_path"])

    def path(self, relative):
        if not isinstance(relative, str):
            raise TeamError("Expected a project-relative path.")
        path = (self.project / relative).resolve()
        if not path.is_relative_to(self.project):
            raise TeamError("Path escapes the project: " + relative)
        return path

    def actor(self, identity, coordinator=False):
        with self.store.connection() as db:
            return self.store.authenticate(db, identity, coordinator=coordinator)

    def doctor(self):
        current = self.store.status()
        result = {"runtime_version": "0.1.0", "platform_supported": os.name == "posix",
                  "python_supported": sys.version_info >= (3, 10), "docs_path": str(self.docs),
                  "git_baseline": gitops.git(self.project, "rev-parse", "--verify", "HEAD", check=False).returncode == 0,
                  "providers": providers.capabilities(self.config), "checks_configured": bool(self.config.get("checks")),
                  "hooks": "configured; native trust and loading require confirmation in each CLI",
                  "last_hook_receipts": [event for event in current["events"] if event["type"] == "hook_received"][-10:]}
        result["ready"] = (result["platform_supported"] and result["python_supported"] and result["git_baseline"]
                           and result["checks_configured"]
                           and all(p["available"] and p.get("structured_output") and p["authenticated"]
                                   for p in result["providers"].values()))
        return result

    def validate_contract(self, plan, spec):
        plan_path, spec_path = self.path(plan), self.path(spec)
        if not plan_path.is_file() or not spec_path.is_file():
            raise TeamError("Save the plan and selected micro spec before dispatch.")
        if not re.search(r"^type:\s*Plan\s*$", plan_path.read_text(), re.M):
            raise TeamError("Assignment plan must be a saved Plan.")
        if not re.search(r"^type:\s*MicroSpec\s*$", spec_path.read_text(), re.M):
            raise TeamError("Assignment spec must be a saved MicroSpec.")
        rows = work_rows(plan_path.read_text())
        selected = next((row for row in rows if row["path"] and (plan_path.parent / row["path"]).resolve() == spec_path), None)
        if not selected or selected["state"] not in {"planned", "in_progress", "blocked"}:
            raise TeamError("Spec must be an open linked row of the assignment plan.")
        states = {row["id"]: row["state"] for row in rows}
        if any(states.get(dependency) != "done" for dependency in selected["depends"]):
            raise TeamError("Assignment dependencies are not done.")
        return selected["id"]

    def dispatch(self, identity, data):
        self.actor(identity, coordinator=True)
        provider = data.get("provider")
        if provider not in {"codex", "claude"}:
            raise TeamError("Assignment provider must be codex or claude.")
        plan, spec = data.get("plan"), data.get("spec")
        spec_id = self.validate_contract(plan, spec)
        scope = data.get("owns", [])
        if not isinstance(scope, list):
            raise TeamError("owns must be an array of explicit paths, or [] for a reader.")
        scope = [gitops.scope_path(path) for path in scope]
        shared = [str(self.docs.relative_to(self.project) / name) for name in
                  ("index.md", "workflow.md", "context.md", "team.md", "team-policy.md", "delegation.md", "_templates", "roles")]
        shared += [plan, spec]
        if gitops.overlap(scope, shared):
            raise TeamError("Workers cannot own shared contracts, progress, or role instructions.")
        checks = data.get("checks", self.config.get("checks", []))
        if (not isinstance(checks, list) or any(not isinstance(argv, list) or not argv or
                                              not all(isinstance(arg, str) and arg for arg in argv) for argv in checks)):
            raise TeamError("Assignment checks must be arrays of command arguments.")
        if not isinstance(data.get("intent"), str) or not data["intent"].strip():
            raise TeamError("Assignment needs a bounded intent.")
        with self.store.transaction() as db:
            actor = self.store.authenticate(db, identity, coordinator=True)
            active = db.execute("SELECT COUNT(*) FROM agents WHERE role='worker' AND status IN ('queued','starting','running','waiting_input')").fetchone()[0]
            if active >= self.config["max_workers"]:
                raise TeamError("Worker limit reached; finish or stop an assignment first.")
            runs = db.execute("SELECT * FROM runs WHERE status IN ('active','integrating','applied_unverified')").fetchall()
            if runs and (runs[0]["plan"] != plan or runs[0]["status"] != "active"):
                raise TeamError("Finish or recover the existing run before starting this batch.")
            if data.get("run_id"):
                run = db.execute("SELECT * FROM runs WHERE id=?", (data["run_id"],)).fetchone()
                if not run or run["plan"] != plan or run["status"] != "active":
                    raise TeamError("Requested run is not an active batch of this plan.")
            else:
                run = runs[0] if runs else None
            if not run:
                run_id = identifier("run")
                baseline = gitops.snapshot(self.project, "refs/okms/runs/" + run_id + "/base")
                db.execute("INSERT INTO runs VALUES(?,?,?,'active',?)", (run_id, baseline, plan, dump({"created_at": now()})))
                self.store.event(db, "run_started", actor["id"], run_id, payload={"baseline": baseline, "plan": plan})
            else:
                run_id, baseline = run["id"], run["baseline"]
            existing = db.execute("SELECT assignment FROM agents WHERE run_id=? AND status NOT IN ('failed','cancelled')", (run_id,)).fetchall()
            if any(gitops.overlap(scope, json.loads(row[0])["owns"]) for row in existing):
                raise TeamError("Write scopes overlap; serialize or split the assignments.")
            agent_id = identifier("worker")
            location = gitops.worktree(self.project, agent_id, baseline)
            from .adoption import worker_overlay
            worker_overlay(self.project, location)
            assignment = {"plan": plan, "spec": spec, "spec_id": spec_id, "provider": provider,
                          "intent": data["intent"], "owns": scope, "checks": checks, "baseline": baseline,
                          "context": data.get("context", []), "role": "worker", "run_id": run_id,
                          "worker_id": agent_id, "worktree": str(location), "contract": self.path(spec).read_text()}
            token = __import__("secrets").token_urlsafe(32)
            agent = {"id": agent_id, "provider": provider, "worktree": str(location), "native_session_id": None}
            providers.command(provider, self.config, self.project, agent, self.store.directory)
            db.execute("INSERT INTO agents(id,provider,role,token,status,run_id,spec_id,worktree,assignment,deadline) VALUES(?,?,'worker',?,'queued',?,?,?,?,?)",
                       (agent_id, provider, token, run_id, spec_id, str(location), dump(assignment),
                        time.time() + self.config["assignment_timeout_seconds"]))
            self.store.event(db, "assignment_queued", actor["id"], run_id, spec_id, assignment)
        result = {"agent_id": agent_id, "run_id": run_id, "worktree": str(location), "baseline": baseline, "status": "queued"}
        if data.get("launch", True):
            result["driver_pid"] = self.launch(agent_id)
        return result

    def launch(self, agent_id, reason="Initial assignment"):
        nonce = identifier("driver")
        with self.store.transaction() as db:
            changed = db.execute("UPDATE agents SET status='starting',driver_nonce=? WHERE id=? AND status='queued'", (nonce, agent_id)).rowcount
            if not changed:
                raise TeamError("Worker already has a driver or is not queued.")
        directory = self.store.directory / "drivers"
        directory.mkdir(exist_ok=True)
        helper = self.project / ".okms/team.py"
        try:
            with (directory / (agent_id + ".log")).open("ab") as log:
                process = subprocess.Popen([sys.executable, str(helper), "_run", "--project", str(self.project),
                                            "--input-json", dump({"agent_id": agent_id, "reason": reason, "nonce": nonce})],
                                           cwd=self.project, stdout=log, stderr=log, start_new_session=True)
        except OSError as error:
            with self.store.transaction() as db:
                db.execute("UPDATE agents SET status='failed',notes=? WHERE id=? AND driver_nonce=?", (dump({"error": str(error)}), agent_id, nonce))
            raise TeamError("Driver launch failed: " + str(error)) from error
        with self.store.transaction() as db:
            db.execute("UPDATE agents SET pid=? WHERE id=? AND status='starting' AND driver_nonce=?", (process.pid, agent_id, nonce))
        CHILDREN[:] = [child for child in CHILDREN if child.poll() is None]
        CHILDREN.append(process)
        return process.pid

    def resume(self, identity, data):
        with self.store.transaction() as db:
            actor = self.store.authenticate(db, identity, coordinator=True)
            target = db.execute("SELECT * FROM agents WHERE id=?", (data.get("agent_id"),)).fetchone()
            if not target or target["role"] != "worker":
                raise TeamError("Resume needs a registered worker.")
            if target["status"] == "running":
                try:
                    os.kill(target["pid"], 0)
                except (OSError, TypeError):
                    pass
                else:
                    raise TeamError("The worker driver is still running.")
            elif target["status"] not in {"queued", "waiting_input", "failed", "cancelled"}:
                raise TeamError("Worker is not resumable; its result has already been returned or integrated.")
            if time.time() >= target["deadline"]:
                extension = data.get("extend_seconds")
                if isinstance(extension, bool) or not isinstance(extension, (int, float)) or not 0 < extension < 10**7:
                    raise TeamError("Deadline expired; an explicit positive extend_seconds is required.")
                db.execute("UPDATE agents SET deadline=? WHERE id=?", (time.time() + extension, target["id"]))
            if target["status"] != "queued" and not target["native_session_id"]:
                raise TeamError("No saved provider session ID; preserve this worktree and dispatch a new assignment explicitly.")
            db.execute("UPDATE agents SET status='queued',pid=NULL WHERE id=?", (target["id"],))
            self.store.event(db, "resume_requested", actor["id"], target["run_id"], target["spec_id"], {"worker": target["id"]})
        return {"agent_id": target["id"], "driver_pid": self.launch(target["id"], data.get("reason", "Explicit resume; inspect saved changes first."))}

    def send(self, identity, data):
        message = self.store.send(identity, data)
        if message["to"] != "coordinator":
            with self.store.transaction() as db:
                target = db.execute("SELECT * FROM agents WHERE id=?", (message["to"],)).fetchone()
                pending = db.execute("SELECT 1 FROM messages WHERE id=? AND acked=0", (message["id"],)).fetchone()
                wake = (pending and target["status"] == "waiting_input" and target["native_session_id"]
                        and time.time() < target["deadline"])
                if wake:
                    db.execute("UPDATE agents SET status='queued' WHERE id=?", (target["id"],))
                    self.store.event(db, "resume_requested", message["from"], target["run_id"], target["spec_id"],
                                     {"worker": target["id"], "message_id": message["id"]})
            if wake:
                self.launch(target["id"], "A peer message is queued; process and acknowledge your inbox.")
        return message

    def verify(self, identity, data):
        actor = self.actor(identity)
        if actor["role"] == "worker":
            checks = json.loads(actor["assignment"])["checks"]
            directory = actor["worktree"]
        elif actor["role"] == "coordinator":
            self.actor(identity, coordinator=True)
            checks = self.config.get("checks", [])
            directory = self.project
        else:
            raise TeamError("Standby sessions cannot execute verification commands.")
        if not checks:
            raise TeamError("Verification commands are unknown; fill actual checks in the team config or assignment.")
        output = self.store.directory / "verification" / identifier("verify")
        evidence = worker.execute_checks(directory, checks, output,
                                         min(self.config["assignment_timeout_seconds"], 1800))
        passed = all(item["exit_code"] == 0 for item in evidence)
        with self.store.transaction() as db:
            self.store.authenticate(db, identity, coordinator=actor["role"] == "coordinator")
            self.store.event(db, "verification_finished", actor["id"], actor["run_id"], actor["spec_id"],
                             {"passed": passed, "evidence": evidence})
            if actor["role"] == "coordinator" and data.get("run_id"):
                run = db.execute("SELECT * FROM runs WHERE id=?", (data["run_id"],)).fetchone()
                if run and run["status"] == "applied_unverified" and passed:
                    metadata = json.loads(run["metadata"])
                    metadata["root_checks"] = evidence
                    db.execute("UPDATE runs SET status='applied',metadata=? WHERE id=?", (dump(metadata), run["id"]))
        return {"passed": passed, "evidence": evidence}

    def integrate(self, identity, data):
        with self.store.transaction() as db:
            actor = self.store.authenticate(db, identity, coordinator=True)
            run = db.execute("SELECT * FROM runs WHERE id=?", (data.get("run_id"),)).fetchone()
            if not run or run["status"] != "active":
                raise TeamError("Integrate needs an active run with returned results.")
            agents = [dict(row) for row in db.execute("SELECT * FROM agents WHERE run_id=? AND status!='cancelled' ORDER BY spec_id,id", (run["id"],))]
            if not agents or any(agent["status"] != "result_ready" for agent in agents):
                raise TeamError("Every noncancelled worker must return a valid result before integration.")
            if not isinstance(data.get("acceptance_review"), str) or not data["acceptance_review"].strip():
                raise TeamError("Coordinator acceptance_review is required, including how reported gaps are covered.")
            required = self.config.get("checks", [])
            extra = data.get("checks", [])
            if not required:
                raise TeamError("Required integration checks are unknown; configure actual commands first.")
            if not isinstance(extra, list):
                raise TeamError("Additional integration checks must be arrays of command arguments.")
            checks = required + [argv for argv in extra if argv not in required]
            db.execute("UPDATE runs SET status='integrating' WHERE id=?", (run["id"],))
        try:
            commits = [json.loads(agent["notes"])["revision"] for agent in agents]
            integration = gitops.combine(self.project, run["baseline"], commits)
            artifacts = self.store.directory / "runs" / run["id"] / identifier("integration-checks")
            checks_result = worker.execute_checks(integration, checks, artifacts, self.config["assignment_timeout_seconds"])
            if not all(result["exit_code"] == 0 for result in checks_result):
                raise TeamError("Combined checks failed; retained evidence: " + str(artifacts))
            integrated = gitops.snapshot(integration, "refs/okms/runs/" + run["id"] + "/integrated")
            changed = gitops.paths_changed(self.project, run["baseline"], integrated)
            scopes = [path for agent in agents for path in json.loads(agent["assignment"])["owns"]]
            if any(not gitops.within(path, scopes) for path in changed):
                raise TeamError("Integration checks changed an unowned path; reconcile the retained worktree.")
            with self.store.transaction() as db:
                self.store.authenticate(db, identity, coordinator=True)
                paths = gitops.apply_to_root(self.project, run["baseline"], integrated)
                metadata = {**json.loads(run["metadata"]), "integration_worktree": str(integration), "revision": integrated,
                            "combined_checks": checks_result, "acceptance_review": data["acceptance_review"], "changed_paths": paths}
                db.execute("UPDATE runs SET status='applied_unverified',metadata=? WHERE id=?", (dump(metadata), run["id"]))
                for agent in agents:
                    db.execute("UPDATE agents SET status='integrated' WHERE id=?", (agent["id"],))
                self.store.event(db, "integration_applied", actor["id"], run["id"], payload=metadata)
            root_checks = worker.execute_checks(self.project, checks, artifacts / "root", self.config["assignment_timeout_seconds"])
            metadata["root_checks"] = root_checks
            passed = all(result["exit_code"] == 0 for result in root_checks)
            with self.store.transaction() as db:
                db.execute("UPDATE runs SET status=?,metadata=? WHERE id=?",
                           ("applied" if passed else "applied_unverified", dump(metadata), run["id"]))
                self.store.event(db, "root_verification_finished", actor["id"], run["id"], payload={"passed": passed, "evidence": root_checks})
            return {"run_id": run["id"], "applied": True, "verified": passed, **metadata}
        except BaseException as error:
            with self.store.transaction() as db:
                db.execute("UPDATE runs SET status='active' WHERE id=? AND status='integrating'", (run["id"],))
                self.store.event(db, "integration_failed", actor["id"], run["id"], payload={"error": str(error)})
            raise

    def checkpoint(self, identity, data):
        plan = self.path(data.get("plan"))
        with self.store.transaction() as db:
            actor = self.store.authenticate(db, identity, coordinator=True)
            text = plan.read_text()
            rows = work_rows(text)
            selected = next((row for row in rows if row["id"] == data.get("spec_id")), None)
            state = data.get("state")
            if not selected or state not in {"planned", "in_progress", "blocked", "done", "cancelled"}:
                raise TeamError("Checkpoint needs an existing spec_id and a valid work state.")
            evidence = data.get("evidence", "Pending.")
            if not isinstance(evidence, str) or any(char in evidence for char in "|\n\r"):
                raise TeamError("Evidence must fit one Work table cell.")
            if state == "done":
                if not data.get("acceptance_review") or re.match(r"^(pending|not run|not verified)\b", evidence, re.I):
                    raise TeamError("Completion needs coordinator acceptance review and actual evidence.")
                pending = db.execute("SELECT agents.id FROM agents JOIN runs ON agents.run_id=runs.id WHERE agents.spec_id=? AND runs.plan=? AND agents.status IN ('queued','starting','running','waiting_input','failed')", (selected["id"], data["plan"])).fetchone()
                unverified = db.execute("SELECT 1 FROM runs WHERE plan=? AND status IN ('integrating','applied_unverified')", (data["plan"],)).fetchone()
                writers = db.execute("SELECT assignment,agents.status FROM agents JOIN runs ON agents.run_id=runs.id WHERE spec_id=? AND runs.plan=? AND agents.status='result_ready'", (selected["id"], data["plan"])).fetchall()
                if pending or unverified or any(json.loads(row["assignment"])["owns"] for row in writers):
                    raise TeamError("Necessary worker execution, integration, or root verification remains incomplete.")
            cells = [cell.strip() for cell in selected["line"].strip().strip("|").split("|")]
            replacement = "| " + " | ".join([cells[0], cells[1], state, evidence]) + " |"
            text = text.replace(selected["line"], replacement, 1)
            resume = data.get("resume")
            if not isinstance(resume, dict) or not all(isinstance(resume.get(key), str) and "\n" not in resume[key]
                                                       for key in ("current", "next", "blocker")):
                raise TeamError("Checkpoint needs resume.current, resume.next, and resume.blocker.")
            for key in ("current", "next", "blocker"):
                text = re.sub(r"^- " + key.title() + r":.*$", lambda m, key=key: "- " + key.title() + ": " + resume[key], text, flags=re.M)
            states = [row["state"] for row in work_rows(text)]
            complete = all(value in {"done", "cancelled"} for value in states)
            plan_state = "done" if complete else "in_progress"
            text = re.sub(r"^work_status:.*$", "work_status: " + plan_state, text, count=1, flags=re.M)
            if complete:
                result = data.get("result")
                if not isinstance(result, str) or not result.strip() or result.startswith("Pending"):
                    raise TeamError("A completed plan needs an actual Result.")
                text = re.sub(r"(^## Result\s*\n).*\Z", lambda match: match[1] + "\n" + result + "\n", text, flags=re.M | re.S)
            write_text(plan, text)
            index = self.docs / "index.md"
            index_text = index.read_text()
            relative = os.path.relpath(plan, self.docs)
            active = re.search(r"(# Active work\s*\n)(.*?)(?=\n# |\Z)", index_text, re.S)
            if active:
                lines = [line for line in active[2].splitlines() if "(" + relative + ")" not in line and not line.startswith("No open work.")]
                if not complete:
                    lines.append("- [Current plan](" + relative + ") - Runtime-managed progress and recovery checkpoint.")
                content = "\n".join(line for line in lines if line.strip()) or "No open work."
                index_text = index_text[:active.start()] + active[1] + "\n" + content + "\n" + index_text[active.end():]
                write_text(index, index_text)
            self.store.event(db, "checkpoint_saved", actor["id"], spec_id=selected["id"],
                             payload={"plan": data["plan"], "state": state, "evidence": evidence,
                                      "acceptance_review": data.get("acceptance_review")})
        return {"plan": data["plan"], "work_status": plan_state, "spec_id": selected["id"], "state": state}

    def stop(self, identity, data):
        with self.store.transaction() as db:
            actor = self.store.authenticate(db, identity, coordinator=True)
            target = db.execute("SELECT * FROM agents WHERE id=?", (data.get("agent_id"),)).fetchone()
            if not target or target["role"] != "worker" or target["status"] == "integrated":
                raise TeamError("Stop needs an unintegrated worker.")
            db.execute("UPDATE agents SET status='cancelled' WHERE id=?", (target["id"],))
            self.store.event(db, "worker_stop_requested", actor["id"], target["run_id"], target["spec_id"],
                             {"worker": target["id"], "reason": data.get("reason", "Explicit stop")})
        return {"agent_id": target["id"], "status": "cancelled", "worktree_retained": target["worktree"]}

    def hook(self, provider, data):
        event = data.get("hook_event_name", "SessionStart")
        bound = os.environ.get("OKMS_AGENT_ID")
        identity = ({"agent_id": bound, "token": os.environ.get("OKMS_AGENT_TOKEN")} if bound else None)
        if not identity:
            settings = self.config.get("providers", {}).get(provider, {})
            if data.get("agent_type") in {settings.get("worker_role", "okms-worker"), settings.get("reviewer_role", "okms-reviewer")}:
                return {"hookSpecificOutput": {"hookEventName": event, "additionalContext":
                        "You are a native helper. Return to your parent; do not claim coordination or alter shared progress."}}
            session = data.get("session_id")
            if not session:
                raise TeamError("Lifecycle hook needs the native session_id.")
            if event == "SessionEnd":
                with self.store.transaction() as db:
                    actor = db.execute("SELECT * FROM agents WHERE provider=? AND session_id=?", (provider, session)).fetchone()
                    if actor:
                        db.execute("UPDATE agents SET status='ended' WHERE id=?", (actor["id"],))
                        db.execute("UPDATE owner SET agent_id=NULL,generation=generation+1 WHERE agent_id=?", (actor["id"],))
                        self.store.event(db, "session_ended", actor["id"])
                return {}
            joined = self.store.join(provider, session)
            identity = {"agent_id": joined["agent_id"], "token": joined["token"]}
            identity_path = joined["identity_file"]
        else:
            identity_path = None
            if event == "SessionEnd":
                return {}
        actor = self.actor(identity)
        with self.store.transaction() as db:
            if "permission_mode" in data:
                db.execute("UPDATE agents SET native_permission_mode=? WHERE id=?", (data["permission_mode"], actor["id"]))
            self.store.event(db, "hook_received", actor["id"], actor["run_id"], actor["spec_id"], {"provider": provider, "event": event})
        inbox = self.store.inbox(identity)
        helper = str(self.project / ".okms/team.py") if identity_path else ".okms/team.py"
        context = "Hybrid Team role: " + actor["role"] + ". Read " + str(self.docs / "workflow.md") + ". "
        if identity_path:
            context += "Runtime identity file: " + identity_path + ". Use python3 " + shlex.quote(helper) + " COMMAND --identity " + shlex.quote(identity_path) + " --input - with JSON stdin. "
        else:
            context += "Use python3 " + shlex.quote(helper) + " COMMAND --input -; worker identity is already in the environment. "
        if actor["role"] == "standby":
            context += "A coordinator is active. Observe or perform an explicit handoff/recovery; do not write shared progress. "
        context += "Acknowledge processed messages; returned worker results require coordinator acceptance. Inbox: " + dump(inbox)
        return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": context}}
