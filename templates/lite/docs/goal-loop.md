---
type: Guide
title: Bounded goal execution
description: Run an explicitly requested goal through verified work attempts with persistent limits, stop conditions, and recovery.
---

# Bounded goal execution

Read this guide when the user explicitly requests a Goal or continued loop execution. Ordinary tasks use the installed workflow without adding a Goal. A file provides the execution contract and checkpoint; it does not start a background process.

## Create or resume the contract

Save [the Goal blueprint](_templates/goal.md) as `work/G001-short-title/goal.md`, with its directory index. Use the next unused `G` ID, render all placeholders, and set `type: Goal`, actual title, and description. Add the Goal to the work index and root Active work. A Goal uses plans for item progress, including Lite's Plan-first fallback. Link plans when their files exist; future plans remain text. Plans retain their usual paths and own all item states and evidence. Keep both open Goal and plan pointers discoverable.

Read context, matching Goal, linked plan, current spec, recorded results, and the working tree on recovery. Preserve IDs, scope, counters, and completed work. Resume the same interrupted attempt before reserving another one; do not recreate a Goal or overwrite its existing plan because the conversation is new.

## Choose execution

`execution: portable` means the agent follows this bounded loop in its current session and saves files before yielding. Use the user's positive iteration limit, or the documented default of 5 when none is supplied. Record it as `max_iterations`. Do not invent a token budget or claim the session will continue in the background.

`execution: native` uses an actual available goal capability. Identify its real start, inspect, completion, and stop operations and applicable rules before activation. Record their mapping under Execution, preserve the returned identifier as `native_id`, and reference the file in the native objective. Set native budgets only as authorized and supported; portable attempt counts are not native token or time accounting. If native support is unavailable, record portable mode explicitly, or remain blocked when the user requires native execution.

| Native integration operation | Required behavior |
| --- | --- |
| Start or attach | Reuse the matching native goal when resuming; create one only for explicitly authorized goal execution. |
| Inspect | Read actual runtime status and limits; reconcile them with the saved checkpoint before continuing. |
| Complete | Request completion only after file Completion evidence and all remaining required work are satisfied. |
| Stop or block | Follow the runtime's actual state rules; preserve file evidence and never manufacture a successful transition. |

A native runtime controls its scheduling and limits. Honor stricter runtime rules and expose the actual result in the checkpoint. This portable package defines the mapping contract; it does not install an agent-specific integration.

## Execute one attempt

1. Check Completion and stop conditions before acting. Select one ready plan item using [the task catalog](_templates/catalog.md). Save a plan if needed; save only the current spec.
2. Before beginning that attempt, increment `iterations_used` once, set `work_status: in_progress` and `stop_reason: none`, and name the current plan item and reserved attempt number in Resume. One attempt includes execution, its verification, and checkpointing. A retry after a failed check consumes another attempt.
3. Execute the spec's scoped outcome, check acceptance, and run required project checks. Use the appropriate evidence: reproduction/regression, findings, decision review, source checks, or rehearsal. Keep failed or missing necessary verification incomplete.
4. Save plan State/Evidence/Resume and Goal Resume/Result before selecting another item. Check cross-item interactions at plan completion. Continue automatically while useful ready work remains and the limits allow it.

An interruption preserves the reserved attempt; finish or diagnose it from saved files before advancing the counter. Independent tasks can continue when one item is blocked and the Goal still has authorized ready work.

## Stop and checkpoint

| Condition | File state and next action |
| --- | --- |
| Completion proven; scoped plans closed | Check every Completion item with supporting evidence, set Goal `work_status: done` and `stop_reason: complete`, record Result, and remove its Active work pointer. |
| `iterations_used` reaches `max_iterations` with work remaining | Keep Goal `in_progress`, set `stop_reason: iteration_limit`, and record the pending item and next action. Yield; do not reset the counter or expand the limit. |
| Missing necessary input/check and no other ready work | Set file Goal `blocked`, `stop_reason: blocked`, and record the dependency and next action. Follow any stricter native transition rules separately. |
| User stops or withdraws scope | Checkpoint immediately; use `cancelled` for withdrawn scope and `stop_reason: user_stop`. For a temporary stop keep incomplete progress and the user's requested checkpoint. |

Only an explicit user extension changes an existing limit; record the prior and new values in Execution before the next attempt. An attempt already reserved at the limit may be resumed, but another attempt requires capacity. Native limits take precedence when they stop execution earlier.

Verification failure calls for diagnosis and correction within the remaining budget, not weaker acceptance. Repeating an unchanged attempt without new evidence is not progress; record the blocker or select another ready outcome. Historical plans and Goal files stay at their paths after closure.
