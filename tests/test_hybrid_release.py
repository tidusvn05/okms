"""Distribution boundary checks with real setup and a fake download transport."""

import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("hybrid_release", ROOT / "scripts/build_hybrid_release.py")
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)
ARCHIVE = "okms-hybrid-team-0.1.0.tar.gz"
PREFIX = ARCHIVE.removesuffix(".tar.gz")


def files(directory):
    return {path.relative_to(directory).as_posix(): path.read_bytes()
            for path in directory.rglob("*") if path.is_file()}


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="okms-release-test-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.project = self.directory / "project $ literal space"
        self.project.mkdir()
        self.assets = self.directory / "release assets"
        release.build(self.assets)
        self.env = {**os.environ, "TMPDIR": str(self.directory), "PYTHONDONTWRITEBYTECODE": "1"}

    def install(self, *args, online=False, env=None):
        argv = ["sh", str(self.assets / "install.sh"), "--project", str(self.project), *args]
        if not online:
            argv.extend(["--release-dir", str(self.assets)])
        return subprocess.run(argv, capture_output=True, text=True, cwd=self.project, env=env or self.env)

    def write(self, name, body):
        path = self.project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)

    def checksums(self):
        (self.assets / "SHA256SUMS").write_text(
            hashlib.sha256((self.assets / ARCHIVE).read_bytes()).hexdigest() + "  " + ARCHIVE + "\n")

    def rewrite_archive(self, transform):
        with tarfile.open(self.assets / ARCHIVE, "r:gz") as source:
            members = [(member, source.extractfile(member).read()) for member in source.getmembers()]
        with tarfile.open(self.assets / ARCHIVE, "w:gz") as target:
            for member, body in members:
                body = transform(member.name, body)
                member.size = len(body)
                target.addfile(member, io.BytesIO(body))
        self.checksums()

    def test_reproducible_archive_has_complete_payload_licenses_and_manifest(self):
        again = self.directory / "second"
        release.build(again)
        self.assertEqual(files(self.assets), files(again))
        with tarfile.open(self.assets / ARCHIVE, "r:gz") as archive:
            bodies = {member.name.removeprefix(PREFIX + "/"): archive.extractfile(member).read()
                      for member in archive.getmembers()}
        manifest = json.loads(bodies.pop("release.json"))
        expected = {path.relative_to(ROOT / "templates/hybrid-team").as_posix()
                    for path in (ROOT / "templates/hybrid-team").rglob("*")
                    if path.is_file() and path.suffix in {".py", ".md", ".toml"} and "__pycache__" not in path.parts}
        self.assertEqual(set(bodies), expected | {"LICENSE-MIT", "LICENSE-APACHE"})
        self.assertEqual(manifest["files"], {name: hashlib.sha256(body).hexdigest() for name, body in bodies.items()})
        self.assertEqual(manifest["version"], "0.1.0")
        self.assertEqual(manifest["tag"], "hybrid-team-v0.1.0")

    def test_dry_run_new_setup_and_source_independent_helper(self):
        self.write("notes.txt", "User note.\n")
        before = files(self.project)
        dry = self.install("--dry-run", "--docs", "team docs")
        self.assertEqual(dry.returncode, 0, dry.stderr)
        self.assertTrue(json.loads(dry.stdout)["dry_run"])
        self.assertEqual(files(self.project), before)
        self.assertFalse(list(self.directory.glob("okms-hybrid-install-*")))
        installed = self.install("--docs", "team docs")
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertEqual(json.loads(installed.stdout)["docs_path"], "team docs")
        shutil.rmtree(self.assets)
        joined = subprocess.run([sys.executable, ".okms/team.py", "join", "--provider", "codex",
                                 "--input-json", '{"session_id":"release-test-root"}'],
                                cwd=self.project, env=self.env, capture_output=True, text=True)
        self.assertEqual(joined.returncode, 0, joined.stdout + joined.stderr)
        identity = json.loads(joined.stdout)["identity_file"]
        status = subprocess.run([sys.executable, ".okms/team.py", "status", "--identity", identity],
                                cwd=self.project, env=self.env, capture_output=True, text=True)
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertEqual(len(json.loads(status.stdout)["agents"]), 1)
        self.assertEqual((self.project / "notes.txt").read_text(), "User note.\n")
        self.assertFalse(list(self.directory.glob("okms-hybrid-install-*")))

    def test_existing_dirty_project_and_repeated_customizations_are_preserved(self):
        self.write("keep.txt", "Baseline.\n")
        self.write("docs/workflow.md", "Existing portable workflow.\n")
        self.write("AGENTS.md", "Keep user instructions.\n")
        subprocess.run(["git", "init", "-q"], cwd=self.project, check=True)
        subprocess.run(["git", "add", "."], cwd=self.project, check=True)
        subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                        "commit", "-qm", "Baseline"], cwd=self.project, check=True)
        self.write("keep.txt", "Staged note.\n")
        subprocess.run(["git", "add", "keep.txt"], cwd=self.project, check=True)
        self.write("keep.txt", "Unstaged note.\n")
        self.write("notes.txt", "Untracked note.\n")
        index = (self.project / ".git/index").read_bytes()
        head = (self.project / ".git/refs/heads").rglob("*")
        refs = {path.name: path.read_bytes() for path in head if path.is_file()}
        installed = self.install()
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertEqual(json.loads(installed.stdout)["docs_path"], "docs/okms")
        self.assertEqual((self.project / "docs/workflow.md").read_text(), "Existing portable workflow.\n")
        self.assertTrue((self.project / "AGENTS.md").read_text().startswith("Keep user instructions.\n"))
        self.assertEqual((self.project / ".git/index").read_bytes(), index)
        self.assertEqual({path.name: path.read_bytes() for path in (self.project / ".git/refs/heads").rglob("*")
                          if path.is_file()}, refs)
        self.assertEqual((self.project / "keep.txt").read_text(), "Unstaged note.\n")
        self.write("docs/okms/context.md", "Project-owned context.\n")
        self.write(".okms/okms_team/worker.py", "# Deliberate project customization.\n")
        config = json.loads((self.project / ".okms/team.json").read_text())
        config["checks"] = [["python3", "project_check.py"]]
        self.write(".okms/team.json", json.dumps(config))
        before = files(self.project)
        repeated = self.install()
        self.assertEqual(repeated.returncode, 0, repeated.stderr)
        self.assertEqual(json.loads(repeated.stdout)["changed"], [])
        self.assertEqual(files(self.project), before)

    def test_corrupt_or_missing_checksums_fail_before_project_mutation(self):
        self.write("notes.txt", "Preserve.\n")
        before = files(self.project)
        with (self.assets / ARCHIVE).open("ab") as archive:
            archive.write(b"Changed distribution bytes")
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("checksum mismatch", result.stderr)
        self.assertEqual(files(self.project), before)
        (self.assets / "SHA256SUMS").write_text("0" * 64 + "  wrong.tar.gz\n")
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no entry", result.stderr)
        self.assertEqual(files(self.project), before)

    def test_manifest_fingerprints_and_version_reject_inconsistent_payloads(self):
        before = files(self.project)
        self.rewrite_archive(lambda name, body: body + b"\n# Inconsistent source\n" if name.endswith("/setup.py") else body)
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Payload fingerprint mismatch", result.stderr)
        self.assertEqual(files(self.project), before)
        release.build(self.assets)
        def wrong_version(name, body):
            if name.endswith("/release.json"):
                manifest = json.loads(body)
                manifest["version"] = "0.2.0"
                return json.dumps(manifest).encode()
            return body
        self.rewrite_archive(wrong_version)
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requested profile/version", result.stderr)
        self.assertEqual(files(self.project), before)

    def test_traversal_links_and_duplicate_members_never_reach_setup(self):
        before = files(self.project)
        for case in ("traversal", "symlink", "duplicate"):
            with self.subTest(case=case):
                with tarfile.open(self.assets / ARCHIVE, "w:gz") as archive:
                    name = PREFIX + "/../../escape" if case == "traversal" else PREFIX + "/setup.py"
                    member = tarfile.TarInfo(name)
                    if case == "symlink":
                        member.type, member.linkname = tarfile.SYMTYPE, "../escape"
                    archive.addfile(member, io.BytesIO(b""))
                    if case == "duplicate":
                        archive.addfile(member, io.BytesIO(b""))
                self.checksums()
                result = self.install()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Unsafe or duplicate", result.stderr)
                self.assertEqual(files(self.project), before)
                self.assertFalse((self.directory / "escape").exists())
                self.assertFalse(list(self.directory.glob("okms-hybrid-install-*")))

    def test_downloads_use_pinned_release_and_transport_failure_preserves_project(self):
        binary = self.directory / "bin"
        binary.mkdir()
        curl = binary / "curl"
        curl.write_text("""#!/usr/bin/env python3
import json, os, pathlib, shutil, sys
args = sys.argv[1:]
with open(os.environ["OKMS_TEST_REQUESTS"], "a") as stream:
    stream.write(json.dumps(args) + "\\n")
if os.environ.get("OKMS_TEST_DOWNLOAD_FAIL"):
    sys.exit(22)
shutil.copyfile(pathlib.Path(os.environ["OKMS_TEST_ASSETS"]) / args[-1].split("/")[-1],
                args[args.index("--output") + 1])
""")
        curl.chmod(0o755)
        requests = self.directory / "requests.jsonl"
        env = {**self.env, "PATH": str(binary) + os.pathsep + os.environ["PATH"],
               "OKMS_TEST_ASSETS": str(self.assets), "OKMS_TEST_REQUESTS": str(requests)}
        result = self.install("--dry-run", online=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(files(self.project), {})
        argv = [json.loads(line) for line in requests.read_text().splitlines()]
        self.assertEqual([args[-1] for args in argv], [
            "https://github.com/tidusvn05/okms/releases/download/hybrid-team-v0.1.0/SHA256SUMS",
            "https://github.com/tidusvn05/okms/releases/download/hybrid-team-v0.1.0/" + ARCHIVE])
        self.assertTrue(all("--fail" in args and "--proto-redir" in args for args in argv))
        result = self.install(online=True, env={**env, "OKMS_TEST_DOWNLOAD_FAIL": "1"})
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(files(self.project), {})
        self.assertFalse(list(self.directory.glob("okms-hybrid-install-*")))


if __name__ == "__main__":
    unittest.main()
