---
type: MicroSpec
kind: implementation
title: P003-MS05 · Review and publish task routing
description: Complete release checks and publish the authorized source while preserving observed results and verification limits.
---

# P003-MS05 · Review and publish task routing

## Intent

Publish the checked v0.2 task routing and bounded Goal templates to the authorized okms repository, with discoverable evaluation and upgrade guidance.

## Constraints

- Always: preserve history, report both observed drafts and the selective-reading exception, and verify the pushed commit against the remote.
- Never: publish raw agent traces, claim native activation, force-push, or equate document validity with passing the unavailable integration gate.

## Acceptance

- Every profile remains a self-contained 16-file bundle at v0.2.0; existing kindless specs and project-owned content remain valid.
- The README, contributor guide, pilot instructions, and measurements agree on the implementation, executed checks, observed outcomes, and limits.
- Required checks, contract tests, source/data fingerprints, OKF L1, and diff review support publication.
- The authorized source is committed and pushed normally; the remote main commit matches local HEAD and the working tree is clean.

## Verify

Run the document checker and relevant contract checks, lint current bundles, audit portable results against all raw artifacts, review the diff, and publish with a normal Git push. Confirm remote HEAD and local status after publication. Reuse passing unchanged checks unless a new change justifies repetition.
