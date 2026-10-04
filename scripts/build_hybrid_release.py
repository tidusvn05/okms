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

ROOT = Path(__file__).resolve().parents[1]


def build(output, root=ROOT):
    source = root / "templates/hybrid-team"
    module = ast.parse((source / "runtime/okms_team/__init__.py").read_text())
    version = next(ast.literal_eval(node.value) for node in module.body if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == "VERSION" for target in node.targets))
    if not isinstance(version, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
        raise ValueError("Hybrid Team VERSION must be major.minor.patch.")
    installer = (root / "install.sh").read_bytes()
    if ('default="' + version + '"').encode() not in installer:
        raise ValueError("Installer default version must match the distributed runtime.")
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
    return {"profile": "hybrid-team", "version": version, "tag": manifest["tag"],
            "payload_files": len(manifest["files"]), "assets": sorted(products)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist", help="Release asset directory (default: dist/)")
    args = parser.parse_args()
    print(json.dumps(build(args.output), indent=2))


if __name__ == "__main__":
    main()
