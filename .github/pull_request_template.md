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
- [ ] Preserved human approval boundaries and linked exact review/evidence revisions where applicable.
