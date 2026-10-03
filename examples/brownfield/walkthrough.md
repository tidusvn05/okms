---
type: Guide
title: Brownfield example walkthrough
description: Replace an assumed baseline with observed behavior before implementing a compatible pagination refactor.
---

# Brownfield example walkthrough

The [plan](work/P003-pagination-compatibility/plan.md) illustrates the additional Baseline and Compatibility sections. Its behavior is an assumed scenario; no actual baseline check has run.

In a real project, explore the endpoint, callers, current docs, and tests. Record actual current behavior and baseline results before implementation. Separate observed facts from assumptions and identify any existing failures with evidence.

Finalize [the refactor spec](work/P003-pagination-compatibility/P003-MS01-centralize-validation.md) from those observations, implement it, and verify both unchanged behavior and the intended maintenance improvement. Record actual commands and results in the plan.

This scenario expects no migration because it changes validation organization without changing persisted data. If the actual change affects storage or public contracts, revise the plan with the relevant migration, rollout, and rollback steps before implementation. Missing intent for a breaking change needs clarification.
