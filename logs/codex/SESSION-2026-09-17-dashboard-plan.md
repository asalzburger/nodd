# SESSION-2026-09-17-dashboard-plan — Project dashboard proposal

## Scope and evidence

Contemporaneous, curated documentation task on main, starting at
fb7aef1af7e8a3835775f40271e2b26ae37804bf with a clean working tree.
Exact usage, client version and thread identifiers are unavailable.

## Selected conversation

User request (paraphrase): plan a dashboard, potentially hosted on GitHub Pages,
covering the project plan, staged and parallel projects, and open/closed reviews.
Assistant outcome: proposed a static Git-backed dashboard with separate work,
document lifecycle and revision-specific review states.

## Decisions and outcomes

Created PLAN-NODD-DASHBOARD-001 as DRAFT and linked it from the documentation index.
Specified views, ownership of canonical data, review history, update workflow,
incremental delivery, validation and optional publication. Stage A closure for
progression and stage B authorization remain intact. Human approval is never
inferred from work completion, PR merge or issue closure.
Official GitHub Pages hosting/workflow documentation was consulted on 2026-09-17;
links are retained in the proposal. No detector sources or parameters changed.

## Commands and validation

Read AGENTS.md, PROJECT.md, PLAN-NODD-001, ADR-002/003/004 and design/sign-off/logging
templates; inspected branch, HEAD and working tree. Created the session pair with
`python3 tools/session_logging/session_log.py new --id SESSION-2026-09-17-dashboard-plan --title 'Plan project tracking and review dashboard'`.
Final checks and results are recorded in the paired JSON. No dashboard or detector
checks apply to this documentation-only task.

## Changes and revision links

Changed docs/DASHBOARD_PLAN.md, docs/README.md and this session pair.
No commit, issue or deployment created. Existing ADRs remain drafts.

## Follow-up

Review the proposal, assign tracking ownership and implement the tracking contract
and local MVP. Choose hosting and authorize publication after a working build is
available. No human sign-off was granted or recorded.

## Token-accounting correction — 2026-09-25

Recovered one completed client turn from the second device using verified
cumulative-to-request counters and persisted turn boundaries. The user-visible
request and session-ID tool references match this task. Exact counters and
evidence hash are in the paired JSON and the
[second-device inventory](../usage/USAGE-2026-09-25-device.json).
No thread/turn IDs overlap PR #18’s recovery. Original narrative and limitations
are retained as historical statements; model identity remains unknown.
