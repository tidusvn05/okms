---
type: MicroSpec
kind: implementation
title: P014-MS04 · Rust binary distribution
description: Build checked platform binaries, install without Python, and publish regular releases from matching tags.
---

# P014-MS04 · Rust binary distribution

## Intent

Distribute standalone Linux/macOS binaries through regular GitHub releases with an installer that needs no Python or source checkout.

## Constraints

- Always: match numeric Cargo/template versions and release tags, verify downloads before execution, preserve project data, and retain historical tags/assets.
- Always: build/check before publication, bound downloads, grant publication writes only to its job, and keep manual rehearsals nonpublishing.
- Never: silently upgrade a Python project copy, bypass native trust, run task agents in ordinary CI, or claim unobserved provider support.

## Acceptance

- Deterministic archives contain a native executable and both licenses; Actions builds and smoke-tests Linux/macOS on both supported architectures.
- Default installation resolves the latest regular release, numeric pins select exact assets, and offline installation works without Python. Dry-run writes nothing; invalid checksums, unsafe archives and setup conflicts fail before installation.
- Tags matching the committed version create regular releases with checked assets; mismatches fail before packaging, and manual dispatch never publishes.
- Current documentation explains binary installation, source builds, activation limits and deliberate legacy upgrades. Required Rust/Python checks and installer regressions pass.

## Verify

- Method: real binary archives/installer subprocesses, independent corruption and extraction controls, cargo fmt/tests/clippy, required maintainer checks, workflow lint and an observed Actions rehearsal.
- Expected: complete checked binary assets and reviewable regular-release automation; actual publication follows the final native spike.
- Tests: Python-free dry/new/repeat/global setup, preservation, exact/latest/offline URLs, corrupt/unsafe/missing assets, tag mismatch and legacy refusal.
