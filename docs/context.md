---
type: Context
title: okms project context
description: Locate the template payloads, durable authoring rules, and checks used to maintain okms.
---

# okms project context

## Purpose

Publish lightweight task contracts and recoverable workflows for agents working in any project. Version 0.3 offers Lite and Plan-first, applies existing-system obligations by affected scope, retains selective task routing and bounded Goal contracts, and keeps okbase optional.

## Durable rules

- All distributed content is in English.
- Each copied template works with ordinary file reads and contains its own workflow and blueprints.
- Every micro spec has Intent, Constraints, Acceptance, and Verify.
- Plans own work-item progress and evidence; historical specs are snapshots of work.
- Adoption preserves existing docs, agent instructions, and active work.
- Verification evidence must distinguish actual results from illustrative or skipped checks.
- Task kind selects a blueprint independently of profile; preserve kindless history and load only the needed contract.
- Record baseline evidence and compatibility obligations when changing or deciding changes to existing contracts; keep the documentation proportional to the affected scope.
- Explicit Goals retain consumed attempts, linked plans, stop reasons, and checkpoints. Native execution requires a real supported integration.

## Verification

- Required: `.venv/bin/python scripts/check_docs.py` after creating the maintainer environment described in CONTRIBUTING.md.
- Required for contract/checker changes: `.venv/bin/python -m unittest discover -s tests -v`.
- Optional integration: run `okbase -b PATH lint --level L1` against `docs/`, each template's `docs/`, and the example bundles.
- Review setup in an empty project and one with existing docs and agent instructions; resume a saved plan without relying on chat history.
- Explicit agent evaluation: run `.venv/bin/python evals/run_agent_pilot.py` when assessing workflow changes; this uses the installed Codex CLI and existing login in disposable projects. Ordinary document checks never invoke it.

## Locations

- Distribution payloads: `templates/`.
- Worked examples: `examples/`.
- Shared formats: [document blueprints](_templates/index.md).
- Release implementation history: [work](work/index.md).
