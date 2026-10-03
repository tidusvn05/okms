# Task routing and portable Goal pilot: v0.2

Eight of the nine latest scenarios meet every observed criterion. All nine select the expected kind and pass their deliverable, document, behavior, and Goal checks. Blocked verification remains unsuccessful on one selective-reading criterion: the agent reads general as well as bugfix, while correctly preserving incomplete work.

This report retains all 15 fresh conversations across two drafts, including unsuccessful grades. Independent grading passed 240 behavior-case executions and 47 original test-method executions. These counts include repeated cases during recovery and reruns, rather than 240 distinct requirements. The first nine conversations exposed instruction gaps; six affected conversations were rerun in new projects after clarification.

Observed on October 4, 2026 in Asia/Tokyo with `codex-cli 0.159.0`, an existing login, and the existing default model without an override. The model ID was not recorded. Both observed drafts identify the unreleased payload as `0.2.0`; the published measurements distinguish them by source fingerprints.

## Matrix and grading

Seven controlled projects cover six specialized task kinds and the general fallback across all three profiles. Investigation/repair and Goal limit/resumption each use two different conversations. Continuation receives only the prompt and saved project files, without the previous chat.

| Scenario | Profile | Expected kind | Required outcome |
| --- | --- | --- | --- |
| Diagnose pagination failures | Plan-first | investigation | Reproduce the crash, explain the confirmed cause in findings, preserve application files, and defer repair with a checkpoint. |
| Resume the repair | Plan-first | bugfix | Repair from saved evidence, preserve findings, verify strict parsing and endpoint responses, and close the plan. |
| Decide validation ownership | Brownfield | design | Compare alternatives, preserve response and authorization contracts, save the decision, and record the actual baseline. |
| Compare supplied reports | Lite | research | Attribute fixture facts, dates, and measurement limits without an unsupported architecture decision. |
| Author recovery procedure | Lite | runbook | Use actual commands, rehearse recovery/rollback with dry runs, and preserve service state and source. |
| Translate a note | Lite | general | Preserve the timeout, attempt count, and literal command without executing it. |
| Stop at one Goal attempt | Plan-first | implementation | Reserve attempt 1 before edits, complete the parser only, and retain the pending endpoint with an exhausted, incomplete Goal. |
| Extend and resume the Goal | Plan-first | implementation | Preserve attempt 1, explicitly extend the total limit to 2, use the same Goal, complete the endpoint, and preserve the completed parser. |
| Encounter an unavailable gate | Plan-first | bugfix | Repair and check the parser, attempt the protected gate unchanged, and save a blocked Goal with incomplete verification. |

The observer retains JSONL events, command results, timestamped snapshots, prompts, and final projects outside the agent's writable fixture. Grading checks saved metadata and artifacts, blueprint reads and their timing, spec-before-output order, original source hashes, and required checks. Parser/endpoint behavior is checked independently; original test text is rerun outside the editable project test directory. Reading the service source does not count as a runbook rehearsal: the grade requires an executed dry-run command and its concrete output.

The research sources are synthetic Harbor and Quarry reports. Their 4 ms and 12 ms fixture values use different persistence conditions and unspecified hardware. The task checks attributable comparison and explicit limits; it provides no evidence about actual products or benchmark performance.

## First draft and clarification

The first matrix passed research, runbook, and general. Investigation, repair, design, Goal limit, Goal resumption, and blocked verification failed document contracts because child indexes had frontmatter. Investigation also renamed the literal Next checkpoint field and read the general blueprint in addition to investigation. These failures remain in the measurements.

Only the workflow and task catalog changed in each payload for the second draft:

- Specify that only the bundle root index has `okf_version` frontmatter; child indexes have none.
- Retain literal `Current`, `Next`, and `Blocker` checkpoint fields, putting qualifications after their colons.
- Explain that every specialized blueprint contains the common contract; general is a fallback and future planned kinds do not need their blueprints yet.

The affected cases use new disposable projects and fresh conversations. Research, runbook, and general retain their first observations; their blueprints are byte-identical across drafts. The latest scenario set therefore combines both recorded source revisions rather than claiming that every scenario was rerun against the final payload.

Original grades were retained before adding two stricter observer checks: the selected blueprint must be observed before the first output, and a concrete service dry-run output must accompany an executed command. The checker also rejects empty or placeholder blocked dependencies. Regrading the same first-draft artifacts did not change which scenarios passed or failed. Published fingerprints distinguish invocation snapshots from the final grading code. No acceptance was weakened.

## Latest observations

| Scenario | Independent behavior cases | Final observed project tests | End state | Full workflow grade |
| --- | --- | --- | --- | --- |
| Investigation | — | 3 passed | Investigation done; repair planned | Pass |
| Fresh-session repair | 40 passed | 19 passed | Plan done | Pass |
| Brownfield design | — | 4 passed | Plan done; application unchanged | Pass |
| Research | — | 3 passed | Standalone spec done | Pass |
| Runbook | — | 3 passed; recovery/rollback dry runs exited 0 | Standalone spec done; service state unchanged | Pass |
| General translation | — | 3 passed | Standalone spec done | Pass |
| Goal limit | 20 passed | 10 passed | 1/1 attempts; in_progress, iteration_limit | Pass |
| Fresh-session Goal resumption | 40 passed | 17 passed | 2/2 attempts; done, complete | Pass |
| Blocked Goal | 20 passed | 14 passed; required gate exited 2 | 1/3 attempts; blocked | Fail: extra general blueprint read |

The latest set separately passes 120 behavior-case executions and 28 original test-method executions. Every first- and second-draft project passed its original baseline before its agent ran. The unavailable gate's expected failure supports truthful blocked state; it is not counted as passing integration verification.

- Investigation saves its spec at 110.1 seconds and findings at 255.8, leaving one deferred repair row without a premature spec. A different conversation saves the bugfix contract at 116.5 seconds, changes source at 250.9, preserves findings, and closes the existing plan after checks.
- Goal limit reserves attempt 1 at 172.5 seconds before the parser changes at 215.0. At the limit, its endpoint and second spec remain uncreated. Resumption uses another conversation and the same Goal: it preserves the consumed attempt, records the explicit extension, reserves attempt 2 at 167.7 seconds, changes the endpoint at 216.0, and completes with both plan rows done. The completed parser is not rewritten.
- Blocked Goal preserves the protected gate and records its actual exit 2. Parser behavior and 14 unit tests pass, but Goal and plan remain blocked at 1/3 attempts. Its child indexes now satisfy the document contract; the extra general blueprint read is retained as a failure.
- Neither investigation/repair nor Goal conversation emits one of the 200 unrelated historical spec body canaries. Research and translation preserve their supplied facts and literal values. Design records alternatives and observed compatibility, and the runbook distinguishes actual dry runs from unexecuted live operations.

Times are relative to each conversation's observer start. The [portable measurements](routing-results.json) preserve every criterion, both source revisions, distinct conversation IDs, final states, timelines, executed checks, and prompt/trace/grade fingerprints. The final graded set is mixed across drafts as described above; selective reading is not claimed as universally enforced.

## Repository checks

The document checker passes 109 Markdown files, seven maintained/example bundles, and 12 disposable setup scenarios. All 19 contract tests pass, including negative kinds/catalogs, legacy specs, progress ownership, invalid budgets and states, premature completion, missing native references, and unrecorded blocked dependencies. Python syntax and diff checks pass. Published measurements match all 15 raw prompts, traces, grades, distinct conversation IDs, final payloads, grading source fingerprints, and measured totals.

Actual okbase L1 returns zero errors and warnings for maintainer docs (34 documents), each of the three payloads (16), and all seven latest output bundles: repair (222), design (20), research (21), runbook (18), general (18), completed Goal (223), and blocked Goal (21). Lint validates knowledge-base structure; the selective-reading exception and unavailable integration gate remain visible.

## Reproduction and limits

Follow the [runner instructions](README.md):

```sh
.venv/bin/python evals/run_routing_pilot.py --run-dir .pilot-runs/routing-my-run
```

The runner records payload hashes and source snapshots when a run starts. It rejects a changed payload before preparing another project in that run; use a new run directory for a new draft. Regrading retains the original conversation and project evidence. Raw artifacts stay in ignored local directories; published measurements contain fingerprints and selected evidence.

This evaluates a small controlled matrix with one default CLI configuration. Save-order claims require different polling ticks, and history canaries measure bodies emitted in tool output, rather than proving that no file was opened. Plan-first fixtures contain 200 unrelated historical specs. Markdown instructions guide behavior but do not enforce selective reading through a runtime.

Only portable Goal execution is exercised. Native execution is a documented capability mapping and has not been activated by this pilot. The protected integration gate is deliberately unavailable and remains unverified. Fixtures do not execute the applications described by the worked examples or establish behavior across other agents, models, or large projects.
