---
type: MicroSpec
kind: implementation
title: P003-MS02 · Route tasks and recover goal loops
description: Integrate selective task routing and bounded Goal execution into all profiles without changing historical work.
---

# P003-MS02 · Route tasks and recover goal loops

## Intent

Let agents select the next task contract automatically, execute it under the installed profile, and continue explicitly requested goals using persistent completion and budget checks.

## Constraints

- Always: honor explicit scope, preserve installed profiles and existing context, and materialize only ready work.
- Always: reserve an attempt before executing it; retain counters and the same interrupted attempt on recovery.
- Never: reset a budget silently, mark exhausted work done, activate a native capability that is unavailable, or require every short reply to create documents.

## Acceptance

- Given a substantive task, When routing runs, Then context and open checkpoints determine the next outcome and only its selected blueprint is loaded.
- Given an explicit portable goal, When one attempt finishes, Then verification and counters are checkpointed before another attempt; limit exhaustion leaves incomplete scope open with a next action.
- Given a fresh continuation, When the checkpoint is read, Then completed items and consumed attempts survive, and only an explicit budget extension raises the limit.
- Given a native-capable agent or an unavailable capability, When native execution is considered, Then the actual integration rules are followed or portable execution is recorded honestly.

## Verify

Review profile differences, portable links, Goal recovery and native mapping guidance, and illustrative examples. Subsequent checks exercise rendered contracts and real agent routing/loop sessions; do not claim those sessions have already run.
