---
type: MicroSpec
kind: implementation
title: Review and delegation validation and pilot runner
description: Add opt-in two-provider observations and independent grading for native readers, missing verification, and saved recovery.
---

# P008-MS03 · Validation and pilot runner

## Intent

Provide reproducible disposable pilots for review findings/no-findings, two native readers, missing child evidence, failed combined verification, and fresh-session recovery using installed Codex and Claude Code.

## Constraints

- Always: keep payload/source fingerprints, raw traces and snapshots outside agent workspaces, preserve protected fixture files, and retain failed criteria.
- Never: install credentials, change user settings, count requested delegation as observed execution, or treat fixtures as worked-example application tests.

## Acceptance

- Fixtures have real application source, standard-library tests, controlled defects/check failures, and optional native roles copied only into disposable projects.
- Each provider's invocation records its actual version, completion, identity, and trace; grading verifies scope/source preservation, review routing, actual worker execution/results, progress ownership, required-check outcomes, and fresh recovery.
- Structural guards and grader tests reject missing parent references, child-owned progress, unsupported findings, and absent native delegation evidence; fixture preparation does not launch task agents.

## Verify

- Method: prepare both providers' fixtures without agents, exercise negative grader cases, run the document checker and unit tests, and inspect source/trace isolation before live execution.
- Expected: passing fixture baselines and guards with no invented runtime evidence; live results remain pending for the next item.
- Tests: meaningful contract and grader tests plus isolated fixture preparation; opt-in CLI sessions are executed and graded separately.
