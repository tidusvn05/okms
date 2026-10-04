---
type: MicroSpec
kind: implementation
title: P011-MS02 · Release-aware installation
description: Select published Hybrid Team releases safely and document installation and tag automation.
---

# P011-MS02 · Release-aware installation

## Intent

Provide a stable installation entrypoint that selects the newest complete published Hybrid Team release, while retaining exact pins and offline setup.

## Constraints

- Always: resolve only namespaced numeric versions with the required uploaded assets; verify checksum/manifest before preserving setup.
- Always: preserve explicit numeric pins, offline assets, native activation requirements, and existing installations/customizations.
- Never: use the stable-only latest endpoint for prereleases, silently fall back after failed discovery, or imply that CI checks establish native agent behavior.

## Acceptance

- Latest selection includes complete published prereleases, skips drafts/incomplete/unrelated releases, orders versions numerically, and follows API pagination.
- Explicit pins skip discovery; offline latest selection performs no network call. Missing/invalid discovery evidence fails before project mutation.
- README's agent and manual setup paths use the release installer; maintainers push a matching tag and let Actions publish the checked assets.
- Required checks/lint and genuine published-release installation pass; authorized workflows are activated and CI/manual rehearsal is observed with publication skipped.

## Verify

- Method: fake API/download fixtures, preserving installer tests, actionlint, required repository checks, actual current-release installation, and GitHub Actions observations.
- Expected: deterministic candidate selection and unchanged failure/dry-run/repeat boundaries; no replacement of the current release or new provider task session.
- Tests: cover numeric order, prerelease completeness, pagination, explicit/offline pins, malformed/empty/failed discovery, and the retained distribution scenarios.
