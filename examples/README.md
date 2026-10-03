# Worked examples

See the [routing and Goal walkthrough](routing.md) for mixed task kinds, source-based outcomes, and bounded loop recovery.

These examples illustrate document shape and workflow decisions. They contain no application code or executable application test suite. All application work remains planned and verification is explicitly unexecuted.

| Example | Scenario | What to look for |
| --- | --- | --- |
| [Lite](lite/index.md) | Reject invalid pagination sizes | One standalone micro spec owns its progress and verification. |
| [Plan-first](plan-first/index.md) | Admin device catalog and request decisions | A saved plan owns two dependent outcomes; only the first spec exists initially. |
| [Brownfield](brownfield/index.md) | Refactor existing pagination validation | An assumed scenario baseline, compatibility obligations, and a real-project verification gate. |

Use [the matching template](../README.md#choose-a-template) in your project, then write your own work from the actual code and requirements. Do not copy fictional baseline claims or test commands into real evidence.

The Plan-first walkthrough includes a proposed second spec inside a code block. It is a preview to write after the first item is checked, not an already-created work document. During actual use, list the plan's future outcomes first and create their specs one at a time.

Compare the [repository's own saved plan](../docs/work/P001-build-okms/plan.md) for actual implementation evidence. The [contribution guide](../CONTRIBUTING.md#agent-workflow-pilot) explains how to evaluate compliance in a disposable application with a real agent session.
