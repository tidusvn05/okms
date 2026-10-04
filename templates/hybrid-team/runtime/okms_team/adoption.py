"""Preflighted project adoption; no provider session, global config, or auth writes."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .state import TeamError


def read_json(path, default):
    if not path.exists():
        return default
    try:
        value = json.loads(path.read_text())
    except ValueError as error:
        raise TeamError("Existing JSON needs review; unchanged: " + str(path)) from error
    if not isinstance(value, dict):
        raise TeamError("Expected an existing JSON object; unchanged: " + str(path))
    return value


def safe_path(project, relative):
    path = project / relative
    if not path.resolve().is_relative_to(project):
        raise TeamError("Installation path escapes project; unchanged: " + relative)
    return path


def merge_hooks(path, provider):
    value = read_json(path, {})
    hooks = value.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise TeamError("Existing hooks must be an object; unchanged: " + str(path))
    command = 'python3 "$(git rev-parse --show-toplevel)/.okms/team.py" hook --provider ' + provider
    for event in ("SessionStart", "UserPromptSubmit", "PostToolUse", "SessionEnd"):
        groups = hooks.setdefault(event, [])
        if not isinstance(groups, list):
            raise TeamError("Existing hook groups must be arrays; unchanged: " + str(path))
        if any(not isinstance(group, dict) or not isinstance(group.get("hooks", []), list) for group in groups):
            raise TeamError("Existing hook groups need review; unchanged: " + str(path))
        matching = any(any(isinstance(item, dict) and item.get("command") == command
                           for item in group.get("hooks", [])) for group in groups)
        if not matching:
            groups.append({"hooks": [{"type": "command", "command": command, "timeout": 5}]})
    if path.exists() and value == read_json(path, {}):
        return path.read_bytes()
    return (json.dumps(value, indent=2) + "\n").encode()


def install(source, project, docs=None, *, dry_run=False):
    source, project = Path(source).resolve(), Path(project).resolve()
    if not project.is_dir():
        raise TeamError("The destination project must already exist.")
    manifest_path = safe_path(project, ".okms/install.json")
    manifest = read_json(manifest_path, {})
    if manifest and manifest.get("profile") != "hybrid-team":
        raise TeamError("Existing .okms installation is not Hybrid Team; preserve it and resolve the namespace explicitly.")
    if manifest and manifest.get("version") != "0.1.0":
        raise TeamError("Repeated setup does not upgrade an existing profile; review the version change explicitly.")
    if manifest:
        selected = manifest["docs_path"]
        if docs and docs != selected:
            raise TeamError("Repeated setup preserves the installed documentation path.")
    elif docs:
        selected = docs
    else:
        selected = "docs"
        path = safe_path(project, selected)
        if path.exists() and any(path.iterdir()):
            selected = "docs/okms"
            path = safe_path(project, selected)
            if path.exists() and any(path.iterdir()):
                selected = "docs/okms-hybrid"
                number = 2
                while safe_path(project, selected).exists() and any(safe_path(project, selected).iterdir()):
                    selected = "docs/okms-hybrid-" + str(number)
                    number += 1
    if (not isinstance(selected, str) or not selected or Path(selected).is_absolute() or
            any(part in {"", ".", ".."} for part in selected.split("/")) or
            selected.split("/")[0] in {".git", ".okms", ".codex", ".claude", ".agents"} or "\\" in selected):
        raise TeamError("Documentation path must be a project-relative documentation directory.")
    destination = safe_path(project, selected)
    if destination.exists() and not destination.is_dir():
        raise TeamError("Documentation destination is not a directory; unchanged.")
    if not manifest and destination.exists() and any(destination.iterdir()):
        workflow = destination / "workflow.md"
        if not workflow.is_file() or not re.search(r"^template:\s*hybrid-team\s*$", workflow.read_text(), re.M):
            raise TeamError("Explicit documentation destination is occupied; unchanged.")
    assets, drift = {}, []
    for path in (source / "runtime").rglob("*"):
        if path.is_file() and path.suffix == ".py" and "__pycache__" not in path.parts:
            assets[".okms/" + path.relative_to(source / "runtime").as_posix()] = path.read_bytes()
    for path in (source / "docs").rglob("*.md"):
        assets[selected + "/" + path.relative_to(source / "docs").as_posix()] = path.read_bytes()
    roles = manifest.get("native_roles", {})
    for provider in ("codex", "claude"):
        for role in ("worker", "reviewer"):
            key = provider + "_" + role
            extension = ".toml" if provider == "codex" else ".md"
            body = (source / "native" / provider / ("okms-" + role + extension)).read_text()
            name = roles.get(key, "okms-" + role)
            count = 2
            while True:
                relative = "." + provider + "/agents/" + name + extension if provider == "codex" else ".claude/agents/" + name + extension
                target = safe_path(project, relative)
                rendered = body.replace("okms-" + role, name)
                if relative in manifest.get("files", {}) or not target.exists() or target.read_text() == rendered:
                    break
                name = "okms-team-" + role + "-" + str(count)
                count += 1
            roles[key] = name
            assets[relative] = rendered.encode()
    for skill in ("okms-coordinate", "okms-work"):
        body = (source / "skills" / skill / "SKILL.md").read_text()
        for native in (".agents", ".claude"):
            name = manifest.get("skills", {}).get(native + "/" + skill, skill)
            count = 2
            while True:
                relative = native + "/skills/" + name + "/SKILL.md"
                target = safe_path(project, relative)
                rendered = body.replace("name: " + skill, "name: " + name, 1)
                if relative in manifest.get("files", {}) or not target.exists() or target.read_text() == rendered:
                    break
                name = skill + "-" + str(count)
                count += 1
            assets[relative] = rendered.encode()
            manifest.setdefault("skills", {})[native + "/" + skill] = name
    if not (project / ".okms/team.json").exists():
        config = {"schema_version": 1, "profile": "hybrid-team", "template_version": "0.1.0", "docs_path": selected,
                  "max_workers": 2, "assignment_timeout_seconds": 1800, "checks": [],
                  "providers": {provider: {"command": [provider], "args": [], "worker_role": roles[provider + "_worker"],
                                            "reviewer_role": roles[provider + "_reviewer"]} for provider in ("codex", "claude")}}
        assets[".okms/team.json"] = (json.dumps(config, indent=2) + "\n").encode()
    else:
        config = read_json(safe_path(project, ".okms/team.json"), {})
        if config.get("profile") != "hybrid-team" or config.get("docs_path") != selected:
            raise TeamError("Existing team config is owned by another installation; unchanged.")
    changes = {}
    for relative, body in assets.items():
        target = safe_path(project, relative)
        if target.exists():
            if target.read_bytes() != body:
                if relative.startswith(selected + "/") or relative in manifest.get("files", {}):
                    drift.append(relative)
                    continue
                raise TeamError("Unmanaged runtime file collision; unchanged: " + relative)
        else:
            changes[relative] = body
    for relative, provider in ((".codex/hooks.json", "codex"), (".claude/settings.json", "claude")):
        target = safe_path(project, relative)
        body = merge_hooks(target, provider)
        if not target.exists() or target.read_bytes() != body:
            changes[relative] = body
    config_path = safe_path(project, ".codex/config.toml")
    if not config_path.exists():
        changes[".codex/config.toml"] = b"# Project-owned Codex configuration; Hybrid Team hooks and roles are alongside this file.\n"
    for relative in ("AGENTS.md", "CLAUDE.md"):
        target = safe_path(project, relative)
        current = target.read_text() if target.exists() else ""
        pointer = "Hybrid Team is the explicitly selected team profile. For runtime-coordinated work, follow [its workflow](" + selected + "/workflow.md), starting with [its index](" + selected + "/index.md). Existing project instructions and work records remain applicable."
        if pointer not in current:
            changes[relative] = (current + ("\n" if current else "") + pointer + "\n").encode()
    ignored = safe_path(project, ".gitignore")
    current = ignored.read_text() if ignored.exists() else ""
    if "/.okms/state/" not in current.splitlines():
        changes[".gitignore"] = (current + ("\n" if current and not current.endswith("\n") else "") + "/.okms/state/\n").encode()
    records = dict(manifest.get("files", {}))
    for relative, body in {**assets, **changes}.items():
        records.setdefault(relative, hashlib.sha256(body).hexdigest())
    updated = {"profile": "hybrid-team", "version": "0.1.0", "docs_path": selected,
               "native_roles": roles, "skills": manifest["skills"], "files": records}
    encoded = (json.dumps(updated, indent=2, sort_keys=True) + "\n").encode()
    if not manifest_path.exists() or read_json(manifest_path, {}) != updated:
        changes[".okms/install.json"] = encoded
    result = {"profile": "hybrid-team", "version": "0.1.0", "docs_path": selected, "dry_run": dry_run,
              "changed": sorted(changes), "preserved_project_edits": sorted(drift), "native_roles": roles,
              "next": "Fill actual context/check argv arrays, run doctor, and review native hook trust/loading. Setup launches no agent."}
    for relative in changes:
        target = safe_path(project, relative)
        temporary = target.with_name(target.name + ".okms-new")
        if temporary.exists() or temporary.is_symlink():
            raise TeamError("Temporary setup path is occupied; preserve it: " + str(temporary))
        for parent in target.parents:
            if parent == project:
                break
            if parent.exists() and not parent.is_dir():
                raise TeamError("Installation parent is not a directory; unchanged: " + str(parent))
    if not dry_run:
        for relative, body in changes.items():
            target = safe_path(project, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(target.name + ".okms-new")
            try:
                temporary.write_bytes(body)
                if target.exists():
                    temporary.chmod(target.stat().st_mode & 0o777)
                temporary.replace(target)
            finally:
                temporary.unlink(missing_ok=True)
    return result


def worker_overlay(project, destination):
    """Supply installed instructions omitted by ignore rules, without application files."""
    project, destination = Path(project), Path(destination)
    manifest = read_json(project / ".okms/install.json", {})
    paths = set(manifest.get("files", {}))
    paths.update({".okms/team.json", ".okms/install.json", ".codex/config.toml", ".claude/settings.local.json"})
    docs = manifest.get("docs_path", "docs")
    for relative in paths:
        if not (relative.startswith((".okms/", ".codex/", ".claude/", ".agents/", docs + "/")) or
                relative in {"AGENTS.md", "CLAUDE.md"}):
            continue
        source = safe_path(project, relative)
        target = safe_path(destination, relative)
        if source.is_file() and not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
