# Two workflows and existing-system obligations: v0.3

Both targeted fresh agent conversations pass every observed criterion. Lite keeps an existing-code fix standalone; Plan-first adds baseline and compatibility sections for a compatible refactor. Independent grading passes 80 behavior cases and seven original test-method executions.

Observed on October 4, 2026 with `codex-cli 0.159.0`, the existing login, and the existing default model without an override. The model ID was not recorded. The observed 0.3.0 draft is identified by the frozen 32-file payload fingerprints and grading-source hashes in [the measurements](workflow-results.json).

## Outcomes

| Scenario | Workflow | Independent behavior cases | Original tests | Observed final project tests | Outcome |
| --- | --- | --- | --- | --- | --- |
| Repair existing page-size parsing | Lite | 20 passed | 3 passed | 6 passed | One standalone bugfix spec; no plan; done with recorded evidence. |
| Consolidate existing endpoint validation | Plan-first | 60 passed | 4 passed | 13 passed | Plan includes conditional Baseline and Compatibility; retained endpoint behavior passes; done. |

These counts distinguish independently specified behavior cases, original test methods rerun outside the agent's editable test directory, and the final test methods observed in the project. They do not count every agent-authored subtest as an independent requirement.

## Observed order and retained behavior

| Scenario | Successful baseline unit check | First saved contract | First application source change |
| --- | --- | --- | --- |
| Lite | 31.5 seconds | MicroSpec at 78.4 seconds | 153.2 seconds |
| Plan-first existing system | 40.8 seconds | Plan at 104.0 seconds | 186.4 seconds |

Times are relative to each CLI invocation. Timestamped command events and 20-millisecond file polling support the observed order; a shared snapshot tick would not prove an ordering claim.

The Lite agent records the passing three-test baseline and probes demonstrating existing invalid-input behavior in Verify before changing the parser. It then adds regression tests, observes them fail against the old implementation, and repairs the parser. Public names, the default value, and the untouched endpoint remain intact.

The Plan-first agent records the actual endpoint baseline and compatibility obligations before source changes. It centralizes validation while retaining defaults, accepted and rejected inputs, item data, response shapes, and authorization order. Its plan also identifies existing conversion exceptions so the refactor does not broaden error handling accidentally. The independent endpoint matrix and original tests pass.

Both final document bundles satisfy the checked contracts. The observed Plan-first plan removes the blueprint's authoring guidance rather than retaining it as task content.

## Scope and limits

These are two controlled projects with one CLI and its current default model. They demonstrate the selected existing-system scenarios; they do not guarantee behavior across agents or arbitrary projects. The full routing, fresh-session recovery, and portable Goal matrix was not rerun for 0.3. Native Goal execution was not activated or tested. Conditional section omission is covered by structural contract fixtures rather than a fresh isolated-new-project agent conversation.

Raw prompts, events, file snapshots, independent tests, and grades remain in ignored run directories outside each agent's writable project. The published measurements retain all criteria and hashes for audit. Historical [v0.1](pilot-report.md) and [v0.2](routing-report.md) reports and measurements remain unchanged and describe their original source versions.
