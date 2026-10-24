## Executive summary

Summarize the purpose, main result, practical consequences, validation status and
next review decision. Keep this current as the PR evolves.

## Change

Describe the problem, resulting behavior and governing design/ADR/issue.
Use `<area>: <description>` with one of: `Magnet System`, `Tracker`,
`Calorimeter`, `Muon System`, `Global`, `Software`, `Documentation`, `Infrastructure`.
See [the naming rule](../AGENTS.md#pull-request-naming-and-conflict-resolution).
`Infrastructure:` replaces the old chore prefix and is excluded from progress
tracking; scientific/evidence work, documentation deliverables and new software capabilities need tracking.

## Dashboard and validation

- [ ] Project PR: updated `project/tracking.json` or `project/reviews.json` with the work, review or evidence change; or infrastructure PR: confirmed no maintenance entries were added to progress tracking.
- [ ] Ran relevant tests and `python3 tools/session_logging/session_log.py validate`; recorded actual results and limitations.
- [ ] Updated this PR's individual `interactions/pr-NNNN.json` with available inputs/responses, named parties, roles, tool provenance and canonical token-account references; refreshed it alongside token accounting and ran `python3 -B tools/interactions/ledger.py validate`.
- [ ] Preserved human approval boundaries and linked exact review/evidence revisions where applicable.
- [ ] Layout prototype change: updated the [layout main page](../docs/layouts/README.md), candidate features/status and decision/PR links, and regenerated its R–Z view when geometry changed; or recorded why it is unaffected. Reconcile final merge metadata immediately after merge; merge alone grants no design sign-off.
