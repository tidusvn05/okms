"""Native embedded setup boundaries; no provider task session starts."""

import json
import os
import shutil
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BINARY = Path(os.environ.get("OKMS_TEST_BINARY", ROOT / "target/debug/okms")).resolve()


def files(project):
    return {p.relative_to(project).as_posix(): p.read_bytes() for p in project.rglob("*") if p.is_file()}


class RustAdoptionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="okms-rust-adoption-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.project = self.directory / "project $ literal space"
        self.project.mkdir()
        self.assertTrue(BINARY.is_file(), "Run cargo build before the Python maintainer tests.")

    def write(self, name, body):
        path = self.project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
        return path

    def call(self, *args, binary=BINARY, env=None, expected=0, input=None):
        result = subprocess.run([str(binary), *args, "--project", str(self.project)],
                                input=input, capture_output=True, text=True, env=env, timeout=45)
        if expected == 0:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_embedded_init_dry_run_repeat_and_customizations(self):
        self.write("notes.txt", "Preserve project notes.\n")
        before = files(self.project)
        preview = self.call("init", "--dry-run")
        self.assertTrue(preview["changed"])
        self.assertEqual(files(self.project), before)
        installed = self.call("init")
        self.assertEqual(installed["runtime"], "rust")
        self.assertEqual(installed["version"], "0.2.0")
        self.assertTrue(os.access(self.project / ".okms/okms", os.X_OK))
        self.assertFalse(list(self.project.rglob("*.py")))
        self.assertTrue((self.project / "docs/team-policy.md").is_file())
        with sqlite3.connect(self.project / ".okms/state/team.sqlite3") as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM agents").fetchone()[0], 0)
        snapshot = files(self.project)
        self.assertEqual(self.call("init")["changed"], [])
        self.assertEqual(files(self.project), snapshot)
        self.write("docs/context.md", "Project-owned context.\n")
        self.write(".okms/okms", "Project-owned runtime customization.\n")
        config = json.loads((self.project / ".okms/team.json").read_text())
        config["checks"] = [["git", "diff", "--check"]]
        self.write(".okms/team.json", json.dumps(config))
        snapshot = files(self.project)
        repeated = self.call("init")
        self.assertEqual(repeated["changed"], [])
        self.assertIn(".okms/okms", repeated["preserved_project_edits"])
        self.assertIn("docs/context.md", repeated["preserved_project_edits"])
        self.assertEqual(files(self.project), snapshot)

    def test_existing_docs_settings_roles_and_skills_survive(self):
        self.write("docs/workflow.md", "Existing portable workflow.\n")
        self.write("docs/work/P003/plan.md", "Active historical plan.\n")
        self.write("AGENTS.md", "Keep project instructions.\n")
        self.write("CLAUDE.md", "@AGENTS.md\nExisting Claude rules.\n")
        self.write(".codex/config.toml", 'model = "project-selected-model"\n')
        self.write(".codex/hooks.json", '{"hooks":{"SessionStart":[{"matcher":"startup","hooks":[{"type":"command","command":"project-hook"}]}]}}\n')
        self.write(".claude/settings.json", '{"permissions":{"deny":["Bash(secret-*)"]},"env":{"PROJECT_SETTING":"retained"}}\n')
        self.write(".claude/agents/okms-worker.md", "Existing project worker.\n")
        self.write(".agents/skills/okms-work/SKILL.md", "Existing project skill.\n")
        original = files(self.project)
        installed = self.call("init")
        self.assertEqual(installed["docs_path"], "docs/okms")
        self.assertEqual(installed["native_roles"]["claude_worker"], "okms-team-worker-2")
        for path in ("docs/workflow.md", "docs/work/P003/plan.md", ".codex/config.toml",
                     ".claude/agents/okms-worker.md", ".agents/skills/okms-work/SKILL.md"):
            self.assertEqual((self.project / path).read_bytes(), original[path])
        for path in ("AGENTS.md", "CLAUDE.md"):
            self.assertTrue((self.project / path).read_bytes().startswith(original[path]))
        settings = json.loads((self.project / ".claude/settings.json").read_text())
        self.assertEqual(settings["permissions"]["deny"], ["Bash(secret-*)"])
        self.assertEqual(settings["env"], {"PROJECT_SETTING": "retained"})
        hooks = json.loads((self.project / ".codex/hooks.json").read_text())["hooks"]["SessionStart"]
        self.assertEqual(hooks[0]["hooks"][0]["command"], "project-hook")
        self.assertIn("/.okms/okms", hooks[-1]["hooks"][0]["command"])
        snapshot = files(self.project)
        self.assertEqual(self.call("init")["changed"], [])
        self.assertEqual(files(self.project), snapshot)
        output = self.call("hook", "--provider", "claude", "--input-json",
                           '{"agent_type":"okms-team-worker-2","session_id":"native-helper"}')
        self.assertIn("native helper", output["hookSpecificOutput"]["additionalContext"])
        with sqlite3.connect(self.project / ".okms/state/team.sqlite3") as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM agents").fetchone()[0], 0)

    def test_copied_binary_and_hook_work_without_python_or_source(self):
        source = self.directory / "temporary-source"
        source.mkdir()
        copied = source / "okms"
        shutil.copy2(BINARY, copied)
        native_path = self.directory / "native-path"
        native_path.mkdir()
        for program in ("git", "sh"):
            (native_path / program).symlink_to(shutil.which(program))
        env = {**os.environ, "PATH": str(native_path)}
        self.call("init", "--docs", "team docs", binary=copied, env=env)
        shutil.rmtree(source)
        helper = self.project / ".okms/okms"
        joined = self.call("join", "--provider", "codex", "--input-json",
                           '{"session_id":"copied-binary"}', binary=helper, env=env)
        self.assertEqual(joined["role"], "coordinator")
        subprocess.run([str(native_path / "git"), "init", "-q"], cwd=self.project, check=True, env=env)
        command = json.loads((self.project / ".claude/settings.json").read_text())["hooks"]["SessionStart"][0]["hooks"][0]["command"]
        emitted = subprocess.run([str(native_path / "sh"), "-c", command], cwd=self.project, env=env,
                                 input='{"hook_event_name":"SessionStart","session_id":"second-root"}',
                                 capture_output=True, text=True)
        self.assertEqual(emitted.returncode, 0, emitted.stdout + emitted.stderr)
        self.assertIn("standby", json.loads(emitted.stdout)["hookSpecificOutput"]["additionalContext"])
        status = self.call("status", "--identity", joined["identity_file"], binary=helper, env=env)
        self.assertEqual(len(status["agents"]), 2)
        self.assertFalse(list(self.project.rglob("*.py")))

    def test_preflight_errors_and_legacy_upgrade_change_nothing(self):
        cases = [(".claude/settings.json", "broken JSON"),
                 (".codex/hooks.json", '{"hooks":{"SessionStart":[{"hooks":42}]}}'),
                 (".okms/okms", "Unmanaged runtime.\n"),
                 (".gitignore.okms-new", "Retain unfinished write.\n"),
                 (".claude/skills", "File occupies a required directory.\n"),
                 (".okms/install.json", '{"profile":"hybrid-team","version":"0.1.0","docs_path":"docs"}')]
        for path, body in cases:
            with self.subTest(path=path):
                location = self.write(path, body)
                before = files(self.project)
                value = self.call("init", expected=1)
                self.assertTrue(value["incomplete"])
                self.assertEqual(files(self.project), before)
                location.unlink()

    def test_invalid_docs_and_escaped_paths_preserve_external_bytes(self):
        for docs in (".", "../outside", ".git/docs", str(self.project / "absolute")):
            with self.subTest(docs=docs):
                self.call("init", "--docs", docs, expected=1)
                self.assertEqual(files(self.project), {})
        outside = self.directory / "outside"
        outside.mkdir()
        (outside / "keep.txt").write_text("Preserve external bytes.\n")
        (self.project / ".okms").symlink_to(outside, target_is_directory=True)
        before = files(outside)
        self.call("init", expected=1)
        self.assertEqual(files(outside), before)

    def test_ignored_binary_and_native_configuration_are_in_worker_overlay(self):
        self.write(".gitignore", ".okms/\n.claude/\n.codex/\n.agents/\ndocs/\n")
        self.write("app.txt", "value = 1\n")
        for args in (("init", "-q"), ("add", "."), ("-c", "user.name=Fixture", "-c",
                     "user.email=fixture@example.invalid", "commit", "-qm", "Baseline")):
            subprocess.run(["git", *args], cwd=self.project, check=True, capture_output=True)
        self.call("init")
        self.write("docs/work/P001/plan.md", "---\ntype: Plan\n---\n## Work\n\n| Spec | Depends on | State | Evidence |\n| --- | --- | --- | --- |\n| [P001-MS01](spec.md) | — | in_progress | Pending. |\n")
        self.write("docs/work/P001/spec.md", "---\ntype: MicroSpec\n---\n## Intent\nChange value.\n")
        owner = self.call("join", "--provider", "codex", "--input-json", '{"session_id":"root"}')
        assignment = self.call("dispatch", "--identity", owner["identity_file"], "--input-json", json.dumps({
            "provider": "claude", "plan": "docs/work/P001/plan.md", "spec": "docs/work/P001/spec.md",
            "intent": "Change value", "owns": ["app.txt"], "launch": False}))
        destination = Path(assignment["worktree"])
        self.assertTrue(os.access(destination / ".okms/okms", os.X_OK))
        self.assertTrue((destination / "docs/roles/worker.md").is_file())
        self.assertTrue((destination / ".claude/settings.json").is_file())
        self.assertFalse((destination / ".okms/state").exists())
        self.assertEqual((self.project / "app.txt").read_text(), "value = 1\n")


if __name__ == "__main__":
    unittest.main()
