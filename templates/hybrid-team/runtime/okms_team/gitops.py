"""Private snapshots and worktrees that preserve the user's index and branch."""

from __future__ import annotations

import hashlib
import os
import subprocess
import tempfile
from pathlib import Path, PurePosixPath

from .state import TeamError, identifier


def git(project, *args, input=None, env=None, check=True):
    result = subprocess.run(["git", "-C", str(project), *args], input=input,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    if check and result.returncode:
        raise TeamError("Git operation failed: " + result.stderr.decode(errors="replace").strip())
    return result


def clean_environment():
    env = os.environ.copy()
    for key in ("GIT_INDEX_FILE", "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"):
        env.pop(key, None)
    env.setdefault("GIT_AUTHOR_NAME", "okms local snapshot")
    env.setdefault("GIT_AUTHOR_EMAIL", "snapshot@okms.invalid")
    env.setdefault("GIT_COMMITTER_NAME", "okms local snapshot")
    env.setdefault("GIT_COMMITTER_EMAIL", "snapshot@okms.invalid")
    return env


def snapshot(project, reference=None):
    project = Path(project).resolve()
    if git(project, "ls-files", "-u").stdout:
        raise TeamError("Resolve the existing Git index conflict before snapshotting.")
    parent = git(project, "rev-parse", "--verify", "HEAD", check=False)
    if parent.returncode:
        raise TeamError("Hybrid Team needs an existing Git commit; initialize the project baseline first.")
    directory = project / ".okms/state"
    directory.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="index-", dir=directory) as temporary:
        env = clean_environment()
        env["GIT_INDEX_FILE"] = str(Path(temporary) / "index")
        git(project, "read-tree", "HEAD", env=env)
        cached = set(git(project, "ls-files", "--cached", "-z", env=env).stdout.split(b"\0")) - {b""}
        candidates = cached | (set(git(project, "ls-files", "--cached", "--others", "--exclude-standard", "-z",
                                      env=clean_environment()).stdout.split(b"\0")) - {b""})
        excluded = {path for path in candidates if path == b".okms/state" or path.startswith(b".okms/state/")}
        if cached & excluded:
            git(project, "update-index", "--force-remove", "-z", "--stdin", input=b"\0".join(sorted(cached & excluded)) + b"\0", env=env)
        selected = {path for path in candidates - excluded if path in cached or
                    (project / os.fsdecode(path)).exists() or (project / os.fsdecode(path)).is_symlink()}
        if selected:
            # Literal selected paths include already-tracked ignored files without adding ignored untracked content.
            git(project, "--literal-pathspecs", "add", "-A", "-f", "--pathspec-from-file=-", "--pathspec-file-nul",
                input=b"\0".join(sorted(selected)) + b"\0", env=env)
        tree = git(project, "write-tree", env=env).stdout.strip().decode()
        commit = git(project, "commit-tree", tree, "-p", parent.stdout.strip().decode(),
                     input=b"okms private current-code snapshot\n", env=env).stdout.strip().decode()
    if reference:
        git(project, "update-ref", reference, commit, env=clean_environment())
    return commit


def worktree(project, name, base):
    path = Path(project) / ".okms/state/worktrees" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    git(project, "worktree", "add", "--detach", str(path), base, env=clean_environment())
    return path.resolve()


def paths_changed(project, before, after):
    result = git(project, "diff", "--name-only", "--no-renames", "-z", before, after).stdout
    return [part.decode() for part in result.split(b"\0") if part]


def scope_path(path):
    if not isinstance(path, str) or not path or "\\" in path:
        raise TeamError("Write scope needs relative project paths using forward slashes.")
    value = PurePosixPath(path)
    if value.is_absolute() or ".." in value.parts or value == PurePosixPath("."):
        raise TeamError("Write scope must be an explicit relative file or directory.")
    if value.parts[0] in {".git", ".okms", ".codex", ".claude", ".agents"} or str(value) in {"AGENTS.md", "CLAUDE.md"}:
        raise TeamError("Workers cannot own shared runtime or native configuration.")
    return value.as_posix().rstrip("/")


def within(path, scope):
    return any(path == own or path.startswith(own + "/") for own in scope)


def overlap(first, second):
    return any(within(path, second) for path in first) or any(within(path, first) for path in second)


def fingerprint(project, path):
    target = Path(project) / path
    if target.is_symlink():
        return "link:" + os.readlink(target)
    if not target.exists():
        return None
    if not target.is_file():
        raise TeamError("Unsupported integration target: " + path)
    return hashlib.sha256(target.read_bytes()).hexdigest() + ":" + str(target.stat().st_mode & 0o777)


def changed_target(project, baseline, paths):
    for path in paths:
        old = git(project, "ls-tree", baseline, "--", path).stdout.decode().strip()
        target = Path(project) / path
        if not old:
            if target.exists() or target.is_symlink():
                return path
            continue
        mode, _, rest = old.split(" ", 2)
        object_id = rest.split("\t", 1)[0]
        if mode == "160000":
            raise TeamError("Submodule changes require manual integration: " + path)
        if mode == "120000":
            if not target.is_symlink() or os.readlink(target).encode() != git(project, "cat-file", "blob", object_id).stdout:
                return path
        elif (not target.is_file() or target.is_symlink() or target.read_bytes() != git(project, "cat-file", "blob", object_id).stdout
              or bool(target.stat().st_mode & 0o111) != (mode == "100755")):
            return path
    return None


def combine(project, baseline, commits):
    integration = worktree(project, identifier("integration"), baseline)
    for commit in commits:
        patch = git(project, "diff", "--binary", "--no-renames", baseline, commit).stdout
        if patch:
            git(integration, "apply", "--check", "--binary", "-", input=patch)
            git(integration, "apply", "--binary", "-", input=patch)
    return integration


def apply_to_root(project, baseline, integrated):
    paths = paths_changed(project, baseline, integrated)
    conflict = changed_target(project, baseline, paths)
    if conflict:
        raise TeamError("Root changed since the baseline; reconcile before applying: " + conflict)
    # Verify all targets before touching any file. git apply does not update the user's index.
    patch = git(project, "diff", "--binary", "--no-renames", baseline, integrated).stdout
    if patch:
        git(project, "apply", "--check", "--binary", "-", input=patch)
        git(project, "apply", "--binary", "-", input=patch)
    return paths
