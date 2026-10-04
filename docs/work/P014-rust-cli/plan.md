---
type: Plan
title: P014 · Standalone Rust CLI
description: Migrate the complete Hybrid Team CLI and runtime to Rust, verify native behavior, and publish a regular release.
work_status: in_progress
---

# P014 · Standalone Rust CLI

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
- The user additionally authorized reviewing and merging stacked PRs #1 (portable metadata 0.4.1) and #2 (project-convention setup). Review exact heads, resolve overlaps with the Rust migration, verify the combined tree and preserve the PR histories before final release. PRs already allocated P012/P013 before this migration; the open Rust plan was moved to P014 after the combined checker exposed duplicate IDs. PR history paths/IDs remain unchanged.

## Work

| Spec | Depends on | State | Evidence |
| --- | --- | --- | --- |
| [P014-MS01 · Rust runtime foundation](P014-MS01-foundation.md) | — | done | Cargo check and five native foundation tests pass: concurrent processes, stale-token handoff/recovery, messages/alias/ack/deduplication, JSON boundaries, secret-free status and escaped-state paths. Initial concurrent journal-mode contention was reproduced and fixed with bounded retry. Checker passes 186 documents. |
| [P014-MS02 · Worktrees, provider drivers, integration and checkpoints](P014-MS02-operations.md) | P014-MS01 | done | All 21 retained operational scenarios pass through the real Rust binary with fake providers; five native foundation tests and clippy -D warnings pass. Rust implements snapshots, drivers, hooks, integration, mandatory checks and checkpoints. Fixtures use Python only for transport/check applications and observing the compatible database. |
| [P014-MS03 · Embedded preserving setup and native configuration](P014-MS03-adoption.md) | P014-MS02 | done | Six native adoption scenarios and five adapted pilot controls pass, including source removal with no Python in PATH, collision/preservation/preflight checks, ignored worker overlays and legacy-upgrade refusal. The active payload contains no Python files; the old checksum-pinned distribution remains a comparison fixture. Checker passes 188 documents; clippy passes. |
| [P014-MS04 · Binary installation, CI and regular tag releases](P014-MS04-distribution.md) | P014-MS03 | done | Seven binary-distribution scenarios pass; all 116 maintainer and six native Rust tests, minimum Rust 1.88, fmt/clippy, shell syntax and actionlint pass. Checker passes 190 documents. [Actions rehearsal](https://github.com/tidusvn05/okms/actions/runs/37201149119) builds/smoke-tests all four platforms and passes prepare; publish is skipped. [CI](https://github.com/tidusvn05/okms/actions/runs/37201141439) passes both toolchain/Python combinations. |
| [P014-MS05 · Bounded descendant cleanup](P014-MS05-processes.md) | P014-MS02 | done | The real descendant-write regression initially failed (seven writes after cancellation instead of one); repaired group cleanup passes in 5.34s. All 116 maintainer scenarios and six native Rust tests pass, with no surviving reproduction process. Minimum Rust 1.88, fmt and clippy pass. |
| [P014-MS07 · Review and merge the portable PRs](P014-MS07-pull-requests.md) | — | done | [Review](PR-review.md) finds no blocking proposal defect. PR #1/#2 integrated trees pass 118 tests, real MkDocs collision/repaired builds, prompt extraction, 197 documents and ten onboarding scenarios. Exact heads 5e6f64e/7cc1493 pass both CI combinations; merges 0dfe3ea/e0440a8 are observed. Main's resulting tree equals the checked #2 head. |
| [P014-MS08 · Hybrid metadata compatibility](P014-MS08-metadata.md) | P014-MS07 | done | Actual Hybrid MkDocs 1.6.1 strict build reproduces TemplateNotFound before the rename and passes afterward. Seven adoption scenarios include matching occupied docs and repeated byte preservation; all 119 maintainer and six Rust tests pass. Checker passes 199 documents/ten onboarding scenarios, tag validation still matches 0.2.0, and fmt/clippy pass. Runtime JSON fields and frozen 0.1.0 assets are retained. |
| [P014-MS06 · Final Rust mixed-provider spike and publication](P014-MS06-release.md) | P014-MS04, P014-MS05, P014-MS07, P014-MS08 | in_progress | All 121 maintainer tests and six Rust tests pass, with minimum Rust/fmt/clippy and checker (200 documents/ten onboarding scenarios). Provenance guards reject changed binaries and grade saved evidence without a current executable. A control exposed the grader's lexical-directory chronology assumption; actual invocation timestamps now order turns while wrong native IDs still fail. Pending final downloaded binary, real native matrix and regular publication. |

## Resume

- Current: P014-MS06.
- Next: verify evidence/provenance guards, obtain the final Actions binary, then run native cases and publish the checked regular release.
- Blocker: none.

## Result

Pending.
