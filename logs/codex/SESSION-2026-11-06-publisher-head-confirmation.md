# SESSION-2026-11-06-publisher-head-confirmation

## Scope and evidence

Start at merged main `4497737721d35df1e8971d5d01e8a5727def14aa` on the
independent `codex/publisher-head-confirmation` branch. This fixes final draft
head confirmation during the task124 publication recovery; original worker and
recovery sessions remain their own canonical records.

## Selected conversation

User asked whether another worker picked up work in the last hour. Assistant
confirmed issue124 at 16:07 Europe/Zurich and found its prepared output was local.
Under the user's existing instruction that every task ends in a draft PR, the
assistant restored the deployed merged publisher and recovered publication.

## Decisions and outcomes

The inactive stable checkout was still before the publisher merge. Recovery
advanced it to merged main while preserving configuration and queue history.
Publishing issue124 created [draft PR125](https://github.com/asalzburger/nodd/pull/125)
and pushed its interaction record, but immediate final verification failed.
A subsequent PR and branch-ref API read both matched local revision
`c4b8107fae7d60d55ce28a5cdd51612934684323`. The original generic error did not
retain the mismatched response field, so a short head-propagation delay is the
supported hypothesis, not a reconstructed fact.

Head confirmation now allows five reads with 0.5/1/2/4-second backoff. The exact
published SHA must still match, and a wrong branch or closed/ready PR still fails
immediately. Persistent SHA mismatch fails after the bound and reports expected
and observed revisions. No acceptance requirement, title policy, artifact guard
or model sandbox is weakened. Updated the operations guide and deployed the
tested publisher module under the existing queue lock; retained rollback source.

## Commands and validation

All 27 queue/publisher tests pass, using a real local bare Git remote and fake
GitHub CLI. New cases simulate a stale head after the final interaction push and
a head that never converges; the latter still fails without a completed result.
Session/interaction validation, token-site build and staged/new-object checks
accompany draft publication. No paid model call or native runtime was invoked.

## Token accounting

Exact per-turn client counters and identifiers are unavailable. Usage remains
empty; this fix has unknown observed input/output, not zero. No original worker
or recovery usage is copied or allocated to this session.

## Follow-up

Review and merge the infrastructure fix, then reconcile the identical local
publisher override against merged main. The queue still runs hourly and never
marks PRs ready or merges them. The software-inventory draft retains its separate
historical-project-object blocker for full make check.

## Published drafts

Recovered task124 publication in [draft PR125](https://github.com/asalzburger/nodd/pull/125),
with final verification passing and its link in state/result. This fix is
[draft PR126](https://github.com/asalzburger/nodd/pull/126). No duplicate task
PR or new model execution was required.
