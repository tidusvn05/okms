---
type: Guide
title: Optional agent delegation
description: Assign bounded work within the current micro spec and recover results without duplicating progress or assuming native runtime support.
---

# Optional agent delegation

Read this guide only when the user or applicable project/skill instructions authorize delegation. Ordinary tasks use [the workflow](workflow.md) without loading these optional formats. Agent tools, permissions, context inheritance, and isolation depend on the actual runtime; Markdown instructions alone do not register agents or enforce access. If tools are unavailable, continue within the current agent when possible and report that limit.

## Choose the contract

- A task kind describes the outcome. A role describes who handles an assignment. Delegation does not change the kind, profile, or Goal mode.
- Use [role instructions](_templates/agent-role.md) only for a reusable specialist. Render with `type: AgentRole`; mission, trigger, authority, output, and escalation remain independent of any task's state.
- A [delegation brief](_templates/delegation-brief.md) assigns part of the current spec. Send short assignments in the task message; save one with `type: DelegationBrief` only when its scope or recovery needs a durable record.
- A [worker result](_templates/worker-result.md) returns observations and actual evidence. Use a message for short results; save `type: WorkerResult` when the result needs to survive the session.

Replace every placeholder in saved documents, give them actual title/description metadata, and list them in their directory index. Optional documents do not have `kind`, `work_status`, or a Work table. The parent micro spec remains the outcome contract; the plan or standalone spec remains its progress owner.

Document links target actual files. Put source line numbers in the link text, such as `[api.py:3](../api.py)`; a filename ending in `:3` is not a portable Markdown target.

## Coordinate the current spec

The coordinator reads the current spec and applicable dependencies, then supplies each worker with the referenced contract, necessary instructions, exact scope/revision, expected output, and stop/return condition. Do not assume the worker sees prior conversation, selected skills, or already-read files. Reference acceptance instead of creating another version of it; a worker cannot weaken the parent's criteria.

Put assignment policy in the plan's Approach, or a standalone spec's Constraints and Verify: who owns shared updates, what independent reads can run concurrently, how results return, who integrates edits, and which checks prove combined acceptance. Allocate IDs and update plans/indexes through one coordinator. Workers report evidence and proposed changes to that owner.

Start with independent readers in parallel; keep edits ordered and explicitly assign their file scope. This guide does not enable parallel execution of independent specs. Several readers can serve one outcome without each needing another plan or micro spec. Separate independently verifiable outcomes remain separate planned rows and are selected through the normal work loop.

## Verify and handle failure

Wait for the assigned results before accepting their conclusions. Check that scope and revision match, findings have supporting references, and required checks actually ran. A worker's summary or passing scoped check does not prove the combined parent outcome. The progress owner reviews every acceptance criterion and runs applicable integration and required project checks.

Record partial coverage, failed probes, unavailable necessary evidence, and missing results without marking the parent done. Continue other useful work within the current scope. Use the workflow's blocked state only when work cannot progress; record the missing input and next action. Bound retries to the assignment's scope and existing execution limits. Delegation neither starts a Goal implicitly nor resets its consumed attempts.

## Handoff and recovery

Checkpoint through the existing plan Resume fields or standalone Verify checkpoint. Reference durable briefs/results when present; record the actual revision/worktree, uncommitted changes, evidence, unresolved gap, and next concrete action. Do not create a second progress ledger.

On a fresh session, inspect saved contracts, current files, and recorded evidence. Runtime agent IDs may no longer be live. Recreate a necessary worker from its saved assignment, verify which work remains, and avoid repeating verified changes. Preserve existing project instructions and native configuration when adopting or upgrading this bundle.
