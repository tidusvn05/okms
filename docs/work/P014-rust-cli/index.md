# P014 · Standalone Rust CLI

- [Plan](plan.md) - Replace the Hybrid Team Python runtime with a standalone Rust binary and publish its verified release.
- [Runtime foundation contract](P014-MS01-foundation.md) - Preserve identities, coordinator fencing, durable messages, and the JSON command interface.
- [Coordination contract](P014-MS02-operations.md) - Scoped worktrees, bounded provider drivers, exact resume, gates, hooks, and checkpoints.
- [Adoption contract](P014-MS03-adoption.md) - Embedded payload, project-local executable, preserving setup, and Python-free native commands.
- [Distribution contract](P014-MS04-distribution.md) - Checked platform archives, Python-free installation, CI and regular tag publication.
- [Process cleanup contract](P014-MS05-processes.md) - Bound descendants after their driver exits during cancellation.
- [PR integration contract](P014-MS07-pull-requests.md) - Review the stacked portable changes and merge a checked combined tree.
- [PR review](PR-review.md) - Exact revisions, findings, integration checks and agent-observation limits.
