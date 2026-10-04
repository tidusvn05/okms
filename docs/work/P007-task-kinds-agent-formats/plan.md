---
type: Plan
title: Research task kinds and agent formats
description: Compare the okms catalog with documented Codex and Claude Code workflows and recommend proportionate extensions.
work_status: done
---

# P007 · Research task kinds and agent formats

## Goal

Produce a source-backed report assessing whether the seven current task kinds are sufficient, which additions have distinct evidence requirements, and which other document contracts help developers use Codex and Claude Code.

Out of scope: changing the distributed catalog or workflows, installing provider configuration, running agent pilots, or implementing orchestration.

## Approach

- Select `research`: the immediate outcome is an evidence-backed assessment and recommendation, rather than adoption of a new contract.
- Compare the repository's current contracts and published pilot limits with official documentation accessed on October 4, 2026.
- Evaluate additions by distinct outcome/evidence, routing clarity, portability, maintenance cost, and recoverability. Separate task kind, agent role, reusable procedure, and execution mode.
- Keep proposed formats illustrative and identify which recommendations need actual runtime evaluation before distribution.

## Work

| Spec | Depends on | State | Evidence |
| --- | --- | --- | --- |
| [P007-MS01 · Source-backed assessment](P007-MS01-source-assessment.md) | — | done | Reviewed repository contracts and pilot limits, checked ten official documentation pages, and saved the assessment in research.md. The document checker passed 109 Markdown files; git diff --check passed. |

## Resume

- Current: none; the scoped research is complete.
- Next: none within this plan; possible adoption and fresh-session pilots are recommendations in the report.
- Blocker: none.

## Result

Saved the [research report](research.md) covering all seven kinds, ranked additions, native provider formats, and illustrative delegation/result contracts. Recommend prototyping review, clarifying pure-refactor routing, and reusing existing plan/checkpoint ownership before introducing optional native adapters or parallel execution.

Source review distinguishes provider documentation, repository observations, and proposed conventions. Read-only version checks returned `codex-cli 0.159.0` and `2.1.284 (Claude Code)`; no task sessions, agent pilots, teams, workflows, or application examples were executed.

`.venv/bin/python scripts/check_docs.py` passed 109 Markdown files, six OKF bundles, two standalone payloads, and eight onboarding scenarios after correcting three out-of-bundle document links. `git diff --check` passed. No distributed workflow, catalog, checker, or native configuration changed; runtime behavior remains an evaluation proposal.
