# SESSION-2026-10-14-siw-service-envelopes - LAYOUT-001 envelope parity

## Scope and selected request

Contemporaneous task starting from clean main e33ae62ce16592c26c581c5311c4dc493d9714b1
in a dedicated worktree, branch codex/layout001-service-envelopes.

User request (verbatim):

> This needs one more adaptation: layout-1 does not yet have the same level of envelope prototyping: service and cooling space for Si-W EM such as the routing through the HCAL is not defined, similar eventual FCAL envelopes are missing.
> Bring them en par with an additional PR, then update the overview document (and PR) you are currently drafting.

The additional prototype PR is independent of open Si-W PR70/71. It will pin
those sources, define service/forward reservations and amend the HCAL outline;
no unreviewed detector production integration or new external package. Existing
PR75 will retain identical common-source Markdown/PR-description/four-page PDF.
All PR70/71/73/74/75 remain open at inspected heads on 2026-10-14; main is e33ae62.

## Decisions and handoffs

Design/evidence stub precedes envelope implementation. Native source parameter
facts, inference and new choices remain separate. The SysArch assignment will
address cross-system interfaces; a separate PhysVal context will assess a frozen
implemented allocation before publication. Root owns implementation, documents,
records and PR75 synchronization. Generic role prompts are explicit assignments,
not native profile loading or human sign-off.

## Commands and checks

Initial upstream metadata and source inspection only; checks and results will be
curated as executed.

## Token accounting

Exact current parent/child completed-turn counters are unavailable. Usage remains
unknown; do not estimate or duplicate previous task observations.
