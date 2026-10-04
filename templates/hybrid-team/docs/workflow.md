---
type: Guide
title: Hybrid Team workflow
description: Coordinate scoped Codex and Claude Code workers with recoverable plans, shared messages, isolated worktrees, and checked integration.
okms_template: hybrid-team
okms_template_version: "0.2.0"
---

# Hybrid Team workflow

## Start here

Follow applicable project instructions and the user's task. Read [the index](index.md), [project context](context.md), and [team policy](team-policy.md). This explicit profile authorizes the coordinator to delegate bounded assignments through the project-local runtime. Opening a session registers a role; start workers only for an actual task.

Use the identity and role supplied by the lifecycle hook or an explicit runtime join. One coordinator owns shared plan/index updates. A second root session is standby until handoff or explicit recovery. A spawned worker keeps its assigned role and never claims coordination. If hook context is missing, review/trust the native hooks as described in [the team guide](team.md); an explicit join is a manual fallback, not proof of automatic startup.

Read [the task catalog](_templates/catalog.md) and only the selected micro spec blueprint. Keep all eight kinds; coordination is a profile and role. Read detailed runtime commands only when assigning, communicating, checking, or recovering work.

## Baseline and compatibility

Inspect affected implementation, callers, data, and shared contracts. Record actual baseline checks or their unavailability and retained behavior before changes. Save a plan using [the plan blueprint](_templates/plan.md), adding Baseline and Compatibility when existing contracts are affected. Plans use Goal / Approach / Work / Resume / Result and work_status; do not weaken acceptance after failures.

Save each selected micro spec before dispatch. It uses Intent / Constraints / Acceptance / Verify, with essential invariants and meaningful outcome checks. Keep code details in code and reports in deliverables. Preserve assigned IDs, existing instructions, context, and historical documents.

## Team work loop

1. Identify the current coordinator and read the current plan, Resume, selected contracts, dependencies, and relevant source files. Short explanations need no new work document.
2. Select ready rows whose dependencies are done. Save their micro specs and directory index entries. Use checkpoint to set progress; only the coordinator writes shared records.
3. Assign independent scopes using the runtime. Give each worker its contract, actual context, owned paths, required evidence, and verification command arrays. Use readers for analysis/review; use the other provider for cross-review when there is only one independent write scope.
4. Workers inspect their worktrees, implement only the assignment, exchange bounded questions through messages, acknowledge processed messages, and return a WorkerResult. Native helpers return to their parent; peer discussion does not allocate new work or change acceptance.
5. Inspect returned results, diffs, actual evidence, and missing checks. Integrate a returned batch only after reviewing acceptance. The runtime checks the combined worktree, detects changed root targets, applies the delta without updating staging, and runs root checks.
6. Check acceptance against the actual integrated project. Update Work and Resume through checkpoint, with actual evidence and a concrete next action. A result_ready event, successful provider turn, timeout, or exhausted limit never completes a micro spec.

Independent ready rows may execute in parallel only when scopes and shared effects permit it. Overlapping writes stay ordered. Dependencies become ready after coordinator acceptance; later batches snapshot the newly integrated project. Plans remain the only task-progress ledger. AgentRun tracks operational session state.

## Recovery and completion

Checkpoint at scope/state changes, handoff, interruption, and integration. Resume retains Current, Next, and Blocker. Recover from the saved plan, working tree, runtime registry, native session IDs, inbox, and actual artifacts. Inspect partial changes before resuming; never use a latest-session shortcut or silently reset consumed assignment time.

Keep required failed or unavailable verification incomplete. Stop/cancel preserves worktrees and raw evidence. A coordinator can explicitly hand off or recover ownership; stale identities cannot dispatch, checkpoint, or integrate through the runtime. Scope checks reject unowned returned changes; native instructions and sandbox policies still govern what an agent can execute.

Mark a plan done after all remaining scoped criteria, interactions, and required checks pass. Remove its Active work pointer while retaining history and indexes. For an explicitly requested Goal, follow [goal execution](goal-loop.md); it keeps its own limits and does not automatically activate worker loops or another native team.
