---
type: MicroSpec
kind: implementation
title: P003-MS03 · Validate task and Goal contracts
description: Extend maintainer checks to validate shared task selection and truthful Goal progress while retaining old documents.
---

# P003-MS03 · Validate task and Goal contracts

## Intent

Detect malformed or inconsistent task catalogs, micro spec kinds, and Goal limits/states while preserving the existing plan format, legacy kindless specs, and standalone payload independence.

## Constraints

- Always: validate adopted project links separately from exported payload boundaries and preserve the default strict boundary.
- Always: reject invalid scalar types cleanly, retain read-only checks, and keep agent execution opt-in.
- Never: mark an exhausted or unverified Goal complete, reject legacy work just because it lacks kind, or weaken common acceptance contracts.

## Acceptance

- Given each copied payload, When checking runs, Then its catalog selects exactly one correctly typed blueprint per supported kind and all shared files and versions agree.
- Given a legacy spec or a valid typed spec, When checking runs, Then the common contract and progress ownership remain valid; unknown or malformed kinds fail clearly.
- Given a Goal at a limit, blocked, or complete, When checking runs, Then counters, stop reasons, linked plan state, completion evidence, and active pointers agree.
- Given negative catalog/Goal fixtures, When checks run, Then premature completion, inconsistent budgets, missing native references, and invalid metadata are rejected without tracebacks.

## Verify

Run the required document checker, focused contract tests with valid and invalid fixtures, and Python syntax checks. Independently lint the exported OKF bundles before running new agent pilots.
