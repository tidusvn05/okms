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
from hybrid_legacy import SOURCE as LEGACY_SOURCE
SPEC = importlib.util.spec_from_file_location("hybrid_release", ROOT / "tests/fixtures/build_hybrid_python_release.py")
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)
ARCHIVE = "okms-hybrid-team-0.1.0.tar.gz"
PREFIX = ARCHIVE.removesuffix(".tar.gz")


def files(directory):
    return {path.relative_to(directory).as_posix(): path.read_bytes()
            for path in directory.rglob("*") if path.is_file()}


def published(version="0.1.0", **fields):
    return {"tag_name": "hybrid-team-v" + version, "draft": False, "prerelease": True,
            "assets": [{"name": name, "state": "uploaded"} for name in
                       ("install.sh", "SHA256SUMS", "okms-hybrid-team-" + version + ".tar.gz")],
            **fields}


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

    def install(self, *args, online=False, env=None, version="0.1.0"):
        argv = ["sh", str(self.assets / "install.sh"), "--project", str(self.project), *args]
        if version is not None:
            argv.extend(["--version", version])
        if not online:
            argv.extend(["--release-dir", str(self.assets)])
        return subprocess.run(argv, capture_output=True, text=True, cwd=self.project, env=env or self.env)

    def download_env(self, pages=None):
        binary = self.directory / "bin"
        binary.mkdir(exist_ok=True)
        listing = self.directory / "listing"
        listing.mkdir(exist_ok=True)
        for page, body in enumerate(pages or [], 1):
            (listing / (str(page) + ".json")).write_text(body if isinstance(body, str) else json.dumps(body))
        curl = binary / "curl"
        curl.write_text("""#!/usr/bin/env python3
import json, os, pathlib, shutil, sys, urllib.parse
args = sys.argv[1:]
with open(os.environ["OKMS_TEST_REQUESTS"], "a") as stream:
    stream.write(json.dumps(args) + "\\n")
if os.environ.get("OKMS_TEST_DOWNLOAD_FAIL"):
    sys.exit(22)
url = urllib.parse.urlparse(args[-1])
if url.netloc == "api.github.com":
    page = urllib.parse.parse_qs(url.query)["page"][0]
    source = pathlib.Path(os.environ["OKMS_TEST_LISTING"]) / (page + ".json")
else:
    source = pathlib.Path(os.environ["OKMS_TEST_ASSETS"]) / url.path.split("/")[-1]
shutil.copyfile(source, args[args.index("--output") + 1])
""")
        curl.chmod(0o755)
        return {**self.env, "PATH": str(binary) + os.pathsep + os.environ["PATH"],
                "OKMS_TEST_ASSETS": str(self.assets), "OKMS_TEST_LISTING": str(listing),
                "OKMS_TEST_REQUESTS": str(self.directory / "requests.jsonl")}

    def requests(self):
        path = self.directory / "requests.jsonl"
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

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
        expected = {path.relative_to(LEGACY_SOURCE).as_posix()
                    for path in LEGACY_SOURCE.rglob("*")
                    if path.is_file() and path.suffix in {".py", ".md", ".toml"} and "__pycache__" not in path.parts}
        self.assertEqual(set(bodies), expected | {"LICENSE-MIT", "LICENSE-APACHE"})
        self.assertEqual(manifest["files"], {name: hashlib.sha256(body).hexdigest() for name, body in bodies.items()})
        self.assertEqual(manifest["version"], "0.1.0")
        self.assertEqual(manifest["tag"], "hybrid-team-v0.1.0")

    def test_tag_mismatch_writes_no_assets_and_valid_tag_generates_pinned_notes(self):
        output = self.directory / "tagged"
        notes = self.directory / "release-notes.md"
        for tag in ("v0.1.0", "hybrid-team-v0.2.0", "hybrid-team-v0.1.0-rc.1", "$(invalid)"):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                release.build(output, tag=tag, notes=notes)
            self.assertFalse(output.exists())
            self.assertFalse(notes.exists())
        result = release.build(output, tag="hybrid-team-v0.1.0", notes=notes)
        self.assertEqual(result["tag"], "hybrid-team-v0.1.0")
        self.assertEqual(result["archive"], ARCHIVE)
        self.assertIn("--version 0.1.0 --project .", notes.read_text())
        self.assertIn("/releases/download/hybrid-team-v0.1.0/install.sh", notes.read_text())
        self.assertIn("fake transports", notes.read_text())

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
        env = self.download_env()
        result = self.install("--dry-run", online=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(files(self.project), {})
        argv = self.requests()
        self.assertEqual([args[-1] for args in argv], [
            "https://github.com/tidusvn05/okms/releases/download/hybrid-team-v0.1.0/SHA256SUMS",
            "https://github.com/tidusvn05/okms/releases/download/hybrid-team-v0.1.0/" + ARCHIVE])
        self.assertTrue(all("--fail" in args and "--proto-redir" in args for args in argv))
        result = self.install(online=True, env={**env, "OKMS_TEST_DOWNLOAD_FAIL": "1"})
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(files(self.project), {})
        self.assertFalse(list(self.directory.glob("okms-hybrid-install-*")))

    def test_latest_includes_complete_prereleases_and_skips_other_candidates(self):
        pending = published("0.4.0")
        pending["assets"][0]["state"] = "starter"
        env = self.download_env([[published(), published("0.0.9", prerelease=False),
                                  published("9.0.0", draft=True),
                                  published("8.0.0", tag_name="portable-v8.0.0"),
                                  published("0.2.0", assets=[]),
                                  published("0.3.0", tag_name="hybrid-team-v0.3.0-rc.1"), pending]])
        result = self.install("--dry-run", online=True, env=env, version=None)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Verified Hybrid Team 0.1.0", result.stderr)
        self.assertEqual(files(self.project), {})
        self.assertEqual([args[-1] for args in self.requests()], [
            "https://api.github.com/repos/tidusvn05/okms/releases?per_page=100&page=1",
            "https://github.com/tidusvn05/okms/releases/download/hybrid-team-v0.1.0/SHA256SUMS",
            "https://github.com/tidusvn05/okms/releases/download/hybrid-team-v0.1.0/" + ARCHIVE])

    def test_latest_reads_later_pages_before_selecting(self):
        env = self.download_env([[published("0.0.9")] * 100, [published()]])
        result = self.install("--dry-run", online=True, env=env, version="latest")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([args[-1] for args in self.requests()][:2], [
            "https://api.github.com/repos/tidusvn05/okms/releases?per_page=100&page=1",
            "https://api.github.com/repos/tidusvn05/okms/releases?per_page=100&page=2"])
        self.assertIn("/hybrid-team-v0.1.0/", self.requests()[-1][-1])

    def test_latest_compares_numeric_versions_instead_of_listing_order(self):
        for lower, higher in (("0.9.9", "0.10.0"), ("0.99.99", "1.0.0"), ("1.0.9", "1.0.10")):
            with self.subTest(lower=lower, higher=higher):
                env = self.download_env([[published(higher), published(lower)]])
                result = self.install("--dry-run", online=True, env=env, version=None)
                # The fixture intentionally has no future bundle. Selection must request
                # the numerically highest version, then fail without touching the project.
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.requests()[-1][-1],
                                 "https://github.com/tidusvn05/okms/releases/download/hybrid-team-v" +
                                 higher + "/SHA256SUMS")
                self.assertEqual(files(self.project), {})

    def test_offline_default_resolves_local_assets_without_network(self):
        env = {**self.download_env(), "OKMS_TEST_DOWNLOAD_FAIL": "1"}
        result = self.install("--dry-run", env=env, version=None)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Verified Hybrid Team 0.1.0", result.stderr)
        self.assertEqual(self.requests(), [])
        self.assertEqual(files(self.project), {})
        (self.assets / "SHA256SUMS").unlink()
        result = self.install(env=env, version=None)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("No complete", result.stderr)
        self.assertEqual(self.requests(), [])
        self.assertEqual(files(self.project), {})

    def test_failed_or_invalid_discovery_stops_before_project_mutation(self):
        self.write("notes.txt", "Preserve.\n")
        before = files(self.project)
        for body in ([], {"message": "API error"}, "not JSON", [None],
                     [published(draft=True)], [published(assets=[])]):
            with self.subTest(body=body):
                env = self.download_env([body])
                result = self.install(online=True, env=env, version=None)
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(self.requests()[-1][-1].startswith("https://api.github.com/"))
                self.assertEqual(files(self.project), before)
                self.assertFalse(list(self.directory.glob("okms-hybrid-install-*")))
        env = {**env, "OKMS_TEST_DOWNLOAD_FAIL": "1"}
        result = self.install(online=True, env=env, version=None)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(files(self.project), before)
        self.assertFalse(list(self.directory.glob("okms-hybrid-install-*")))


if __name__ == "__main__":
    unittest.main()
