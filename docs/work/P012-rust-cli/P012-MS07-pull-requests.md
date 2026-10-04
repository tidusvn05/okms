---
type: MicroSpec
kind: implementation
title: P012-MS07 · Review and merge portable changes
description: Integrate the user's stacked metadata and setup-convention PRs after exact-source review and compatible checks.
---

# P012-MS07 · Review and merge portable changes

## Intent

Merge PR #1 and its dependent PR #2 when review and actual checks support including their changes in the upcoming release.

## Constraints

- Always: review exact head/diff, merge the parent first, preserve Rust runtime/distribution behavior and prior installation recognition, and retain author/history paths.
- Never: treat old-branch CI as proof of the combined tree, change unrelated task contracts, or claim unobserved agent compliance.

## Acceptance

- Record review scope, supported findings or absence of findings, concrete checks and limits before merging.
- Resolve overlapping docs/checker changes without reverting Rust or portable 0.4.1 behavior; check MkDocs acceptance in a disposable project and retain legacy-recognition controls.
- Required maintainer/Rust checks pass on the integrated source, both PRs become merged into main in dependency order, and CI verifies the resulting source.
- Release notes account for both independently versioned profiles; native Rust evaluation uses the final embedded payload.

## Verify

- Method: exact PR diff/code review, isolated integration worktree, temporary MkDocs before/after build, document checker, full regression suite, cargo tests/clippy/fmt and observed GitHub merge/check states.
- Expected: reviewed compatible PRs merged with truthful evidence and remaining native activation limits.
