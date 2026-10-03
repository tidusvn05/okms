---
type: Guide
title: Device administration walkthrough
description: Show a saved two-outcome plan and create its request-decision spec after the catalog outcome is checked.
---

# Device administration walkthrough

The [saved plan](work/P002-device-administration/plan.md) lists both outcomes and their dependency. Only [the catalog spec](work/P002-device-administration/P002-MS01-device-catalog.md) exists as a work document. Application work is still planned, and no application tests have run.

In a real project, inspect its code and context, save the plan, finalize the first spec, implement it, and record verification in the plan's Work table. Update Resume before proceeding. A fresh session uses that checkpoint and the working tree instead of prior chat.

## Next spec preview

After the first item is done, save `P002-MS02-request-decision.md` with a specific `MicroSpec` title and description. The following preview clarifies the final approval result and the failed-reservation case:

```markdown
# P002-MS02 · Decide a pending request

## Intent

Let an administrator approve or reject a pending request exactly once and preserve the decision, actor, time, and reason for the requester.

## Constraints

- Always: transition conditionally from pending and persist audit with the successful decision; for this D1 scenario, use a non-empty batch.
- Never: reprocess cancelled or decided requests, approve a retired device, or leave a partial decision after reservation failure.

## Acceptance

- Given a pending request, When an administrator rejects it with a reason, Then rejection, reason, actor, time, and audit are stored.
- Given a pending request for an active device and valid reservation, When an administrator approves it, Then approval, reservation, actor, time, and audit are stored together.
- Given invalid reservation or a retired device, When approval is attempted, Then no approval, reservation, or successful-decision audit is stored.
- Given an empty rejection reason, When rejection is attempted, Then the request remains unchanged and a clear business error is returned.
- Given a non-administrator, a non-pending request, or competing decisions, When deciding, Then unauthorized or repeated mutation is rejected and at most one decision succeeds.

## Verify

Use the real migrated schema, reservation service, and admin router to check success, refusal, rollback, and competing decisions. Use the actual project's command; a [p002-ms02] test label is optional.
```

Do not record this preview as created or done in the plan until it is saved and checked in the actual workflow. If a migration or required check cannot run, record the missing verification and leave the relevant item incomplete.
