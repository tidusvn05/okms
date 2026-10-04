# Hybrid Team walkthrough

This is illustrative. No application commands or provider sessions are executed by this example. Use the opt-in runner in [evals](../evals/README.md) for actual observations.

Explicitly install [Hybrid Team](../templates/hybrid-team/docs/index.md). Keep project policy in TeamSpec, acceptance in MicroSpecs, and progress in a Plan. Opening Codex first makes that session coordinator after native hook activation; opening Claude Code afterward makes it standby. If hooks have not loaded, use the documented explicit join and record that startup limitation.

Suppose a saved plan has two independent ready rows: normalize labels and format integer durations. Save each micro spec before dispatch, reference existing baseline/compatibility evidence, and assign separate owned module paths. A Codex worker receives labels; a Claude Code worker receives durations. Their worktrees share one snapshot of current code, including the root's unstaged edits and nonignored new files.

| Record | Responsibility |
| --- | --- |
| TeamSpec | Project routing, authority, communication, integration, and recovery policy. |
| AgentRole | Reusable coordinator, worker, or reviewer behavior. |
| DelegationBrief / WorkerResult | One assignment and its actual observations/evidence/gaps. |
| AgentRun | Operational assignment state, deadline, worktree, and native session ID. |
| Message / Event | Directed request/response/notice with acknowledgment; ordered append-only observation. |
| Plan / MicroSpec | Verified progress and outcome acceptance. |

The label worker needs a naming decision. It sends a request addressed to the duration worker, then returns waiting_input. The peer responds with reply_to and acknowledges the request. The runtime wakes the original worker using its exact saved native session ID; it acknowledges the response and finishes its assigned scope. Peer discussion cannot allocate work or change acceptance.

Both result_ready records are candidates. The coordinator reads diffs and evidence, combines the batch in an integration worktree, runs real project checks, applies the accepted delta without updating the root index, and verifies the actual root. Only then does checkpoint mark the rows done. If a required root check fails, the applied_unverified batch and plan remain incomplete until explicit successful re-verification.

For handoff, the active coordinator transfers to the registered standby identity. Pending messages addressed to coordinator follow the new owner. A lost owner needs explicit recovery; stale tokens cannot dispatch, integrate, or checkpoint. Worktrees, session IDs, consumed time, failed checks, and the Plan's Resume survive. Native trust/permissions and evidence gaps remain visible.
