#![cfg(unix)]

use okms::process;
use std::fs;
use std::process::{Command, Stdio};
use std::time::{Duration, Instant};

struct Cleanup(i32);

impl Drop for Cleanup {
    fn drop(&mut self) {
        // The test owns this isolated group, including on an assertion failure.
        unsafe { libc::kill(-self.0, libc::SIGKILL) };
    }
}

#[test]
fn cancellation_stops_descendants_after_the_direct_child_exits() {
    let directory = tempfile::tempdir().unwrap();
    let ticks = directory.path().join("ticks");
    let mut command = Command::new("sh");
    command
        .args([
            "-c",
            "sh -c 'trap \"\" TERM; while :; do printf x >> ticks; sleep 0.05; done' & wait",
        ])
        .current_dir(directory.path())
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null());
    process::isolate(&mut command);
    let mut child = command.spawn().unwrap();
    let _cleanup = Cleanup(child.id() as i32);
    let ready = Instant::now() + Duration::from_secs(5);
    while !ticks.exists() {
        assert!(Instant::now() < ready, "Descendant did not start");
        std::thread::sleep(Duration::from_millis(20));
    }
    let started = Instant::now();
    process::stop(&mut child);
    assert!(started.elapsed() < Duration::from_secs(8));
    assert!(child.try_wait().unwrap().is_some());
    let stopped = fs::read(&ticks).unwrap();
    std::thread::sleep(Duration::from_millis(300));
    assert_eq!(
        fs::read(ticks).unwrap(),
        stopped,
        "Descendant remained active after cancellation"
    );
}
