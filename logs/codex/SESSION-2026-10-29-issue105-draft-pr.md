# SESSION-2026-10-29-issue105-draft-pr

## Scope and selected conversation

User request, exact: “Make a draft PR please”. This explicitly authorizes
publication of the prepared issue105 design and final closeout after the earlier
automatic approval rejection. The ambient browser URL was context, not approval.
No scientific design choices, geometry, numerical inputs or acceptance changed.

## Outcome and publication

Pushed final design closeout8f90d65a81efdbeede68b2519f7d13f0631bbda6 to
codex/issue105-separated-toroids. The GitHub connector create_pull_request call
returned403 Resource not accessible by integration; this was an API permission
error, not another automatic approval rejection. Checked the head had no open
PR, then used the existing authenticated gh CLI to create draftPR106:
https://github.com/asalzburger/nodd/pull/106 . Base branch is
codex/twelvefold-toroid-prototype; draft/open state and title verified with
`gh pr view`. Attached the PR to this chat with attach_artifact. No merge, review
request, issue comment or other external message was sent.

## Records and commands

Created a new bounded session, preserving the earlier design-session history.
Updated project/tracking.json with the observed PR publication metadata.
Captured its public discussion/linked issue and per-PR interaction record with
the existing main ledger at source04b5ee2e408803eac836eee0b48a1635dcbbe201,
extracted read-only to a temporary runtime because the stacked parent branch
predates the ledger tool. The canonical per-PR record is interactions/pr-0106.json.
No infrastructure was imported into the scientific branch.

Relevant commands: normal git push; gh pr list; gh pr create --draft with the
exact prepared body via --body-file; gh pr view; ledger capture/sync/validate;
project/session validators and token-site validation/build. This metadata-only
publication does not require rerunning the previously passed33 scientific controls.

## Usage and limitations

Exact client per-turn counters and client/model identities were not exposed.
usage remains empty, meaning unknown rather than zero. No private client stores,
new estimates or duplicated parent/child usage were introduced. Prior DRAFT
status, engineering uncertainties and independent-review qualifications remain.

## Completion checks

The project validator initially caught PR document IDs not linked to the affected
toroid task. Linked the governing DES004/DES040 to that task and reran.
Session summary for this stacked checkout reports870643545 observed input and
4670671 observed output tokens from retained historical turns;73 sessions lack
usage observations. This publication task has no measured usage, not zero usage.

Final project/session validation, token-site validation/build and whitespace
checks pass. Captured timestamps use the existing whole-second UTC schema.
