---
type: MicroSpec
kind: implementation
title: P012-MS01 · Rust runtime foundation
description: Introduce a standalone Rust command interface and preserve durable ownership, identities, messages, and events.
---

# P012-MS01 · Rust runtime foundation

## Intent

Replace the Python CLI foundation with native Rust operations, preserving the existing JSON and SQLite contracts for coordination.

## Constraints

- Always: authenticate operations, fence stale owners, serialize ownership changes, retain directed durable messages and append-only events.
- Always: accept only object command input and project-bounded paths; emit actionable JSON errors without implying completion.
- Never: invoke Python for runtime operations, bypass native permissions, or change application progress during status/message operations.

## Acceptance

- The compiled okms binary exposes the existing runtime command names, version/help, JSON file/stdin/argument input, project selection, and native identity selection.
- Concurrent joins yield one coordinator; handoff and explicit recovery rotate identities and reject stale coordinator writes.
- Messages retain schema/id/run/spec/from/to/type/reply/payload/time, idempotent delivery, recipient-only acknowledgement, and persistence across fresh processes.
- Invalid inputs/identities and unrelated worker messages fail; status omits secrets and operations preserve application files and Git staging.

## Verify

- Method: cargo test and real binary/process regression scenarios using disposable projects and the current Python state schema as reference.
- Expected: retained success and failure boundaries without a Python subprocess or provider task session.
- Tests: concurrent ownership, stale tokens, durable send/ack/deduplication, coordinator alias, malformed inputs, and secret-free status.
