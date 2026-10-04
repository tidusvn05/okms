---
type: MicroSpec
kind: implementation
title: P009-MS02 · Preserving Hybrid Team adoption
description: Install the self-contained optional profile with project-local runtime, reusable roles, skills, and preserving native configuration.
---

# P009-MS02 · Preserving Hybrid Team adoption

## Intent

Make explicit Hybrid Team setup prepare a project for coordinator startup and bounded workers without replacing existing documents, instructions, or configuration.

## Constraints

- Always: retain existing context, active work, native settings, and instructions; use a fresh documentation namespace when a different profile exists.
- Always: keep the copied project independent of the source checkout and distinguish configured hooks from observed native activation.
- Never: provision credentials, bypass hook trust, implicitly synchronize project edits, or launch agents during ordinary setup checks.

## Acceptance

- Fresh and existing projects receive runtime files, a TeamSpec, role/brief/result contracts, native worker/reviewer configurations, and two scoped skills.
- Setup preflights collisions, preserves project-owned files and settings, and repeats without duplicates or overwrites.
- Copied commands and hook responses work after the source checkout is unavailable; bound workers do not claim coordinator authority.
- Actual verification commands remain project-owned; unknown commands and missing native prerequisites are reported truthfully.

## Verify

- Method: preserving-adoption fixtures, copied-runtime subprocess checks, native schema inspection, skill validation, and required repository checks.
- Expected: self-contained setup and role/ownership contracts pass while Lite and Plan-first retain their existing behavior.
- Tests: ordinary fixtures do not start provider sessions; native activation is additionally evaluated in the live pilot.
