---
type: Context
title: Existing pagination scenario
description: Describe assumed pagination compatibility obligations for a refactor that must be grounded in real project evidence.
---

# Existing pagination scenario

## Purpose

Illustrative existing API whose pagination validation is duplicated. No implementation, callers, or tests are included; the behavior below is a scenario assumption to replace with observations in a real project.

## Durable rules

- Preserve existing parameter names, defaults, boundary behavior, and public error shape.
- Preserve authentication and response shape through the refactor.

## Verification

- Baseline and regression commands: unknown until the project is inspected.
- Relevant checks: existing endpoint tests, parser boundaries, error shape, defaults, and callers.
- Required checks and actual paths: read project instructions and manifests.
