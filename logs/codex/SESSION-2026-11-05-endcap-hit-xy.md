# SESSION-2026-11-05-endcap-hit-xy — ECAL sensitive-hit x–y view

## Scope and selected request

User, exact request: “Can you make a 2d (x/y) projection view of the sensitive hits in the Endcap to see the readout module segmentation?”
Context selects the Si–W ECAL endcap used in PR118. Started at
e4d478b34c6392130d4de21383d87eb55245b13c with a clean working tree.
The user-directed Marlin deferral stays active. This task reads saved raw
Geant4/EDM4hep hits; it runs no new transport or digitization.

## Outcome and provenance

Created a full +z endcap projection across48 sensitive layers and a layer14
zoom that exposes the5.1mm local virtual readout grid and the gap/orientation
change between modules13/14. Grey outlines are source-derived silicon wedges,
not fabricated hit coverage. ODD has continuous sensitive wedges with virtual
cells rather than individual wafer tiling. Fixed-phi illumination and unhit
regions are labelled explicitly.

Input: saved50GeV electron, eta2, phi0.123,200 events. Selected309693 +z
SimHit entries; excluded30 opposite-endcap entries. Layer14 has12924 entries;
656 cell bins including edge padding are retained for the zoom. Source
ODD pin d70556f33b1c36abdf101a07ad8cf57eb56fbdf1 and exact geometry/input/script
hashes are in the compact JSON. No event-level payload is committed.

The four-bit stored module field uses0 for source factory module16. The
source-derived cell centres match all selected native positions with maximum
residuals0.000061/0.000057/0.000098mm in x/y/z, within the predeclared bound
4*float32epsilon*max(1mm,absolute expected coordinate). Repeated cell IDs in an
event, bad input hashes, unexpected identities and count mismatches fail.

## Commands and actual checks

- acts-spack preflight returned2: registry setup/lockfile fingerprints changed.
  Warned the user before dependent work. Active ROOT6.40.04/podio imported and
  the actual saved-file reads succeeded; no shared software was installed.
- endcap_xy.py extract:200events,309693 selected entries; native-position,
  identity, histogram and per-cell occupancy checks passed.
- Matplotlib-only render and visual QA: fixed initial clipping outside the
  axes and caption spacing, then inspected the final two-panel figure.
- Re-extracted after final helper edits so the committed script hash matches
  the data provenance. Replot needs only the committed JSON and Matplotlib.
- Reference/source catalogue, project tracking and report were updated for
  inspection evidence, without design sign-off or performance acceptance.

## Publication and token accounting

Add the figure to the existing PR with immutable image/data links. Preserve
both earlier previews. Public URL/read-back and final ledger/journal/project
checks are recorded in the paired JSON. No exact disjoint client-reported token
counters were exposed; input/output totals remain unknown, usage empty.
No private client archives or hidden reasoning were accessed.

Published asset commit: `ce609eb6cedf459594134d12994db01882f219fe`. The raw
public image returned the exact local PNG bytes, SHA-256
`a0d17e52ac584514c74a6654cd2356b95a138c6804d820b8061bfe4276860040`.
PR118 read-back contains all three figure embeds and remains draft.

Final checks passed:256 paired session records, PR118 ledger, project records,
token-site build and whitespace. Task input/output totals remain unknown;
no exact client counters were exposed.

## 2026-11-10 token recovery and work label

Supersedes the earlier unavailable-counter note for the recovered closed turns only. Exact app-visible requests/results, verified parent/child role metadata and this journal's bounded assignments identify 1 previously unowned observations. Imported with session_log.py after a successful dry run; replay adds zero. Observed input 8,796,311 + output 44,192 = 8,840,503; cached input/reasoning are subsets, not additions. See [the scoped inventory](../usage/USAGE-2026-11-10-pr118-prototype.json) and [readiness/accounting record](SESSION-2026-11-10-pr118-merge-readiness.md). This existing session title labels the work in the cumulative usage view. Original task outcomes, gates and source versions remain unchanged; model/client version and excluded active/other-device usage stay unknown.
