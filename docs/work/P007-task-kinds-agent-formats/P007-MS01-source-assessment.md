---
type: MicroSpec
kind: research
title: Source-backed task kind and agent format assessment
description: Assess task coverage and distinguish portable work contracts from provider-specific agent configuration.
---

# P007-MS01 · Source-backed assessment

## Intent

Assess the current okms kinds and additional developer-facing formats in a research report stored in this plan directory. Use current repository contracts and official OpenAI and Anthropic documentation accessed on October 4, 2026.

## Constraints

- Always: distinguish documented behavior, repository observations, and proposed design; compare by outcome/evidence, routing clarity, portability, maintenance, and recovery.
- Never: treat a Markdown convention as runtime enforcement, claim unexecuted agent pilots, or change distributed workflows as part of this assessment.

## Acceptance

- The report evaluates all seven kinds and ranks candidate additions with concrete selection boundaries and evidence requirements.
- The report compares project instructions, skills, native agent definitions, delegation, orchestration, and handoff, with checked primary sources for material provider claims.
- Proposed lightweight formats reference the existing micro spec and progress owner, including write ownership, verification, and recovery responsibilities.
- Recommendations identify limitations and a concrete evaluation sequence before adoption.

## Verify

- Method: open official sources, review claims against their documented schemas and behavior, inspect repository contracts and pilot limits, and run `.venv/bin/python scripts/check_docs.py` plus `git diff --check`.
- Expected: attributable conclusions, clearly labeled illustrative proposals, and passing repository document checks.
- Tests: source and document review suffice for this research-only change; no runtime or example-application execution is claimed.
