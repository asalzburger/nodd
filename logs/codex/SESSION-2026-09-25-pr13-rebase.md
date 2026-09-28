# SESSION-2026-09-25-pr13-rebase — PR13 conflict resolution and rebase

## Request, scope and starting revisions

User (exact): “PR#13 needs conflict resolving and rebasing, but is then ready to
be merged.” This explicitly permits the rebase and resulting lease-protected
branch update, overriding the repository's usual ordinary-merge preference for
this task. It permits integration of the draft study, not detector sign-off.

Original PR head: `f57e26e83b826867c2720edcd702e808fe946854`.
Main target: `58136c8adad0d10bb046bef3a574e181b7e1463c`.
Isolated worktree `/tmp/nodd-pr13-rebase`, branch `repair/pr13-rebase`.
Unrelated main-worktree token-gate/workflow edits and caches were left untouched.

## Conflict decisions and preserved evidence

Replayed eleven non-merge PR commits onto main. Three replay stops concerned
`project/tracking.json`: preserved tracker, Spack and publication task/evidence
records by stable ID; retained main's newer merged PR16 metadata and PR17 record;
kept the expert update's current A/C1 scope. An initial local helper assertion
failed; that unpushed attempt was aborted and restarted. Valid JSON, unique IDs
and exact preserved records were checked before subsequent continuation.

Immediately after rebase, the scientific documents, figures, numerical reports,
tracker source, source manifest and review register were byte-for-byte identical
to the old PR head. The subsequent user-directed naming update below changes
presentation only and leaves historical numerical artifacts intact. Main's logging/publication changes and every tracking ID remain present.
No historical evidence artifacts were regenerated and no review target was rewritten.
The old head was published as `archive/pr13-before-rebase-2026-09-25` so
historical review/source links remain reachable after the requested history rewrite.

The user has authorized merging the draft research. GitHub's historical
`noemina` CHANGES_REQUESTED review is preserved, as are unresolved scientific
questions. No expert approval or final design sign-off is inferred from the
user's repository-integration instruction.

## User-directed proposal names

During this task the user additionally requested (exact): “A -> cobe (classical
barrel encap), C1 -> pint (progressive inclined transition)”. The documented
expansion spells out “endcap”; the requested lower-case names are preserved.

Added the current cobe/pint catalogue, Markdown/PDF briefs and separate labelled
figures. The named catalogue records legacy candidate IDs and the exact source
hash; every physical layer and stable layer ID is identical to the retained
A/C1 catalogue. Historical A/C1 briefs, drawings, scans and reviews remain intact.
Updated active design narrative, tracking and plot presentation. Added two tests
for physical invariance/source immutability and rejection of unexpected options.
The existing optimisation still emits its historical keys; the documented naming
step publishes the new names without rerunning or reinterpreting that search.

The repository-pinned PyMuPDF 1.28.2 renderer was unavailable locally. Installed
it in `/tmp/nodd-pr13-pdf-venv`; the initial sandbox network attempt failed and
the permitted retry succeeded. Rendered both named briefs: exactly two A4 pages
each, and visually inspected all four pages. Generated the named figures from
retained numerical results using Matplotlib 3.11.0. No new physics scan.

## Token provenance

Imported twelve completed turns already curated and assigned in the two existing
usage inventories: six for first layouts, four for inclined review, one for C1/C2
and one for expert review. The exact entries retain source IDs and evidence.
Total newly imported historical usage is 36,548,583 input / 196,911 output tokens.
No raw private client state was inspected and no estimates were made. The source
inventories remain immutable snapshots; dated notes in each session record
explain the import and supersede old missing-usage wording for those turns.

Current rebase-turn counters are unavailable. The main-worktree instruction
requires every changed session to have measured accounting and explicitly says
pending/unavailable text is not an exemption. The current session remains empty;
the committed-branch accounting checker must be run before merging. Neither
historical imports nor successful hosted CI can waive that local requirement.

## Actual checks and limits

Passed after naming update: 29 tracker, 27 dashboard, 32 logging/recovery and 5 node-preflight unit
tests; 14 JavaScriptCore assertions; dashboard validation/build; session-log
validation (47 records); scientific-tree identity and all-main-record preservation.
Summary: 42/47 sessions with usage, 79 recorded turns, observed historical
input/output totals 134,594,309 / 674,111. These totals do not measure this rebase.

No DD4hep/Geant4/ACTS or IdRes runtime rerun: the scientific files are unchanged.
Existing prototype limits and historical artifact hashes remain applicable.
The first GitHub branch-protection query returned 404 (unprotected branch);
that does not waive repository instructions. Publication, final whitespace,
accounting and hosted-check outcomes are reported after execution.

## Files and follow-up

Paired JSON lists files edited by this integration task. The rebase itself also
retains all PR scientific commits and current main infrastructure. Published original-head archive and rebased PR head `69ea15b` using an
exact-head lease. PR title and description now use cobe/pint. GitHub reports
MERGEABLE/CLEAN, and hosted build run `36142049953` passed at that head.
The local required token gate failed (exit 1) only for this new rebase session.
Merge remains pending until its completed-turn accounting is available or the
human explicitly authorizes an exception. A merge does not advance DES-006 out of DRAFT/PROTOTYPE.
