# SESSION-2026-09-28-acts-workflow-infrastructure-pr — Publish ACTS sister-checkout workflow as infrastructure PR

## Scope and evidence

New bounded infrastructure task at the user's request, 2026-09-28. Starting
nODD revision `0d90d75d6f998f732adaad2f0a49787b5cbc46fa`. The branch is
`infrastructure/acts-local-workflow`. The initial changes are the previously
requested AGENTS.md sister-checkout guidance and its paired session record;
they are intentionally included and preserved. No unrelated changes discarded.

## Selected conversation

User: “make an infrastructure PR out of this work, so that it is documented.”
Assistant scope: publish the local acts-nodd setup guidance and curated records,
linking the separate implementation and validation in nODD PR #14 / ACTS #6176.
The prior request authorized access to the explicit local sibling path and
recording its build/test/run instructions. This task adds no detector software.

## Decisions and outcomes

AGENTS.md records the authorized source checkout, actual local branch/revision,
setup helper, build/test/run commands, installed virtual environment and default
build/install directories. It explains the build/runtime helper's writes and
requires rechecking capabilities and preserving local changes. README links the
workflow. Follow-up links point to the exact posted review response and upstream
binding PR, with source HEAD, uncommitted patches and installed artifacts kept
distinct. Changed environment fingerprints and the observed Geant4 warning remain
explicit; this documentation does not promote a node capability or approval.

The earlier sister-checkout session pair is published unchanged. Its lack of
runtime verification describes that earlier read-only task; later runtime
results belong to PR #14, not this infrastructure PR. The expert reply and
upstream draft were already published, and the human subsequently marked the
upstream PR ready for review. No approval is inferred.

This Infrastructure PR is excluded from project progress tracking, as required
by AGENTS.md. No work item, review, milestone increment or PR entry is added to
project/tracking.json or project/reviews.json. Governing workflow: ADR-004;
no design/ADR/issue lifecycle or scientific source-catalogue change.

## Commands and validation

Create the infrastructure branch while retaining the existing changes; create
this session pair; read repository PR naming/update rules; validate logs and
dashboard, test session/document links and PR update policy, and build the
static dashboard. Actual results are recorded in the paired JSON at completion.
No ACTS build, simulation or geometry tests are rerun for this publication task.

## Changes and revision links

AGENTS.md, README.md, the earlier SESSION-2026-09-28-acts-sister-checkout pair,
and this session pair. PR link and published revisions are appended when known.

## Token accounting

No exact per-turn token counters or stable client thread/turn identifiers are
available. Usage remains empty; this session's observed input/output totals are
unknown, not zero. No historical usage observations are duplicated.

## Follow-up

Human review/merge of the infrastructure PR. Rerun runtime preflight before
future dependent tasks and retain exact source/patch/artifact provenance.
