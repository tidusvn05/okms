"""Transactional ownership and durable delivery; plans own business progress."""

from __future__ import annotations

import json
import secrets
import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path


class TeamError(Exception):
    """An actionable runtime failure, never evidence of completed acceptance."""


def identifier(prefix):
    return prefix + "-" + uuid.uuid4().hex[:16]


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def dump(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        temporary.write_text(dump(value) + "\n", encoding="utf-8")
        temporary.chmod(0o600)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


class Store:
    def __init__(self, project):
        self.project = Path(project).resolve()
        self.directory = self.project / ".okms/state"
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / "team.sqlite3"
        with self.connection() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY, provider TEXT NOT NULL, session_id TEXT,
                    role TEXT NOT NULL, token TEXT NOT NULL, status TEXT NOT NULL,
                    run_id TEXT, spec_id TEXT, worktree TEXT, native_session_id TEXT,
                    pid INTEGER, assignment TEXT, deadline REAL, notes TEXT, driver_nonce TEXT,
                    native_permission_mode TEXT,
                    UNIQUE(provider, session_id)
                );
                CREATE TABLE IF NOT EXISTS owner (
                    singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                    agent_id TEXT, generation INTEGER NOT NULL
                );
                INSERT OR IGNORE INTO owner VALUES(1, NULL, 0);
                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY, baseline TEXT NOT NULL, plan TEXT NOT NULL,
                    status TEXT NOT NULL, metadata TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY, envelope TEXT NOT NULL, recipient TEXT NOT NULL,
                    acked INTEGER NOT NULL DEFAULT 0, deliveries INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT, envelope TEXT NOT NULL
                );
            """)

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=30, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=30000")
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA synchronous=FULL")
        try:
            yield db
        finally:
            db.close()

    @contextmanager
    def transaction(self):
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                yield db
                db.execute("COMMIT")
            except BaseException:
                db.execute("ROLLBACK")
                raise

    def event(self, db, kind, actor=None, run_id=None, spec_id=None, payload=None):
        record = dict(schema_version=1, id=identifier("event"), run_id=run_id,
                      spec_id=spec_id, **{"from": actor, "to": None}, type=kind,
                      reply_to=None, payload=payload or {}, created_at=now())
        cursor = db.execute("INSERT INTO events(envelope) VALUES(?)", (dump(record),))
        return {**record, "sequence": cursor.lastrowid}

    def authenticate(self, db, identity, *, coordinator=False):
        if not isinstance(identity, dict):
            raise TeamError("An identity is required; join first or use the worker environment.")
        agent = db.execute("SELECT * FROM agents WHERE id=?", (identity.get("agent_id"),)).fetchone()
        if not agent or not secrets.compare_digest(agent["token"], str(identity.get("token", ""))):
            raise TeamError("Unknown or stale identity; obtain the current session identity.")
        if agent["status"] == "ended":
            raise TeamError("This session has ended; join or explicitly resume it.")
        if coordinator:
            owner = db.execute("SELECT * FROM owner WHERE singleton=1").fetchone()
            if agent["role"] != "coordinator" or owner["agent_id"] != agent["id"]:
                raise TeamError("Only the current coordinator may perform this operation.")
            if agent["native_permission_mode"] == "plan":
                raise TeamError("The coordinator is in native plan mode; implementation operations remain unavailable.")
        return dict(agent)

    def join(self, provider, session_id):
        if provider not in {"codex", "claude"} or not isinstance(session_id, str) or not session_id:
            raise TeamError("join needs provider codex/claude and a nonempty session_id.")
        with self.transaction() as db:
            existing = db.execute("SELECT * FROM agents WHERE provider=? AND session_id=?",
                                  (provider, session_id)).fetchone()
            owner = db.execute("SELECT * FROM owner WHERE singleton=1").fetchone()
            agent_id = existing["id"] if existing else identifier("agent")
            role = "coordinator" if owner["agent_id"] in {None, agent_id} else "standby"
            token = existing["token"] if existing and existing["status"] != "ended" else secrets.token_urlsafe(32)
            if existing:
                db.execute("UPDATE agents SET role=?,token=?,status='active' WHERE id=?",
                           (role, token, agent_id))
            else:
                db.execute("INSERT INTO agents(id,provider,session_id,role,token,status) VALUES(?,?,?,?,?,'active')",
                           (agent_id, provider, session_id, role, token))
            if role == "coordinator" and owner["agent_id"] is None:
                db.execute("UPDATE owner SET agent_id=?,generation=generation+1 WHERE singleton=1", (agent_id,))
                self.event(db, "coordinator_changed", agent_id, payload={"previous": None})
            identity = {"agent_id": agent_id, "token": token, "role": role, "provider": provider}
        path = self.directory / "identities" / (agent_id + ".json")
        atomic_json(path, identity)
        return {**identity, "identity_file": str(path)}

    def handoff(self, identity, target=None, *, recover=False):
        previous_identity = None
        with self.transaction() as db:
            actor = self.authenticate(db, identity, coordinator=not recover)
            owner = db.execute("SELECT * FROM owner WHERE singleton=1").fetchone()
            if recover:
                if actor["role"] != "standby":
                    raise TeamError("Recovery is for a joined standby session.")
                target = actor["id"]
                # Recovery is explicit; fence the old session even when its end hook was lost.
            receiver = db.execute("SELECT * FROM agents WHERE id=?", (target,)).fetchone()
            if not receiver or receiver["role"] == "worker" or receiver["status"] != "active":
                raise TeamError("Handoff target must be an active coordinator/standby session.")
            if owner["agent_id"]:
                previous = db.execute("SELECT * FROM agents WHERE id=?", (owner["agent_id"],)).fetchone()
                previous_token = secrets.token_urlsafe(32)
                db.execute("UPDATE agents SET role='standby',token=? WHERE id=?",
                           (previous_token, owner["agent_id"]))
                if owner["agent_id"] != target:
                    previous_identity = {"agent_id": previous["id"], "token": previous_token,
                                         "role": "standby", "provider": previous["provider"]}
            token = secrets.token_urlsafe(32)
            db.execute("UPDATE agents SET role='coordinator',token=? WHERE id=?", (token, target))
            db.execute("UPDATE owner SET agent_id=?,generation=generation+1 WHERE singleton=1", (target,))
            self.event(db, "coordinator_changed", actor["id"], payload={"previous": owner["agent_id"], "current": target,
                                                                       "recovery": recover})
            value = {"agent_id": target, "token": token, "role": "coordinator", "provider": receiver["provider"]}
        if previous_identity:
            atomic_json(self.directory / "identities" / (previous_identity["agent_id"] + ".json"), previous_identity)
        atomic_json(self.directory / "identities" / (target + ".json"), value)
        return {**value, "identity_file": str(self.directory / "identities" / (target + ".json"))}

    def send(self, identity, data):
        recipient, kind = data.get("to"), data.get("type", "notice")
        if kind not in {"request", "response", "notice"} or not isinstance(data.get("payload"), dict):
            raise TeamError("A message needs request/response/notice and an object payload.")
        with self.transaction() as db:
            actor = self.authenticate(db, identity)
            target = None if recipient == "coordinator" else db.execute("SELECT * FROM agents WHERE id=?", (recipient,)).fetchone()
            if recipient != "coordinator" and (not target or target["status"] == "ended"):
                raise TeamError("Unknown or ended recipient.")
            if actor["role"] == "worker" and target and target["run_id"] != actor["run_id"]:
                raise TeamError("Peer communication is limited to this assignment's run.")
            message = dict(schema_version=1, id=data.get("id") or identifier("message"),
                           run_id=actor["run_id"] or (target["run_id"] if target else None),
                           spec_id=actor["spec_id"] or (target["spec_id"] if target else None),
                           **{"from": actor["id"], "to": recipient}, type=kind,
                           reply_to=data.get("reply_to"), payload=data["payload"], created_at=now())
            previous = db.execute("SELECT envelope FROM messages WHERE id=?", (message["id"],)).fetchone()
            if previous:
                saved = json.loads(previous["envelope"])
                if any(saved[key] != message[key] for key in message if key != "created_at"):
                    raise TeamError("Message ID already exists with different content.")
                return saved
            if message["reply_to"] and not db.execute("SELECT 1 FROM messages WHERE id=?", (message["reply_to"],)).fetchone():
                raise TeamError("reply_to must reference an existing message.")
            db.execute("INSERT INTO messages(id,envelope,recipient) VALUES(?,?,?)", (message["id"], dump(message), recipient))
            self.event(db, "message_queued", actor["id"], message["run_id"], message["spec_id"], {"message_id": message["id"], "to": recipient})
            return message

    def inbox(self, identity, *, deliver=True):
        with self.transaction() as db:
            actor = self.authenticate(db, identity)
            recipients = [actor["id"]] + (["coordinator"] if actor["role"] == "coordinator" else [])
            rows = db.execute("SELECT * FROM messages WHERE acked=0 AND recipient IN (" +
                              ",".join("?" for _ in recipients) + ") ORDER BY rowid LIMIT 20", recipients).fetchall()
            if deliver:
                for row in rows:
                    db.execute("UPDATE messages SET deliveries=deliveries+1 WHERE id=?", (row["id"],))
                    self.event(db, "message_delivered", actor["id"], actor["run_id"], actor["spec_id"], {"message_id": row["id"]})
            return [json.loads(row["envelope"]) for row in rows]

    def ack(self, identity, message_id):
        with self.transaction() as db:
            actor = self.authenticate(db, identity)
            message = db.execute("SELECT * FROM messages WHERE id=?", (message_id,)).fetchone()
            if not message or message["recipient"] not in {actor["id"], "coordinator" if actor["role"] == "coordinator" else actor["id"]}:
                raise TeamError("Only the recipient may acknowledge a message.")
            if not message["acked"]:
                db.execute("UPDATE messages SET acked=1 WHERE id=?", (message_id,))
                self.event(db, "message_acknowledged", actor["id"], actor["run_id"], actor["spec_id"], {"message_id": message_id})
        return {"id": message_id, "acknowledged": True}

    def status(self):
        with self.connection() as db:
            agents = [dict(row) for row in db.execute("SELECT * FROM agents ORDER BY rowid")]
            for agent in agents:
                agent.pop("token", None)
                agent.pop("driver_nonce", None)
                agent["assignment"] = json.loads(agent["assignment"]) if agent["assignment"] else None
            return {"owner": dict(db.execute("SELECT * FROM owner").fetchone()), "agents": agents,
                    "runs": [dict(row) for row in db.execute("SELECT id,baseline,plan,status FROM runs")],
                    "events": [{**json.loads(row["envelope"]), "sequence": row["sequence"]}
                               for row in db.execute("SELECT * FROM events ORDER BY sequence")]}
