---
type: MicroSpec
kind: implementation
title: P012-MS03 · Embedded preserving setup
description: Install an embedded Rust Hybrid Team payload and native helper commands while preserving project ownership.
---

# P012-MS03 · Embedded preserving setup

## Intent

Make okms init install its embedded documentation, binary, native roles/hooks, and skills without Python or a source checkout.

## Constraints

- Always: preflight paths/configuration/collisions before writes; preserve existing docs, instructions, settings, staging, active work, and customizations.
- Always: keep copied docs self-contained, select available role/skill names, and use the project-local Rust helper in native instructions.
- Never: launch provider task sessions during setup, enable untrusted hooks, copy credentials, or silently upgrade the Python installation.

## Acceptance

- A copied binary initializes a fresh/occupied-docs project, supports dry-run and custom docs, and remains functional after the source binary/checkout is removed.
- Repeated initialization is byte-preserving; project settings and custom edits survive, native collisions receive stable alternative names, and unmanaged conflicts/malformed settings/escaped paths fail before writes.
- Ignored binary/config/docs/native instructions remain available in scoped worker worktrees; installed startup commands execute the Rust helper.
- The active payload contains no Python runtime/setup files. A checksum-pinned historical fixture retains the old behavior for comparison, and maintainers check Rust metadata and embedded source contracts.

## Verify

- Method: cargo build/tests, native adoption subprocess scenarios, retained Python-baseline comparisons, the document checker, and fixture/grader controls adapted to Rust setup.
- Expected: Python-free setup/runtime with intact project ownership and truthful activation limits.
- Tests: fresh/repeat/dry-run/source removal, collisions/settings/hooks, preflight failure, symlink/path boundaries, ignored overlays, and explicit legacy-upgrade refusal.
