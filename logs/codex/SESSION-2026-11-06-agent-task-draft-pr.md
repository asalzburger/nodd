# SESSION-2026-11-06-agent-task-draft-pr

## Scope and evidence

Implement the standing delivery rule and scheduled worker publication. Start:
`2ce4e9c81006a3779e89a3cedc3a45a7f1bf72d7`, clean dedicated branch
`codex/agent-task-draft-pr`. The original task #120 result and its publication
are recorded separately, including its [draft PR #121](https://github.com/asalzburger/nodd/pull/121).

## Selected conversation

User, exact: "Make it a rule that tasks always end in a draft PR 0 and make one now"

Assistant, paraphrase: will make a draft PR mandatory for completion and publish
#120 immediately, using separate focused infrastructure PRs. The user explicitly
authorizes task-result pushes and draft PR creation. Existing rules forbidding
publication by the scheduled runner are superseded for that bounded purpose;
there is no authorization to mark PRs ready, merge, change labels/permissions or
grant design sign-off.

## Decisions and outcomes

AGENTS.md now requires a draft PR for every completed repository task, including
reviewable investigation/blocked/no-code session records. The sandboxed agent
returns a structured PR title/body and local changes. The host publishes the
assigned branch, creates a draft, captures its individual interaction record and
checks that the open draft points to the final remote SHA. A zero model exit alone
cannot complete a task. Publication failures remain failed and retain any known
draft link. Existing drafts are reused on publication retries; a ready/closed PR
is not modified by the publisher. PR tasks target the source PR head branch and
stop when its captured head has changed.

The host validates title, branch/origin, curated records, staged paths and all
new Git blobs. New/staged files above 5 MiB and obvious credential paths require
manual review. Size manifests remain local; this is not a complete secret/content
scanner. Process groups are terminated on command timeout/interruption. No model
sandbox or approval setting was broadened. ADR-004 remains DRAFT; no scientific
tracking entry, detector parameter or sign-off changes.

## Live deployment

Under the existing queue lock, deployed `poll.py`, `publish.py` and the final
response schema to the stable `nodd-main` checkout. Preserved the user-edited
permission configuration byte-for-byte and the queue history; retained rollback
copies locally. The LaunchAgent program path and schedule were not changed or
bootstrapped again. Authenticated dry-run found task #118 eligible without
claiming it. The next scheduled pickup uses the deployed publisher. Task #120's
existing state/result now links to PR #121, and its original worktree is retained.
These are explicit local source overrides until this draft is merged; reconcile
against merged main without overwriting the independent permission config.

## Commands and validation

All 25 queue/publisher tests passed with no paid model calls. Integration tests
use real Git commits/pushes to a local bare remote and a fake GitHub CLI, including
lost-response/idempotence, individual interaction commit/push, PR-task source
branch, ready-PR protection and large blobs committed then removed. Existing
queue tests cover deduplication, actor allowlist, canceled requests, locks and
process cleanup. Curated sessions/interactions and token site are validated and
built before publication; staged files and new objects are inspected.

## Token accounting

Exact client per-turn counters and identifiers were unavailable. Usage stays
empty; this task's observed input/output sums are unknown, not zero. No usage
from other sessions is copied or allocated here. No raw client archive or hidden
reasoning was collected.

## Follow-up

Review and merge this infrastructure draft to retain the standing rule in main.
Inspect the next real scheduled task's draft PR; model work itself was not
re-executed during deployment. Any permission/publication error leaves a failed
attempt with local diagnostic information and any known PR URL.

An initial validation caught historical PR IDs auto-linking this independent
rule session into an old ledger. Narrowed structured related IDs to this bounded
task and reran validation, preserving historical records.
