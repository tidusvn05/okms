---
type: MicroSpec
title: P002-MS02 · Execute and grade independent pilots
description: Run fresh agent conversations and assess actual application behavior, workflow order, recovery, and evidence honesty.
---

# P002-MS02 · Execute and grade independent pilots

## Intent

Observe the distributed workflows in actual agent sessions, including recovery and unavailable verification, and distinguish successful code from compliance with the saved-document loop.

## Constraints

- Always: inspect unexpected grades against the raw trace and preserve the original run when correcting a grader or template defect.
- Always: resume with a fresh conversation and only a task pointer; measure history reads from emitted evidence with explicit limits.
- Never: weaken behavior expectations, report the intentionally unavailable gate as passed, or substitute simulation for a missing session.

## Acceptance

- Given existing docs and instructions, When setup runs twice, Then the selected namespaced profile and original content survive without duplicate pointers.
- Given two dependent Plan-first outcomes, When the first session stops as requested and another resumes, Then the first remains complete, the second spec is created when needed, and independent parser/endpoint checks pass.
- Given Brownfield endpoints, When validation is shared, Then an observed baseline precedes code edits and the independent compatibility matrix still passes.
- Given an unavailable required gate, When the agent implements the fix and checks it, Then the protected gate is attempted, its failure is recorded, and work remains incomplete with a blocker.

## Verify

Run the opt-in pilot runner, grade all seven fresh conversations, inspect command/file-change events and snapshots, and rerun independently specified behavior matrices and original project tests. Record failed or inconclusive criteria honestly; rerun affected scenarios only when a correction requires new agent evidence.
