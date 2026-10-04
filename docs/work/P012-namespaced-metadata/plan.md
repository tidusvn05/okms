---
type: Plan
title: P012 · Namespaced template metadata
description: Rename portable workflow identity keys to okms_template and okms_template_version while still recognizing earlier installations.
work_status: done
---

# P012 · Namespaced template metadata

## Goal

Installed Lite and Plan-first copies must build inside documentation sites. Identify portable workflows with `okms_template` and `okms_template_version`, keep recognizing the unprefixed keys of earlier installations, and release the change as 0.4.1.

Out of scope: Hybrid Team metadata and runtime (identified by `.okms/install.json`; changing it needs a new runtime version), other setup-prompt improvements, and automatic upgrades of installed copies.

## Baseline

At 1d0716b the checker passes 182 Markdown files, seven bundles, and eight onboarding scenarios; 82 tests pass. Portable workflows carry `template: <profile>` and `template_version: "0.4.0"`. A Plan-first copy installed at `docs/okms/` in a MkDocs project failed `mkdocs build --strict` with `jinja2.exceptions.TemplateNotFound: 'plan-first'`, because MkDocs reads page `template` metadata as a theme template name.

## Compatibility

Setup must still reuse, never overwrite, an installation carrying only the unprefixed keys. Profiles, payload files, task contracts, and destinations stay unchanged. Distributed payloads and the maintainer workflow carry only the namespaced keys. Upgrading an earlier copy is a manual rename of two keys.

## Approach

- One implementation spec covers payloads, checker, tests, setup instructions, and maintainer docs, because the key names are a single contract.
- The checker rejects unprefixed identity in payloads and accepts either form when recognizing an installation; a legacy onboarding scenario proves reuse.
- Patch version 0.4.1: recognition stays backward compatible and no contract section changes.

## Work

| Spec | Depends on | State | Evidence |
| --- | --- | --- | --- |
| [P012-MS01 · Namespaced metadata](P012-MS01-metadata.md) | — | done | `python3 scripts/check_docs.py`: PASS, 185 Markdown files, seven bundles, 10 onboarding scenarios (two new legacy-reuse scenarios). `python3 -m unittest discover -s tests`: 84 tests OK. With legacy recognition removed, the legacy scenario fails as expected. PyYAML 6.0.2 from the system Python; no venv was available. |

## Resume

- Current: complete.
- Next: none; a later Hybrid Team version may adopt the same keys.
- Blocker: none.

## Result

Lite and Plan-first 0.4.1 identify themselves with `okms_template` and `okms_template_version`; setup prompts and the manual procedure recognize both forms, and the checker pins both rules. No agent pilot ran; MkDocs acceptance of a 0.4.1 copy follows from the absent `template` key and was not rebuilt in this repository.
