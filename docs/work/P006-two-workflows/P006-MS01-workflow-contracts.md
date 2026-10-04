---
type: MicroSpec
kind: implementation
title: P006-MS01 · Scope-based existing-system guidance
description: Apply baseline and compatibility obligations within Lite and Plan-first according to the affected scope.
---

# P006-MS01 · Scope-based existing-system guidance

## Intent

Offer two standalone workflow payloads. Agents recognize existing-system obligations from affected behavior, interfaces, data, and shared dependencies while retaining the workflow chosen for the work's size and dependencies.

## Constraints

- Always: Record actual baseline results or their unavailability before changing existing behavior; preserve retained contracts and record intentional changes.
- Always: Keep Lite evidence concise and make additional plan sections conditional; include migration, rollout, and rollback only when applicable.
- Never: Require a third profile, promote every small fix to a plan, invent successful checks, or rewrite historical plans and measurements.

## Acceptance

- Given a small independent change to an existing system, when Lite is followed, then its MicroSpec records baseline evidence and compatibility constraints without requiring a plan solely because code exists.
- Given Plan-first work affecting existing contracts, when its plan is saved, then Baseline and Compatibility describe the affected scope before implementation and verification checks retained behavior.
- Given an isolated new outcome or a report that changes no existing contracts, when planning, then extra compatibility sections and migration procedures are omitted.
- Given a copied distribution, when inspecting its files, then only Lite and Plan-first are distributed, both at version 0.3.0 with the shared catalog and plan blueprint.

## Verify

- Method: Review new, existing, and mixed-scope routing scenarios; validate each copied bundle with `Checker.check_bundle`; compare shared guidance and payload inventories.
- Expected: Two self-contained bundles with conditional obligations, valid contracts and links, and no legacy Brownfield distribution.
- Tests: Later P006 items update repository checks and exercise observed agent behavior; this item checks the scoped contract and copied documents.
