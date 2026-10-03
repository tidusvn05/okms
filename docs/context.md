---
type: Context
title: okms project context
description: Locate the template payloads, durable authoring rules, and checks used to maintain okms.
---

# okms project context

## Purpose

Publish lightweight behavior contracts and recoverable workflows for coding agents working in any project. The initial release contains Lite, Plan-first, and Brownfield templates, with optional okbase support.

## Durable rules

- All distributed content is in English.
- Each copied template works with ordinary file reads and contains its own workflow and blueprints.
- Every micro spec has Intent, Constraints, Acceptance, and Verify.
- Plans own work-item progress and evidence; historical specs are snapshots of work.
- Adoption preserves existing docs, agent instructions, and active work.
- Verification evidence must distinguish actual results from illustrative or skipped checks.

## Verification

- Required: `.venv/bin/python scripts/check_docs.py` after creating the maintainer environment described in CONTRIBUTING.md.
- Optional integration: run `okbase -b PATH lint --level L1` against `docs/`, each template's `docs/`, and the example bundles.
- Review setup in an empty project and one with existing docs and agent instructions; resume a saved plan without relying on chat history.
- Explicit agent evaluation: run `.venv/bin/python evals/run_agent_pilot.py` when assessing workflow changes; this uses the installed Codex CLI and existing login in disposable projects. Ordinary document checks never invoke it.

## Locations

- Distribution payloads: `templates/`.
- Worked examples: `examples/`.
- Shared formats: [document blueprints](_templates/index.md).
- Release implementation history: [work](work/index.md).
