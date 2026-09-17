## Change

Describe the problem, resulting behavior and governing design/ADR/issue.
For repository maintenance, use `chore: ...` or `chore(scope): ...` as the title.
Chore PRs are excluded from project progress tracking; scientific/evidence work
belongs in a project PR.

## Dashboard and validation

- [ ] Project PR: updated `project/tracking.json` or `project/reviews.json` with the work, review or evidence change; or chore PR: confirmed no chore entries were added to progress tracking.
- [ ] Ran relevant tests and `python3 tools/session_logging/session_log.py validate`; recorded actual results and limitations.
- [ ] Preserved human approval boundaries and linked exact review/evidence revisions where applicable.
