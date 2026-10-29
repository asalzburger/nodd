# LAYOUT-002 — Tracker + inner 3 T solenoid + LAr ECAL + FCAL

**Alternative DRAFT / PROTOTYPE · updated 2026-10-29.** The tracker and conditional inner magnet are shared with 01. The LAr component envelopes remain pinned to their independent proposal; DES039 adds a common forward body and a short EM collar.

![LAYOUT-002 with common forward body and short EM collar](figures/LAYOUT-002-FCAL-rz.png)

| Component | Candidate features | Evidence / status |
| --- | --- | --- |
| Tracker | Gen3 mixed pixels and strips, 46,250 sensitive planes (balanced) | [DES025](../design/DES-025-tracker-dd4hep-gen3.md); [PR104 — selected baseline](https://github.com/asalzburger/nodd/pull/104) |
| Inner solenoid | 3 T central target; unchanged inner allocation | [PR64](https://github.com/asalzburger/nodd/pull/64); conditional |
| LAr ECAL | ALLEGRO-style inclined barrel and three-wheel turbine endcaps; package R301–2949 mm, abs(z)=4900–5860 mm | [Pinned DES032](https://github.com/asalzburger/nodd/blob/72d37ee9a56182e4ba974791a848a738c19cf092/docs/design/DES-032-allegro-lar-barrel.md), [pinned DES033](https://github.com/asalzburger/nodd/blob/72d37ee9a56182e4ba974791a848a738c19cf092/docs/design/DES-033-allegro-lar-endcaps.md); open PR73/74 |
| HCAL | Steel/scintillator context; endcap abs(z)=6360–7855.9 mm, minimum bore300 mm | Pinned DES033 envelope; detailed neighbouring HCAL not imported |
| Common FCAL | Tungsten/quartz fibres, R50–290 mm, abs(z)=4850–6650 mm; 1200 mm sampling | [DES039](../design/DES-039-common-forward-calorimeter.md); isolated prototype |
| EM collar | Same technology, R50–450 mm, abs(z)=4400–4840 mm; 100 mm sampling | [ADR010](../decisions/ADR-010-common-forward-calorimeter.md); bridges geometric EM handover |
| Forward services | Collar collector4840–4890 mm, new R298 mm neck; rear radial handoff7905.9–8055.9 mm to R4850 mm | Explicit draft additions; complete manifold/load/cooling qualification pending |
| Muon system / magnets | Absent | Future work |

The R50 mm bore is an explicit amendment of the former empty R80 mm allocation. The collider pipe is described only to absolute z4000 mm; machine protection, downstream pipe, shielding and beam heat remain unresolved. Collar service neck clearances are only 2 mm to HCAL and 3 mm to the cryostat; these are ideal geometric checks before engineering tolerances.

The native FCAL checks cover both ends, body/collar component solids and conservative neighbouring guards. This drawing combines pinned envelopes with the FCAL proposal; it does not establish complete LAr/FCAL construction, a magnetic field solution, optical response or calorimeter performance. Core and collar seams, transition depth and eta5 edge leakage require joint shower validation.

[FCAL design and results](../design/DES-039-common-forward-calorimeter.md) · [Named inputs](LAYOUT-002-FCAL.json) · [Vector drawing](figures/LAYOUT-002-FCAL-rz.svg) · [Independent original layout source](https://github.com/asalzburger/nodd/blob/72d37ee9a56182e4ba974791a848a738c19cf092/docs/layouts/LAYOUT-002.json) · [All layouts](README.md)

Reproduce with `python3 -B tools/forward_calorimeter/draw.py` in an environment with matplotlib. Full source revisions and hashes are retained in the named inputs.

The tracker overlay is extracted from the maintained balanced DD4hep export in [tracker-baseline-balanced.json](tracker-baseline-balanced.json). It updates only the tracker sensitive bounds; the independently pinned calorimeter and magnet contexts are unchanged. The earlier pre-FCAL layout remains a historical control.
