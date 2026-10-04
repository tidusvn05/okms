---
type: Context
title: okms project context
description: Locate the template payloads, durable authoring rules, and checks used to maintain okms.
---

# okms project context

## Purpose

Publish task contracts and recoverable workflows for agents working in any project. Lite and Plan-first 0.4.0 remain portable Markdown with eight kinds and optional delegation. Hybrid Team 0.2.0 is an opt-in standalone Rust/Git runtime for local Codex and Claude Code workers; its independent version does not upgrade portable copies.

## Durable rules

- All distributed content is in English.
- Each copied template works with ordinary file reads and contains its own workflow and blueprints.
- Every micro spec has Intent, Constraints, Acceptance, and Verify.
- Plans own work-item progress and evidence; historical specs are snapshots of work.
- Adoption preserves existing docs, agent instructions, and active work.
- Verification evidence must distinguish actual results from illustrative or skipped checks.
- Task kind selects a blueprint independently of profile; preserve kindless history and load only the needed contract.
- Roles, delegation briefs, and worker results do not own progress. Load the delegation guide only for authorized assignments; the existing progress owner verifies combined acceptance and records recovery.
- Record baseline evidence and compatibility obligations when changing or deciding changes to existing contracts; keep the documentation proportional to the affected scope.
- Explicit Goals retain consumed attempts, linked plans, stop reasons, and checkpoints. Native execution requires a real supported integration.
- Hybrid Team separates TeamSpec policy, plan-owned progress, operational AgentRun state, directed Messages, and append-only Events. Preserve root staging/edits, fence coordinator operations, and require combined/root checks before completion.
- Hybrid Team publication uses new hybrid-team-vX.Y.Z tags matching Cargo and template versions. Check and rehearse before a scoped write-permission job publishes regular releases; retain existing tags/assets. Default installation selects the latest regular release; numeric pins and offline setup remain supported.

## Verification

- Required: `.venv/bin/python scripts/check_docs.py` after creating the maintainer environment described in CONTRIBUTING.md.
- Required for contract/checker changes: `.venv/bin/python -m unittest discover -s tests -v`.
- Required for Rust changes: `cargo build --locked`, `cargo fmt --all -- --check`, `cargo test --locked` and `cargo clippy --locked --all-targets -- -D warnings`.
- Optional integration: run `okbase -b PATH lint --level L1` against `docs/`, each template's `docs/`, and the example bundles.
- Review setup in an empty project and one with existing docs and agent instructions; resume a saved plan without relying on chat history.
- Explicit agent evaluation: run `.venv/bin/python evals/run_agent_pilot.py` when assessing workflow changes; this uses the installed Codex CLI and existing login in disposable projects. Ordinary document checks never invoke it.
- Review/delegation evaluation: run `.venv/bin/python evals/run_review_pilot.py` for disposable Codex/Claude Code sessions with existing authentication; see `evals/README.md` for scope and evidence handling.
- Hybrid Team evaluation: run `.venv/bin/python evals/run_hybrid_pilot.py` only for explicit mixed-CLI observations. Ordinary checks use fake transports; preserve live failures, source fingerprints, native IDs, and startup limits. See `evals/hybrid-report.md` for scoped passes and retained limits.

## Locations

- Distribution payloads: `templates/`.
- Worked examples: `examples/`.
- Shared formats: [document blueprints](_templates/index.md).
- Release implementation history: [work](work/index.md).
- Rust runtime and preserving setup: `src/`; embedded payload: `templates/hybrid-team/`; native binary scenarios: `tests/test_rust_runtime.py`, `tests/test_rust_adoption.py` and `tests/foundation.rs`. Immutable Python comparisons: `tests/fixtures/`.
- Binary installer: `install.sh`; deterministic asset builder: `scripts/build_hybrid_release.py`; distribution checks: `tests/test_rust_release.py`. CI and tag publication: `.github/workflows/`; maintainer procedure: `CONTRIBUTING.md`. Publication requires the user's authorization and preserves prior tags/assets.
