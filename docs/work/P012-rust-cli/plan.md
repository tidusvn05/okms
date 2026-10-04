---
type: Plan
title: P012 · Standalone Rust CLI
description: Migrate the complete Hybrid Team CLI and runtime to Rust, verify native behavior, and publish a regular release.
work_status: in_progress
---

# P012 · Standalone Rust CLI

## Goal

Deliver a standalone okms Rust binary for complete Hybrid Team setup and coordination without Python, integrate the user's two reviewed portable-profile PRs, and complete the authorized spike and official GitHub release after verification.

Out of scope: unrelated portable contract changes, automatic upgrades of existing installations, credential changes, native trust bypass, and unsupported remote/desktop integrations.

## Baseline

Main is clean at 1d0716b. The checker passes 183 documents/seven bundles and all 82 tests pass. Hybrid Team 0.1.0 is a published Python prerelease with preserved assets; current release automation always publishes experimental prereleases. The runtime has 15 JSON commands, transactional SQLite ownership/messages/events, preserving adoption, dirty-code worktrees, bounded mixed-provider drivers, exact resume, and gated integration/checkpoints. The earlier mixed matrix passed selected cases before the final Codex guidance correction; a complete final-payload matrix remains necessary.

## Compatibility

Preserve JSON envelopes, identity fencing, SQLite schema, plan-owned progress, scoped writes, root HEAD/index, mandatory gates, actual check evidence, and existing project documents/native settings. Replace Python entrypoints and installed helper commands with Rust okms for new installations. Retain the 0.1.0 prerelease and historical observations. Existing Python copies require an explicit reviewed upgrade; repeated setup never converts them silently.

## Approach

- The user selected full CLI/runtime migration, rather than a Rust wrapper around Python.
- Use implementation for the runtime, adoption, distribution, and evidence-harness changes; save each spec immediately before executing it.
- Implement a Rust crate with an embedded documentation/native/skill payload, bundled SQLite, JSON command inputs, and project-local executable helpers.
- Port operational contracts and exercise the Rust binary through the existing independently specified regression scenarios; retain the Python baseline as historical evidence until comparisons are complete.
- Build native Linux/macOS archives through Actions, replace the Python installer with checked binary installation, and publish a new independent Hybrid Team version after final checks.
- Run the explicitly authorized mixed-provider spike against the final Rust payload; preserve all failed attempts and diagnose failures before rerunning. Automatic hook trust remains user-owned.
- Activate CI/release workflows, verify published asset downloads and Python-free installation, and record the supported release scope and any measured limitations.
- The user additionally authorized reviewing and merging stacked PRs #1 (portable metadata 0.4.1) and #2 (project-convention setup). Review exact heads, resolve overlaps with the Rust migration, verify the combined tree and preserve the PR histories before final release. Concurrent plans retain their assigned IDs in distinct existing directories; explicit paths identify their scope.

## Work

| Spec | Depends on | State | Evidence |
| --- | --- | --- | --- |
| [P012-MS01 · Rust runtime foundation](P012-MS01-foundation.md) | — | done | Cargo check and five native foundation tests pass: concurrent processes, stale-token handoff/recovery, messages/alias/ack/deduplication, JSON boundaries, secret-free status and escaped-state paths. Initial concurrent journal-mode contention was reproduced and fixed with bounded retry. Checker passes 186 documents. |
| [P012-MS02 · Worktrees, provider drivers, integration and checkpoints](P012-MS02-operations.md) | P012-MS01 | done | All 21 retained operational scenarios pass through the real Rust binary with fake providers; five native foundation tests and clippy -D warnings pass. Rust implements snapshots, drivers, hooks, integration, mandatory checks and checkpoints. Fixtures use Python only for transport/check applications and observing the compatible database. |
| [P012-MS03 · Embedded preserving setup and native configuration](P012-MS03-adoption.md) | P012-MS02 | done | Six native adoption scenarios and five adapted pilot controls pass, including source removal with no Python in PATH, collision/preservation/preflight checks, ignored worker overlays and legacy-upgrade refusal. The active payload contains no Python files; the old checksum-pinned distribution remains a comparison fixture. Checker passes 188 documents; clippy passes. |
| [P012-MS04 · Binary installation, CI and regular tag releases](P012-MS04-distribution.md) | P012-MS03 | in_progress | Seven binary-distribution scenarios pass, including Python-free setup and independent integrity/extraction controls. All 116 maintainer tests, six native Rust tests, minimum Rust 1.88 compilation, fmt/clippy, shell syntax and actionlint pass; checker passes 190 documents. Two checker-fixture errors were corrected by including the new Rust source metadata. Pending observed Actions build/rehearsal. |
| [P012-MS05 · Bounded descendant cleanup](P012-MS05-processes.md) | P012-MS02 | done | The real descendant-write regression initially failed (seven writes after cancellation instead of one); repaired group cleanup passes in 5.34s. All 116 maintainer scenarios and six native Rust tests pass, with no surviving reproduction process. Minimum Rust 1.88, fmt and clippy pass. |
| [P012-MS07 · Review and merge the portable PRs](P012-MS07-pull-requests.md) | — | in_progress | PR #1 head 41d9f41 and stacked #2 head 8ad8c6c have passing old CI. Reviewing current diff/compatibility and resolving the Rust overlaps before merging. |
| P012-MS06 · Final Rust mixed-provider spike and publication | P012-MS04, P012-MS05, P012-MS07 | planned | Pending. |

## Resume

- Current: P012-MS07; the P012-MS04 Actions rehearsal is also running.
- Next: review and integrate PR #1 before #2, check their combined tree, then freeze the final release binary for native evaluation.
- Blocker: none.

## Result

Pending.
