use crate::util::{atomic_json, identifier, now, string, token};
use anyhow::{Context, Result, bail, ensure};
use rusqlite::{Connection, OptionalExtension, Params, TransactionBehavior, params};
use serde_json::{Map, Value, json};
use std::fs;
use std::path::{Path, PathBuf};
use std::time::Duration;
use subtle::ConstantTimeEq;

#[derive(Clone)]
pub struct Store {
    pub project: PathBuf,
    pub directory: PathBuf,
    pub path: PathBuf,
}

pub fn rows<P: Params>(db: &Connection, sql: &str, arguments: P) -> Result<Vec<Value>> {
    let mut statement = db.prepare(sql)?;
    let names = statement
        .column_names()
        .iter()
        .map(|s| (*s).to_string())
        .collect::<Vec<_>>();
    let values = statement.query_map(arguments, |row| {
        let mut object = Map::new();
        for (index, name) in names.iter().enumerate() {
            let value = match row.get_ref(index)? {
                rusqlite::types::ValueRef::Null => Value::Null,
                rusqlite::types::ValueRef::Integer(v) => json!(v),
                rusqlite::types::ValueRef::Real(v) => json!(v),
                rusqlite::types::ValueRef::Text(v) => json!(String::from_utf8_lossy(v)),
                rusqlite::types::ValueRef::Blob(v) => json!(v),
            };
            object.insert(name.clone(), value);
        }
        Ok(Value::Object(object))
    })?;
    Ok(values.collect::<rusqlite::Result<Vec<_>>>()?)
}

pub fn first<P: Params>(db: &Connection, sql: &str, arguments: P) -> Result<Option<Value>> {
    Ok(rows(db, sql, arguments)?.into_iter().next())
}

impl Store {
    pub fn new(project: &Path) -> Result<Self> {
        let project = project.canonicalize()?;
        let directory = crate::util::project_path(&project, ".okms/state")?;
        fs::create_dir_all(&directory)?;
        let path = crate::util::project_path(&project, ".okms/state/team.sqlite3")?;
        let value = Self {
            project,
            path,
            directory,
        };
        value.connection()?.execute_batch(
            "CREATE TABLE IF NOT EXISTS agents (
             id TEXT PRIMARY KEY, provider TEXT NOT NULL, session_id TEXT,
             role TEXT NOT NULL, token TEXT NOT NULL, status TEXT NOT NULL,
             run_id TEXT, spec_id TEXT, worktree TEXT, native_session_id TEXT,
             pid INTEGER, assignment TEXT, deadline REAL, notes TEXT, driver_nonce TEXT,
             native_permission_mode TEXT, UNIQUE(provider, session_id));
             CREATE TABLE IF NOT EXISTS owner (
             singleton INTEGER PRIMARY KEY CHECK(singleton=1), agent_id TEXT, generation INTEGER NOT NULL);
             INSERT OR IGNORE INTO owner VALUES(1,NULL,0);
             CREATE TABLE IF NOT EXISTS runs (
             id TEXT PRIMARY KEY, baseline TEXT NOT NULL, plan TEXT NOT NULL,
             status TEXT NOT NULL, metadata TEXT NOT NULL);
             CREATE TABLE IF NOT EXISTS messages (
             id TEXT PRIMARY KEY, envelope TEXT NOT NULL, recipient TEXT NOT NULL,
             acked INTEGER NOT NULL DEFAULT 0, deliveries INTEGER NOT NULL DEFAULT 0);
             CREATE TABLE IF NOT EXISTS events (
             sequence INTEGER PRIMARY KEY AUTOINCREMENT, envelope TEXT NOT NULL);")?;
        Ok(value)
    }

    pub fn connection(&self) -> Result<Connection> {
        let db = Connection::open(&self.path)?;
        db.busy_timeout(Duration::from_secs(30))?;
        // Concurrent first opens can contend while SQLite switches journal mode;
        // this pragma can return BUSY without invoking the configured busy handler.
        let deadline = std::time::Instant::now() + Duration::from_secs(30);
        loop {
            match db.pragma_update(None, "journal_mode", "WAL") {
                Ok(()) => break,
                Err(rusqlite::Error::SqliteFailure(code, _))
                    if matches!(
                        code.code,
                        rusqlite::ffi::ErrorCode::DatabaseBusy
                            | rusqlite::ffi::ErrorCode::DatabaseLocked
                    ) && std::time::Instant::now() < deadline =>
                {
                    std::thread::sleep(Duration::from_millis(10));
                }
                Err(error) => return Err(error.into()),
            }
        }
        db.pragma_update(None, "synchronous", "FULL")?;
        Ok(db)
    }

    pub fn transact<T>(&self, action: impl FnOnce(&Connection) -> Result<T>) -> Result<T> {
        let mut db = self.connection()?;
        let transaction = db.transaction_with_behavior(TransactionBehavior::Immediate)?;
        let value = action(&transaction)?;
        transaction.commit()?;
        Ok(value)
    }

    pub fn event(
        &self,
        db: &Connection,
        kind: &str,
        actor: Option<&str>,
        run: Option<&str>,
        spec: Option<&str>,
        payload: Value,
    ) -> Result<Value> {
        let mut value = json!({"schema_version":1,"id":identifier("event"),"run_id":run,
            "spec_id":spec,"from":actor,"to":null,"type":kind,"reply_to":null,"payload":payload,"created_at":now()});
        db.execute(
            "INSERT INTO events(envelope) VALUES(?)",
            [value.to_string()],
        )?;
        value["sequence"] = json!(db.last_insert_rowid());
        Ok(value)
    }

    pub fn authenticate(
        &self,
        db: &Connection,
        identity: &Value,
        coordinator: bool,
    ) -> Result<Value> {
        let id = identity
            .get("agent_id")
            .and_then(Value::as_str)
            .unwrap_or("");
        let supplied = identity.get("token").and_then(Value::as_str).unwrap_or("");
        let agent = first(db, "SELECT * FROM agents WHERE id=?", [id])?
            .context("Unknown or stale identity; obtain the current session identity.")?;
        ensure!(
            bool::from(
                agent["token"]
                    .as_str()
                    .unwrap_or("")
                    .as_bytes()
                    .ct_eq(supplied.as_bytes())
            ),
            "Unknown or stale identity; obtain the current session identity."
        );
        ensure!(
            agent["status"] != "ended",
            "This session has ended; join or explicitly resume it."
        );
        if coordinator {
            let owner: Option<String> =
                db.query_row("SELECT agent_id FROM owner WHERE singleton=1", [], |r| {
                    r.get(0)
                })?;
            ensure!(
                agent["role"] == "coordinator" && owner.as_deref() == Some(id),
                "Only the current coordinator may perform this operation."
            );
            ensure!(
                agent["native_permission_mode"] != "plan",
                "The coordinator is in native plan mode; implementation operations remain unavailable."
            );
        }
        Ok(agent)
    }

    pub fn join(&self, provider: &str, session: &str) -> Result<Value> {
        ensure!(
            ["codex", "claude"].contains(&provider) && !session.is_empty(),
            "join needs provider codex/claude and a nonempty session_id."
        );
        let identity = self.transact(|db| {
            let existing = first(db, "SELECT * FROM agents WHERE provider=? AND session_id=?", params![provider,session])?;
            let owner: Option<String> = db.query_row("SELECT agent_id FROM owner WHERE singleton=1", [], |r| r.get(0))?;
            let id = existing.as_ref().and_then(|v| v["id"].as_str()).map(str::to_string).unwrap_or_else(|| identifier("agent"));
            let role = if owner.is_none() || owner.as_deref() == Some(&id) { "coordinator" } else { "standby" };
            let secret = existing.as_ref().filter(|v| v["status"] != "ended").and_then(|v| v["token"].as_str()).map(str::to_string).unwrap_or_else(token);
            if existing.is_some() {
                db.execute("UPDATE agents SET role=?,token=?,status='active' WHERE id=?", params![role,secret,id])?;
            } else {
                db.execute("INSERT INTO agents(id,provider,session_id,role,token,status) VALUES(?,?,?,?,?,'active')", params![id,provider,session,role,secret])?;
            }
            if role == "coordinator" && owner.is_none() {
                db.execute("UPDATE owner SET agent_id=?,generation=generation+1 WHERE singleton=1", [&id])?;
                self.event(db,"coordinator_changed",Some(&id),None,None,json!({"previous":null}))?;
            }
            Ok(json!({"agent_id":id,"token":secret,"role":role,"provider":provider}))
        })?;
        self.save_identity(identity)
    }

    fn save_identity(&self, mut identity: Value) -> Result<Value> {
        let path = crate::util::project_path(
            &self.project,
            &format!(
                ".okms/state/identities/{}.json",
                string(&identity, "agent_id")?
            ),
        )?;
        atomic_json(&path, &identity)?;
        identity["identity_file"] = json!(path);
        Ok(identity)
    }

    pub fn handoff(&self, identity: &Value, target: Option<&str>, recover: bool) -> Result<Value> {
        let (value, previous_identity) = self.transact(|db| {
            let actor = self.authenticate(db,identity,!recover)?;
            if recover { ensure!(actor["role"] == "standby","Recovery is for a joined standby session."); }
            let target = if recover { string(&actor,"id")? } else { target.context("Handoff needs a target.")? };
            let receiver = first(db,"SELECT * FROM agents WHERE id=?",[target])?.context("Handoff target must be an active coordinator/standby session.")?;
            ensure!(receiver["role"] != "worker" && receiver["status"] == "active",
                "Handoff target must be an active coordinator/standby session.");
            let owner: Option<String> = db.query_row("SELECT agent_id FROM owner WHERE singleton=1",[],|r|r.get(0))?;
            let mut previous_identity = None;
            if let Some(previous_id) = &owner {
                let previous = first(db,"SELECT * FROM agents WHERE id=?",[previous_id])?.context("Missing previous owner.")?;
                let secret = token();
                db.execute("UPDATE agents SET role='standby',token=? WHERE id=?",params![secret,previous_id])?;
                if previous_id != target {
                    previous_identity = Some(json!({"agent_id":previous_id,"token":secret,"role":"standby","provider":previous["provider"]}));
                }
            }
            let secret = token();
            db.execute("UPDATE agents SET role='coordinator',token=? WHERE id=?",params![secret,target])?;
            db.execute("UPDATE owner SET agent_id=?,generation=generation+1 WHERE singleton=1",[target])?;
            self.event(db,"coordinator_changed",actor["id"].as_str(),None,None,json!({"previous":owner,"current":target,"recovery":recover}))?;
            Ok((json!({"agent_id":target,"token":secret,"role":"coordinator","provider":receiver["provider"]}),previous_identity))
        })?;
        if let Some(previous) = previous_identity {
            self.save_identity(previous)?;
        }
        self.save_identity(value)
    }

    pub fn send(&self, identity: &Value, data: &Value) -> Result<Value> {
        let recipient = string(data, "to")?;
        let kind = data.get("type").and_then(Value::as_str).unwrap_or("notice");
        ensure!(
            ["request", "response", "notice"].contains(&kind)
                && data.get("payload").is_some_and(Value::is_object),
            "A message needs request/response/notice and an object payload."
        );
        self.transact(|db| {
            let actor = self.authenticate(db,identity,false)?;
            let target = if recipient == "coordinator" { None } else {
                let value = first(db,"SELECT * FROM agents WHERE id=?",[recipient])?.context("Unknown or ended recipient.")?;
                ensure!(value["status"] != "ended","Unknown or ended recipient.");
                Some(value)
            };
            if actor["role"] == "worker" && let Some(target) = &target {
                ensure!(target["run_id"] == actor["run_id"],"Peer communication is limited to this assignment's run.");
            }
            let id = if data.get("id").is_some() { string(data,"id")?.to_string() } else { identifier("message") };
            let fallback = |field: &str| target.as_ref().map(|v| v[field].clone()).unwrap_or(Value::Null);
            let value = json!({"schema_version":1,"id":id,
                "run_id":if actor["run_id"].is_null(){fallback("run_id")}else{actor["run_id"].clone()},
                "spec_id":if actor["spec_id"].is_null(){fallback("spec_id")}else{actor["spec_id"].clone()},
                "from":actor["id"],"to":recipient,"type":kind,"reply_to":data.get("reply_to"),
                "payload":data["payload"],"created_at":now()});
            if let Some(previous) = db.query_row("SELECT envelope FROM messages WHERE id=?",[&id],|r|r.get::<_,String>(0)).optional()? {
                let saved: Value = serde_json::from_str(&previous)?;
                for (key, content) in value.as_object().unwrap() {
                    if key != "created_at" && saved[key] != *content { bail!("Message ID already exists with different content."); }
                }
                return Ok(saved);
            }
            if !value["reply_to"].is_null() {
                let reply = string(&value,"reply_to")?;
                ensure!(db.query_row("SELECT 1 FROM messages WHERE id=?",[reply],|r|r.get::<_,i64>(0)).optional()?.is_some(),
                    "reply_to must reference an existing message.");
            }
            db.execute("INSERT INTO messages(id,envelope,recipient) VALUES(?,?,?)",params![id,value.to_string(),recipient])?;
            self.event(db,"message_queued",actor["id"].as_str(),value["run_id"].as_str(),value["spec_id"].as_str(),json!({"message_id":id,"to":recipient}))?;
            Ok(value)
        })
    }

    pub fn inbox(&self, identity: &Value) -> Result<Vec<Value>> {
        self.transact(|db| {
            let actor = self.authenticate(db,identity,false)?;
            let id = string(&actor,"id")?;
            let alias = if actor["role"] == "coordinator" { "coordinator" } else { id };
            let pending = rows(db,"SELECT * FROM messages WHERE acked=0 AND recipient IN (?,?) ORDER BY rowid LIMIT 20",params![id,alias])?;
            let mut messages = Vec::new();
            for row in pending {
                db.execute("UPDATE messages SET deliveries=deliveries+1 WHERE id=?",[string(&row,"id")?])?;
                self.event(db,"message_delivered",Some(id),actor["run_id"].as_str(),actor["spec_id"].as_str(),json!({"message_id":row["id"]}))?;
                messages.push(serde_json::from_str(row["envelope"].as_str().context("Invalid message envelope.")?)?);
            }
            Ok(messages)
        })
    }

    pub fn ack(&self, identity: &Value, message_id: &str) -> Result<Value> {
        self.transact(|db| {
            let actor = self.authenticate(db, identity, false)?;
            let message = first(db, "SELECT * FROM messages WHERE id=?", [message_id])?
                .context("Only the recipient may acknowledge a message.")?;
            ensure!(
                message["recipient"] == actor["id"]
                    || (actor["role"] == "coordinator" && message["recipient"] == "coordinator"),
                "Only the recipient may acknowledge a message."
            );
            if message["acked"] == 0 {
                db.execute("UPDATE messages SET acked=1 WHERE id=?", [message_id])?;
                self.event(
                    db,
                    "message_acknowledged",
                    actor["id"].as_str(),
                    actor["run_id"].as_str(),
                    actor["spec_id"].as_str(),
                    json!({"message_id":message_id}),
                )?;
            }
            Ok(json!({"id":message_id,"acknowledged":true}))
        })
    }

    pub fn status(&self) -> Result<Value> {
        let db = self.connection()?;
        let mut agents = rows(&db, "SELECT * FROM agents ORDER BY rowid", [])?;
        for agent in &mut agents {
            agent.as_object_mut().unwrap().remove("token");
            agent.as_object_mut().unwrap().remove("driver_nonce");
            if let Some(assignment) = agent["assignment"].as_str() {
                agent["assignment"] = serde_json::from_str(assignment)?;
            }
        }
        let mut events = Vec::new();
        for row in rows(&db, "SELECT * FROM events ORDER BY sequence", [])? {
            let mut event: Value = serde_json::from_str(string(&row, "envelope")?)?;
            event["sequence"] = row["sequence"].clone();
            events.push(event);
        }
        Ok(
            json!({"owner":first(&db,"SELECT * FROM owner WHERE singleton=1",[])?, "agents":agents,
            "runs":rows(&db,"SELECT id,baseline,plan,status FROM runs",[])?, "events":events}),
        )
    }
}
