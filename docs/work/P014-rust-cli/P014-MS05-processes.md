---
type: MicroSpec
kind: bugfix
title: P014-MS05 · Bound descendant cleanup
description: Keep cancellation bounded when a terminated driver leaves descendants that ignore graceful termination.
---

# P014-MS05 · Bound descendant cleanup

## Intent

Ensure driver/check cancellation ends its isolated process group even when the direct child exits before a descendant that ignores TERM.

## Constraints

- Always: signal only managed isolated groups, allow bounded graceful cleanup, and reap the direct child.
- Never: let early parent exit leave background work running beyond the cancellation bound.

## Acceptance

- A real isolated parent/descendant reproduction shows the boundary violation before repair.
- Cancellation stops a TERM-ignoring descendant after its parent exits, within the five-second grace plus scheduling tolerance.
- Ordinary driver/check regressions, native identity behavior, minimum Rust compilation, and required repository checks remain valid.

## Verify

- Method: OS subprocess regression with independent observable descendant writes, cleanup guards and a finite deadline; cargo tests/clippy and existing runtime scenarios.
- Expected: the initial regression fails, the repaired boundary passes, and no reproduction process survives test cleanup.
