#!/bin/sh
# Explicit Hybrid Team adoption from a pinned release; no global CLI installation.
set -eu
if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3.10+ is required for Hybrid Team setup." >&2
    exit 1
fi
exec python3 - "$@" <<'PY'
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path, PurePosixPath


def fetch(name, destination, release_dir, base):
    if release_dir:
        shutil.copyfile(release_dir / name, destination)
    else:
        if not shutil.which("curl"):
            raise ValueError("curl is required to download release assets.")
        subprocess.run(["curl", "--fail", "--location", "--silent", "--show-error",
                        "--proto", "=https", "--proto-redir", "=https", "--retry", "2",
                        "--connect-timeout", "15", "--max-time", "180",
                        "--output", str(destination), base + "/" + name], check=True)


def unpack(archive, destination, prefix, version):
    with tarfile.open(archive, "r:gz") as bundle:
        members = bundle.getmembers()
        if len(members) > 200 or sum(member.size for member in members) > 10 * 1024 * 1024:
            raise ValueError("Release archive exceeds the expected payload limits.")
        seen = set()
        for member in members:
            path = PurePosixPath(member.name)
            if (path.is_absolute() or "\\" in member.name or
                    any(part in {"", ".", ".."} for part in member.name.rstrip("/").split("/")) or
                    not path.parts or path.parts[0] != prefix or member.name in seen or
                    not (member.isfile() or member.isdir()) or member.issparse()):
                raise ValueError("Unsafe or duplicate archive member: " + member.name)
            seen.add(member.name)
        # Write regular bytes only; do not depend on version-specific tar extraction defaults.
        for member in members:
            target = destination.joinpath(*PurePosixPath(member.name).parts)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with bundle.extractfile(member) as source, target.open("wb") as output:
                    shutil.copyfileobj(source, output)
    source = destination / prefix
    manifest = json.loads((source / "release.json").read_text())
    if (not isinstance(manifest, dict) or manifest.get("schema_version") != 1 or
            manifest.get("profile") != "hybrid-team" or manifest.get("version") != version or
            manifest.get("tag") != "hybrid-team-v" + version or not isinstance(manifest.get("files"), dict)):
        raise ValueError("Release manifest does not match the requested profile/version.")
    actual = {path.relative_to(source).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in source.rglob("*") if path.is_file() and path != source / "release.json"}
    if actual != manifest["files"]:
        raise ValueError("Payload fingerprint mismatch; project setup was not started.")
    if not (source / "setup.py").is_file():
        raise ValueError("Release payload has no setup.py.")
    return source


def main():
    parser = argparse.ArgumentParser(description="Install the experimental Hybrid Team profile into a project.")
    parser.add_argument("--version", default="0.1.0", help="Pinned release version (default: 0.1.0)")
    parser.add_argument("--project", type=Path, default=Path.cwd(), help="Existing destination project (default: current directory)")
    parser.add_argument("--docs", help="Explicit new/Hybrid Team documentation directory")
    parser.add_argument("--dry-run", action="store_true", help="Verify assets and report setup without project changes")
    parser.add_argument("--release-dir", type=Path, help="Use local release assets instead of downloading")
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        parser.error("Python 3.10+ is required.")
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", args.version):
        parser.error("--version must be a numeric major.minor.patch version.")
    project = args.project.resolve()
    if not project.is_dir():
        parser.error("--project must be an existing directory.")
    release_dir = args.release_dir.resolve() if args.release_dir else None
    prefix = "okms-hybrid-team-" + args.version
    name = prefix + ".tar.gz"
    base = "https://github.com/tidusvn05/okms/releases/download/hybrid-team-v" + args.version
    with tempfile.TemporaryDirectory(prefix="okms-hybrid-install-") as temporary:
        directory = Path(temporary)
        sums, archive = directory / "SHA256SUMS", directory / name
        fetch("SHA256SUMS", sums, release_dir, base)
        entries = {}
        for line in sums.read_text().splitlines():
            match = re.fullmatch(r"([a-f0-9]{64})  ([A-Za-z0-9_.-]+)", line)
            if not match or match[2] in entries:
                raise ValueError("Invalid or duplicate release checksum entry.")
            entries[match[2]] = match[1]
        if name not in entries:
            raise ValueError("Release checksum file has no entry for " + name)
        fetch(name, archive, release_dir, base)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != entries[name]:
            raise ValueError("Release checksum mismatch; project setup was not started.")
        source = unpack(archive, directory / "source", prefix, args.version)
        argv = [sys.executable, str(source / "setup.py"), "--project", str(project)]
        if args.docs is not None:
            argv.extend(["--docs", args.docs])
        if args.dry_run:
            argv.append("--dry-run")
        print("Verified Hybrid Team " + args.version + "; running preserving project setup.", file=sys.stderr)
        return subprocess.run(argv, check=False).returncode


try:
    sys.exit(main())
except (OSError, ValueError, tarfile.TarError, subprocess.SubprocessError) as error:
    print("Hybrid Team installation failed: " + str(error), file=sys.stderr)
    sys.exit(1)
PY
