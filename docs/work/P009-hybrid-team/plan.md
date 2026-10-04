---
type: Plan
title: P009 · Hybrid Team
description: Implement a self-contained optional profile for Codex and Claude Code workers with local coordination and truthful verification.
work_status: done
---

# P009 · Hybrid Team

## Goal

Deliver the authorized Hybrid Team design: CLI coordinators, a project-local runtime, isolated parallel writers, current-code snapshots, persistent messages/events, and recoverable progress.

Out of scope: remote workers, desktop/IDE integration, automatic provider authentication, and implicit upgrades of Lite or Plan-first.

## Baseline

The working tree contains completed P007/P008 changes that must be preserved. Lite and Plan-first contain 21 Markdown files each and eight task kinds. Before this change, `.venv/bin/python scripts/check_docs.py` passes 134 documents, six bundles, two payloads, and eight onboarding scenarios; `.venv/bin/python -m unittest discover -s tests -v` passes 37 tests. Existing delegation orders edits within one spec and does not launch mixed-provider workers.

## Compatibility

Retain both portable payloads and their 0.4.0 contracts, existing task kinds, plan columns, assigned IDs, active work, and history. Hybrid Team is an explicit opt-in 0.1.0 profile with runtime dependencies. Adoption preserves project instructions and configuration. Plans remain the progress owner; runtime state describes sessions and delivery.

## Approach

- Use implementation contracts for runtime, adoption, and publication, followed by observed pilot evidence. Save each next spec before its execution.
- Implement a Python 3.10+ standard-library runtime with SQLite, JSON command input, ownership tokens, provider adapters, and Git worktrees.
- Snapshot current tracked and nonignored untracked content through an alternate Git index without altering user staging or branches.
- Default to two workers and 30 minutes per assignment, preserving CLI login/model configuration and never bypassing native permission or hook trust requirements.
- Validate operational invariants using disposable Git projects and fake transports, then execute real mixed-provider pilots with retained raw traces.

## Work

| Spec | Depends on | State | Evidence |
| --- | --- | --- | --- |
| [P009-MS01 · Recoverable runtime](P009-MS01-runtime.md) | — | done | 20 runtime scenarios and 37 retained tests pass; checker passes 161 documents/seven bundles; git diff --check passes. |
| [P009-MS02 · Self-contained setup and agent contracts](P009-MS02-setup-contracts.md) | P009-MS01 | done | Six adoption scenarios and all 63 tests pass; copied helper works after removing source; both skills validate; checker passes 170 documents/seven bundles. |
| [P009-MS03 · Publication and repository checks](P009-MS03-publication.md) | P009-MS02 | done | Checker passes 172 documents/seven bundles; all 67 tests and git diff --check pass; fixture-only runner prepares all three cases without provider sessions. |
| [P009-MS04 · Live pilots and observed evidence](P009-MS04-pilots.md) | P009-MS03 | done | evals/hybrid-report.md and hybrid-results.json retain eight executed cases: three scoped passes, four failures, one interruption. Both coordinator directions pass 15/15 independent root cases; the failed mandatory gate leaves both rows blocked with no application. Final Codex guidance passes an actual worker probe and seven independent cases without coordinator input; Claude's schema probe passes. All 69 tests, both skill validations, checker (174 documents/seven bundles), and git diff --check pass. |

## Resume

- Current: none; all scoped work is complete.
- Next: none.
- Blocker: none.

## Result

Published experimental Hybrid Team 0.1.0 with a preserving project installer, self-contained policy/roles/skills, two mixed-provider workers, isolated dirty-code snapshots, persistent messages/events, exact-session recovery, fenced handoff, and verified integration/checkpoints. Lite and Plan-first retain their portable 0.4.0 contracts and eight task kinds.

Live observations support selected local CLI behavior and retain failures. The final provider-specific prompt correction has component evidence; the full mixed matrix was not rerun afterward. Codex hooks still require native trust review; pilots use explicit actual-ID bootstrap. Native Codex custom-role discovery, automatic trusted-hook startup, native skill activation, other platforms/models, and desktop/IDE/remote integrations remain outside the observed evidence. Ordinary tests/checker start no provider task session; worked examples remain illustrative.
