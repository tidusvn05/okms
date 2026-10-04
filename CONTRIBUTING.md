# Contributing to okms

Keep templates portable, English, and small enough to read once at task start. Use the repository's [Plan-first workflow](docs/workflow.md) and save the current micro spec before implementation.

## Maintainer checks

Lite and Plan-first have no runtime dependencies. Hybrid Team uses Python 3.10+, SQLite from the standard library, Git, and installed/logged-in provider CLIs. The repository checker uses Python 3.10+ and PyYAML to parse frontmatter:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/check_docs.py
.venv/bin/python -m unittest discover -s tests -v
```

On Windows, use `.venv\Scripts\python.exe` for the last two commands. The checker validates Markdown links, YAML, index coverage, document contracts, plan progress, payload independence, and temporary onboarding scenarios. It does not invoke an agent or run the applications described by the examples.

If okbase is available, also check the bundles against its L1 rules:

```sh
okbase -b docs lint --level L1
okbase -b templates/lite/docs lint --level L1
okbase -b templates/plan-first/docs lint --level L1
okbase -b templates/hybrid-team/docs lint --level L1
okbase -b examples/lite lint --level L1
okbase -b examples/plan-first lint --level L1
okbase -b examples/existing-system lint --level L1
```

## Review changes

- Copy each payload to a different directory and follow its links; no required link may depend on the okms checkout.
- Exercise Hybrid Team setup in disposable Git projects, remove the temporary source, and check preserving JSON hook merges, agent/skill collisions, repeated setup, and standalone commands. Ordinary tests use fake transports and never start provider sessions.
- Preserve existing project docs and instructions during setup; repeat setup without overwriting context or adding duplicate pointers.
- Keep shared blueprints consistent across Lite and Plan-first. Apply baseline and compatibility obligations by affected scope in either workflow; extra plan sections are conditional.
- Render blueprints with actual types, titles, descriptions, and values before treating them as work. Never execute a placeholder.
- Keep plan progress in its Work table, standalone progress in its spec, and evidence truthful. Future specs remain text entries until their files exist.
- Keep historical paths and indexes stable. Promote lasting rules into current docs rather than loading all history.
- Select task kinds independently of profiles. Keep catalog rows, blueprint kinds, and shared copies consistent; kindless historical specs stay valid.
- Review findings include scope/revision, location, impact, evidence, and limits. Behavior-preserving refactors use implementation with baseline and retained-behavior checks.
- Optional role, delegation brief, and worker result records reference the existing contract and never own progress. Load them only for authorized delegation; one coordinator updates shared records and checks combined acceptance.
- Goals reference plans and preserve reserved attempts. Exercise budget exhaustion, explicit extension, blocked verification, and fresh-session recovery; never equate an exhausted limit with completion.

## Agent workflow pilot

Use a disposable project with actual code and applicable checks. These scenarios need an agent session; structural checks alone cannot demonstrate agent compliance.

1. Ask for one independent existing-code change with Lite. Confirm baseline evidence and retained behavior are recorded in its standalone spec before implementation, and Verify records actual results.
2. Ask for two dependent outcomes with Plan-first. Confirm the plan is saved first, the second spec is written when needed, and progress is updated after checking the first.
3. Start a fresh session after a checkpoint. Give it the task and project instruction pointer without prior chat. Confirm it selects the matching plan, inspects current files, and continues from Resume.
4. Use Plan-first for a compatible refactor. Confirm conditional Baseline and Compatibility sections record current behavior and real baseline results before implementation, and retained behavior is checked afterward. For an isolated new outcome, confirm unnecessary sections are omitted.
5. Introduce a failed required check or unavailable necessary verification. Confirm the item stays incomplete, the blocker is recorded, and acceptance is not weakened.
6. Add unrelated historical specs. Confirm the agent loads current work and applicable constraints, expanding its reads only when the task warrants it.

Record the task, profile, agent/version, files read, observed state transitions, and actual verification results. Identify unexpected behavior instead of presenting instructions as guaranteed enforcement.

For task routing, observe all seven specialized kinds and general, investigation-to-repair recovery, review findings/no-findings limits, behavior-preserving refactors, design compatibility, supplied source limits, runbook rehearsal, and portable Goal exhaustion/extension/blocking. Record unnecessary blueprint reads as exceptions even when the chosen kind and output are correct. Native activation needs its own actual runtime evaluation.

For optional delegation, observe two bounded readers within one saved spec, actual results/evidence, missing child verification, failed combined checks, and recovery in a fresh conversation. Check native role loading and application/shared-document ownership from traces and snapshots; a requested delegation is not proof that workers ran. Preserve failed criteria and distinguish optional adapter behavior from portable contract checks.

Run the opt-in, executable [agent pilots](evals/README.md) when evaluating workflow changes. The [v0.4 report](evals/review-report.md) covers review/delegation and retained workflow behavior, including observed failures and runtime limits. The historical [v0.3 report](evals/workflow-report.md) covers targeted existing-system work; [v0.2](evals/routing-report.md) retains both drafts and the selective-reading exception, and [v0.1](evals/pilot-report.md) remains historical. Raw traces and disposable projects stay outside the published templates; the normal maintainer checker does not launch an agent.

## Build and publish Hybrid Team

Run the required checker/test suite first, then build the pinned distribution:

```sh
.venv/bin/python scripts/build_hybrid_release.py --output dist
sh dist/install.sh --release-dir dist --project /path/to/disposable-project --dry-run
sh dist/install.sh --release-dir dist --project /path/to/disposable-project
```

The builder emits `okms-hybrid-team-0.1.0.tar.gz`, `install.sh`, and `SHA256SUMS`. The archive contains the exact Hybrid Team payload, both license notices, and `release.json` with every file hash. It fixes member ordering, timestamps, ownership, and gzip metadata for reproducibility. `tests/test_hybrid_release.py` exercises real setup, downloaded/offline assets, dirty-project preservation, dry-run/repeat, integrity failures, and unsafe extraction without provider task sessions. Distribution assets stay in ignored `dist/`.

After explicit publication authorization, commit reviewed changes, push main, and tag that committed source. Publish the three assets as a prerelease:

```sh
git tag -a hybrid-team-v0.1.0 -m "Hybrid Team 0.1.0 experimental prerelease"
git push origin hybrid-team-v0.1.0
gh release create hybrid-team-v0.1.0 dist/okms-hybrid-team-0.1.0.tar.gz dist/install.sh dist/SHA256SUMS --verify-tag --prerelease --latest=false --title "Hybrid Team 0.1.0 (experimental)" --generate-notes
```

Include the profile's experimental status, project-local installation, required tools, preserving setup, and native trust/observation limits in release notes. Verify published downloads and actual installation in a disposable project. Pin download URLs to this tag; prereleases do not serve as GitHub's latest stable release. Bump the runtime version and installer default together for future distributions, and retain prior tags/assets.

## Versioning and upgrades

Lite and Plan-first are `0.4.0`; change both portable workflows' versions together for updated contracts. Hybrid Team is independently versioned experimental `0.1.0`. Review copies manually during an upgrade: preserve project context, active work, and history, and merge workflow/blueprint changes deliberately. Shared task contracts remain consistent across all profiles.

Keep existing spec IDs, plan columns, kindless historical files, and project instructions during deliberate upgrades. Repeated setup alone does not upgrade an installation or change its profile.

For a v0.3 portable installation, merge the review catalog/blueprint, revised implementation contract, optional delegation guide/blueprints, and index entries deliberately. Existing general reviews keep their historical kind. Optional adapter examples remain separate from portable adoption. Explicit Hybrid Team setup merges its native files; edits and effective native trust/permissions remain project/user-owned.

Check the final change and describe behavior, evidence, and limits. Hybrid Team's preflighted setup is opt-in; repeated adoption preserves modifications rather than synchronizing them. Live mixed-provider observations use the opt-in runner in [evals](evals/README.md); retain failed criteria and exact native IDs/traces. Structural checks cannot establish native hook activation.

Contributions are provided under MIT OR Apache-2.0, matching this repository.
