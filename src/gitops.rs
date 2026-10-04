use crate::util::{identifier, project_path};
use anyhow::{Context, Result, bail, ensure};
use std::collections::BTreeSet;
use std::fs;
use std::io::Write;
use std::path::{Component, Path, PathBuf};
use std::process::{Command, Output, Stdio};

pub fn git(
    project: &Path,
    args: &[&str],
    input: Option<&[u8]>,
    index: Option<&Path>,
    check: bool,
) -> Result<Output> {
    let mut command = Command::new("git");
    command
        .arg("-C")
        .arg(project)
        .args(args)
        .stdin(if input.is_some() {
            Stdio::piped()
        } else {
            Stdio::null()
        })
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .env("GIT_OPTIONAL_LOCKS", "0");
    for key in [
        "GIT_INDEX_FILE",
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_COMMON_DIR",
    ] {
        command.env_remove(key);
    }
    for (key, value) in [
        ("GIT_AUTHOR_NAME", "okms local snapshot"),
        ("GIT_AUTHOR_EMAIL", "snapshot@okms.invalid"),
        ("GIT_COMMITTER_NAME", "okms local snapshot"),
        ("GIT_COMMITTER_EMAIL", "snapshot@okms.invalid"),
    ] {
        if std::env::var_os(key).is_none() {
            command.env(key, value);
        }
    }
    if let Some(index) = index {
        command.env("GIT_INDEX_FILE", index);
    }
    let mut process = command
        .spawn()
        .context("Git is required for coordination.")?;
    if let Some(bytes) = input {
        process
            .stdin
            .take()
            .context("Missing Git stdin.")?
            .write_all(bytes)?;
    }
    let output = process.wait_with_output()?;
    if check && !output.status.success() {
        bail!(
            "Git operation failed: {}",
            String::from_utf8_lossy(&output.stderr).trim()
        );
    }
    Ok(output)
}

fn paths(bytes: &[u8]) -> BTreeSet<Vec<u8>> {
    bytes
        .split(|byte| *byte == 0)
        .filter(|p| !p.is_empty())
        .map(<[u8]>::to_vec)
        .collect()
}

fn path_input(paths: &BTreeSet<Vec<u8>>) -> Vec<u8> {
    paths
        .iter()
        .flat_map(|p| p.iter().copied().chain(std::iter::once(0)))
        .collect()
}

pub fn snapshot(project: &Path, reference: Option<&str>) -> Result<String> {
    ensure!(
        git(project, &["ls-files", "-u"], None, None, true)?
            .stdout
            .is_empty(),
        "Resolve the existing Git index conflict before snapshotting."
    );
    let parent = git(
        project,
        &["rev-parse", "--verify", "HEAD"],
        None,
        None,
        false,
    )?;
    ensure!(
        parent.status.success(),
        "Hybrid Team needs an existing Git commit; initialize the project baseline first."
    );
    let directory = project_path(project, ".okms/state")?;
    fs::create_dir_all(&directory)?;
    let temporary = tempfile::Builder::new()
        .prefix("index-")
        .tempdir_in(&directory)?;
    let index = temporary.path().join("index");
    git(project, &["read-tree", "HEAD"], None, Some(&index), true)?;
    let cached = paths(
        &git(
            project,
            &["ls-files", "--cached", "-z"],
            None,
            Some(&index),
            true,
        )?
        .stdout,
    );
    let mut candidates = cached.clone();
    candidates.extend(paths(
        &git(
            project,
            &[
                "ls-files",
                "--cached",
                "--others",
                "--exclude-standard",
                "-z",
            ],
            None,
            None,
            true,
        )?
        .stdout,
    ));
    let excluded = candidates
        .iter()
        .filter(|p| p.as_slice() == b".okms/state" || p.starts_with(b".okms/state/"))
        .cloned()
        .collect::<BTreeSet<_>>();
    let tracked_excluded = cached
        .intersection(&excluded)
        .cloned()
        .collect::<BTreeSet<_>>();
    if !tracked_excluded.is_empty() {
        git(
            project,
            &["update-index", "--force-remove", "-z", "--stdin"],
            Some(&path_input(&tracked_excluded)),
            Some(&index),
            true,
        )?;
    }
    let mut selected = BTreeSet::new();
    for path in candidates.difference(&excluded) {
        let relative = std::str::from_utf8(path)
            .context("Non-UTF-8 application paths require explicit manual coordination.")?;
        if cached.contains(path) || fs::symlink_metadata(project.join(relative)).is_ok() {
            selected.insert(path.clone());
        }
    }
    if !selected.is_empty() {
        git(
            project,
            &[
                "--literal-pathspecs",
                "add",
                "-A",
                "-f",
                "--pathspec-from-file=-",
                "--pathspec-file-nul",
            ],
            Some(&path_input(&selected)),
            Some(&index),
            true,
        )?;
    }
    let tree = String::from_utf8(git(project, &["write-tree"], None, Some(&index), true)?.stdout)?
        .trim()
        .to_string();
    let parent = String::from_utf8(parent.stdout)?.trim().to_string();
    let revision = String::from_utf8(
        git(
            project,
            &["commit-tree", &tree, "-p", &parent],
            Some(b"okms private current-code snapshot\n"),
            Some(&index),
            true,
        )?
        .stdout,
    )?
    .trim()
    .to_string();
    if let Some(reference) = reference {
        git(
            project,
            &["update-ref", reference, &revision],
            None,
            None,
            true,
        )?;
    }
    Ok(revision)
}

pub fn worktree(project: &Path, name: &str, base: &str) -> Result<PathBuf> {
    let path = project_path(project, &format!(".okms/state/worktrees/{name}"))?;
    fs::create_dir_all(path.parent().context("Worktree needs a parent.")?)?;
    let location = path.to_str().context("Worktree path must be UTF-8.")?;
    git(
        project,
        &["worktree", "add", "--detach", location, base],
        None,
        None,
        true,
    )?;
    Ok(path.canonicalize()?)
}

pub fn paths_changed(project: &Path, before: &str, after: &str) -> Result<Vec<String>> {
    let output = git(
        project,
        &["diff", "--name-only", "--no-renames", "-z", before, after],
        None,
        None,
        true,
    )?;
    output
        .stdout
        .split(|b| *b == 0)
        .filter(|p| !p.is_empty())
        .map(|p| Ok(String::from_utf8(p.to_vec())?))
        .collect()
}

pub fn scope_path(path: &str) -> Result<String> {
    let value = Path::new(path);
    ensure!(
        !path.is_empty()
            && !path.contains('\\')
            && !value.is_absolute()
            && value
                .components()
                .all(|part| matches!(part, Component::Normal(_))),
        "Write scope must be an explicit relative file or directory."
    );
    let normal = path.trim_end_matches('/');
    let first = normal.split('/').next().unwrap_or("");
    ensure!(
        ![".git", ".okms", ".codex", ".claude", ".agents"].contains(&first)
            && !["AGENTS.md", "CLAUDE.md"].contains(&normal),
        "Workers cannot own shared runtime or native configuration."
    );
    Ok(normal.to_string())
}

pub fn within(path: &str, scope: &[String]) -> bool {
    scope
        .iter()
        .any(|own| path == own || path.starts_with(&format!("{own}/")))
}

pub fn overlap(first: &[String], second: &[String]) -> bool {
    first.iter().any(|p| within(p, second)) || second.iter().any(|p| within(p, first))
}

pub fn changed_target(project: &Path, baseline: &str, paths: &[String]) -> Result<Option<String>> {
    for path in paths {
        project_path(project, path)?;
        let old = git(
            project,
            &["ls-tree", baseline, "--", path],
            None,
            None,
            true,
        )?
        .stdout;
        let target = project.join(path);
        if old.is_empty() {
            if fs::symlink_metadata(&target).is_ok() {
                return Ok(Some(path.clone()));
            }
            continue;
        }
        let line = std::str::from_utf8(&old)?;
        let mut pieces = line.split_whitespace();
        let mode = pieces.next().context("Invalid Git tree mode.")?;
        pieces.next().context("Invalid Git tree kind.")?;
        let object = pieces.next().context("Invalid Git tree object.")?;
        ensure!(
            mode != "160000",
            "Submodule changes require manual integration: {path}"
        );
        let blob = git(project, &["cat-file", "blob", object], None, None, true)?.stdout;
        let unchanged = if mode == "120000" {
            #[cfg(unix)]
            {
                use std::os::unix::ffi::OsStrExt;
                fs::read_link(&target).is_ok_and(|value| value.as_os_str().as_bytes() == blob)
            }
            #[cfg(not(unix))]
            {
                false
            }
        } else if let Ok(metadata) = fs::symlink_metadata(&target) {
            #[cfg(unix)]
            let executable = {
                use std::os::unix::fs::PermissionsExt;
                metadata.permissions().mode() & 0o111 != 0
            };
            #[cfg(not(unix))]
            let executable = false;
            metadata.is_file() && fs::read(&target)? == blob && executable == (mode == "100755")
        } else {
            false
        };
        if !unchanged {
            return Ok(Some(path.clone()));
        }
    }
    Ok(None)
}

pub fn combine(project: &Path, baseline: &str, commits: &[String]) -> Result<PathBuf> {
    let integration = worktree(project, &identifier("integration"), baseline)?;
    for commit in commits {
        let patch = git(
            project,
            &["diff", "--binary", "--no-renames", baseline, commit],
            None,
            None,
            true,
        )?
        .stdout;
        if !patch.is_empty() {
            git(
                &integration,
                &["apply", "--check", "--binary", "-"],
                Some(&patch),
                None,
                true,
            )?;
            git(
                &integration,
                &["apply", "--binary", "-"],
                Some(&patch),
                None,
                true,
            )?;
        }
    }
    Ok(integration)
}

pub fn apply_to_root(project: &Path, baseline: &str, integrated: &str) -> Result<Vec<String>> {
    let paths = paths_changed(project, baseline, integrated)?;
    if let Some(conflict) = changed_target(project, baseline, &paths)? {
        bail!("Root changed since the baseline; reconcile before applying: {conflict}");
    }
    let patch = git(
        project,
        &["diff", "--binary", "--no-renames", baseline, integrated],
        None,
        None,
        true,
    )?
    .stdout;
    if !patch.is_empty() {
        git(
            project,
            &["apply", "--check", "--binary", "-"],
            Some(&patch),
            None,
            true,
        )?;
        git(
            project,
            &["apply", "--binary", "-"],
            Some(&patch),
            None,
            true,
        )?;
    }
    Ok(paths)
}
