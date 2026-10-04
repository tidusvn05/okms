---
type: Guide
title: Hybrid Team delegation
description: Assign bounded work through durable role, brief, and result contracts while retaining coordinator-owned acceptance.
---

# Hybrid Team delegation

This explicit profile authorizes bounded runtime delegation for the user's actual task. Read [team policy](team-policy.md) and [the runtime guide](team.md) when delegating. Use [AgentRole](_templates/agent-role.md), [DelegationBrief](_templates/delegation-brief.md), and [WorkerResult](_templates/worker-result.md) for reusable or recoverable records. Short exchanges can remain messages.

Each brief references one saved micro spec and its plan, actual context/revision, owned scope or read-only boundary, required evidence, and the return/escalation condition. Roles and results never own task kind or work progress. Runtime assignment JSON preserves the same reference/intent/scope/check information.

Independent ready scopes may run in isolated worktrees; dependencies and overlapping writes stay ordered. Workers communicate through addressed messages and acknowledge processed requests. Native helpers are bounded parent-managed readers; their parent represents them on the mixed-provider message bus. Do not create nested coordinators or unbounded worker trees.

Return actual results, diffs, evidence, missing checks, and a next action. A worker may propose a scope change but cannot allocate it, alter acceptance, update shared plan/index state, or integrate. The current coordinator checks combined acceptance and the actual root before checkpointing completion.

Preserve assignment IDs, saved sessions, raw traces, partial changes, and consumed limits on recovery. Scope violations, missing evidence, timeout, and permission denial remain visible and incomplete. The provider's native roles, hooks, and sandbox rules still apply; runtime scope checks are acceptance guards rather than a complete filesystem boundary.
