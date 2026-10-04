---
type: MicroSpec
kind: implementation
title: P009-MS01 · Recoverable mixed-provider runtime
description: Coordinate scoped Codex and Claude Code assignments with durable delivery, isolated worktrees, and verified integration.
---

# P009-MS01 · Recoverable mixed-provider runtime

## Intent

Provide a project-local runtime that lets one CLI coordinator manage recoverable Codex and Claude Code workers, including peer communication and isolated edits.

## Constraints

- Always: preserve root branch, staging, original edits, native permissions, and plan-owned progress.
- Always: reject stale coordinator operations and retain actual execution evidence and incomplete outcomes.
- Never: equate a successful provider turn or ready result with completed acceptance, silently retry partial work, or use a latest-session shortcut.

## Acceptance

- Concurrent joins select one coordinator; handoff invalidates its predecessor's authority.
- Addressed messages persist, support acknowledgment and deduplication, and survive fresh processes.
- Parallel workers share a current-code baseline in independent worktrees; out-of-scope changes and changed integration targets prevent application.
- Combined changes are checked in an integration worktree before application while preserving staging; failed checks remain incomplete.
- Provider sessions, results, timeout, denial, stop, and explicit resume retain identifiers and evidence.

## Verify

- Method: focused runtime unit/integration tests in disposable Git projects, followed by the repository's required checks.
- Expected: ownership, delivery, preservation, execution, and failure invariants pass without invoking real agents in ordinary tests.
- Tests: real provider behavior is additionally evaluated under P009-MS04; fixtures do not establish native CLI compliance.
