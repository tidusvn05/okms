---
type: MicroSpec
kind: implementation
title: P010-MS01 · Downloadable distribution
description: Deliver a complete reproducible release bundle and a checksum-verifying installer that preserves project content.
---

# P010-MS01 · Downloadable distribution

## Intent

Allow explicit Hybrid Team adoption from a pinned GitHub release without requiring a source checkout.

## Constraints

- Always: verify bundle integrity and safe extraction before invoking the existing preserving setup; retain the observed runtime payload and include its license notices.
- Always: clean temporary downloads and support project paths containing spaces and shell characters.
- Never: invoke providers, modify global settings/authentication, overwrite project customizations, or implicitly upgrade an existing installation.

## Acceptance

- Identical source produces identical archive bytes containing all runtime, docs, native roles, skills, and licenses with an attributable file manifest.
- Both curl downloads and local release assets support new setup, dry-run, and repeated setup through the project-local helper.
- Corrupt checksums, unsafe archive members, inconsistent manifests, and failed downloads stop before any project mutation.
- README instructions use real pinned prerelease asset names and preserve the distinction between installation and native hook activation.

## Verify

- Method: distribution unit tests with disposable projects, fake curl transport, real setup execution, and the required repository checker/test suite.
- Expected: preserving adoption succeeds; all rejected distributions leave the project unchanged; no provider task session starts.
- Tests: cover deterministic packaging, dirty-project preservation, dry-run/repeat, download requests, integrity/manifest failures, and archive traversal/link rejection.
