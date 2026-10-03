---
type: MicroSpec
kind: implementation
title: P003-MS01 · Add portable task contracts
description: Define selectable task-specific micro specs and a recoverable Goal format shared by all three payloads.
---

# P003-MS01 · Add portable task contracts

## Intent

Give agents small contracts for implementation, bugfix, investigation, design, research, and runbook authoring, plus a general fallback, without requiring them to read every blueprint.

## Constraints

- Always: retain the four micro spec sections and keep detailed results in the actual code or deliverable.
- Always: distinguish an installed profile, task kind, and execution mode; keep shared files identical across standalone copies.
- Never: label unknown findings as confirmed, duplicate plan-owned item progress, or make a Goal file pretend a native runtime was activated.

## Acceptance

- Given a task category, When the agent reads the catalog, Then it can identify one blueprint and its expected output and evidence.
- Given each specialized blueprint, When it is rendered, Then it records the selected kind and uses the common four-section contract with relevant success and failure criteria.
- Given a kindless historical spec or an unsupported task category, When routing resumes, Then the existing contract remains readable and the general fallback is available.
- Given a Goal, When its template is rendered, Then completion, bounded execution, linked work, stop conditions, and recovery can be recorded without copying item state out of plans.

## Verify

Compare shared inventories and content across all payloads, review category boundaries and verification instructions, and check the rendered contracts. Full checker updates and fresh agent evidence follow in the dependent work items.
