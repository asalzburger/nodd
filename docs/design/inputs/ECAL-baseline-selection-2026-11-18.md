# Restored LAr EM working-baseline selection

2026-11-18. **Human-selected working simulation baseline.** Engineering sign-off
and full-detector acceptance remain open; DES-032/033 retain their lifecycle states.

The user explicitly directed “the new LAr design becomes baseline for the EM
calorimeter”, together with stacking the recent drafts and token accounting.
This selects PR148's restored variant, rather than its earlier dense 2.6 mm Pb
control. Selection authority is the project user in the recorded session; no
identified engineering reviewer or formal sign-off is supplied by that request.

**NODD DESIGN CHOICE — user selected:** retain 1.8 mm barrel Pb, 1248 periods at
50.18°, and the 11 normalized radial compartment fractions while allowing the
thicker annulus. Materials, local services, readout and the 650 mm turbine-endcap
sampling depth remain those of the validated restored model.

| Interface / parameter | Selected value | Evidence / scope |
| --- | --- | --- |
| Solenoid assembly reservation + interface | 1640 + 60 mm | DES-026, conditional magnet |
| Barrel warm bore | 1700 mm | Restored native model |
| Front warm wall / vacuum / cold wall / bath | 10 / 49 / 3.8 / 10 mm | Retained simulation budgets; no vessel certification |
| Barrel sampling radii | 1772.8–2350 mm | Restored native model |
| Barrel warm outer radius / warm half-length | 2641.7 / 4100 mm | Restored native model |
| Rear bath | 210 mm | Three cold-board banks and utility reservation |
| Endcap warm package | R=301–2949 mm, abs(z)=5100–6260 mm | Restored native model |
| Endcap sampling | abs(z)=5210–5860 mm | 650 mm depth; retained wheel radii/49° inclination |
| Front / rear axial service reservation | 1000 / 500 mm | Restored service configuration |
| HCAL barrel front / half-length | 3130 / 6260 mm | Envelope context, absent from tracker+ECAL compact |
| HCAL endcap front / back | abs(z)=6760–8255.9 mm | Retained 1495.9 mm depth; context only |

**INFERENCE:** barrel warm outer surface to HCAL front spans 488.3 mm. This
contains service allocations; it is not certified free clearance. The retained
endcap governs the external 3029 mm service route. Pressure, ports, supports,
thermal performance, high-rate operation and engineering tolerances remain open.

## Evidence and maintained selection

The geometry was frozen at `53797385c374118838b2ade1ec3362328683cf75`; the
updated sector drawing also checked source-byte identity at
`8f7a7c8bd86f4d9c67c11b37d91aea76790feee4`.
[Restored controls](../../validation/lar-restored/README.md) retain native
zero-overlap checks, a finite material scan with 26.800197 X0 minimum over its
specified fully traversed directions, and the matched 10k-electron sample with
12 workers. This establishes neither all-angle nor multi-TeV containment.
The restored barrel partly recovers the dense compact control's degradation;
its held-out calibrated core is still broader than the original larger LAr
reference. Raw distributions, all-event statistics and calibration conditions
remain in that report. Baseline selection does not assert precision equivalence.

`detector/config/ecal-baseline.json` records the selection. Running
`tools/calorimeter_baselines/export.py` without `--layout` now composes the
maintained tracker with this explicitly selected restored barrel/endcaps and
local services. Explicit `--layout LAYOUT-002` selects the same model;
`--layout LAYOUT-001` retains Si–W for comparison. Standalone historical LAr
exporters and the dense prototype specification remain reproducible controls.
The integrated compact contains tracker+ECAL only; no solenoid field, HCAL or
FCAL is constructed. A new integration receipt records its own artifact hashes.

The retained calibration models keep their original ECAL-only compact/material/
sample identity guards. **They are not automatically applied to tracker+ECAL:**
added upstream material and new artifact identity require matched validation
before claiming its calibrated resolution, especially with an installed field.

Current R–Z input and drawing use the restored envelopes. The old DES039 FCAL/
collar result remains historical: its 7905.9–8055.9 mm rear handoff precedes the
new HCAL back at 8255.9 mm. Joint FCAL routing must be reassessed; old clearance
results are not transferred. HCAL/magnet/FCAL construction and engineering remain
separate from the current tracker+ECAL stage.

## Stack and approval boundary

Draft merge order: **147 → 148 → 149 → baseline selection**. Ordinary merges
preserve studies, figures, session pairs and sole token owners. Individual PR
interaction records reference canonical accounts; completed turns are counted
once and missing/active observations remain unknown. No merge or agent check
promotes a design record to SIGNED OFF or ACCEPTED.
