# SESSION-2026-09-22-pixel-branch-reconciliation

## Scope and authorization

User requested the new PR prefixes, application to open PRs and conflict
resolution, preserving both changes by default for logging. This bounded
subrecord covers only PR #8 reconciliation; the naming policy and other PR title
changes are recorded in SESSION-2026-09-22-pr-naming. Tokens are unobserved.

An isolated checkout started at d237f146b578915cc032b30efa50044cf6344d5f and
merged main 8472892bee490a7e04e58bab7d1332493cb615b9 without rewriting history.
The session scaffold was created after merge inspection; its initial changes
are those produced by this authorized merge, not unrelated user work.

## Resolution

Conflicts were in docs/README.md, project/tracking.json and project/reviews.json.
Both documentation links and independent task/document/evidence/PR/review entries
were retained. JSON records were reconciled by stable ID/path with a three-way
comparison; unchanged/base values yield to the edited side, identical edits stay
single, and ambiguous scalar changes would stop. None required a scientific
choice. Catalogue and session logs merged automatically. The curated tracking
date and PR #8 title were updated to Tracker: Propose reusable RD53i modules with
component material accounts. No review target, design content or approval changed.

## Validation and follow-up

Actual checks are recorded in the paired JSON. Preserve this merge on the
existing draft PR branch; no main merge or design sign-off is authorized here.
