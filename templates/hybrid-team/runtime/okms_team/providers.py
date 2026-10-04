"""CLI transport adapters; raw streams are retained independently of results."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from .state import TeamError


RESULT_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "summary": {"type": "string"},
        "evidence": {"type": "array", "items": {"type": "string"}},
        "remaining": {"type": "array", "items": {"type": "string"}},
        "next": {"type": "string"},
        "disposition": {"type": "string", "enum": ["result_ready", "waiting_input"]},
    },
    "required": ["summary", "evidence", "remaining", "next", "disposition"],
}


def valid_result(value):
    return (isinstance(value, dict) and set(value) == set(RESULT_SCHEMA["required"])
            and all(isinstance(value[key], str) for key in ("summary", "next"))
            and all(isinstance(value[key], list) and all(isinstance(item, str) for item in value[key])
                    for key in ("evidence", "remaining"))
            and value["disposition"] in {"result_ready", "waiting_input"})


def parse_result(value):
    if isinstance(value, str):
        try:
            value = json.loads(value.strip())
        except (TypeError, ValueError):
            return None
    return value if valid_result(value) else None


def command(provider, config, project, agent, artifact):
    settings = config.get("providers", {}).get(provider, {})
    executable = settings.get("command", [provider])
    extra = settings.get("args", [])
    if (not isinstance(executable, list) or not executable or not isinstance(extra, list) or
            not all(isinstance(part, str) and part for part in executable + extra)):
        raise TeamError("Provider command and args must be argument arrays.")
    if any(part in {"--dangerously-skip-permissions", "--dangerously-bypass-approvals-and-sandbox",
                    "--dangerously-bypass-hook-trust", "bypassPermissions", "--ephemeral", "--no-session-persistence",
                    "--last", "--continue", "--ignore-rules"} for part in extra):
        raise TeamError("Worker arguments cannot bypass native trust/permissions or discard session identity.")
    session = agent.get("native_session_id")
    if provider == "codex":
        args = executable + ["--no-daemon", "--sandbox", "workspace-write", "--add-dir", str(Path(project) / ".okms/state")]
        args += extra + ["exec"]
        if session:
            args += ["resume", session]
        args += ["--json", "--output-schema", str(artifact / "result-schema.json"), "-"]
    elif provider == "claude":
        # Schema delivery is itself a tool; keep it available in the restricted surface.
        args = executable + ["-p", "--verbose", "--output-format", "stream-json",
                             "--json-schema", json.dumps(RESULT_SCHEMA),
                             "--permission-mode", "acceptEdits", "--permission-prompts", "none",
                             "--add-dir", str(Path(project) / ".okms/state"),
                             "--tools", "Read,Glob,Grep,Edit,Write,Bash,StructuredOutput",
                             "--allowedTools", "Read,Glob,Grep,Edit,Write,StructuredOutput", "Bash(python3 .okms/team.py *)"]
        role = settings.get("worker_role", "okms-worker")
        if (Path(agent["worktree"]) / ".claude/agents" / (role + ".md")).exists():
            args += ["--agent", role]
        if session:
            args += ["--resume", session]
        args += extra
    else:
        raise TeamError("Unsupported provider: " + str(provider))
    return args


def environment(project, agent):
    env = os.environ.copy()
    # This is a separate CLI session, not a nested Claude Code/SDK session.
    env.pop("CLAUDECODE", None)
    env.update(OKMS_PROJECT=str(project), OKMS_AGENT_ID=agent["id"], OKMS_AGENT_TOKEN=agent["token"])
    return env


def observation(provider, record):
    """Extract public stream fields without treating turn completion as task completion."""
    value = {"native_session_id": None, "result": None, "error": None}
    kind = record.get("type")
    if provider == "codex":
        if kind == "thread.started":
            value["native_session_id"] = record.get("thread_id")
        elif kind == "item.completed" and record.get("item", {}).get("type") == "agent_message":
            value["result"] = parse_result(record["item"].get("text"))
        elif kind in {"turn.failed", "error"}:
            value["error"] = record.get("error") or record.get("message") or "Provider reported failure."
    elif provider == "claude":
        value["native_session_id"] = record.get("session_id")
        if kind == "result":
            value["result"] = parse_result(record.get("structured_output")) or parse_result(record.get("result"))
            if record.get("is_error") or record.get("permission_denials"):
                value["error"] = record.get("permission_denials") or record.get("result") or "Provider reported failure."
        elif kind == "system" and record.get("subtype") == "permission_denied":
            value["error"] = record
    return value


def capabilities(config):
    values = {}
    for provider in ("codex", "claude"):
        prefix = config.get("providers", {}).get(provider, {}).get("command", [provider])
        found = isinstance(prefix, list) and bool(prefix) and shutil.which(prefix[0]) is not None
        record = {"available": found, "version": None, "authenticated": None}
        if found:
            try:
                result = subprocess.run(prefix + ["--version"], capture_output=True, text=True, timeout=10)
                record["version"] = (result.stdout or result.stderr).strip()[:200]
                help_args = ["exec", "--help"] if provider == "codex" else ["--help"]
                help_result = subprocess.run(prefix + help_args, capture_output=True, text=True, timeout=10)
                help_text = help_result.stdout + help_result.stderr
                flags = ("--json", "--output-schema") if provider == "codex" else ("--json-schema", "--output-format", "--resume")
                record["structured_output"] = help_result.returncode == 0 and all(flag in help_text for flag in flags)
                auth_args = ["login", "status"] if provider == "codex" else ["auth", "status", "--json"]
                auth = subprocess.run(prefix + auth_args, capture_output=True, text=True, timeout=10)
                if provider == "codex":
                    record["authenticated"] = auth.returncode == 0
                else:
                    record["authenticated"] = auth.returncode == 0 and json.loads(auth.stdout).get("loggedIn") is True
            except (OSError, subprocess.TimeoutExpired, ValueError):
                record["probe_incomplete"] = True
        values[provider] = record
    return values
