"""Immutable Python v0.1.0 fixture; never part of the Rust distribution."""

import hashlib
import shutil
import tarfile
import tempfile
from pathlib import Path

ARCHIVE = Path(__file__).resolve().parent / "fixtures/hybrid-python-0.1.0.tar.gz"
SHA256 = "0fd9a27a172ad83226df7fca437e299c34aab07ae1fc3af06a45c4a12acb121e"
TEMPORARY = tempfile.TemporaryDirectory(prefix="okms-python-baseline-")
SOURCE = Path(TEMPORARY.name) / "okms-hybrid-team-0.1.0"
if hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() != SHA256:
    raise ValueError("Historical fixture differs from the published Python release.")
with tarfile.open(ARCHIVE, "r:gz") as archive:
    for member in archive.getmembers():
        if not member.isfile() or not member.name.startswith("okms-hybrid-team-0.1.0/") or ".." in Path(member.name).parts:
            raise ValueError("Invalid historical fixture member.")
        target = Path(TEMPORARY.name) / member.name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(archive.extractfile(member).read())
ROOT = Path(TEMPORARY.name) / "builder-root"
shutil.copytree(SOURCE, ROOT / "templates/hybrid-team")
for name in ("LICENSE-MIT", "LICENSE-APACHE"):
    shutil.copyfile(SOURCE / name, ROOT / name)
shutil.copyfile(ARCHIVE.with_name("hybrid-python-latest-install.sh"), ROOT / "install.sh")
