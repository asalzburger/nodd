# SESSION-2026-10-23-pr96-accounting — Reconcile issue95 and PR96 token accounting

## Scope and evidence

Bounded follow-up to [PR96](https://github.com/asalzburger/nodd/pull/96) and
[issue95](https://github.com/asalzburger/nodd/issues/95), starting from clean
`e7b4b90701b2b0269cbbe42af0e2cd9ce5f4f59c` on `codex/issue95-unrooted`.
The [human comment](https://github.com/asalzburger/nodd/pull/96#issuecomment-6361616493)
requests accounting in this PR before merge. Read the repository and logging
instructions and preserved existing implementation, validation and journal history.

## Selected conversation

User request, exact: “There’s a comment on 96, count all tokens for 96 and the issue 95 for the merge.”

Assistant outcome: recovered every completed turn in the explicitly identified
issue95/PR96 chat and imported its disjoint counters into the original journal.
The installation, validation and PR delivery share one completed turn, counted
once. The current accounting turn remains explicitly active and provisional.

## Decisions and outcomes

Used the authorized usage-only recovery tool against the selected local desktop
thread `01a167a1-7906-7b73-9408-509e483359fc`. It decodes only token-count events
and reads turn metadata; no raw rollout or private model state is retained.
The original user request, existing journal and current chat identify the exact
work. Other unrooted development and neighbouring nODD tasks are excluded.
The recorded child-thread metadata has no children for this parent.

The [curated inventory](../usage/USAGE-2026-10-23-pr96-accounting.json) records
one completed turn: 60 observed requests, 7,137,997 input, 24,680 output and
7,162,677 total tokens. Cached input 7,031,040 and reasoning output 8,526 are
subsets. Every cumulative increase equals its last-request counters from zero;
no repeated snapshots or outside-turn events occur. No pre-existing canonical
owner was found. The original installation journal owns the entry once; the
inventory only corroborates it and never adds another contribution.

The active accounting turn has no closing boundary. Its snapshot is an excluded
lower bound, not a finalized total. Actual model/client version, billing and
other-device completeness remain unknown. No estimate or artificial boundary
was used to claim final accounting for an unfinished turn.

## Commands and validation

- Read issue95 and PR96 comments and PR metadata; the request is accounting-only.
- `git fetch origin main codex/issue95-unrooted`: sandbox DNS failed, approved
  network retry succeeded; remote branch and main still match the expected base.
- `recover_usage.py --thread-id 01a167a1-7906-7b73-9408-509e483359fc`: succeeded
  with one closed and one active turn, no duplicates or outside-turn events.
- `session_log.py import-usage --dry-run`: one prospective addition.
- `session_log.py import-usage`: one actual addition.
- Identical replay with `--dry-run`: zero additions and one unchanged entry.
- Initial session tests found 17 link subtest failures in ignored upstream uv-cache
  documentation with unbuilt example images. Relocated that download cache outside
  the checkout; no source, test gate or installed environment changed. All 33
  session/recovery tests and all 10 token-site tests then passed.
- Session, token, project, unit-test, preview and whitespace outcomes are retained
  in the paired JSON. No plotting code changed, so the installation smoke was
  not unnecessarily rerun. Original hosted checks at the starting revision passed.

## Changes and revision links

Updated the original journal pair with a dated recovery correction and exact
usage; added the curated usage inventory, its README summary and this accounting
journal pair; linked the evidence from the existing software task. No separate
infrastructure task, detector design approval or merge is recorded. The PR body
shows the same disjoint totals and the active-turn exclusion. The paired JSON
lists the exact changed files; Git history identifies the enclosing revision.

## Token accounting

The original task owns 7,137,997 input + 24,680 output = 7,162,677 tokens.
This follow-up has no final counters yet, so its own `usage` remains empty.
The project summary after this import is 196 sessions, 125 with usage and 71
without; 234 disjoint observed turns sum to 736,838,845 input + 4,154,365 output =
740,993,210 tokens. These are observed project totals with missing coverage,
not complete billing. Cached and reasoning subsets are never added again.

## Follow-up

Review PR96 after checks pass on the accounting commit. Recover this accounting
turn after its completed boundary becomes available; assign it only to this
follow-up journal without reimporting the original issue95/PR96 turn. The current
request prepares the PR for merge and does not itself merge it.
