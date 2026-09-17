# DES-003 input — Muon envelopes and magnet interfaces

> First-round input retained for traceability. The [2026-09-17 review update](DES-003-muon-review-1.md) supersedes conflicting recommendations.

- Status: DRAFT; subsystem advice for the global architecture proposal.
- Date: 2026-09-16.
- Role: Muon subsystem technician.
- Human approval: pending; no production geometry or response change authorized here.
- Scope: envelopes, interfaces and alternatives; no chamber design or claimed efficiency.

## Recommendation

**NODD DESIGN CHOICE — proposed, approving humans pending:** retain the ODD-sized barrel and endcap reservations below for the first global comparison. Their justification is continuity and space for technology alternatives, not a demonstrated optimum. Initially describe the function as **muon identification and tracker-matched trajectory measurement**. A standalone momentum spectrometer remains an explicit alternative requiring a physically credible external field and its magnet/material allocation. Do not turn ODD's nominal outer-field parameter into an assumed field throughout these stations.

## What the inspected ODD actually allocates

**FACT:** SRC-ODD-UPSTREAM, study revision `c167363f3d4ad1540a577af99071283caf54f3a6`, defines the following air parent volumes. Locators: `xml/OpenDataDetectorEnvelopes.xml`, constants `ms_b_*` and `ms_e_*`; `xml/detectors/MuonSystem.xml`, detector dimensions and layer elements; `factory/muons/ODDMuonBarrel_geo.cpp:35,178` and `ODDMuonEndCap_geo.cpp:34,51–53,148–150`. The factories pass `dz` directly as the Tube half-length and then translate by the detector `z`. These are neither full lengths nor bounds of sensitive gas.

| Reservation | Radial interval (m) | Global axial interval (m) |
| --- | --- | --- |
| Barrel parent | 3.536–6.762 | −7.200 to +7.200 |
| Positive endcap parent | 0.54073–7.000 | +7.200 to +10.270 |
| Negative endcap parent | 0.54073–7.000 | −10.270 to −7.200 |

**INFERENCE — exact arithmetic from the source dimensions:** endcap edges are `8.735 ± 1.535 m`. The barrel and endcap parent faces therefore meet at `|z| = 7.200 m`; there is no reserved axial clearance at that plane. This observation is not a constructed-geometry overlap result.

**FACT:** the barrel has three named layer allocations, bounded radially by 3.536/4.607/5.680/6.762 m. Its factory places chamber boxes directly inside the barrel parent; these radial intervals are not uniformly sensitive shells. Each endcap has four layer volumes of half-thickness 0.380 m. The first pair uses radii 0.54073–5.000 m; the second pair uses 0.946–7.000 m.

**INFERENCE — translation arithmetic:** the endcap layer centres are at `|z| = 7.580, 8.350, 9.120, 9.890 m`. Use those as inherited station locations for a comparison sketch, with their provenance visible. Do not infer active coverage from the much larger parent annulus. The chambers are segmented, and barrel/endcap transitions need explicit station-crossing tests.

**NODD DESIGN CHOICE — proposed, approving humans pending:** the reservation table and inherited station locations are the initial envelope hypothesis. Its alternatives are a more compact tracker-assisted identification system or expanded spacing/magnet allocations for independent spectrometry. The global architect may adjust these boundaries following calorimeter depth, service and magnet studies; the ODD dimensions are not requirements.

## Experimental evidence and its limits

The cited PDFs are already registered in the [source catalogue](../../../reference/manifest.yaml). PDF pages below are one-based. The 2008 papers describe historical designs; the upgrade TDRs describe their dated proposals, not the current installed state.

- **FACT — SRC-ATLAS-JINST-2008, §6.1, printed p.164/PDF194; Figs.6.1–6.2/PDF195:** ATLAS uses approximately 5, 7.5 and 10 m barrel station radii and endcap locations around 7.4, 10.8, 14 and 21.5 m. Precision measurement extends to `|η| < 2.7`. Chambers are arranged around barrel/endcap toroids. The paper explicitly describes service gaps. [ATLAS detector paper](https://doi.org/10.1088/1748-0221/3/08/S08003)
- **FACT — SRC-CMS-JINST-2008, Chapter7, printed pp.162–165/PDF189–192:** CMS uses four barrel stations and four endcap stations interspersed with flux-return steel. DT coverage is `|η| < 1.2`; CSC coverage reaches `|η| = 2.4`. §7.1.1 relates station allocation directly to yoke geometry and discusses unavoidable support gaps. [CMS detector paper](https://doi.org/10.1088/1748-0221/3/08/S08004)
- **FACT — SRC-CMS-TDR-016, §1.5.3, printed/PDF p.39:** the Phase-2 proposal places ME0 behind HGCAL to extend identification to `|η| = 2.8`; this is a dedicated forward assembly, not simply a wider claim for the existing four stations. Local PDF1 verifies title *The Phase-2 Upgrade of the CMS Muon Detectors*, CMS Collaboration, CERN-LHCC-2017-012, dated 2017-09-12 (outer cover also dated 2018-10-22).
- **FACT — SRC-ATLAS-TDR-026, §1.4.4, printed p.11/PDF31:** the proposed high-η tagger covers `2.7 < |η| < 4.0`, relies on ITk momentum, and occupies a region without significant magnetic field. The text explicitly defers approval to a later dedicated TDR. PDF3 verifies title *Technical Design Report for the Phase-II Upgrade of the ATLAS Muon Spectrometer*, ATLAS Collaboration, CERN-LHCC-2017-017, created/modified 2017-12-15; PDF1 cover is dated 2018-07-17. This provides precedent for separating identification coverage from spectrometer coverage, not authorization to copy this proposal.

**INFERENCE:** three or four stations alone do not confer ATLAS/CMS momentum performance. Lever arm, field integral, alignment, multiple scattering and station resolution enter together. ODD's shorter outer lever arm cannot inherit ATLAS's standalone performance goals. HL-LHC relevance also requires forward-background and rate assumptions; dimensions alone do not supply them.

## Architecture alternatives

| Alternative | Envelope implication | Required evidence |
| --- | --- | --- |
| Inner solenoid plus tracker-assisted muon identification | Start with inherited reservations; reserve shielding/support/service space explicitly | Transport from tracker through calorimeters; station matching; punch-through and background rejection; actual fringe field |
| Solenoid with instrumented iron return | Allocate yoke plates and chamber gaps jointly; retain or revise outer boundary after flux/material accounting | Magnetic return concept, mapped field including saturation assumptions, scattering and penetration studies |
| External air-core spectrometer | Reserve toroid coils, cryostats, supports and service sectors; inherited free space is not proof of fit | Field integral and bending orientation, coil/support material, station placement and lever arm |

All three are proposed design alternatives without human approval. No numeric external field or yoke thickness is selected. A zero-external-field calculation may be an explicitly labelled diagnostic control, not a physical assertion about solenoid fringe fields.

## Interfaces and follow-up questions

1. **System architect:** is independent momentum measurement a requirement, or is tracker-assisted identification sufficient? Resolve this before promising a spectrometer.
2. **Calorimeter/muon interface:** establish the absorber depth and leakage reaching each station versus angle. Extra steel cannot be added merely to suppress punch-through plots.
3. **Magnet interface:** assign coil/cryostat/return/shielding volumes to one owner; require identical field definitions in transport and reconstruction. Include forward return paths.
4. **Services:** reserve gas, power, data and cooling routes plus electronics footprints and support attachments. Distinguish shared corridors from station-owned material; avoid double counting.
5. **Coverage:** choose separate goals for identification, tracker-matched momentum and independent spectrometry. Scan barrel/endcap transitions, forward apertures, service sectors and minimum station multiplicity. Compare optional forward tagging with its tracker and shielding dependencies.
6. **Software/physics:** start with geometric station intersections and path lengths, then propagation through a stated field and material. Neither parent-volume intersection nor nominal station count is hit efficiency.
7. **Technology:** choose rate-capable chamber families and realistic inactive edges only after the envelope and role are agreed. Keep alignment and electronics assumptions visible.

## Verification in this pass

Inspected the pinned XML/factory definitions and the cited local PDF passages; searched public primary-source literature to cross-check the historical magnet/station distinction. No DD4hep construction, overlap check, transport, field integration or reconstruction was run. The parent session records this contribution; technical and human review remain pending.
