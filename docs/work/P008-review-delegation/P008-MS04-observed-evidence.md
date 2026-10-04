---
type: MicroSpec
kind: implementation
title: Observed review and delegation evidence
description: Execute disposable agent sessions and publish trace-backed results and limits for the v0.4 contracts.
---

# P008-MS04 · Observed pilots and evidence

## Intent

Assess the new contracts in actual Codex and Claude Code sessions and publish a report with measured criteria, source/trace fingerprints, native role observations, and remaining runtime limits.

## Constraints

- Always: use existing logins/default models, preserve raw evidence outside agent workspaces, retain failed criteria, and distinguish fixture behavior from general guarantees.
- Never: rewrite historical reports, repeat sessions solely for a pass, claim unobserved native role execution, or report worked-example commands as executed application tests.

## Acceptance

- Scoped findings/no-findings, delegated readers, missing evidence, failed combined verification, and fresh-session recovery are exercised or have an explicit actual availability failure.
- Targeted Lite repair and compatible-refactor regression pilots assess retained workflow behavior; results and verification limits are recorded honestly.
- Published measurements correspond to actual invocations, source fingerprints, traces, snapshots, grades, and independent fixture checks. Necessary contract defects are resolved and re-evaluated with preserved prior evidence.
- Current docs link the new report, preserve historical reports, and pass required project checks.

## Verify

- Method: run the opt-in runners, inspect raw native calls/results and file ownership, review reports against controlled source facts, then run document and unit checks plus `git diff --check`.
- Expected: truthful evidence for the evaluated matrix and no unsupported compliance or productivity claims.
- Tests: actual disposable CLI sessions, independent behavior cases, contract/grader tests, and repository document checks.
- Observed: `evals/review-report.md` and `evals/review-results.json` retain 16 selected conversations, 12 full observed passes, three timeouts, native-visibility/link exceptions, and two targeted recoveries after citation clarification. All 178 selected-session behavior cases and seven original test-method executions pass.
- Repository checks: `.venv/bin/python scripts/check_docs.py` passes 134 Markdown files, six bundles, two payloads, and eight onboarding scenarios; all 37 unit tests and `git diff --check` pass.
