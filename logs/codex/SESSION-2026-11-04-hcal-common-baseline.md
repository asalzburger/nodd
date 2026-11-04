# SESSION-2026-11-04-hcal-common-baseline — HCAL common baseline design preparation

## Scope and evidence

Assignment `CAL114-CaloTech-update`, explicit CaloTech developer mandate through
generic child context. Main input `cd3ec20da56537617ac6fbbcf28bd6f28104cc64`;
original PR81 head `abd95bdc64b9d7971561d659bf953e71de4e7e99`. The assigned checkout was clean before integration.
The journal was created after the merge began and its initial-change capture
therefore described this assignment's changes, not unrelated user edits.

## Selected conversation

User request, paraphrase: update HCAL/FCAL PRs as baseline design options, add
task IDs and accounting, prepare merging within the two-ECAL campaign.
Coordinator assignment, paraphrase: preserve histories through ordinary merges,
keep main CI/tracker/FCAL content, retain common-module source and scope, prepare
regional siblings locally and leave remote publication/token recovery to root.

## Decisions and outcomes

Merged the original common-module history into current main; integration commit
`8e06de4ca9bc35b57c2597544d0e3eb3c760bef9`. Tracking and source records were merged by stable ID. The CI addition
merged without conflict and retains all current-main checks. Module source,
factory and retained validation bytes match original PR81.

The unchanged common module is the shared HCAL baseline design option; existing
regional studies describe SiW. LAr adaptation remains follow-up. No geometry,
material recipe, identifier, retained native result or formal lifecycle changed.

## Commands and validation

44 common-module/provenance controls,14 historical calorimeter controls, project
validation (90 tasks,45 documents,24 review rounds) and session validation
(237 records) passed on integrated source. The initial merge returned1 for
expected JSON conflicts; stable-ID reconciliation resolved them and validation
passed. Subsequent accounting/site checks are recorded in paired JSON.
No fresh native/DD4hep/Geant4 execution is claimed.

## Changes and revision links

See paired JSON inventory and [campaign report](../../docs/validation/DES-036/campaign-2026-11-04.md).
Original branch evidence and both parent histories are retained.

## Token accounting

Exact current-turn counters are unavailable while the campaign is active.
`usage` remains empty and does not denote zero. The coordinator handles
historical exact recovery and remote interaction refresh, with canonical
thread/turn deduplication. No counters are copied or allocated across PRs.

## Follow-up

Prepare sibling regions using this current common history; review LAr placement
adaptation, full assemblies, optical/shower/digitization response, operating
contracts and engineering qualification. Human sign-off remains pending.

## Completed bounded common-module preparation

All project/session/interactions/token validators and the token-site build pass.
Session validation initially rejected the expected merge exit1 incorrectly
labelled PASS; its entry was corrected to FAIL, preserving the conflict and
remedy, and all checks reran successfully. Project observed subtotal is
1,817,405,271 input +8,258,578 output across378 turns in151/237 sessions;
86 sessions have no usage observations. These are project totals, not PR81
cost or current campaign usage. No current counters were estimated.

## Campaign accounting reference

Completed HCAL specialist turns are owned once by `SESSION-2026-11-04-calorimeter-campaign`, shared with the other campaign PRs. The canonical inventory in PR116 and individual ledgers retain exact counters, parent edges and visible interactions. This per-PR narrative owns no additional copy. Root coordinator usage remains active and excluded.
