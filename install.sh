#!/bin/sh
# Explicit Hybrid Team adoption from published assets; no global CLI installation.
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


def download(url, destination):
    if not shutil.which("curl"):
        raise ValueError("curl is required to download release assets.")
    subprocess.run(["curl", "--fail", "--location", "--silent", "--show-error",
                    "--proto", "=https", "--proto-redir", "=https", "--retry", "2",
                    "--connect-timeout", "15", "--max-time", "180",
                    "--output", str(destination), url], check=True)


def fetch(name, destination, release_dir, base):
    if release_dir:
        shutil.copyfile(release_dir / name, destination)
    else:
        download(base + "/" + name, destination)


def latest_version(release_dir, directory):
    candidates = []
    if release_dir:
        if (release_dir / "install.sh").is_file() and (release_dir / "SHA256SUMS").is_file():
            for path in release_dir.glob("okms-hybrid-team-*.tar.gz"):
                match = re.fullmatch(r"okms-hybrid-team-([0-9]+\.[0-9]+\.[0-9]+)\.tar\.gz", path.name)
                if match and path.is_file():
                    candidates.append(match[1])
    else:
        page = 1
        while True:
            response = directory / "releases.json"
            download("https://api.github.com/repos/tidusvn05/okms/releases?per_page=100&page=" + str(page), response)
            releases = json.loads(response.read_text())
            if not isinstance(releases, list) or any(not isinstance(item, dict) for item in releases):
                raise ValueError("Invalid GitHub release listing.")
            for release in releases:
                tag = release.get("tag_name")
                match = re.fullmatch(r"hybrid-team-v([0-9]+\.[0-9]+\.[0-9]+)", tag) if isinstance(tag, str) else None
                assets = release.get("assets")
                if not match or release.get("draft") is not False or not isinstance(assets, list):
                    continue
                uploaded = {asset.get("name") for asset in assets
                            if isinstance(asset, dict) and asset.get("state") == "uploaded" and
                            isinstance(asset.get("name"), str)}
                required = {"install.sh", "SHA256SUMS", "okms-hybrid-team-" + match[1] + ".tar.gz"}
                if required <= uploaded:
                    candidates.append(match[1])
            if len(releases) < 100:
                break
            page += 1
    if not candidates:
        raise ValueError("No complete published Hybrid Team release found; use --version or --release-dir explicitly.")
    return max(candidates, key=lambda version: (tuple(int(part) for part in version.split(".")), version))


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
    parser.add_argument("--version", default="latest", help="Numeric version or latest complete release, including prereleases (default: latest)")
    parser.add_argument("--project", type=Path, default=Path.cwd(), help="Existing destination project (default: current directory)")
    parser.add_argument("--docs", help="Explicit new/Hybrid Team documentation directory")
    parser.add_argument("--dry-run", action="store_true", help="Verify assets and report setup without project changes")
    parser.add_argument("--release-dir", type=Path, help="Use local release assets instead of downloading")
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        parser.error("Python 3.10+ is required.")
    if args.version != "latest" and not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", args.version):
        parser.error("--version must be latest or a numeric major.minor.patch version.")
    project = args.project.resolve()
    if not project.is_dir():
        parser.error("--project must be an existing directory.")
    release_dir = args.release_dir.resolve() if args.release_dir else None
    with tempfile.TemporaryDirectory(prefix="okms-hybrid-install-") as temporary:
        directory = Path(temporary)
        version = latest_version(release_dir, directory) if args.version == "latest" else args.version
        prefix = "okms-hybrid-team-" + version
        name = prefix + ".tar.gz"
        base = "https://github.com/tidusvn05/okms/releases/download/hybrid-team-v" + version
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
        source = unpack(archive, directory / "source", prefix, version)
        argv = [sys.executable, str(source / "setup.py"), "--project", str(project)]
        if args.docs is not None:
            argv.extend(["--docs", args.docs])
        if args.dry_run:
            argv.append("--dry-run")
        print("Verified Hybrid Team " + version + "; running preserving project setup.", file=sys.stderr)
        return subprocess.run(argv, check=False).returncode


try:
    sys.exit(main())
except (OSError, ValueError, tarfile.TarError, subprocess.SubprocessError) as error:
    print("Hybrid Team installation failed: " + str(error), file=sys.stderr)
    sys.exit(1)
PY
