# SESSION-2026-09-25-short-strip-cell-choice — Agreed baseline and fallback

## Scope and selected conversation

Follow-up to DES-007 / draft PR #21 and issue #20. Starting branch:
`research/short-strip-modules`; revision `41bbac5` (full hash in paired JSON).
Worktree `/tmp/nodd-short-strip` was clean. Unrelated main-worktree changes remain
untouched. Collection is contemporaneous; exact client usage is unavailable.

The assistant recommended (exact): “keep 0.5 mm as the research baseline and
study 1.5 mm as the fallback” until electronics feasibility is clearer.
The user replied (exact): “Agreed.”

## Outcome and scope of agreement

DES-007 C01 now records 75 µm × 0.5 mm as the agreed research baseline and
75 µm × 1.5 mm as the fallback. The research cell-length question is resolved.
The 1.0 mm point and sourced CMS cell remain comparison cases. Electronics
feasibility, module-family choice, services and formal design sign-off stay
open. A fallback switch requires an explicit decision; the user did not approve
hardware, authorize integration, or promote the design lifecycle status.

Updated the design, comparison narrative and TRK-SSTRIP dashboard record.
Updated the descriptions of PR #21 and issue #20 with the same agreement. Numerical inputs, scripts and
retained results are unchanged; no scientific scan was rerun for this wording
and research-direction update. Older session records preserve the historical
open question; this new record supersedes that preference status.

## Validation and commands

`gh pr view 21` verified remote/local heads matched before editing; `gh issue
view 20` retrieved its current description. Dashboard validate/build and
`git diff --check` passed. Session-log validation and summary are recorded in
the paired JSON after execution. The existing PR accounting requirement still
needs exact completed-turn counters; unavailable text is not an exemption.

## Token accounting and follow-up

Usage is empty and unknown, not zero. No raw private client state was collected
and no historical turn was assigned to this task. Proceed with electronics
feasibility against the agreed baseline and fallback; no further preference
confirmation is needed. Import exact completed-turn evidence before merge.
