# Review and delegation walkthrough

These examples are illustrative. No application review, probes, tests, or agent delegation was executed here. Render real scope, revisions, paths, and evidence from the project; do not copy hypothetical findings into a review report.

## Review with a finding

"Review the authorization change and report defects; do not repair it" selects `review`. Save the review micro spec before producing its report. A finding needs a concrete location, impact, and supporting reasoning or a probe. This is a hypothetical shape:

```text
Scope: the assigned endpoint diff against its recorded base revision
Finding: a response path returns restricted records before authorization
Location: actual endpoint symbol and line range from the reviewed revision
Impact: an unauthorized caller can receive protected records
Evidence: cite the observed control flow and any actual reproduction
Limits: identify unexamined callers and checks that did not run
```

A subsequent authorized repair is another outcome. Keep the review report as evidence; use bugfix for a demonstrated contract violation. Do not silently turn findings into application edits.

For a document citation, link to the actual source file and keep the line number in its label: `[api.py:3](../api.py)`. A `file.py:3` link target usually names a nonexistent file.

## Review with no findings

A no-findings report still needs scope and limits:

```text
Scope/revision: the exact parser change and its recorded comparison base
Criteria: defaults, rejected values, and retained public signatures
Checked areas: enumerate the examined paths and relevant tests
Findings: no supported issue in the checked scope
Evidence: actual review reasoning and any executed probes/results
Limits: unexamined integration paths and unavailable checks
```

This shape does not claim the entire system has no defects. Missing evidence needed for a required conclusion leaves the parent outcome incomplete. Tests can be skipped with a justified reason when code review supplies the necessary evidence; required project checks still apply.

## Assign readers within one spec

For a coordinated review, the plan can have one review row. Its Approach names a coordinator, two independent readers, their scope, and the combined verification method. Save the selected spec first, then read the optional delegation guide. A reader role uses Mission / Trigger / Authority / Output / Escalation and owns no work state.

Example assignment content:

```text
Reference: the current review spec and its progress owner
Context: actual revision, parser paths, and applicable project instructions
Intent: review the parser's retained input contract
Constraints: read-only; shared plan and index updates belong to coordinator
Acceptance: the parent's parser criterion, with supported findings and limits
Verify: return code references and actual/absent probe evidence
```

Give the second reader the authorization paths. Neither needs another micro spec merely because it runs in a separate thread. Their messages can suffice; persist a brief/result only when needed for recovery. Native agent setup is optional and depends on the actual tool.

## Return results and checkpoint

A worker returns Reference / Result / Evidence / Remaining / Next. If a required probe is unavailable, Remaining names that gap and Next identifies how the coordinator can resolve it. A worker saying "finished" does not close the plan row.

The coordinator waits for both results, validates their scope and supporting references, and checks combined acceptance. Ordered edits need explicit ownership and integration checks. When a required check fails, retain the missing evidence and incomplete state; do not weaken acceptance or alter the protected check.

For a handoff, reuse the plan checkpoint:

```text
- Current: review spec; both scoped reader results saved, verification pending.
- Next: inspect the actual revision and saved results, then run the remaining check.
- Blocker: identify an unavailable required check, or none.
```

A new session reads the saved contract and current files without prior chat. It preserves verified work and IDs, checks whether old worker references still exist, and runs only remaining work. There is no second progress ledger in roles, briefs, or results.
