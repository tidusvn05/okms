"""JSON command interface and provider-specific hook responses."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from .runtime import Runtime
from .state import TeamError, dump
from . import worker


COMMANDS = ("doctor", "join", "dispatch", "send", "inbox", "ack", "status", "resume", "handoff",
            "checkpoint", "integrate", "verify", "stop", "hook", "_run")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=COMMANDS)
    parser.add_argument("--project", type=Path)
    parser.add_argument("--identity", type=Path)
    parser.add_argument("--provider", choices=("codex", "claude"))
    parser.add_argument("--input", type=str, help="JSON input file, or - for stdin")
    parser.add_argument("--input-json", help="JSON input for programmatic argument arrays")
    args = parser.parse_args(argv)
    try:
        project = args.project or os.environ.get("OKMS_PROJECT") or Path(__file__).resolve().parents[2]
        runtime = Runtime(project)
        data = json.loads(args.input_json) if args.input_json else json.loads(
            sys.stdin.read() if args.input == "-" or args.command == "hook" else Path(args.input).read_text()) if args.input or args.command == "hook" else {}
        if not isinstance(data, dict):
            raise TeamError("Command input must be a JSON object.")
        identity = json.loads(args.identity.read_text()) if args.identity else {
            "agent_id": os.environ.get("OKMS_AGENT_ID"), "token": os.environ.get("OKMS_AGENT_TOKEN")}
        if args.command == "doctor":
            result = runtime.doctor()
        elif args.command == "join":
            result = runtime.store.join(args.provider or data.get("provider"), data.get("session_id"))
        elif args.command == "hook":
            if not args.provider:
                raise TeamError("hook requires --provider.")
            result = runtime.hook(args.provider, data)
        elif args.command == "_run":
            result = worker.run(runtime.project, data["agent_id"], data.get("reason", "Initial assignment"), data.get("nonce"))
        elif args.command == "status":
            runtime.actor(identity)
            wait = data.get("wait_seconds", 0)
            if isinstance(wait, bool) or not isinstance(wait, (int, float)) or not 0 <= wait <= 50:
                raise TeamError("wait_seconds must be between 0 and 50.")
            deadline = time.monotonic() + wait
            result = runtime.store.status()
            while any(agent["status"] in {"queued", "starting", "running"} for agent in result["agents"]) and time.monotonic() < deadline:
                time.sleep(0.25)
                result = runtime.store.status()
        elif args.command == "inbox":
            result = {"messages": runtime.store.inbox(identity)}
        elif args.command == "ack":
            result = runtime.store.ack(identity, data.get("id"))
        elif args.command == "handoff":
            result = runtime.store.handoff(identity, data.get("to"), recover=data.get("recover", False))
        else:
            result = getattr(runtime, args.command)(identity, data)
        print(dump(result), flush=True)
        return 0
    except (TeamError, OSError, ValueError, KeyError, TypeError) as error:
        if args.command == "_run":
            try:
                with runtime.store.transaction() as db:
                    changed = db.execute("UPDATE agents SET status='failed',pid=NULL,notes=? WHERE id=? AND status='starting' AND driver_nonce=?",
                                         (dump({"error": str(error)}), data["agent_id"], data.get("nonce"))).rowcount
                    if changed:
                        runtime.store.event(db, "worker_failed", data["agent_id"], payload={"error": str(error)})
            except Exception:
                pass
        if args.command == "hook":
            print(dump({"systemMessage": "Hybrid Team setup/recovery required: " + str(error)}))
        else:
            print(dump({"error": str(error), "incomplete": True}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
