# Task routing and Goal walkthrough

This walkthrough is illustrative. It has no application, executed experiments, or claimed passing checks. Use the supplied project's real code and commands when rendering these contracts.

## Mixed work in one profile

For "find and repair the unexpected retry failures, then document recovery", Plan-first can start with these rows:

| Spec | Depends on | State | Evidence |
| --- | --- | --- | --- |
| P004-MS01 · Explain the observed retry failure | — | planned | Pending investigation. |
| P004-MS02 · Repair the confirmed violation | P004-MS01 | planned | Pending diagnosis. |
| P004-MS03 · Document operational recovery | P004-MS02 | planned | Pending repair verification. |

Write only the first spec when starting. Its `kind: investigation` uses the investigation blueprint and a findings deliverable. After evidence supports the required conclusion, checkpoint its result and select `bugfix` for the repair. The repair needs before/after evidence. The final `runbook` points to a procedure document and records actual rehearsal limits. The plan owns progress throughout; each spec retains four sections.

"Compare source reports about storage behavior" routes to research. "Choose the storage architecture under our latency and durability requirements" routes to design. "Translate this note while retaining commands and values" uses general. The next required output, explicit scope, and current checkpoint determine the selection.

## Illustrative Goal before execution

Render a Goal with actual metadata and links only when referenced plans exist. This example deliberately has no created plan and no completed work:

```markdown
---
type: Goal
title: G001 · Complete retry recovery
description: Explain and repair retry failures, then document recovery under a bounded portable execution contract.
work_status: planned
execution: portable
max_iterations: 2
iterations_used: 0
stop_reason: none
---

# G001 · Complete retry recovery

## Goal

Retry failures are understood, repaired, and covered by an operator procedure.

## Scope

- Included: diagnosis, focused repair, regression checks, and runbook authoring.
- Excluded: unrelated interface or infrastructure changes.
- Work plans: P004 is planned; link it after saving the file.

## Completion

- [ ] Findings and repair satisfy their acceptance with reproducible evidence.
- [ ] Required checks and recovery rehearsal support the documented result.

## Execution

- Mode: portable, limited to two attempts.
- Adapter: none.
- Plans own item states and evidence; this file owns the goal and counter.

## Stop

Stop when complete, blocked without other ready work, explicitly stopped, or at two consumed attempts. A limit does not imply completion.

## Resume

- Current: not started.
- Next: save P004, select investigation, save its spec, and reserve attempt 1.
- Blocker: none.

## Result

Pending. No application work or verification has run.
```

With three outcomes and a two-attempt limit, some scope may remain at the limit. Preserve `iterations_used: 2`, leave the Goal `in_progress`, record `stop_reason: iteration_limit`, and checkpoint the next item. A new conversation recovers from those files. It needs an explicit extension before reserving attempt 3; it does not create a replacement Goal or reset the counter.

If an attempt is interrupted, resume that reserved attempt before incrementing again. If a necessary check is unavailable and no other ready outcome remains, record a blocker. Native execution follows the actual agent's mapped operations and returned identifier; this example only describes portable mode.
