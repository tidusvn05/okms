---
type: Plan
title: P002 · Device administration
description: Deliver admin-only device catalog mutations and one-time pending-request decisions with preserved history and audit.
work_status: planned
---

# P002 · Device administration

## Goal

Allow administrators to create, update, retire devices, and decide pending requests while preserving asset-code uniqueness, loan history, reservations, and audit.

Out of scope: hard deletion, requester UI redesign, and changing the existing loan model. This is a document illustration, not an included application.

## Approach

- Explore the actual schema, migrations, authorization routes, lending service, and audit behavior.
- Complete the catalog outcome before request decisions so retired-device behavior is established.
- Use conditional transitions and the destination database's real transactional guarantees for decisions.
- Keep the D1 non-empty batch requirement only if D1 is actually used.

## Work

| Spec | Depends on | State | Evidence |
| --- | --- | --- | --- |
| [P002-MS01 · Admin device catalog](P002-MS01-device-catalog.md) | — | planned | Not run; illustrative document. |
| P002-MS02 · Decide a pending request | P002-MS01 | planned | Not created yet; preview is in the walkthrough. |

## Resume

- Current: P002-MS01.
- Next: locate real migration, service, and router checks, finalize verification, and implement the catalog behavior.
- Blocker: an actual application and its commands are not included in this example.

## Result

Not implemented or verified. When used in a real project, record actual per-item results and check retirement/approval interactions before closing the plan.
