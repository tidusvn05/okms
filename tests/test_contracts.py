"""Contract fixtures test observable guard behavior, not agent compliance."""

import importlib.util
import re
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
MODULE_SPEC = importlib.util.spec_from_file_location("docs_checker", ROOT / "scripts/check_docs.py")
checker = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(checker)


def concept(path, metadata, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\n" + yaml.safe_dump(metadata, sort_keys=False) + "---\n\n" + body)


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="okms-contracts-")
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name)
        self.bundle = self.project / "docs"
        shutil.copytree(ROOT / "templates/plan-first/docs", self.bundle)
        self.plan = self.bundle / "work/P001-fixture/plan.md"
        self.goal = self.bundle / "work/G001-fixture/goal.md"

    def errors(self, link_root=None):
        instance = checker.Checker(self.bundle)
        instance.load()
        instance.check_links()
        instance.check_bundle(self.bundle, link_root=link_root)
        return instance.errors

    def active(self, paths):
        path = self.bundle / "index.md"
        entries = "".join(f"- [Current work]({p.relative_to(self.bundle).as_posix()}) - Fixture work checkpoint.\n" for p in paths) or "No open work.\n"
        text = re.sub(r"(# Active work\n\n).*?(?=\n# )", lambda match: match.group(1) + entries, path.read_text(), flags=re.S)
        path.write_text(text)

    def make_spec(self, *, task_kind="bugfix", standalone=False):
        path = self.bundle / ("work/MS001-fixture.md" if standalone else "work/P001-fixture/P001-MS01-fixture.md")
        metadata = {"type": "MicroSpec", "title": "Fixture behavior contract",
                    "description": "Provide a structural fixture for task kind and progress ownership checks."}
        if task_kind is not None:
            metadata["kind"] = task_kind
        if standalone:
            metadata["work_status"] = "in_progress"
        concept(path, metadata, "# Fixture spec\n\n## Intent\n\nVerify a bounded fixture outcome.\n\n"
                "## Constraints\n\n- Never: treat synthetic fixture evidence as an application result.\n\n"
                "## Acceptance\n\n- The fixture contract can be structurally checked.\n\n"
                "## Verify\n\nMethod: fixture review; expected valid structure.\n")
        if standalone:
            with (self.bundle / "work/index.md").open("a") as handle:
                handle.write("\n- [Fixture spec](MS001-fixture.md) - Standalone kind validation fixture.\n")
            self.active([path])
        return path

    def make_goal(self, *, state="in_progress", reason="iteration_limit", limit=1, used=1,
                  plan_state="in_progress", completion=False, mode="portable", native_id=None):
        spec_path = self.make_spec()
        self.plan.parent.mkdir(parents=True, exist_ok=True)
        (self.plan.parent / "index.md").write_text(
            "# Fixture plan\n\n- [Plan](plan.md) - Structural fixture work plan.\n"
            "- [Spec](P001-MS01-fixture.md) - Fixture behavior and evidence contract.\n")
        item_state = "done" if plan_state == "done" else "in_progress"
        concept(self.plan, {"type": "Plan", "title": "P001 · Fixture plan",
                "description": "Track a structural fixture item for Goal and plan consistency checks.",
                "work_status": plan_state},
                "# P001 · Fixture plan\n\n## Goal\n\nReview a fixture.\n\n## Approach\n\nUse fixture-only evidence.\n\n"
                "## Work\n\n| Spec | Depends on | State | Evidence |\n| --- | --- | --- | --- |\n"
                f"| [P001-MS01 · Fixture](P001-MS01-fixture.md) | — | {item_state} | Fixture-only review evidence supplied by this test. |\n\n"
                "## Resume\n\n- Current: fixture item.\n- Next: review fixture.\n- Blocker: none.\n\n"
                "## Result\n\nFixture-only structural review evidence; no application execution is claimed.\n")
        self.goal.parent.mkdir(parents=True, exist_ok=True)
        (self.goal.parent / "index.md").write_text("# Fixture Goal\n\n- [Goal](goal.md) - Bounded structural fixture goal.\n")
        with (self.bundle / "work/index.md").open("a") as handle:
            handle.write("\n- [Fixture plan](P001-fixture/index.md) - Fixture progress and evidence.\n"
                         "- [Fixture Goal](G001-fixture/index.md) - Fixture bounded execution contract.\n")
        metadata = {"type": "Goal", "title": "G001 · Fixture Goal",
                    "description": "Exercise persistent budget, completion, and plan-reference contracts without an agent.",
                    "work_status": state, "execution": mode, "max_iterations": limit,
                    "iterations_used": used, "stop_reason": reason}
        if native_id is not None:
            metadata["native_id"] = native_id
        concept(self.goal, metadata,
                "# G001 · Fixture Goal\n\n## Goal\n\nComplete a fixture review.\n\n"
                "## Scope\n\n- Work plans: [P001](../P001-fixture/plan.md).\n\n"
                f"## Completion\n\n- [{'x' if completion else ' '}] The scoped fixture review is supported by evidence.\n\n"
                f"## Execution\n\n- Mode: {mode}.\n- Adapter: fixture-only mapping, not an activated runtime.\n\n"
                "## Stop\n\nStop when complete, at the limit, or blocked.\n\n"
                "## Resume\n\n- Current: P001-MS01, reserved attempt.\n- Next: complete the fixture review.\n"
                f"- Blocker: {'fixture dependency unavailable' if state == 'blocked' else 'none'}.\n\n"
                "## Result\n\nFixture-only evidence; no application execution is claimed.\n")
        self.active(([self.plan] if plan_state != "done" else []) + ([self.goal] if state not in {"done", "cancelled"} else []))
        return metadata

    def change_goal(self, metadata, **updates):
        body = self.goal.read_text().split("---", 2)[2].lstrip()
        concept(self.goal, {**metadata, **updates}, body)

    def test_copied_payload_is_valid(self):
        self.assertFalse(self.errors())

    def test_conditional_plan_sections_are_valid_in_either_workflow(self):
        self.make_goal()
        original = self.plan.read_text()
        for profile in checker.PROFILES:
            shutil.copyfile(ROOT / "templates" / profile / "docs/workflow.md", self.bundle / "workflow.md")
            for extra in ("", "## Baseline\n\nFixture-only current behavior and check evidence.\n\n"
                          "## Compatibility\n\nPreserve the fixture interface.\n\n"):
                with self.subTest(profile=profile, conditional=bool(extra)):
                    self.plan.write_text(original.replace("## Approach", extra + "## Approach"))
                    self.assertFalse(self.errors())

    def test_partial_conditional_plan_sections_are_rejected(self):
        self.make_goal()
        original = self.plan.read_text()
        for name in ("Baseline", "Compatibility"):
            with self.subTest(section=name):
                self.plan.write_text(original.replace("## Approach", f"## {name}\n\nFixture-only evidence.\n\n## Approach"))
                self.assertTrue(any("expected sections" in error for error in self.errors()))

    def test_unexpected_third_profile_is_rejected(self):
        repository = self.project / "repository"
        shutil.copytree(ROOT / "docs", repository / "docs")
        shutil.copytree(ROOT / "templates", repository / "templates")
        shutil.copytree(repository / "templates/plan-first", repository / "templates/extra-profile")
        instance = checker.Checker(repository)
        instance.load()
        instance.check_profiles()
        self.assertTrue(any("only Lite and Plan-first" in error for error in instance.errors))

    def test_legacy_kindless_spec_stays_valid(self):
        self.make_spec(task_kind=None, standalone=True)
        self.assertFalse(self.errors())

    def test_all_supported_task_kinds_are_valid(self):
        path = self.make_spec(standalone=True)
        original = path.read_text()
        for task_kind in checker.TASK_KINDS:
            with self.subTest(kind=task_kind):
                path.write_text(original.replace("kind: bugfix", f"kind: {task_kind}"))
                self.assertFalse(self.errors())

    def test_unknown_and_nonscalar_kind_are_rejected(self):
        path = self.make_spec(standalone=True)
        original = path.read_text()
        for value in ("unsupported", "[bugfix]", "{name: bugfix}"):
            with self.subTest(value=value):
                path.write_text(original.replace("kind: bugfix", f"kind: {value}"))
                self.assertTrue(any("supported task category" in error for error in self.errors()))

    def test_catalog_cannot_route_bugfix_to_research(self):
        path = self.bundle / "_templates/catalog.md"
        path.write_text(path.read_text().replace("[Bugfix](micro-spec-bugfix.md)", "[Bugfix](micro-spec-research.md)"))
        self.assertTrue(any("exactly its bugfix blueprint" in error for error in self.errors()))

    def test_catalog_requires_matching_blueprint_kind(self):
        path = self.bundle / "_templates/micro-spec-bugfix.md"
        path.write_text(path.read_text().replace("kind: bugfix", "kind: research"))
        self.assertTrue(any("matching kind" in error for error in self.errors()))

    def test_specialized_blueprint_keeps_common_sections(self):
        path = self.bundle / "_templates/micro-spec-design.md"
        path.write_text(path.read_text().replace("## Acceptance", "## Alternatives"))
        self.assertTrue(any("expected sections" in error for error in self.errors()))

    def test_limit_checkpoint_is_valid_and_incomplete(self):
        self.make_goal()
        self.assertFalse(self.errors())

    def test_completed_goal_requires_completed_plan_and_evidence(self):
        self.make_goal(state="done", reason="complete", plan_state="done", completion=True)
        self.assertFalse(self.errors())

    def test_goal_cannot_claim_completion_for_open_work(self):
        self.make_goal(state="done", reason="complete", completion=True)
        self.assertTrue(any("incomplete scoped plans" in error for error in self.errors()))

    def test_goal_cannot_claim_unchecked_completion(self):
        self.make_goal(state="done", reason="complete", plan_state="done")
        self.assertTrue(any("unverified Completion" in error for error in self.errors()))

    def test_blocked_goal_is_valid_with_dependency(self):
        self.make_goal(state="blocked", reason="blocked", limit=3)
        self.assertFalse(self.errors())

    def test_blocked_goal_requires_a_recorded_dependency(self):
        self.make_goal(state="blocked", reason="blocked", limit=3)
        original = self.goal.read_text()
        for value in ("", ".", "none", "Pending."):
            with self.subTest(blocker=value):
                self.goal.write_text(original.replace("fixture dependency unavailable.", value))
                self.assertTrue(any("actual dependency" in error for error in self.errors()))

    def test_budget_types_and_overruns_are_rejected_without_crash(self):
        metadata = self.make_goal()
        for updates in ({"max_iterations": True}, {"max_iterations": [1]}, {"max_iterations": 0},
                        {"iterations_used": "1"}, {"iterations_used": {"value": 1}}, {"iterations_used": -1},
                        {"iterations_used": 2}, {"work_status": ["done"]}, {"stop_reason": ["complete"]}):
            with self.subTest(updates=updates):
                self.change_goal(metadata, **updates)
                self.assertTrue(self.errors())

    def test_limit_reason_requires_actual_exhaustion(self):
        self.make_goal(limit=3, used=1)
        self.assertTrue(any("at the recorded limit" in error for error in self.errors()))

    def test_started_native_goal_requires_runtime_reference(self):
        metadata = self.make_goal(mode="native")
        self.assertTrue(any("actual native_id" in error for error in self.errors()))
        self.change_goal(metadata, native_id="fixture-reference-not-an-activated-runtime")
        self.assertFalse(self.errors())

    def test_plan_owned_spec_cannot_duplicate_state(self):
        self.make_goal()
        path = self.plan.parent / "P001-MS01-fixture.md"
        path.write_text(path.read_text().replace("type: MicroSpec", "type: MicroSpec\nwork_status: done"))
        self.assertTrue(any("duplicates its plan" in error for error in self.errors()))

    def test_adopted_project_links_keep_export_boundary_strict(self):
        (self.project / "code.py").write_text("# Fixture code\n")
        path = self.bundle / "context.md"
        path.write_text(path.read_text() + "\n[Project source](../code.py)\n")
        self.assertTrue(any("outside file" in error for error in self.errors()))
        self.assertFalse(self.errors(link_root=self.project))
        path.write_text(path.read_text() + "\n[Other project](../../elsewhere.md)\n")
        self.assertTrue(any("outside file" in error for error in self.errors(link_root=self.project)))

    def test_nonscalar_maintainer_version_is_rejected(self):
        repository = self.project / "repository"
        shutil.copytree(ROOT / "docs", repository / "docs")
        shutil.copytree(ROOT / "templates", repository / "templates")
        path = repository / "docs/workflow.md"
        path.write_text(re.sub(r"^template_version:.*$", "template_version: [invalid]", path.read_text(), flags=re.M))
        instance = checker.Checker(repository)
        instance.load()
        instance.check_profiles()
        self.assertTrue(any("maintainer workflow version" in error for error in instance.errors))


if __name__ == "__main__":
    unittest.main()
