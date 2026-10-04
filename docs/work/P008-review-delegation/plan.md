---
type: Plan
title: Add review and delegation contracts
description: Extend portable task routing with review, clarify refactoring, and verify optional agent assignment and reporting contracts.
work_status: done
---

# P008 · Add review and delegation contracts

## Goal

Publish v0.4 with a review kind, explicit behavior-preserving refactor routing, optional role/delegation/result formats, examples, structural guards, and source-backed observations from Codex and Claude Code pilots.

Out of scope: migration or operation kinds, automatic native agent installation, executable orchestration, parallel execution of independent specs, publishing a remote release, or changing user credentials/settings.

## Baseline

- The v0.3 payload has seven kinds and 16 files per profile. Review uses general; implementation wording excludes pure refactor even though the existing-system pilot exercises it.
- Micro specs retain four sections; plans or standalone specs own progress. The work loop is sequential and plans have one writer. Existing native adapters and multi-agent pilots are absent.
- Before implementation, `.venv/bin/python scripts/check_docs.py` passed 109 Markdown files, six bundles, two payloads, and eight onboarding scenarios; all 22 contract tests passed.
- Preserve the completed P007 research and its existing work-index entry. No baseline failures were observed.

## Compatibility

- Retain Lite/Plan-first adoption, IDs, plan columns, legacy kindless specs, Goal counters, historical artifacts, existing instructions, and mandatory evidence checks.
- Add review without rewriting history. Broaden implementation to include behavior-preserving structural improvements; require baseline and retained-behavior evidence when applicable.
- Optional role, brief, and result documents have no work progress. Delegation serves the current spec; its existing progress owner verifies combined acceptance. Ordinary tasks need no delegation reads.
- Keep copied bundles self-contained. Deliberate upgrades merge current workflow/blueprint changes; repeated setup remains reuse, not an upgrade or native configuration install.

## Approach

- Select implementation for the new portable contracts and author the remaining specs when their dependencies are ready.
- Use the P007 assessment: separate outcome kind, reusable role, assignment, result, and execution policy. Put coordinator rules in one optional guide and reuse Resume for recovery.
- Update canonical shared documents and both payloads together. Increase the version to 0.4.0 and keep native schemas outside the required execution path.
- Test observable structural guards, then run opt-in disposable pilots using existing installed CLIs/logins. Record failures and availability limits instead of implying documentation guarantees enforcement.

## Work

| Spec | Depends on | State | Evidence |
| --- | --- | --- | --- |
| [P008-MS01 · Portable contracts](P008-MS01-portable-contracts.md) | — | done | Review/refactor routing and optional formats synchronized across 21-file payloads; document checker passed 127 Markdown files and all 26 contract tests passed. |
| [P008-MS02 · Examples and adoption guidance](P008-MS02-examples-guidance.md) | P008-MS01 | done | Added illustrative review/delegation/recovery walkthrough and optional native reader examples outside payloads; checker passed 131 Markdown files and setup prompts remained unchanged. |
| [P008-MS03 · Validation and pilot runner](P008-MS03-validation-pilots.md) | P008-MS02 | done | Ten isolated fixture baselines passed without task agents; checker passed 132 Markdown files and all 31 contract/grader tests passed. Runtime observations remain pending. |
| [P008-MS04 · Observed pilots and evidence](P008-MS04-observed-evidence.md) | P008-MS03 | done | Published `evals/review-report.md` and `evals/review-results.json`: 12/16 selected conversations pass all observed criteria, with original failures retained; all 178 independent behavior cases and seven original test-method executions pass. Citation guidance was clarified and two supplemental recoveries pass. Final document checks pass 134 Markdown files; all 37 tests and `git diff --check` pass. |

## Resume

- Current: P008 complete; contracts, guidance, validator, and observed evidence published locally.
- Next: no remaining scoped work. Evaluate Codex native role binding again only when the runtime provides auditable dispatch/role/result metadata.
- Blocker: none.

## Result

Version 0.4.0 adds review as the eighth kind, includes artifact/structural changes under implementation, and supplies optional AgentRole, DelegationBrief, and WorkerResult contracts without another progress owner. Both 21-file payloads are self-contained. Existing adoption prompts, historical work, native user configuration, and v0.1–v0.3 reports are preserved.

Native reviewer examples, an illustrative walkthrough, structural/grader tests, and opt-in two-tool observation/recovery tooling are available. The final report records six passing Claude review sessions, passing Codex ordinary reviews and workflow regressions, four original Codex exceptions, and two passing supplemental recoveries after citation clarification. Current source and native/import fingerprints match the published measurements.

Limits: Codex's captured stream cannot establish custom-role binding or reader dispatch/returns; three original conversations timed out and the original checkpoint/recovery retains invalid links. The clarified final contracts were assessed with targeted recovery, not a repeated full matrix. Runtime security, native Goal activation, and arbitrary integrations are untested. These limits remain explicit rather than being treated as enforcement guarantees.
