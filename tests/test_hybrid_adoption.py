"""Preserving setup and independent copied commands; no provider session runs."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "templates/hybrid-team"
sys.path.insert(0, str(SOURCE / "runtime"))
from okms_team.adoption import install
from okms_team.providers import command
from okms_team.runtime import Runtime
from okms_team.state import TeamError


def files(path):
    return {file.relative_to(path).as_posix(): file.read_bytes() for file in path.rglob("*") if file.is_file()}


class AdoptionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="okms-adoption-")
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name) / "project $ literal space"
        self.project.mkdir()

    def write(self, name, content):
        path = self.project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def git(self, *args):
        result = subprocess.run(["git", *args], cwd=self.project, capture_output=True, text=True, check=True)
        return result.stdout.strip()

    def helper(self, *args, input=None, env=None):
        return subprocess.run([sys.executable, ".okms/team.py", *args], cwd=self.project,
                              input=json.dumps(input) if input is not None else None,
                              capture_output=True, text=True, env=env, check=True)

    def test_fresh_setup_repeat_and_project_edits(self):
        result = install(SOURCE, self.project)
        self.assertEqual(result["docs_path"], "docs")
        self.assertFalse(json.loads((self.project / ".okms/team.json").read_text())["checks"])
        self.assertTrue((self.project / "docs/team-policy.md").exists())
        self.assertTrue((self.project / ".agents/skills/okms-coordinate/SKILL.md").exists())
        self.assertTrue((self.project / ".claude/agents/okms-worker.md").exists())
        before = files(self.project)
        self.assertEqual(install(SOURCE, self.project)["changed"], [])
        self.assertEqual(files(self.project), before)
        self.write("docs/context.md", "Project-owned context and gate.\n")
        config = json.loads((self.project / ".okms/team.json").read_text())
        config["checks"] = [["python3", "-m", "unittest"]]
        self.write(".okms/team.json", json.dumps(config))
        self.write(".okms/okms_team/worker.py", "# Deliberate project customization.\n")
        edited = files(self.project)
        repeated = install(SOURCE, self.project)
        self.assertIn("docs/context.md", repeated["preserved_project_edits"])
        self.assertIn(".okms/okms_team/worker.py", repeated["preserved_project_edits"])
        self.assertEqual(files(self.project), edited)

    def test_existing_profile_instructions_settings_roles_and_skills_survive(self):
        self.write("docs/workflow.md", "---\ntemplate: lite\n---\nExisting workflow\n")
        self.write("docs/work/P003/plan.md", "Active historical plan\n")
        self.write("AGENTS.md", "Keep the parser API.\n")
        self.write("CLAUDE.md", "@AGENTS.md\nExisting Claude rules.\n")
        self.write(".codex/config.toml", 'model = "project-selected-model"\n')
        self.write(".codex/hooks.json", json.dumps({"hooks": {"SessionStart": [{"matcher": "startup", "hooks": [{"type": "command", "command": "project-hook"}]}]}}))
        self.write(".claude/settings.json", json.dumps({"permissions": {"deny": ["Bash(secret-*)"]}, "env": {"PROJECT_SETTING": "retained"}}))
        self.write(".claude/agents/okms-worker.md", "Existing team worker\n")
        self.write(".agents/skills/okms-work/SKILL.md", "Existing team skill\n")
        original = files(self.project)
        result = install(SOURCE, self.project)
        self.assertEqual(result["docs_path"], "docs/okms")
        self.assertEqual(result["native_roles"]["claude_worker"], "okms-team-worker-2")
        for name in ("docs/workflow.md", "docs/work/P003/plan.md", ".codex/config.toml", ".claude/agents/okms-worker.md", ".agents/skills/okms-work/SKILL.md"):
            self.assertEqual((self.project / name).read_bytes(), original[name])
        for name in ("AGENTS.md", "CLAUDE.md"):
            self.assertTrue((self.project / name).read_bytes().startswith(original[name]))
        settings = json.loads((self.project / ".claude/settings.json").read_text())
        self.assertEqual(settings["permissions"]["deny"], ["Bash(secret-*)"])
        self.assertEqual(settings["env"], {"PROJECT_SETTING": "retained"})
        hooks = json.loads((self.project / ".codex/hooks.json").read_text())["hooks"]["SessionStart"]
        self.assertEqual(hooks[0]["hooks"][0]["command"], "project-hook")
        config = json.loads((self.project / ".okms/team.json").read_text())
        argv = command("claude", config, self.project, {"worktree": str(self.project)}, self.project)
        self.assertEqual(argv[argv.index("--agent") + 1], "okms-team-worker-2")
        before = files(self.project)
        self.assertEqual(install(SOURCE, self.project)["changed"], [])
        self.assertEqual(files(self.project), before)
        result = Runtime(self.project).hook("claude", {"agent_type": "okms-team-worker-2", "session_id": "native-helper"})
        self.assertIn("native helper", result["hookSpecificOutput"]["additionalContext"])
        self.assertEqual(Runtime(self.project).store.status()["agents"], [])

    def test_dry_run_and_source_independent_copy(self):
        before = files(self.project)
        self.assertTrue(install(SOURCE, self.project, dry_run=True)["changed"])
        self.assertEqual(files(self.project), before)
        copied = Path(self.temporary.name) / "temporary-source"
        shutil.copytree(SOURCE, copied, ignore=shutil.ignore_patterns("__pycache__"))
        setup = subprocess.run([sys.executable, str(copied / "setup.py"), "--project", str(self.project)],
                               capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(setup.stdout)["profile"], "hybrid-team")
        shutil.rmtree(copied)
        joined = json.loads(self.helper("join", "--provider", "codex", "--input", "-", input={"session_id": "copied-session"}).stdout)
        self.assertEqual(joined["role"], "coordinator")
        self.git("init", "-q")
        hook = json.loads((self.project / ".claude/settings.json").read_text())["hooks"]["SessionStart"][0]["hooks"][0]["command"]
        emitted = subprocess.run(["sh", "-c", hook], cwd=self.project,
                                 input=json.dumps({"hook_event_name": "SessionStart", "session_id": "second-root"}),
                                 capture_output=True, text=True, check=True)
        self.assertIn("standby", json.loads(emitted.stdout)["hookSpecificOutput"]["additionalContext"])
        identity = {"OKMS_AGENT_ID": joined["agent_id"], "OKMS_AGENT_TOKEN": joined["token"]}
        bound = json.loads(self.helper("hook", "--provider", "codex", input={"session_id": "worker-native"}, env={**os.environ, **identity}).stdout)
        self.assertIn("coordinator", bound["hookSpecificOutput"]["additionalContext"])
        self.assertEqual(len(Runtime(self.project).store.status()["agents"]), 2)

    def test_preflight_failures_change_nothing(self):
        cases = [(".claude/settings.json", "broken JSON"),
                 (".codex/hooks.json", '{"hooks":{"SessionStart":[{"hooks":42}]}}'),
                 (".okms/team.py", "Unmanaged runtime\n"),
                 (".gitignore.okms-new", "Retain this unfinished write\n"),
                 (".claude/skills", "File occupies a required directory\n")]
        for name, content in cases:
            with self.subTest(name=name):
                location = self.project / name
                self.write(name, content)
                before = files(self.project)
                with self.assertRaises((TeamError, OSError)):
                    install(SOURCE, self.project)
                self.assertEqual(files(self.project), before)
                location.unlink()

    def test_invalid_destination_or_external_symlink_is_unchanged(self):
        for docs in (".", "../outside", ".git/docs", str(self.project / "absolute")):
            with self.subTest(docs=docs), self.assertRaises(TeamError):
                install(SOURCE, self.project, docs)
            self.assertEqual(files(self.project), {})
        outside = Path(self.temporary.name) / "external"
        outside.mkdir()
        (self.project / ".okms").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(TeamError):
            install(SOURCE, self.project)
        self.assertEqual(files(outside), {})

    def test_ignored_installed_runtime_is_available_in_worker_worktree(self):
        self.write(".gitignore", ".okms/\n.claude/\n.codex/\n.agents/\ndocs/\n")
        self.write("app.py", "value = 1\n")
        self.git("init", "-q")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "Baseline")
        install(SOURCE, self.project)
        self.write("docs/work/P001/plan.md", "---\ntype: Plan\n---\n## Work\n\n| Spec | Depends on | State | Evidence |\n| --- | --- | --- | --- |\n| [P001-MS01](spec.md) | — | in_progress | Pending. |\n")
        self.write("docs/work/P001/spec.md", "---\ntype: MicroSpec\n---\n## Intent\nChange value.\n")
        runtime = Runtime(self.project)
        root = runtime.store.join("codex", "root")
        assignment = runtime.dispatch({"agent_id": root["agent_id"], "token": root["token"]}, {
            "provider": "claude", "plan": "docs/work/P001/plan.md", "spec": "docs/work/P001/spec.md",
            "intent": "Change value", "owns": ["app.py"], "launch": False})
        destination = Path(assignment["worktree"])
        self.assertTrue((destination / ".okms/team.py").is_file())
        self.assertTrue((destination / "docs/roles/worker.md").is_file())
        self.assertTrue((destination / ".claude/settings.json").is_file())
        self.assertFalse((destination / ".okms/state").exists())
        self.assertEqual(self.git("status", "--porcelain", "--", "app.py"), "")


if __name__ == "__main__":
    unittest.main()
