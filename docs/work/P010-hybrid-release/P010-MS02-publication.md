---
type: MicroSpec
kind: implementation
title: P010-MS02 · Commit, push, and publish
description: Publish the user-authorized committed source and verified prerelease assets with truthful installation evidence.
---

# P010-MS02 · Commit, push, and publish

## Intent

Make the authorized changes and pinned curl installer available on GitHub as an experimental Hybrid Team release.

## Constraints

- Always: publish the checked committed source, exact built assets, and native trust/observed limitations; retain historical tags and evaluation failures.
- Always: keep raw pilot projects, credentials, runtime state, caches, and local build artifacts out of the commit.
- Never: force-push, replace an existing release/tag silently, or report a local installer rehearsal as a public-download verification.

## Acceptance

- Remote main contains the reviewed source and a pushed tag identifies its release commit.
- GitHub hosts prerelease hybrid-team-v0.1.0 with the archive, installer, and SHA256SUMS matching local hashes.
- The actual public installer downloads its assets and supports dry-run, new adoption, and repeat in a disposable project while preserving existing content and staging.
- Required repository checks pass and the completed plan records the public URL, source commit, downloaded verification, and retained native activation limits.

## Verify

- Method: required checker/test suite, staged diff review, remote ref/release API observations, public curl downloads and hashes, and actual setup/helper commands.
- Expected: published refs/assets match checked source; setup is usable without a source checkout; native provider task sessions are not started.
- Tests: reuse passing distribution/runtime/adoption coverage; verify the actual released transport and preservation boundary after publication.
