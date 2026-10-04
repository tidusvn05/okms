---
type: MicroSpec
kind: implementation
title: Review and delegation examples and adoption guidance
description: Explain new portable formats through illustrative reports, assignments, and checkpoints while preserving existing project adoption.
---

# P008-MS02 · Examples and adoption guidance

## Intent

Show review findings, bounded no-findings reporting, reusable roles, delegated scope, partial evidence, and fresh-session recovery, and document the v0.4 payload and upgrade behavior.

## Constraints

- Always: keep distributed content English, distinguish examples from observed pilots, and preserve setup prompts and existing project/native instructions.
- Never: claim illustrative checks ran, introduce mandatory native configuration, or rewrite completed history.

## Acceptance

- Examples cover a supported-finding shape and no-findings coverage/limits without claiming an executed application review.
- Delegation examples reuse the parent spec and one progress owner, return actual/absent evidence honestly, and recover through existing checkpoint fields.
- Current README, context, and contribution guidance describe eight kinds, 21-file payloads, conditional optional reads, and deliberate v0.4 upgrades; native registration remains outside automatic adoption.

## Verify

- Method: review examples and setup prompts, check shared payload consistency, and run `.venv/bin/python scripts/check_docs.py` and `git diff --check`.
- Expected: accurate self-contained instructions and passing documentation checks.
- Tests: meaningful document/contract checks cover this guidance change; observed agent behavior is assessed in the later pilot item.
