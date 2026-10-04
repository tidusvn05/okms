---
type: MicroSpec
kind: implementation
title: P014-MS08 · Site-compatible Hybrid metadata
description: Apply the verified namespaced metadata boundary to the new independent Rust Hybrid Team version.
---

# P014-MS08 · Site-compatible Hybrid metadata

## Intent

Make the new Hybrid Team 0.2.0 documentation build inside MkDocs without the reserved page-template collision established by the portable PR review.

## Constraints

- Always: align the embedded workflow, source checker, package validation and preserving setup recognition on namespaced workflow identity.
- Always: preserve JSON runtime/config contracts and refuse silent upgrades; leave published 0.1.0 assets and historical fixtures unchanged.
- Never: change either PR's historical scope/evidence or claim that prose compliance was observed.

## Acceptance

- A disposable Hybrid documentation build reproduces the unprefixed collision and passes after the rename.
- New installed workflows use okms_template/okms_template_version; Rust recognizes an occupied matching namespace and repeated setup preserves project bytes.
- Package/tag validation still matches Cargo 0.2.0; full native/adoption/distribution regressions and required checks pass before final native evaluation.

## Verify

- Method: real MkDocs strict build before/after, copied-binary setup with matching occupied docs, Cargo checks, document checks and the complete maintainer suite.
- Expected: matching source/install metadata with preserved runtime behavior and historical assets.
