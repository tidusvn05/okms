use crate::{runtime::Runtime, util};
use anyhow::{Context, Result, ensure};
use clap::{Parser, ValueEnum};
use serde_json::{Value, json};
use std::io::Read;
use std::path::PathBuf;
use std::time::{Duration, Instant};

#[derive(Debug, Clone, Copy, ValueEnum)]
enum Command {
    Init,
    Doctor,
    Join,
    Dispatch,
    Send,
    Inbox,
    Ack,
    Status,
    Resume,
    Handoff,
    Checkpoint,
    Integrate,
    Verify,
    Stop,
    Hook,
    #[value(name = "_run")]
    Run,
}

#[derive(Parser)]
#[command(
    name = "okms",
    version,
    about = "Portable workflows and project-local coding agent coordination"
)]
struct Args {
    #[arg(value_enum)]
    command: Command,
    #[arg(long)]
    project: Option<PathBuf>,
    #[arg(long)]
    identity: Option<PathBuf>,
    #[arg(long, value_parser = ["codex", "claude"])]
    provider: Option<String>,
    #[arg(
        long,
        conflicts_with = "input_json",
        help = "JSON input file, or - for stdin"
    )]
    input: Option<String>,
    #[arg(long, help = "Object JSON for programmatic argument arrays")]
    input_json: Option<String>,
    #[arg(long)]
    docs: Option<String>,
    #[arg(long)]
    dry_run: bool,
}

fn execute(args: &Args) -> Result<Value> {
    let data = if let Some(input) = &args.input_json {
        serde_json::from_str(input)?
    } else if args.input.as_deref() == Some("-")
        || (matches!(args.command, Command::Hook) && args.input.is_none())
    {
        let mut input = String::new();
        std::io::stdin().read_to_string(&mut input)?;
        serde_json::from_str(&input)?
    } else if let Some(path) = &args.input {
        util::json(&PathBuf::from(path))?
    } else {
        json!({})
    };
    ensure!(data.is_object(), "Command input must be a JSON object.");
    let project = util::discover_project(args.project.as_deref())?;
    if matches!(args.command, Command::Init) {
        return crate::adoption::install(&project, args.docs.as_deref(), args.dry_run);
    }
    ensure!(
        args.docs.is_none() && !args.dry_run,
        "--docs and --dry-run apply only to init."
    );
    ensure!(
        project.join(".okms/team.json").is_file(),
        "Hybrid Team is not installed here; run okms init first."
    );
    let runtime = Runtime::new(&project)?;
    let store = &runtime.store;
    let identity = if let Some(path) = &args.identity {
        util::json(path)?
    } else {
        json!({"agent_id":std::env::var("OKMS_AGENT_ID").ok(), "token":std::env::var("OKMS_AGENT_TOKEN").ok()})
    };
    match args.command {
        Command::Join => store.join(
            args.provider
                .as_deref()
                .or(data["provider"].as_str())
                .context("join requires provider.")?,
            util::string(&data, "session_id")?,
        ),
        Command::Doctor => runtime.doctor(),
        Command::Dispatch => runtime.dispatch(&identity, &data),
        Command::Send => runtime.send(&identity, &data),
        Command::Inbox => Ok(json!({"messages":store.inbox(&identity)?})),
        Command::Ack => store.ack(&identity, util::string(&data, "id")?),
        Command::Handoff => store.handoff(
            &identity,
            data["to"].as_str(),
            data["recover"].as_bool().unwrap_or(false),
        ),
        Command::Resume => runtime.resume(&identity, &data),
        Command::Checkpoint => runtime.checkpoint(&identity, &data),
        Command::Integrate => runtime.integrate(&identity, &data),
        Command::Verify => runtime.verify(&identity, &data),
        Command::Stop => runtime.stop(&identity, &data),
        Command::Hook => runtime.hook(
            args.provider
                .as_deref()
                .context("hook requires --provider.")?,
            &data,
        ),
        Command::Run => runtime.run(&data),
        Command::Status => {
            store.authenticate(&store.connection()?, &identity, false)?;
            let wait = data
                .get("wait_seconds")
                .map(|v| v.as_f64().context("wait_seconds must be between 0 and 50."))
                .transpose()?
                .unwrap_or(0.);
            ensure!(
                wait.is_finite() && (0. ..=50.).contains(&wait),
                "wait_seconds must be between 0 and 50."
            );
            let deadline = Instant::now() + Duration::from_secs_f64(wait);
            loop {
                let result = store.status()?;
                let busy = result["agents"].as_array().unwrap().iter().any(|v| {
                    matches!(
                        v["status"].as_str(),
                        Some("queued" | "starting" | "running")
                    )
                });
                if !busy || Instant::now() >= deadline {
                    return Ok(result);
                }
                std::thread::sleep(Duration::from_millis(250));
            }
        }
        Command::Init => unreachable!("Initialization is handled before runtime loading."),
    }
}

pub fn main() -> i32 {
    let args = Args::parse();
    match execute(&args) {
        Ok(value) => {
            println!("{value}");
            0
        }
        Err(error) => {
            if matches!(args.command, Command::Hook) {
                println!(
                    "{}",
                    json!({"systemMessage":format!("Hybrid Team setup/recovery required: {error:#}")})
                );
            } else {
                println!(
                    "{}",
                    json!({"error":format!("{error:#}"),"incomplete":true})
                );
            }
            1
        }
    }
}
