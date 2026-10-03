---
type: Context
title: Device administration scenario
description: Identify administrator authorization, preserved loan history, and audit obligations in a fictional equipment application.
---

# Device administration scenario

## Purpose

Illustrative equipment-lending application where administrators manage devices and decide pending requests. No application or database is included.

## Durable rules

- Catalog and decision routes require administrator authorization.
- Historical loans remain available after a device is retired.
- Every successful mutation stores an audit record.

## Verification

- Actual router, migration, service, and test paths: unknown until applied to a real project.
- Run focused checks through the project's real migrated schema and relevant service/router paths.
- Required project commands: discover them from project instructions and manifests; do not invent a runner.

Cloudflare D1 batch behavior is a scenario-specific constraint. Retain it only when the destination application actually uses D1.
