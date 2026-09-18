# SESSION-2026-09-18-tracker-reviewers — Address the tracker plan reviewer-coverage comment

## Scope and evidence

Contemporaneous record of addressing the reviewer-coverage comment on PR #11.
Starting revision: `8c76dc4cea9e0005453fb86c2e2e8cd042bf64bf`, branch
`design/tracker-system-plan`; the working tree was clean and the remote branch
matched. Related records: DES-005 and TASK-B-TRACKER-PLAN.

The source is the public [reviewer comment](https://github.com/asalzburger/nodd/pull/11#issuecomment-5729274384),
created on 2026-09-18. Professional reviewer identities belong in the plan and
tracking records. Exact token usage, client version, thread ID and actual
conversation start time are unavailable.

## Selected conversation

- User request (exact quote): “There's a comment to pick upon”.
- Review comment (paraphrase): the plan makes sense; named people can cover
  general tracker layout, parametric performance, hits/track and material-budget
  estimates, with a separately named reviewer for DD4hep–ACTS interplay. One
  invitation is stated as sent; participation acceptance is not recorded.
- Assistant outcome: added a sourced reviewer map, routed the stated topics to
  the existing packages and updated specialist-header references and PR metadata.

## Decisions and outcomes

Recorded the nominations within their stated expertise. The plan distinguishes
invitation sent from confirmed participation and completed review; it does not
invent GitHub identities for names supplied without handles. Other component,
engineering, reconstruction and timing expertise remains open.

The existing final sign-off authority is unchanged. General support for the plan
is not recorded as formal sign-off. DES-005 remains DRAFT; review outcome remains
pending. The old exact-revision request is retained as withdrawn and superseded
by a request for the revised plan. No additional invitations, review-request
notifications or comment replies are sent in this task.

## Commands and validation

Read PR #11 comments/reviews and inline comments with `gh pr view` and `gh api`.
One conversation comment was present; GitHub reviews and inline comments were
empty. Read repository instructions, project review policy, DES-005, specialist
inputs and task/review records; fetched origin and verified branch identity.
Created this paired record using the session-logging tool. Validation and
publication results are recorded in the paired JSON after execution.

## Changes and revision links

Changed DES-005 and the TrackTech/PhysVal/SoftEng header pointers, task/review
metadata and this paired record. The SysArch technical input and scientific
parameters are unchanged. The comment is linked as project decision provenance;
no external technical source catalogue entry changes.

See the paired JSON for exact paths and commits. PR #11 remains the review venue.

## Follow-up

Confirm participation, assign uncovered specialist topics, and obtain explicit
human plan sign-off against the current target. No approval, merge or detector
implementation is performed here. Final hosted checks are reported to the user.

## Completion evidence

Published plan revision `9f984e85e35c109aef3560493cf67388de06b728` and updated
the PR description to that exact review target. Follow-up metadata preserves the
prior request and records the revised pending request; the plan bytes match the
target. Fifteen logging/documentation tests and three targeted review-history
tests passed. Final dashboard validation (27 tasks, 8 documents, 5 review rounds),
dashboard build, session validation (34 records) and whitespace checks passed.
The publication metadata commit follows the plan commit and is not self-recorded.
Hosted checks on the final pushed head are checked separately and reported to the user.
