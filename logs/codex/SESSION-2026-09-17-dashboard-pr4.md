# SESSION-2026-09-17-dashboard-pr4 — Rebase and merged baseline review

## Scope and evidence

Contemporaneous curated infrastructure task on feature/project-dashboard, starting
at 445ae6c8c6bf959eb88d8473810c8cffc41e6def with a clean working tree. The session
pair was created after rebase; original starting SHA was verified from ORIG_HEAD.
Latest fetched main: b106610b929cdfa603dd5f1ef2a6e79dbb633a7f. Exact usage and client
identifiers are unavailable.

## Selected conversation

User (exact quote): “Can you rebase to main and update the dashboard with the first
signed-off and merged PR ?”
Assistant outcome: rebased onto fetched main, retained both documentation-index
changes, and displayed PR #4's explicit envelope-baseline approval and merge.
The merged DES-003 and ADR-006 still declare DRAFT, and no formal sign-off record
exists. The dashboard exposes that discrepancy without promoting documents or
creating approval records on a human's behalf.

## Decisions and outcomes

Added completed TASK-B-ENVELOPES and linked DES-003, ADR-006, analytic diagnostics,
review dispositions and study catalogue. Added curated PR metadata with exact head,
merge revision and collection time. Recorded two changes-requested rounds followed
by explicit human technical baseline approval at cb654ee91457b22d899a898faf2c8bf6e0fc275e;
review evidence is linked directly in the tracking records. The decision scope is
envelopes only; production geometry, full magnet design and performance acceptance
remain outside this decision. Historical rounds no longer appear as current
blockers after a later review is recorded.

Extended schema optional metadata and document adapters for existing emphasized
and semicolon-qualified status fields. Added tests of the actual review history
and invalid merge metadata; preserved separation of technical approval, document
lifecycle and formal sign-off. Source documents and accepted evidence were not
edited or regenerated. External scientific-source provenance was inherited from
main, not independently altered by this dashboard update.

Preserved original commits under local branch
archive/dashboard-before-main-rebase-2026-09-17 so older logged hashes remain
reachable. Rebased dashboard commits are 8cb7706 and 5efc477. No remote history
was rewritten or force-pushed.

## Commands and validation

Fetched main and read the design/ADR/review documents and PR #4. Initial sandbox
GitHub access failed; escalated read-only retry succeeded. A guessed DES-001 path
was absent; used the actual DES-003 files. The first unpaginated review listing
omitted later reviews, so verified all pages before recording approval.
Rebase paused on docs/README.md; kept both sets of links and continued successfully.
Actual checks and failures are retained in the paired JSON: 19 dashboard, 15
logging/documentation and 11 envelope tests; 14 synthetic JavaScript assertions;
tracking/build validation; 170 local links over 24 pages; 27 session records;
whitespace and main-ancestry checks.
No browser layout, hosted CI, transport or performance checks are claimed.

## Changes and revision links

See paired inventory. No detector geometry, source parameters, formal approval
record or document lifecycle was changed. Git history locates this record's
resulting revision without a self-referential hash.

## Follow-up

An identified human should reconcile the existing baseline approval with formal
sign-off/lifecycle documentation under the normal workflow. Review the refreshed
local preview and browser/mobile rendering. Publication remains separate.
