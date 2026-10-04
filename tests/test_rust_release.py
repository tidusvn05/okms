"""Exercise real Rust distribution assets; no provider task session starts."""

import hashlib
import importlib.util
import io
import json
import os
import shlex
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BINARY = Path(os.environ.get("OKMS_TEST_BINARY", ROOT / "target/debug/okms")).resolve()
TARGET = "x86_64-unknown-linux-musl"
SPEC = importlib.util.spec_from_file_location("rust_release", ROOT / "scripts/build_hybrid_release.py")
RELEASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RELEASE)


def files(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


class RustReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shared = tempfile.TemporaryDirectory(prefix="okms-rust-assets-")
        cls.addClassCleanup(cls.shared.cleanup)
        cls.assets = Path(cls.shared.name) / "assets"
        cls.metadata = RELEASE.build(cls.assets, BINARY, TARGET)

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="okms-rust-install-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.project = self.directory / "project $ literal space"
        self.project.mkdir()
        self.bin_dir = self.directory / "bin space"
        self.release = self.directory / "assets"
        shutil.copytree(self.assets, self.release)

    def call(self, *args, expected=0, env=None, online=False):
        argv = ["sh", str(ROOT / "install.sh"), "--bin-dir", str(self.bin_dir), *args]
        if not online:
            argv += ["--release-dir", str(self.release)]
        result = subprocess.run(argv, capture_output=True, text=True, env=env, timeout=60)
        if expected == 0:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def rewrite_archive(self, members):
        path = self.release / self.metadata["archive"]
        with tarfile.open(path, "w:gz") as archive:
            for name, kind in members:
                member = tarfile.TarInfo(name)
                member.type = kind
                body = b"payload"
                if kind == tarfile.REGTYPE:
                    member.size = len(body)
                else:
                    member.linkname = "../outside"
                archive.addfile(member, io.BytesIO(body) if kind == tarfile.REGTYPE else None)
        self.hashes()

    def hashes(self):
        text = "".join(hashlib.sha256(path.read_bytes()).hexdigest() + "  " + path.name + "\n"
                       for path in sorted(self.release.glob("*")) if path.name != "SHA256SUMS")
        (self.release / "SHA256SUMS").write_text(text)

    def test_deterministic_archive_members_licenses_and_numeric_tags(self):
        other = self.directory / "other"
        metadata = RELEASE.build(other, BINARY, TARGET, tag="hybrid-team-v0.2.0")
        self.assertEqual(files(self.assets), files(other))
        with tarfile.open(other / metadata["archive"]) as archive:
            self.assertEqual(sorted(archive.getnames()), ["LICENSE-APACHE", "LICENSE-MIT", "okms"])
            self.assertEqual(archive.getmember("okms").mode, 0o755)
            self.assertEqual(archive.extractfile("okms").read(), BINARY.read_bytes())
            for name in ("LICENSE-MIT", "LICENSE-APACHE"):
                self.assertEqual(archive.extractfile(name).read(), (ROOT / name).read_bytes())
        rejected = self.directory / "rejected"
        with self.assertRaises(ValueError):
            RELEASE.build(rejected, BINARY, TARGET, tag="hybrid-team-v0.9.0")
        self.assertFalse(rejected.exists())
        with self.assertRaises(FileNotFoundError):
            RELEASE.assemble(rejected)

    def test_python_free_dry_global_project_repeat_and_source_removal(self):
        native_path = self.directory / "native-path"
        native_path.mkdir()
        for program in ("sh", "awk", "uname", "tar", "gzip", "sha256sum", "mktemp", "rm", "cp",
                        "wc", "mkdir", "chmod", "mv", "cat", "git"):
            (native_path / program).symlink_to(shutil.which(program))
        env = {**os.environ, "PATH": str(native_path)}
        self.call("--project", str(self.project), "--dry-run", env=env)
        self.assertEqual(files(self.project), {})
        self.assertFalse(self.bin_dir.exists())
        self.call(env=env)
        self.assertEqual(files(self.project), {})
        binary = self.bin_dir / "okms"
        self.assertEqual(subprocess.check_output([str(binary), "--version"], env=env, text=True).strip(), "okms 0.2.0")
        self.call("--project", str(self.project), env=env)
        before = files(self.project)
        self.call("--project", str(self.project), env=env)
        self.assertEqual(files(self.project), before)
        shutil.rmtree(self.release)
        result = subprocess.run([str(self.project / ".okms/okms"), "join", "--project", str(self.project),
                                 "--provider", "codex", "--input-json", '{"session_id":"installed-native"}'],
                                env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["role"], "coordinator")

    def test_dirty_head_index_documents_and_customizations_survive(self):
        subprocess.run(["git", "init", "-q"], cwd=self.project, check=True)
        (self.project / "keep.txt").write_text("Original.\n")
        subprocess.run(["git", "add", "."], cwd=self.project, check=True)
        subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                        "commit", "-qm", "Fixture"], cwd=self.project, check=True)
        (self.project / "keep.txt").write_text("Staged.\n")
        subprocess.run(["git", "add", "keep.txt"], cwd=self.project, check=True)
        (self.project / "keep.txt").write_text("Unstaged.\n")
        (self.project / "notes.txt").write_text("Untracked.\n")
        (self.project / "docs").mkdir()
        (self.project / "docs/existing.md").write_text("Existing docs.\n")
        index = (self.project / ".git/index").read_bytes()
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.project)
        self.call("--project", str(self.project))
        self.assertEqual((self.project / ".git/index").read_bytes(), index)
        self.assertEqual(subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.project), head)
        self.assertEqual((self.project / "docs/existing.md").read_text(), "Existing docs.\n")
        self.assertEqual((self.project / "keep.txt").read_text(), "Unstaged.\n")
        (self.project / "docs/okms/context.md").write_text("User context.\n")
        before = files(self.project)
        self.call("--project", str(self.project))
        self.assertEqual(files(self.project), before)

    def test_corrupt_missing_duplicate_checksum_and_pin_fail_before_writes(self):
        original = files(self.release)
        archive = self.release / self.metadata["archive"]
        for variation in ("corrupt", "missing", "duplicate", "bad_pin"):
            with self.subTest(variation=variation):
                for name, body in original.items():
                    (self.release / name).write_bytes(body)
                if variation == "corrupt":
                    archive.write_bytes(archive.read_bytes() + b"bad")
                elif variation == "missing":
                    (self.release / "SHA256SUMS").write_text("")
                elif variation == "duplicate":
                    sums = self.release / "SHA256SUMS"
                    sums.write_text(sums.read_text() * 2)
                args = ["--project", str(self.project)]
                if variation == "bad_pin":
                    args += ["--version", "0.8.0"]
                self.call(*args, expected=1)
                self.assertEqual(files(self.project), {})
                self.assertFalse(self.bin_dir.exists())

    def test_unsafe_links_duplicate_and_missing_members_fail_before_writes(self):
        valid = [("okms", tarfile.REGTYPE), ("LICENSE-MIT", tarfile.REGTYPE),
                 ("LICENSE-APACHE", tarfile.REGTYPE)]
        cases = [valid + [("../outside", tarfile.REGTYPE)],
                 [("okms", tarfile.SYMTYPE), *valid[1:]],
                 [("okms", tarfile.LNKTYPE), *valid[1:]],
                 [*valid, valid[0]], valid[1:]]
        for members in cases:
            with self.subTest(members=members):
                self.rewrite_archive(members)
                self.call("--project", str(self.project), expected=1)
                self.assertEqual(files(self.project), {})
                self.assertFalse(self.bin_dir.exists())
                self.assertFalse((self.directory / "outside").exists())

    def test_preflight_conflicts_and_legacy_upgrade_preserve_project_and_cli(self):
        (self.project / ".okms").mkdir()
        for name, content in [("okms", "Unmanaged runtime.\n"),
                              ("install.json", '{"profile":"hybrid-team","version":"0.1.0","docs_path":"docs"}')]:
            with self.subTest(name=name):
                path = self.project / ".okms" / name
                path.write_text(content)
                before = files(self.project)
                self.call("--project", str(self.project), expected=1)
                self.assertEqual(files(self.project), before)
                self.assertFalse(self.bin_dir.exists())
                path.unlink()

    def test_online_latest_and_exact_pins_use_only_selected_asset_urls(self):
        fake_bin = self.directory / "fake-bin"
        fake_bin.mkdir()
        log = self.directory / "urls.txt"
        script = "#!/bin/sh\nurl=\noutput=\nwhile [ \"$#\" -gt 0 ]; do\n" \
                 "case \"$1\" in https://*) url=$1 ;; --output) shift; output=$1 ;; esac\nshift\ndone\n" \
                 "printf '%s\\n' \"$url\" >> " + shlex.quote(str(log)) + "\n" \
                 "asset=${url##*/}\ncp " + shlex.quote(str(self.release)) + "/\"$asset\" \"$output\"\n"
        curl = fake_bin / "curl"
        curl.write_text(script)
        curl.chmod(0o755)
        env = {**os.environ, "PATH": str(fake_bin) + os.pathsep + os.environ["PATH"]}
        self.call("--dry-run", online=True, env=env)
        urls = log.read_text().splitlines()
        self.assertEqual(urls, ["https://github.com/tidusvn05/okms/releases/latest/download/" + name
                               for name in ("SHA256SUMS", self.metadata["archive"])])
        log.unlink()
        self.call("--dry-run", "--version", "0.2.0", online=True, env=env)
        self.assertTrue(all("/releases/download/hybrid-team-v0.2.0/" in url for url in log.read_text().splitlines()))
        self.assertFalse(self.bin_dir.exists())
        curl.write_text("#!/bin/sh\nexit 22\n")
        self.call("--project", str(self.project), online=True, env=env, expected=1)
        self.assertEqual(files(self.project), {})
        self.assertFalse(self.bin_dir.exists())


if __name__ == "__main__":
    unittest.main()
