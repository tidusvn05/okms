use crate::util::{atomic_json, seconds};
use anyhow::{Context, Result, ensure};
use serde_json::{Value, json};
use std::fs::{self, File};
use std::io::{Read, Seek, SeekFrom, Write};
use std::path::Path;
use std::process::{Child, Command, Stdio};
use std::time::{Duration, Instant};

pub fn isolate(command: &mut Command) {
    #[cfg(unix)]
    {
        use std::os::unix::process::CommandExt;
        command.process_group(0);
    }
}

pub fn alive(pid: i64) -> bool {
    if pid <= 0 || pid > i32::MAX as i64 {
        return false;
    }
    #[cfg(unix)]
    {
        // Signal zero performs a process existence/permission check and changes no state.
        unsafe {
            libc::kill(pid as libc::pid_t, 0) == 0
                || std::io::Error::last_os_error().raw_os_error() == Some(libc::EPERM)
        }
    }
    #[cfg(not(unix))]
    {
        let _ = pid;
        false
    }
}

pub fn stop(child: &mut Child) {
    #[cfg(unix)]
    let group = child.id() as libc::pid_t;
    #[cfg(unix)]
    {
        // Every managed child is created in its own process group, so descendants are bounded too.
        unsafe {
            libc::kill(-group, libc::SIGTERM);
        }
    }
    #[cfg(not(unix))]
    let _ = child.kill();
    let deadline = Instant::now() + Duration::from_secs(5);
    loop {
        let parent_done = child.try_wait().ok().flatten().is_some();
        #[cfg(unix)]
        let group_alive = unsafe {
            libc::kill(-group, 0) == 0
                || std::io::Error::last_os_error().raw_os_error() == Some(libc::EPERM)
        };
        #[cfg(not(unix))]
        let group_alive = false;
        if parent_done && !group_alive {
            return;
        }
        if Instant::now() >= deadline {
            break;
        }
        std::thread::sleep(Duration::from_millis(20));
    }
    #[cfg(unix)]
    unsafe {
        libc::kill(-group, libc::SIGKILL);
    }
    let _ = child.kill();
    let _ = child.wait();
}

pub fn validate_checks(checks: &Value) -> Result<Vec<Vec<String>>> {
    checks
        .as_array()
        .context("Checks must be arrays of command arguments.")?
        .iter()
        .map(|argv| {
            let result = argv
                .as_array()
                .context("Checks must be nonempty argument arrays, without a shell.")?
                .iter()
                .map(|s| {
                    s.as_str()
                        .filter(|s| !s.is_empty())
                        .map(str::to_string)
                        .context("Check arguments must be nonempty strings.")
                })
                .collect::<Result<Vec<_>>>()?;
            ensure!(
                !result.is_empty(),
                "Checks must be nonempty argument arrays, without a shell."
            );
            Ok(result)
        })
        .collect()
}

pub(crate) fn wait(child: &mut Child, timeout: f64) -> Result<Option<i32>> {
    let deadline = Instant::now() + Duration::from_secs_f64(timeout);
    loop {
        if let Some(status) = child.try_wait()? {
            return Ok(status.code());
        }
        if Instant::now() >= deadline {
            stop(child);
            return Ok(None);
        }
        std::thread::sleep(Duration::from_millis(25));
    }
}

pub fn checks(
    directory: &Path,
    checks: &[Vec<String>],
    output: &Path,
    timeout: f64,
) -> Result<Vec<Value>> {
    fs::create_dir_all(output)?;
    let mut evidence = Vec::new();
    for (number, argv) in checks.iter().enumerate() {
        ensure!(
            !argv.is_empty() && argv.iter().all(|s| !s.is_empty()),
            "Checks must be nonempty argument arrays, without a shell."
        );
        let path = output.join(format!("check-{}.log", number + 1));
        let mut stream = File::create(&path)?;
        let start = seconds();
        let mut command = Command::new(&argv[0]);
        command
            .args(&argv[1..])
            .current_dir(directory)
            .stdin(Stdio::null())
            .stdout(stream.try_clone()?)
            .stderr(stream.try_clone()?);
        isolate(&mut command);
        let code = match command.spawn() {
            Ok(mut child) => wait(&mut child, timeout)?,
            Err(error) => {
                writeln!(stream, "{error}")?;
                None
            }
        };
        evidence.push(json!({"argv":argv,"exit_code":code,"artifact":path,"elapsed_seconds":((seconds()-start)*1000.).round()/1000.}));
    }
    atomic_json(&output.join("checks.json"), &json!(evidence))?;
    Ok(evidence)
}

pub fn capture(
    directory: &Path,
    argv: &[String],
    timeout: f64,
) -> Result<(Option<i32>, String, String)> {
    ensure!(!argv.is_empty(), "Command needs an executable.");
    let mut stdout = tempfile::tempfile()?;
    let mut stderr = tempfile::tempfile()?;
    let mut command = Command::new(&argv[0]);
    command
        .args(&argv[1..])
        .current_dir(directory)
        .stdin(Stdio::null())
        .stdout(stdout.try_clone()?)
        .stderr(stderr.try_clone()?);
    isolate(&mut command);
    let code = wait(&mut command.spawn()?, timeout)?;
    stdout.seek(SeekFrom::Start(0))?;
    stderr.seek(SeekFrom::Start(0))?;
    let mut out = String::new();
    let mut err = String::new();
    stdout.take(1024 * 1024).read_to_string(&mut out)?;
    stderr.take(1024 * 1024).read_to_string(&mut err)?;
    Ok((code, out, err))
}
