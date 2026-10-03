---
type: Context
title: Lite pagination scenario
description: Frame a small API validation change without pretending an application or its checks are included.
---

# Lite pagination scenario

## Purpose

Illustrative HTTP API that lists articles. The intended change handles a supplied page size; there is no application in this example directory.

## Durable rules

- Validation errors use the existing public error contract when applied to a real project.
- Omitted page size keeps the default of 20.

## Verification

- Required project checks: unknown until applied to an actual project; inspect its agent instructions and manifests.
- Targeted tests: valid values, omission, malformed input, and boundaries.
- Application code and test paths: not included; locate them during exploration.
