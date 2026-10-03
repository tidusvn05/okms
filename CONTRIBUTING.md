# Contributing to okms

Keep templates portable, English, and small enough to read once at task start. Use the repository's [Plan-first workflow](docs/workflow.md) and save the current micro spec before implementation.

## Maintainer checks

The copied templates have no dependencies. The repository checker uses Python 3.10+ and PyYAML to parse frontmatter:

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
okbase -b templates/brownfield/docs lint --level L1
okbase -b examples/lite lint --level L1
okbase -b examples/plan-first lint --level L1
okbase -b examples/brownfield lint --level L1
```

## Review changes

- Copy each payload to a different directory and follow its links; no required link may depend on the okms checkout.
- Preserve existing project docs and instructions during setup; repeat setup without overwriting context or adding duplicate pointers.
- Keep shared blueprints consistent across profiles. Make profile differences explicit in the workflow; Brownfield adds baseline and compatibility to the plan.
- Render blueprints with actual types, titles, descriptions, and values before treating them as work. Never execute a placeholder.
- Keep plan progress in its Work table, standalone progress in its spec, and evidence truthful. Future specs remain text entries until their files exist.
- Keep historical paths and indexes stable. Promote lasting rules into current docs rather than loading all history.
- Select task kinds independently of profiles. Keep catalog rows, blueprint kinds, and shared copies consistent; kindless historical specs stay valid.
- Goals reference plans and preserve reserved attempts. Exercise budget exhaustion, explicit extension, blocked verification, and fresh-session recovery; never equate an exhausted limit with completion.

## Agent workflow pilot

Use a disposable project with actual code and applicable checks. These scenarios need an agent session; structural checks alone cannot demonstrate agent compliance.

1. Ask for one independent change with Lite. Confirm its saved spec precedes implementation and its Verify section records actual results.
2. Ask for two dependent outcomes with Plan-first. Confirm the plan is saved first, the second spec is written when needed, and progress is updated after checking the first.
3. Start a fresh session after a checkpoint. Give it the task and project instruction pointer without prior chat. Confirm it selects the matching plan, inspects current files, and continues from Resume.
4. Use Brownfield for a compatible change. Confirm current behavior and real baseline results are recorded before implementation, and retained behavior is checked afterward.
5. Introduce a failed required check or unavailable necessary verification. Confirm the item stays incomplete, the blocker is recorded, and acceptance is not weakened.
6. Add unrelated historical specs. Confirm the agent loads current work and applicable constraints, expanding its reads only when the task warrants it.

Record the task, profile, agent/version, files read, observed state transitions, and actual verification results. Identify unexpected behavior instead of presenting instructions as guaranteed enforcement.

For task routing, observe all six specialized kinds and general, investigation-to-repair recovery, design compatibility, supplied source limits, runbook rehearsal, and portable Goal exhaustion/extension/blocking. Record unnecessary blueprint reads as exceptions even when the chosen kind and output are correct. Native activation needs its own actual runtime evaluation.

Run the opt-in, executable [agent pilots](evals/README.md) when evaluating workflow changes. The [v0.2 report](evals/routing-report.md) retains 15 fresh conversations across two drafts and the selective-reading exception; the [v0.1 report](evals/pilot-report.md) remains historical. Raw traces and disposable projects stay outside the published templates; the normal maintainer checker does not launch an agent.

## Versioning and upgrades

The current payload version is `0.2.0`, recorded in each `workflow.md`. Change every profile's version together when publishing updated contracts. Review copies manually during an upgrade: preserve project context, active work, and history, and merge workflow/blueprint changes deliberately.

For a v0.1 copy, add the task catalog, six specialized blueprints, Goal blueprint, and Goal guide; merge indexes and workflow rules deliberately. Keep existing spec IDs, plan columns, and kindless historical files. Broaden the existing instruction pointer from implementation tasks to substantive project tasks when adopting the new routing rules, while retaining other project instructions. Repeated setup alone does not upgrade an installation or change its profile.

Check the final change, describe its behavior and evidence, and keep the release focused on templates, documentation, and examples. Installers and automatic synchronization belong in a later proposal.

Contributions are provided under MIT OR Apache-2.0, matching this repository.
