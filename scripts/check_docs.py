#!/usr/bin/env python3
"""Read-only document checks and disposable setup fixtures, not an installer."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required for maintainer checks: install requirements-dev.txt.")


PROFILES = ("lite", "plan-first", "brownfield")
STATES = {"planned", "in_progress", "blocked", "done", "cancelled"}
SPEC_SECTIONS = ["Intent", "Constraints", "Acceptance", "Verify"]
PLAN_SECTIONS = ["Goal", "Approach", "Work", "Resume", "Result"]
GOAL_SECTIONS = ["Goal", "Scope", "Completion", "Execution", "Stop", "Resume", "Result"]
TASK_KINDS = ("implementation", "bugfix", "investigation", "design", "research", "runbook", "general")
BLUEPRINTS = {kind: f"micro-spec-{kind}.md" for kind in TASK_KINDS if kind != "general"}
BLUEPRINTS["general"] = "micro-spec.md"
STOP_REASONS = {"none", "complete", "iteration_limit", "blocked", "user_stop"}
PAYLOAD_FILES = {
    "index.md", "workflow.md", "context.md", "_templates/index.md",
    "_templates/plan.md", "_templates/catalog.md", "_templates/goal.md", "goal-loop.md", "work/index.md",
    *(f"_templates/{name}" for name in BLUEPRINTS.values()),
}
SHARED_FILES = {"goal-loop.md", "_templates/index.md", "_templates/catalog.md", "_templates/goal.md",
                *(f"_templates/{name}" for name in BLUEPRINTS.values())}
ID_PATTERN = r"(?:P\d+-MS\d+|MS\d+)"
UNEXECUTED = re.compile(r"^(?:pending|not run|not created|not implemented|not verified)\b", re.I)


def valid_state(value) -> bool:
    return isinstance(value, str) and value in STATES


class UniqueLoader(yaml.SafeLoader):
    """Reject duplicate keys instead of silently keeping the last value."""

    def construct_mapping(self, node, deep=False):
        self.flatten_mapping(node)
        result = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in result:
                raise yaml.constructor.ConstructorError(
                    "duplicate frontmatter key", node.start_mark, str(key), key_node.start_mark
                )
            result[key] = self.construct_object(value_node, deep=deep)
        return result


def visible_markdown(text: str) -> str:
    """Ignore fenced examples and inline code when finding actual links/headings."""
    output, fence = [], None
    for line in text.splitlines():
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})(.*)$", line)
        if match:
            marker, rest = match.groups()
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence) and not rest.strip():
                fence = None
            continue
        if fence is None:
            output.append(re.sub(r"(`+).*?\1", "", line))
    return "\n".join(output)


def headings(body: str) -> list[str]:
    return re.findall(r"^## (.+?)\s*$", visible_markdown(body), re.M)


def section(body: str, name: str) -> str:
    match = re.search(r"^##? " + re.escape(name) + r"\s*\n(.*?)(?=^##? |\Z)", body, re.M | re.S)
    return match.group(1).strip() if match else ""


def anchors(body: str) -> set[str]:
    counts, result = {}, set()
    for heading in re.findall(r"^#{1,6} (.+?)\s*$", visible_markdown(body), re.M):
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        number = counts.get(slug, 0)
        counts[slug] = number + 1
        result.add(slug if number == 0 else f"{slug}-{number}")
    return result


def local_links(path: Path, body: str):
    for raw in re.findall(r"\[[^\]\n]*\]\(([^)\n]+)\)", visible_markdown(body)):
        href = raw.strip().split(' "', 1)[0].strip("<>")
        url = urlsplit(href)
        if url.scheme or url.netloc:
            continue
        target = (path.parent / unquote(url.path)).resolve() if url.path else path
        yield target, unquote(url.fragment), href


def markdown_files(root: Path):
    for path in sorted(root.rglob("*.md")):
        if not any(part.startswith(".") or part == "__pycache__" for part in path.relative_to(root).parts):
            yield path.resolve()


class Checker:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.documents = {}
        self.errors = []

    def error(self, path: Path, message: str):
        label = path.relative_to(self.root) if path.is_relative_to(self.root) else path
        self.errors.append(f"{label}: {message}")

    def load(self):
        for path in markdown_files(self.root):
            text = path.read_text(encoding="utf-8")
            metadata, body = None, text
            if text.startswith("---\n"):
                match = re.match(r"\A---\n(.*?)\n---(?:\n|\Z)(.*)\Z", text, re.S)
                if not match:
                    self.error(path, "unterminated frontmatter")
                else:
                    body = match.group(2)
                    try:
                        metadata = yaml.load(match.group(1), Loader=UniqueLoader)
                        if not isinstance(metadata, dict):
                            self.error(path, "frontmatter must be a mapping")
                            metadata = None
                    except (yaml.YAMLError, TypeError) as exc:
                        self.error(path, f"invalid YAML: {exc}")
            self.documents[path] = (metadata, body)

    def check_links(self):
        for path, (_, body) in self.documents.items():
            for target, fragment, href in local_links(path, body):
                if not target.exists():
                    self.error(path, f"broken link: {href}")
                elif fragment and target.suffix == ".md":
                    target_body = self.documents.get(target, (None, target.read_text()))[1]
                    if fragment not in anchors(target_body):
                        self.error(path, f"unknown heading: {href}")

    def check_bundle(self, root: Path, *, link_root: Path | None = None):
        root = root.resolve()
        allowed_link_root = (link_root or root).resolve()
        if not root.is_relative_to(allowed_link_root):
            raise ValueError("bundle must be inside its allowed link root")
        documents = {p: value for p, value in self.documents.items() if p.is_relative_to(root)}
        if not documents:
            self.error(root, "missing Markdown bundle")
            return
        for path, (metadata, body) in documents.items():
            if path.name == "index.md":
                expected = {"okf_version": "0.2"} if path.parent == root else None
                if metadata != expected:
                    self.error(path, "only a bundle root index has frontmatter: okf_version: '0.2'")
            else:
                if metadata is None:
                    self.error(path, "missing concept frontmatter")
                    continue
                for key in ("type", "title", "description"):
                    if not isinstance(metadata.get(key), str) or not metadata[key].strip():
                        self.error(path, f"missing or invalid {key}")
                description = metadata.get("description", "")
                if isinstance(description, str) and not 20 <= len(description) <= 300:
                    self.error(path, "description must be a useful sentence of 20–300 characters")
                if metadata.get("title") == description:
                    self.error(path, "description repeats the title")
                if "status" in metadata and (not isinstance(metadata["status"], str) or metadata["status"] not in {"draft", "stable", "deprecated"}):
                    self.error(path, "OKF status is a document lifecycle, not work progress")
                if "work_status" in metadata and not valid_state(metadata["work_status"]):
                    self.error(path, "invalid work_status")
                kind = metadata.get("type")
                if "kind" in metadata and (not isinstance(metadata["kind"], str) or metadata["kind"] not in TASK_KINDS):
                    self.error(path, "kind must be a supported task category")
                expected_sections = None
                if kind == "MicroSpec" or (kind == "Template" and path.name in BLUEPRINTS.values()):
                    expected_sections = SPEC_SECTIONS
                elif kind == "Plan" or (kind == "Template" and path.name == "plan.md"):
                    expected_sections = PLAN_SECTIONS
                    if "Baseline" in headings(body) or "Compatibility" in headings(body):
                        expected_sections = ["Goal", "Baseline", "Compatibility", *PLAN_SECTIONS[1:]]
                elif kind == "Goal" or (kind == "Template" and path.name == "goal.md"):
                    expected_sections = GOAL_SECTIONS
                if expected_sections and headings(body) != expected_sections:
                    self.error(path, f"expected sections: {' / '.join(expected_sections)}")
                if kind in ("Plan", "MicroSpec", "Goal") and "{{" in body:
                    self.error(path, "work document contains an unresolved placeholder")
            for target, _, href in local_links(path, body):
                if not target.is_relative_to(allowed_link_root):
                    self.error(path, f"bundle link depends on an outside file: {href}")

        for directory in {p.parent for p in documents}:
            index = directory / "index.md"
            if index not in documents:
                self.error(directory, "missing directory index")
                continue
            listed = {target for target, _, _ in local_links(index, documents[index][1])}
            for child in directory.iterdir():
                if child.name in {"index.md", "log.md"} or child.name.startswith("."):
                    continue
                if child.is_file() and child.suffix == ".md" and child not in listed:
                    self.error(index, f"does not list {child.name}")
                elif child.is_dir() and any(p.is_relative_to(child) for p in documents):
                    if not any(target.is_relative_to(child) for target in listed):
                        self.error(index, f"does not list {child.name}/")
        self.check_work(root, documents)
        if root / "_templates/catalog.md" in documents:
            self.check_catalog(root, documents)

    def check_catalog(self, root: Path, documents: dict):
        path = root / "_templates/catalog.md"
        body = documents[path][1]
        seen = set()
        for line in body.splitlines():
            match = re.match(r"^\|\s*([a-z]+)\s*\|", line)
            if not match:
                continue
            task_kind = match.group(1)
            if task_kind in seen:
                self.error(path, f"duplicate catalog kind: {task_kind}")
            seen.add(task_kind)
            if task_kind not in BLUEPRINTS:
                self.error(path, f"unsupported catalog kind: {task_kind}")
                continue
            links = [target for target, _, _ in local_links(path, line)]
            expected = path.parent / BLUEPRINTS[task_kind]
            if links != [expected]:
                self.error(path, f"catalog must select exactly its {task_kind} blueprint")
            metadata = documents.get(expected, (None, ""))[0]
            if not metadata or metadata.get("type") != "Template" or metadata.get("kind") != task_kind:
                self.error(expected, "catalog blueprint must be a Template with its matching kind")
        if seen != set(TASK_KINDS):
            self.error(path, "catalog must cover the six specialized task kinds and general fallback")

    def check_work(self, root: Path, documents: dict):
        owners, item_states, dependencies = {}, {}, []
        plans = {p: value for p, value in documents.items() if value[0] and value[0].get("type") == "Plan"}
        for path, (metadata, body) in plans.items():
            if not valid_state(metadata.get("work_status")):
                self.error(path, "plan needs work_status")
            lines = [line for line in section(body, "Work").splitlines() if line.startswith("|")]
            cells = [list(map(str.strip, re.split(r"(?<!\\)\|", line.strip().strip("|")))) for line in lines]
            if len(cells) < 3 or cells[0] != ["Spec", "Depends on", "State", "Evidence"]:
                self.error(path, "Work needs Spec / Depends on / State / Evidence and at least one item")
                continue
            states = []
            for row in cells[2:]:
                if len(row) != 4:
                    self.error(path, "malformed Work row; escape literal pipes")
                    continue
                label, depends, state, evidence = row
                match = re.search(ID_PATTERN, label)
                if not match:
                    self.error(path, "work item needs a stable micro spec ID")
                    continue
                work_id = match.group()
                if work_id in item_states:
                    self.error(path, f"duplicate work item ID: {work_id}")
                item_states[work_id] = state
                states.append(state)
                dependencies.append((path, work_id, state, re.findall(ID_PATTERN, depends)))
                if state not in STATES:
                    self.error(path, f"invalid State for {work_id}")
                if state == "done" and (not evidence or UNEXECUTED.match(evidence)):
                    self.error(path, f"done item lacks completion evidence: {work_id}")
                linked = [target for target, _, _ in local_links(path, label)]
                if state in {"in_progress", "done"} and not linked:
                    self.error(path, f"started item has no saved spec link: {work_id}")
                for target in linked:
                    target_metadata = documents.get(target, (None, ""))[0]
                    if not target_metadata or target_metadata.get("type") != "MicroSpec":
                        self.error(path, f"work item link is not a saved MicroSpec: {work_id}")
                    elif target in owners:
                        self.error(path, f"spec progress is owned twice: {work_id}")
                    else:
                        owners[target] = path
            if metadata.get("work_status") == "done":
                if any(state not in {"done", "cancelled"} for state in states):
                    self.error(path, "done plan contains incomplete items")
                if not section(body, "Result") or UNEXECUTED.match(section(body, "Result")):
                    self.error(path, "done plan needs a final result")
            if not all(f"- {field}:" in section(body, "Resume") for field in ("Current", "Next", "Blocker")):
                self.error(path, "Resume needs Current, Next, and Blocker")

        graph = {work_id: deps for _, work_id, _, deps in dependencies}
        for path, work_id, state, deps in dependencies:
            for dependency in deps:
                if dependency not in item_states:
                    self.error(path, f"unknown dependency {dependency} for {work_id}")
                elif state in {"in_progress", "done"} and item_states[dependency] != "done":
                    self.error(path, f"{work_id} started before dependency {dependency} was done")
            stack = list(deps)
            seen = set()
            while stack:
                dependency = stack.pop()
                if dependency == work_id:
                    self.error(path, f"dependency cycle involving {work_id}")
                    break
                if dependency not in seen:
                    seen.add(dependency)
                    stack.extend(graph.get(dependency, []))

        active = {target for target, _, _ in local_links(root / "index.md", section(documents.get(root / "index.md", (None, ""))[1], "Active work"))}
        for path, (metadata, body) in documents.items():
            if not metadata or metadata.get("type") not in ("Plan", "MicroSpec", "Goal"):
                continue
            if metadata["type"] == "MicroSpec" and path in owners:
                if "work_status" in metadata:
                    self.error(path, "planned spec duplicates its plan's progress")
                continue
            state = metadata.get("work_status")
            if not valid_state(state):
                self.error(path, "standalone work needs work_status")
            elif state in {"done", "cancelled"} and path in active:
                self.error(path, "closed work remains in Active work")
            elif state in {"planned", "in_progress", "blocked"} and path not in active:
                self.error(path, "open work is missing from Active work")
            if metadata["type"] == "MicroSpec" and state == "done":
                result = re.search(r"\bResults?:\s*(.+)", section(body, "Verify"), re.I)
                if not result or UNEXECUTED.match(result.group(1)):
                    self.error(path, "done standalone spec needs an actual Result in Verify")
            if metadata["type"] == "Goal":
                self.check_goal(path, metadata, body, documents)

    def check_goal(self, path: Path, metadata: dict, body: str, documents: dict):
        state = metadata.get("work_status") if valid_state(metadata.get("work_status")) else None
        limit, used = metadata.get("max_iterations"), metadata.get("iterations_used")
        valid_limit = type(limit) is int and limit > 0
        valid_used = type(used) is int and used >= 0
        if not valid_limit:
            self.error(path, "max_iterations must be a positive integer")
        if not valid_used:
            self.error(path, "iterations_used must be a nonnegative integer")
        if valid_limit and valid_used and used > limit:
            self.error(path, "Goal consumed more attempts than its recorded limit")
        mode = metadata.get("execution")
        if not isinstance(mode, str) or mode not in {"portable", "native"}:
            self.error(path, "Goal execution must be portable or native")
        if mode == "native" and ((valid_used and used > 0) or state == "done"):
            if not isinstance(metadata.get("native_id"), str) or not metadata["native_id"].strip():
                self.error(path, "started native Goal needs the actual native_id")
        reason = metadata.get("stop_reason")
        if not isinstance(reason, str) or reason not in STOP_REASONS:
            self.error(path, "invalid Goal stop_reason")
        if reason == "iteration_limit" and not (state == "in_progress" and valid_limit and valid_used and used == limit):
            self.error(path, "iteration_limit requires incomplete work at the recorded limit")
        if reason == "complete" and state != "done":
            self.error(path, "complete stop_reason requires a done Goal")
        if state == "done" and reason != "complete":
            self.error(path, "done Goal needs complete stop_reason")
        if (state == "blocked") != (reason == "blocked"):
            self.error(path, "blocked Goal and blocked stop_reason must agree")
        if state == "planned" and (used != 0 or reason != "none"):
            self.error(path, "planned Goal must have no consumed attempts or stop reason")
        if reason == "user_stop" and state not in {"in_progress", "cancelled"}:
            self.error(path, "user_stop preserves incomplete progress or cancelled scope")
        if state == "cancelled" and reason != "user_stop":
            self.error(path, "cancelled Goal needs user_stop and a recorded withdrawal")
        resume = section(body, "Resume")
        if not all(f"- {field}:" in resume for field in ("Current", "Next", "Blocker")):
            self.error(path, "Goal Resume needs Current, Next, and Blocker")
        blocker = re.search(r"^- Blocker:[ \t]*(.*)$", resume, re.M)
        blocker_text = blocker.group(1).strip() if blocker else ""
        if state == "blocked" and (not re.search(r"\w", blocker_text)
                                   or re.fullmatch(r"(?:none|pending)\.?", blocker_text, re.I)):
            self.error(path, "blocked Goal needs its actual dependency")
        criteria = re.findall(r"^- \[([ xX])\] (\S.+)$", section(body, "Completion"), re.M)
        if not criteria:
            self.error(path, "Goal Completion needs measurable checkbox criteria")
        targets = [target for target, _, _ in local_links(path, section(body, "Scope"))
                   if target.name == "plan.md" or documents.get(target, ({}, ""))[0] and
                   documents[target][0].get("type") == "Plan"]
        plans = []
        for target in targets:
            info = documents.get(target, (None, ""))[0]
            if not info or info.get("type") != "Plan":
                self.error(path, "Goal work link must reference a saved Plan")
            else:
                plans.append(info)
        if (state in {"in_progress", "done"} or valid_used and used > 0) and not plans:
            self.error(path, "started Goal needs a saved work plan in Scope")
        if state == "done":
            if not criteria or any(marker.lower() != "x" for marker, _ in criteria):
                self.error(path, "done Goal has unverified Completion criteria")
            if any(not isinstance(plan.get("work_status"), str) or plan["work_status"] not in {"done", "cancelled"} for plan in plans):
                self.error(path, "done Goal references incomplete scoped plans")
            result = section(body, "Result")
            if not result or UNEXECUTED.match(result):
                self.error(path, "done Goal needs actual completion evidence in Result")

    def check_profiles(self):
        versions = set()
        standard = (self.root / "docs/_templates/plan.md").read_bytes()
        for profile in PROFILES:
            bundle = self.root / "templates" / profile / "docs"
            inventory = {str(p.relative_to(bundle)) for p in markdown_files(bundle)}
            if inventory != PAYLOAD_FILES:
                self.error(bundle, "profile must contain exactly the sixteen payload files")
            metadata = self.documents.get(bundle / "workflow.md", ({}, ""))[0] or {}
            if metadata.get("template") != profile:
                self.error(bundle, "workflow template metadata disagrees with its profile")
            version = metadata.get("template_version")
            if isinstance(version, str):
                versions.add(version)
            else:
                self.error(bundle, "template_version must be a string")
            for name in SHARED_FILES:
                source, target = self.root / "docs" / name, bundle / name
                if not source.is_file() or not target.is_file() or source.read_bytes() != target.read_bytes():
                    self.error(target, "shared catalog, contract, or Goal guide drifted")
            if profile != "brownfield" and (bundle / "_templates/plan.md").read_bytes() != standard:
                self.error(bundle, "shared plan blueprint drifted")
            if profile == "brownfield" and headings(self.documents[bundle / "_templates/plan.md"][1]) != ["Goal", "Baseline", "Compatibility", *PLAN_SECTIONS[1:]]:
                self.error(bundle, "Brownfield plan needs baseline and compatibility")
        if len(versions) != 1 or not all(isinstance(v, str) and re.fullmatch(r"\d+\.\d+\.\d+", v) for v in versions):
            self.error(self.root / "templates", "profile versions must match and use three numeric parts")
        maintainer_version = (self.documents.get(self.root / "docs/workflow.md", ({}, ""))[0] or {}).get("template_version")
        if not isinstance(maintainer_version, str) or versions != {maintainer_version}:
            self.error(self.root / "docs/workflow.md", "maintainer workflow version must match the payloads")


def fixture_adopt(source: Path, project: Path) -> Path:
    """Model the documented copy guards inside a temporary project only."""
    agents = project / "AGENTS.md"
    existing_text = agents.read_text() if agents.exists() else ""
    pointed = [target for target, _, _ in local_links(agents, existing_text)]
    defaults = [project / "docs/workflow.md", project / "docs/okms/workflow.md"]

    def installed(path):
        if not path.is_file() or not path.read_text().startswith("---\n"):
            return False
        metadata = yaml.load(path.read_text().split("---", 2)[1], Loader=UniqueLoader)
        return isinstance(metadata, dict) and metadata.get("template") in PROFILES and "template_version" in metadata

    candidates = list(dict.fromkeys(path for path in pointed if installed(path)))
    if not candidates:
        candidates = [path.resolve() for path in defaults if installed(path)]
    if len(candidates) > 1:
        raise ValueError("ambiguous existing installation")
    if candidates:
        destination = candidates[0].parent
    else:
        docs = project / "docs"
        destination = docs if not docs.exists() or not any(docs.iterdir()) else docs / "okms"
        if destination.exists() and any(destination.iterdir()):
            raise ValueError("destination is occupied")
        shutil.copytree(source, destination, dirs_exist_ok=True)
    relative = destination.relative_to(project).as_posix()
    workflow = (destination / "workflow.md").resolve()
    if workflow not in pointed:
        rule = f"For substantive project tasks, read and follow [the workflow]({relative}/workflow.md), starting with [the docs index]({relative}/index.md)."
        agents.write_text(existing_text + ("\n" if existing_text else "") + rule + "\n")
    return destination


def onboarding_smoke(root: Path) -> int:
    scenarios = 0
    with tempfile.TemporaryDirectory(prefix="okms-onboarding-") as temporary:
        scratch = Path(temporary)
        for profile in PROFILES:
            source = root / "templates" / profile / "docs"
            for mode in ("fresh", "empty-docs", "existing-docs"):
                project = scratch / f"{profile}-{mode}"
                project.mkdir()
                if mode != "fresh":
                    (project / "docs").mkdir()
                if mode == "existing-docs":
                    (project / "docs/README.md").write_text("Keep my existing docs.\n")
                (project / "AGENTS.md").write_text("# Project rules\n\nKeep my existing instructions.\n")
                destination = fixture_adopt(source, project)
                expected = project / ("docs/okms" if mode == "existing-docs" else "docs")
                assert destination == expected
                fixture = Checker(destination)
                fixture.load()
                fixture.check_links()
                fixture.check_bundle(destination)
                assert not fixture.errors, fixture.errors
                context = destination / "context.md"
                context.write_text(context.read_text().replace("{{PROJECT_PURPOSE_AND_AUDIENCE}}", "Project-owned context."))
                (destination / "work/project-owned.txt").write_text("Keep my active work.\n")
                snapshot = {p: p.read_bytes() for p in project.rglob("*") if p.is_file()}
                # A repeated request, including another profile, must reuse the installed one.
                assert fixture_adopt(source, project) == destination
                other = "brownfield" if profile != "brownfield" else "lite"
                assert fixture_adopt(root / "templates" / other / "docs", project) == destination
                assert snapshot == {p: p.read_bytes() for p in project.rglob("*") if p.is_file()}
                assert (project / "AGENTS.md").read_text().count("For substantive project tasks,") == 1
                scenarios += 1
            conflict = scratch / f"{profile}-occupied"
            (conflict / "docs/okms").mkdir(parents=True)
            sentinel = conflict / "docs/okms/owned.txt"
            sentinel.write_text("Keep my file.\n")
            try:
                fixture_adopt(source, conflict)
            except ValueError:
                assert sentinel.read_text() == "Keep my file.\n"
                assert not (conflict / "AGENTS.md").exists()
            else:
                raise AssertionError("occupied destination was overwritten")
            scenarios += 1
    return scenarios


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    root = parser.parse_args().root.resolve()
    checker = Checker(root)
    checker.load()
    checker.check_links()
    bundles = [root / "docs"] + [root / "templates" / p / "docs" for p in PROFILES] + [root / "examples" / p for p in PROFILES]
    for bundle in bundles:
        checker.check_bundle(bundle)
    if not checker.errors:
        checker.check_profiles()
    scenarios = 0
    if not checker.errors:
        try:
            scenarios = onboarding_smoke(root)
        except (AssertionError, ValueError, OSError) as exc:
            checker.error(root, f"onboarding fixture failed: {exc}")
    if checker.errors:
        for error in checker.errors:
            print(f"FAIL {error}", file=sys.stderr)
        return 1
    print(f"PASS: {len(checker.documents)} Markdown files, {len(bundles)} OKF bundles, 3 standalone payloads, {scenarios} onboarding scenarios.")
    print("This command checks documents and fixtures; it does not run agent pilots or example application tests.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
