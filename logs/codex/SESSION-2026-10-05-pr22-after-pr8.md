# SESSION-2026-10-05-pr22-after-pr8 — Synchronize PR #22 after PR #8

## Scope and request

User (exact): “ok #21 and #22 need rebasing again.”
This record covers PR #22; its companion covers the other branch.
Starting revision: `c0bd87165229c22f8e991ff9464d54b37783681e`; clean isolated worktree.
Main advanced to `5290b265a5cc158198da1f40ad506028d8a0ebc5` after PR #8
merged. The user's main checkout and unrelated untracked files were preserved.

## Resolution

Used the repository's ordinary-merge workflow (`git merge --no-commit --no-ff
origin/main`) to update the existing shared branch without rewriting history.
The expected conflict exit identified `project/tracking.json` and
`reference/manifest.yaml`. Combined records by stable ID and three-way comparison.
The sole remaining scalar conflict was the ATLAS strip TDR verification account:
retained the dated 2026-09-15, 2026-09-25 and 2026-09-29 inspections, without
repeating the common September 29 paragraph. This adds no new source lookup.
Preserved source facts, prior logs, token observations and exact review records.
Updated the strip task evidence and PR #8's observed merge metadata; its merge
is not a design sign-off. DES-008, design parameters and study artifacts remain
unchanged. Manual changes are inventoried in the paired JSON; other merge files
are unchanged main imports. Git history identifies the enclosing merge commit.

## Validation and commands

Fetched origin; inspected branch status, root instructions, PROJECT.md,
DES-008, issue #20 and merged PR #8 metadata. Executed the branch strip tests,
dashboard and session-logging tests, dashboard build, structural validators,
source/review/log preservation audit and whitespace check. Exact outcomes are
recorded in the paired JSON after completion. No artifacts were regenerated.

## Usage and follow-up

Exact client per-turn counters are unavailable, so no usage was imported or
estimated. Historical journal summaries overlap between branches and are not
new-task usage. Push the ordinary merge commit and verify GitHub mergeability;
CI provides the JavaScript check unavailable locally. Human design-review and
sign-off requirements remain unchanged.
