---
type: TeamSpec
title: Project Hybrid Team policy
description: Define project-owned coordination, provider routing, communication, evidence, integration, and recovery responsibilities.
---

# Project Hybrid Team policy

## Purpose

Complete the user's scoped project work through verified micro specs and recoverable coordination. Follow existing project instructions and [context](context.md). Opening a session registers its role; the user's task supplies execution scope.

## Members

One active coordinator manages shared contracts/progress. Codex and Claude Code workers implement or inspect bounded scopes; a reviewer assesses actual revisions. Native helpers return to their parent. Defaults and approved checks live in `.okms/team.json`; refer to that file rather than duplicating operational values here.

## Routing

Use both providers for independent ready scopes when useful. With one write scope, use the other provider for review/analysis. Choose by assignment needs and observed capabilities, preserving the user's model choices. Keep overlapping writes and unresolved dependencies ordered. Never expand scope to keep a worker busy.

## Communication

Use addressed runtime messages for questions, answers, and proposals. Acknowledge processed messages and link replies. Peer exchanges cannot change parent acceptance, allocate new scopes, or authorize integration. Record significant observations through artifacts/results; the runtime persists delivery/events.

## Integration

Only the current coordinator dispatches workers, updates shared progress, and integrates. Review returned diffs and missing evidence, check combined behavior, and verify the actual root. Keep plan-owned progress incomplete until acceptance is supported. Preserve original code, staging, existing instructions, and historical records.

## Recovery

Read the plan checkpoint and actual working tree before continuing. Use saved run/session IDs and retained worktrees. Explicitly hand off or recover ownership and fence stale operations. Preserve failed evidence, unavailable checks, consumed time, and concrete next actions. See [the runtime guide](team.md).
