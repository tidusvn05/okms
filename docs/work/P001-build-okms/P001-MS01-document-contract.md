---
type: MicroSpec
title: P001-MS01 · Define the document contract
description: Give each workflow a consistent behavior contract, progress location, and recoverable implementation loop.
---

# P001-MS01 · Define the document contract

## Intent

Define portable micro spec and plan formats that preserve essential behavior while keeping implementation details in code. Use the saved-plan workflow to build this repository itself.

## Constraints

- Always: save the plan and the current micro spec before their implementation; use English and OKF-compatible frontmatter.
- Always: keep each work item's state and evidence in one authoritative location and checkpoint the next action.
- Never: treat completed historical specs as current requirements or claim checks were run without evidence.

## Acceptance

- Given a micro spec, When an agent reads it, Then Intent, Constraints, Acceptance, and Verify identify an observable outcome and its verification.
- Given a plan, When a new session resumes, Then Goal, Approach, Work, Resume, and Result identify the scope, dependencies, current item, and next action.
- Given OKF tooling, When it reads the documents, Then work progress uses work_status independently of document lifecycle status.
- Given this repository, When implementation starts, Then a persisted plan and the current spec already exist.

## Verify

Inspect the saved artifacts, parse their frontmatter, and review the workflow against the agreed plan. Confirm the shared blueprints have no fabricated commands or verification evidence.
