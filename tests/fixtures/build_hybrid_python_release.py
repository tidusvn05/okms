#!/usr/bin/env python3
"""Build deterministic Hybrid Team assets without runtime state or provider calls."""

from __future__ import annotations

import argparse
import ast
import gzip
import hashlib
import io
import json
import re
import tarfile
from pathlib import Path

from hybrid_legacy import ROOT


def profile_version(root=ROOT):
    source = root / "templates/hybrid-team"
    module = ast.parse((source / "runtime/okms_team/__init__.py").read_text())
    version = next(ast.literal_eval(node.value) for node in module.body if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == "VERSION" for target in node.targets))
    if not isinstance(version, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
        raise ValueError("Hybrid Team VERSION must be major.minor.patch.")
    return version


def validate_tag(tag, root=ROOT):
    version = profile_version(root)
    if tag is not None and tag != "hybrid-team-v" + version:
        raise ValueError("Release tag must match the committed runtime version: hybrid-team-v" + version)
    return version


def release_notes(version):
    tag = "hybrid-team-v" + version
    base = "https://github.com/tidusvn05/okms"
    return f"""# Hybrid Team {version} (experimental)

An opt-in, project-local Python runtime for coordinating Codex and Claude Code
with scoped worktrees, durable messages, explicit handoff, and verified integration.
Lite and Plan-first remain portable Markdown profiles with independent versions.

## Install this version

~~~sh
curl -fL {base}/releases/download/{tag}/install.sh -o /tmp/okms-install.sh
sh /tmp/okms-install.sh --version {version} --project . --dry-run
sh /tmp/okms-install.sh --version {version} --project .
python3 .okms/team.py doctor
~~~

Installation requires curl and Python 3.10+. Task execution requires Git with an
existing commit, installed/authenticated Codex and Claude Code CLIs, real configured
project checks, and native permissions for runtime Git/state and external CLI operations.
Setup preserves project docs, instructions and customizations; it starts no task agent,
installs no provider, copies no credentials, and does not upgrade an existing installation.

The assets are okms-hybrid-team-{version}.tar.gz, install.sh, and SHA256SUMS.
The archive contains the complete profile, both licenses, and a hashed file manifest.
The installer verifies the archive and manifest before preserving setup.

## Native activation and evidence

Review Codex hook trust through /hooks and Claude Code project settings. Installed
configuration alone does not prove automatic startup or role/skill activation.
Repository checks use fake transports; native behavior requires separate observations.
The retained pilot report records the versions tested, failures, and scoped limits.
Desktop/IDE/remote sessions remain outside the current profile's scope.

Read the [setup guide]({base}/blob/{tag}/README.md) and
[observed report]({base}/blob/{tag}/evals/hybrid-report.md).
"""


def build(output, root=ROOT, *, tag=None, notes=None):
    source = root / "templates/hybrid-team"
    version = validate_tag(tag, root)
    installer = (root / "install.sh").read_bytes()
    assets = {"setup.py": (source / "setup.py").read_bytes()}
    extensions = {"docs": {".md"}, "runtime": {".py"}, "native": {".md", ".toml"}, "skills": {".md"}}
    for directory, suffixes in extensions.items():
        for path in sorted((source / directory).rglob("*")):
            if "__pycache__" in path.parts:
                continue
            if path.is_symlink():
                raise ValueError("Release payload must not contain symlinks: " + str(path))
            if path.is_file() and path.suffix in suffixes:
                assets[path.relative_to(source).as_posix()] = path.read_bytes()
    for name in ("LICENSE-MIT", "LICENSE-APACHE"):
        assets[name] = (root / name).read_bytes()
    manifest = {"schema_version": 1, "profile": "hybrid-team", "version": version,
                "tag": "hybrid-team-v" + version,
                "files": {name: hashlib.sha256(body).hexdigest() for name, body in sorted(assets.items())}}
    assets["release.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    prefix = "okms-hybrid-team-" + version
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
            for name, body in sorted(assets.items()):
                member = tarfile.TarInfo(prefix + "/" + name)
                member.size = len(body)
                member.mode = 0o644
                member.mtime = 0
                archive.addfile(member, io.BytesIO(body))
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    products = {prefix + ".tar.gz": buffer.getvalue(), "install.sh": installer}
    products["SHA256SUMS"] = "".join(hashlib.sha256(body).hexdigest() + "  " + name + "\n"
                                    for name, body in sorted(products.items())).encode()
    for name, body in products.items():
        path = output / name
        path.write_bytes(body)
        path.chmod(0o755 if name == "install.sh" else 0o644)
    if notes is not None:
        notes = Path(notes)
        notes.parent.mkdir(parents=True, exist_ok=True)
        notes.write_text(release_notes(version), encoding="utf-8")
    return {"profile": "hybrid-team", "version": version, "tag": manifest["tag"],
            "archive": prefix + ".tar.gz", "payload_files": len(manifest["files"]), "assets": sorted(products)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist", help="Release asset directory (default: dist/)")
    parser.add_argument("--tag", help="Validate the pushed tag against the committed runtime version")
    parser.add_argument("--notes", type=Path, help="Write versioned release notes for publication")
    parser.add_argument("--validate-only", action="store_true", help="Check the source version/tag without writing assets")
    args = parser.parse_args()
    try:
        if args.validate_only:
            version = validate_tag(args.tag)
            result = {"profile": "hybrid-team", "version": version, "tag": "hybrid-team-v" + version}
        else:
            result = build(args.output, tag=args.tag, notes=args.notes)
        print(json.dumps(result, indent=2))
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
