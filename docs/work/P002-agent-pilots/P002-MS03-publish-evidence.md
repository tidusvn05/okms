---
type: MicroSpec
title: P002-MS03 · Publish pilot evidence
description: Publish measured agent outcomes, reproducible commands, and verification limits while preserving raw local evidence.
---

# P002-MS03 · Publish pilot evidence

## Intent

Make the executed pilot reviewable and repeatable, clearly distinguishing observed workflow behavior, independent code checks, and deliberately blocked verification.

## Constraints

- Always: preserve historical P001 limits and report the grader correction explicitly; separate raw local artifacts from portable published measurements.
- Always: record the actual CLI version, fresh-session evidence, check outcomes, and limits of polling and history canaries.
- Never: claim a model ID that was not recorded, treat the blocked gate as passed, or imply the worked examples' applications were tested.

## Acceptance

- Given the seven observed sessions, When reading the published report, Then each scenario's outcome, independent check counts, end state, and evidence source are clear.
- Given a new checkout and an existing CLI login, When following the documented opt-in command, Then the same fixtures and grading can be run without coupling ordinary document checks to agent execution.
- Given the completed repository, When required document checks and applicable OKF lint run, Then links, contracts, progress, and actual generated bundles pass without altering template payloads to excuse grader behavior.

## Verify

Review the report against raw events and final projects, validate published JSON, run `.venv/bin/python scripts/check_docs.py`, lint the new knowledge-base documents and observed bundles with okbase L1, and run `git diff --check`.
