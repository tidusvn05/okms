---
type: Plan
title: P002 · Run independent agent pilots
description: Execute fresh Codex sessions against real code fixtures and publish outcome and workflow evidence.
work_status: done
---

# P002 · Run independent agent pilots

## Goal

Run the previously documented agent pilot: setup and repeat setup, Lite, two dependent Plan-first outcomes, a fresh-session checkpoint handoff, Brownfield compatibility, blocked required verification, and selective reading among unrelated history.

Out of scope: publishing remotely, changing authentication or user settings, benchmarking multiple models, and treating a small pilot as guaranteed agent compliance.

## Approach

- Use the installed Codex CLI with its existing login and default model in isolated disposable projects; preserve a fresh conversation for every invocation.
- Give agents actual Python code, standard-library tests, and a project instruction pointer to the copied workflow.
- Capture JSONL events and external file snapshots, then grade code independently of agent-authored tests and final summaries.
- Separate application outcomes, workflow order, honest evidence, recovery, and observed history reads.
- Preserve raw local traces, publish a reproducible runner and a concise report, and fix concrete template defects if the pilots expose them.

## Work

| Spec | Depends on | State | Evidence |
| --- | --- | --- | --- |
| [P002-MS01 · Observed pilot runner](P002-MS01-pilot-runner.md) | — | done | Runner syntax and five fixture baselines pass; real Lite session completed with trace/snapshots, 20 independent behavior cases and 3 original tests passing. |
| [P002-MS02 · Execute and grade pilots](P002-MS02-execute-pilots.md) | P002-MS01 | done | All 7 fresh conversations pass after correcting adopted-project link scope in the grader; 160 independent behavior cases and 16 original test executions pass. Protected integration gate exits 2 and work stays blocked as expected. |
| [P002-MS03 · Record findings and final checks](P002-MS03-publish-evidence.md) | P002-MS02 | done | Published report and fingerprinted JSON match all raw traces; checker passes 64 Markdown files and 12 setup scenarios, six new/observed bundles pass okbase L1 with zero diagnostics, Python syntax and diff checks pass. |

## Resume

- Current: P002-MS01, P002-MS02, and P002-MS03 are done.
- Next: none; all scoped pilot execution, evidence publication, and final checks are complete.
- Blocker: none.

## Result

Seven actual fresh Codex conversations passed the observed workflow criteria. Independent grading passed 160 behavior-case executions and 16 original test-method executions; setup preserved existing content, Plan-first resumed from files, and Brownfield retained the exercised compatibility matrix. The intentionally unavailable required gate exited 2 and its work remained correctly blocked.

Evidence is published in `evals/pilot-report.md` and `evals/pilot-results.json`, with reproduction in `evals/README.md`. Raw local traces, snapshots, original rejected setup grades, and final projects remain in ignored `.pilot-runs/` directories. The adopted-context link-scope grader defect was corrected and the same traces regraded; template payloads were unchanged. The document checker passed 64 Markdown files and 12 setup scenarios; maintainer docs and all five observed final bundles passed okbase L1 without errors or warnings. Python syntax and diff checks passed.

Limits: one CLI default configuration, small Python fixtures, observed polling order, and history canaries in emitted output. The model ID was not recorded; illustrative example applications were not tested, and the intentionally unavailable integration gate did not pass. P001 remains the historical record of structural checks before independent agent pilots existed.
