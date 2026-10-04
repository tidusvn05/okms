---
type: MicroSpec
kind: implementation
title: P014-MS02 · Complete Rust coordination
description: Preserve scoped worktrees, bounded provider execution, resume, mandatory integration gates, hooks, and checkpoints in Rust.
---

# P014-MS02 · Complete Rust coordination

## Intent

Run the complete coordination lifecycle through the Rust binary, preserving operational behavior and application data.

## Constraints

- Always: keep root HEAD/index and unrelated files; reserve disjoint bounded scopes and snapshot dirty/untracked code privately.
- Always: retain raw provider/check artifacts, exact native resume IDs, native permission failures, coordinator fencing, required combined/root checks, and truthful incomplete state.
- Never: bypass trust/permissions, execute arbitrary shell check strings, discard failed worktrees, silently retry expired work, or complete an unverified writer.

## Acceptance

- Dispatch validates saved plan/spec/dependencies, worker limits, shared paths, and provider argv before starting isolated bounded workers.
- Worker results are schema-checked candidates; messages wake the exact session, including a message arriving before waiting. Failure, cancellation, scope violations, missing results, and timeout remain incomplete.
- Integration reviews returned results, preserves configured gates, refuses changed root targets/stale owners, and verifies the actual root before completion.
- Hooks preserve native helper/root roles; checkpoint owns plan/index progress, prevents unsupported completion, and supports explicit recovery/reverification.

## Verify

- Method: Rust build/tests and the existing operational regression scenarios executed through the real binary with fake provider transports.
- Expected: the retained scenarios pass with Python used only as a fixture/check application, never as the runtime implementation.
- Tests: dirty staging/snapshot, two returned workers, peers/resume, denial/malformed output, deadlines/cancellation, required gates, integration conflicts/handoff, root verification, and checkpoint recovery.
