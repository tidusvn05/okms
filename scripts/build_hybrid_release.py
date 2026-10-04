#!/usr/bin/env python3
"""Package deterministic standalone binaries; never invoke provider task sessions."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import re
import subprocess
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ("x86_64-unknown-linux-musl", "aarch64-unknown-linux-musl",
           "x86_64-apple-darwin", "aarch64-apple-darwin")


def profile_version(root=ROOT):
    package = (root / "Cargo.toml").read_text().split("[dependencies]", 1)[0]
    match = re.search(r'^version\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+)"$', package, re.M)
    if not match:
        raise ValueError("Cargo package version must be major.minor.patch.")
    version = match.group(1)
    workflow = (root / "templates/hybrid-team/docs/workflow.md").read_text()
    if not re.search(r'^template_version:\s*[\"\x27]?' + re.escape(version) + r'[\"\x27]?\s*$', workflow, re.M):
        raise ValueError("Hybrid Team template_version must match Cargo.")
    return version


def validate_tag(tag, root=ROOT):
    version = profile_version(root)
    if tag is not None and tag != "hybrid-team-v" + version:
        raise ValueError("Release tag must match Cargo: hybrid-team-v" + version)
    return version


def release_notes(version):
    base = "https://github.com/tidusvn05/okms"
    tag = "hybrid-team-v" + version
    return f"""# Hybrid Team {version}

Standalone Rust CLI and coordination runtime for Codex and Claude Code, with
embedded preserving setup, isolated worktrees, durable messages/events, exact
native-session resume, explicit handoff, and checked integration.

## Install

~~~sh
curl -fL {base}/releases/download/{tag}/install.sh -o /tmp/okms-install.sh
sh /tmp/okms-install.sh --version {version}
export PATH="$HOME/.local/bin:$PATH"
okms init --project . --dry-run
okms init --project .
.okms/okms doctor
~~~

Binaries support Linux/WSL and macOS, on x86_64 and arm64. Installation requires
curl, tar, and sha256sum or shasum, with no Python or Rust compiler.
The four archives contain okms and both licenses; SHA256SUMS covers all archives
and install.sh. Numeric pins and offline --release-dir installation are supported.

Task coordination requires Git with an existing commit, installed/authenticated
provider CLIs, real configured project checks, and native permissions for
runtime Git/state and external CLI operations. Setup preserves project docs,
instructions, settings and customizations and starts no task session.

Existing Python 0.1.0 installations are not silently upgraded. Retain their
history/state and use a deliberate reviewed migration; the old prerelease and
its assets remain available. Lite and Plan-first remain portable Markdown 0.4.0.

## Activation and observations

Review Codex hook trust through /hooks and Claude Code project settings.
Explicit root join is supported when automatic hooks are unavailable; installed
configuration alone does not prove startup or role/skill activation. Native
mixed-provider evidence is scoped to the observed Linux CLI versions; platform
binary smoke tests do not establish native provider behavior on every OS.
Desktop/IDE/remote sessions remain outside the observed scope.

Read the [setup guide]({base}/blob/{tag}/README.md), the
[Rust observations]({base}/blob/{tag}/evals/rust-report.md), and the retained
[Python pilot history]({base}/blob/{tag}/evals/hybrid-report.md).
"""


def write_metadata(output, version, archives, root):
    products = {path.name: path.read_bytes() for path in archives}
    products["install.sh"] = (root / "install.sh").read_bytes()
    products["SHA256SUMS"] = "".join(
        hashlib.sha256(body).hexdigest() + "  " + name + "\n"
        for name, body in sorted(products.items())).encode()
    for name, body in products.items():
        path = output / name
        path.write_bytes(body)
        path.chmod(0o755 if name == "install.sh" else 0o644)
    return {"profile": "hybrid-team", "version": version, "tag": "hybrid-team-v" + version,
            "archives": sorted(path.name for path in archives), "assets": sorted(products)}


def build(output, binary, target, root=ROOT, *, tag=None, notes=None):
    version = validate_tag(tag, root)
    if target not in TARGETS:
        raise ValueError("Unsupported binary target: " + target)
    binary = Path(binary)
    if not binary.is_file() or binary.is_symlink():
        raise ValueError("Binary must be an existing regular file.")
    observed = subprocess.check_output([str(binary.resolve()), "--version"], text=True, timeout=10).strip()
    if observed != "okms " + version:
        raise ValueError("Binary version does not match committed Cargo version.")
    assets = {"okms": binary.read_bytes()}
    assets.update({name: (root / name).read_bytes() for name in ("LICENSE-MIT", "LICENSE-APACHE")})
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode="w", format=tarfile.USTAR_FORMAT) as archive:
            for name, body in sorted(assets.items()):
                member = tarfile.TarInfo(name)
                member.size, member.mode, member.mtime = len(body), 0o755 if name == "okms" else 0o644, 0
                archive.addfile(member, io.BytesIO(body))
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    archive = output / ("okms-" + target + ".tar.gz")
    archive.write_bytes(buffer.getvalue())
    metadata = write_metadata(output, version, [archive], root)
    metadata["archive"], metadata["target"] = archive.name, target
    if notes:
        Path(notes).parent.mkdir(parents=True, exist_ok=True)
        Path(notes).write_text(release_notes(version), encoding="utf-8")
    return metadata


def assemble(output, root=ROOT, *, tag=None, notes=None):
    version = validate_tag(tag, root)
    output = Path(output)
    archives = [output / ("okms-" + target + ".tar.gz") for target in TARGETS]
    for path in archives:
        with tarfile.open(path, "r:gz") as archive:
            members = archive.getmembers()
            if sorted(member.name for member in members) != ["LICENSE-APACHE", "LICENSE-MIT", "okms"] \
                    or any(not member.isfile() for member in members):
                raise ValueError("Unexpected binary archive members: " + path.name)
            if archive.extractfile("LICENSE-MIT").read() != (root / "LICENSE-MIT").read_bytes() \
                    or archive.extractfile("LICENSE-APACHE").read() != (root / "LICENSE-APACHE").read_bytes():
                raise ValueError("Archive license notices do not match source.")
    metadata = write_metadata(output, version, archives, root)
    if notes:
        Path(notes).parent.mkdir(parents=True, exist_ok=True)
        Path(notes).write_text(release_notes(version), encoding="utf-8")
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    parser.add_argument("--binary", type=Path)
    parser.add_argument("--target", choices=TARGETS)
    parser.add_argument("--tag")
    parser.add_argument("--notes", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--assemble", action="store_true")
    args = parser.parse_args()
    try:
        if args.validate_only:
            version = validate_tag(args.tag)
            result = {"profile": "hybrid-team", "version": version, "tag": "hybrid-team-v" + version}
        elif args.assemble:
            result = assemble(args.output, tag=args.tag, notes=args.notes)
        else:
            if not args.binary or not args.target:
                raise ValueError("--binary and --target are required for packaging.")
            result = build(args.output, args.binary, args.target, tag=args.tag, notes=args.notes)
    except (ValueError, OSError, subprocess.SubprocessError, tarfile.TarError) as error:
        parser.exit(1, str(error) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
