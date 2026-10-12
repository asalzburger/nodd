# SESSION-2026-10-05-pr39-dashboard-fix — Restore historical Git evidence in CI

## Scope and selected request

User, exact: “The building of the project dashboard is still breaking in PR #39”.
This is a bounded workflow repair on the existing PR39 branch, starting at
`cb76e517dc0ac8f1dd7bcf6f5184b3361ef50d0b`. The existing isolated worktree was
clean. Primary local main and unrelated detector/display edits and usage records
were preserved. No subagents or Spack runtime were needed for this Git/Python fix.
ADR003 governs traceable evidence and ADR004 the session record; no scientific
parameters, design states or review decisions change.

## Diagnosis and correction

[Failed hosted run 37317957178](https://github.com/asalzburger/nodd/actions/runs/37317957178)
failed during project-record validation: the PR37 historical merge commit
`78bc60bb6da0c9d234baf00d37cadea9dd4964b4` was absent. Rebase removed it from
PR39 ancestry. The earlier local checkout retained the Git object, so local
validation did not reproduce CI's missing-history condition. The assistant
explained that gap and reproduced the exact failure with a fresh single-branch
GitHub clone before changing validation inputs.

The workflow now runs a separate `fetch_evidence.py` preparation step before
record validation. It collects merged PR heads/merges and review target SHAs,
validates all full SHAs before network work, fetches only missing commits from
an existing remote, and rechecks their presence. Fetch failure or absent evidence
fails explicitly. The existing offline builder, ancestry checks and approval
checks remain unchanged. History is recovered rather than replacing review SHAs,
removing PR37 metadata, fabricating a merge, or changing acceptance rules.

A reusable regression fixture creates a fresh clone with inaccessible local
historical objects. It verifies exact merge/review recovery, ancestry and an
idempotent second invocation. Additional controls reject malformed revisions
before fetch, fail unavailable commits, and leave open-PR metadata snapshots
outside the required historical evidence set. Test records are synthetic.

The README documents the explicit network preparation command. PR39's scope
notes this workflow correction without adding an infrastructure progress task.
No literature or material provenance changed. Public GitHub objects and the
original recorded commit identities are the source evidence.

## Commands and observed checks

The paired JSON lists actual commands, exits and results.

- Original hosted failure inspected; exact validation failure reproduced in a
  single-branch clone of PR39 with no shared local object database.
- Explicit history fetch recovered seven absent commits from GitHub, including
  PR37 merge and original head. Same-clone dashboard validation and build pass.
- Four new recovery controls and the full 31-test dashboard suite pass.
- Existing-worktree preparation is a no-op; local validation and build pass.
- Whitespace and final session checks are run before publication.

Network requests initially failed in the sandbox and were retried through
approved escalation. No shared dependencies, local detector edits or history
were discarded. Historical scientific/native validation files are preserved.

## Publication and follow-up

This initial record precedes the normal fix push. Hosted CI is followed to
verify the requested dashboard outcome; observed run/revision details are added
at closeout. Commit and changed-file inventories are in the paired JSON.

## Token accounting

Exact client-reported per-turn counters were unavailable; `usage` is empty.
This task's input/output are unknown. Historical observations are not duplicated.
The required summary at closeout distinguishes observed totals from missing
coverage; it cannot measure this task.
