# DES-003 input — Tracker envelope request

- Status: DRAFT; stage-B architecture input, not approved geometry.
- Date: 2026-09-16.
- Role: Tracker technician; human technical reviewer and approving humans: pending.
- Governing context: [project](../../../PROJECT.md), [development plan](../../DEVELOPMENT_PLAN.md), ADR-001/003 (both DRAFT).
- Source IDs resolve in the [catalogue](../../../reference/manifest.yaml).

## Recommendation

**NODD DESIGN CHOICE — proposed:** retain the ODD-scale all-silicon tracker allocation
for the first global drawing: **0.025 ≤ r ≤ 1.140 m, |z| ≤ 3.150 m**. This is an
allocation for an assembly, not a fully sensitive cylinder, a layer prescription,
or an achieved acceptance. Keep the outer tracker scale while allowing the pixel/
outer-tracker boundary to move after RD53-module and support studies.

Request a separately owned service/timing/interface reservation outside this
allocation. Do not label ODD's existing small clearances as sufficient. The System
Architect must negotiate its dimensions with the magnet and calorimeter owners.

**NODD DESIGN CHOICE — proposed:** investigate tracking to **|η| ≈ 4**, with robust
central tracking and a separately assessed forward capability. Approving humans:
pending. This is motivated by both experiment TDRs, but is not a demonstrated nODD
performance statement. A cheaper/reduced-coverage alternative remains legitimate
if its effect on forward physics and pile-up association is documented.

## Source facts and what they establish

All PDF page numbers below are one-based physical pages. The ATLAS source is the
local 2018 edition; CMS is the 2017 TDR with a later cover stamp. These are
historical engineering proposals, not assertions about final installed systems.

| Classification | Observation and exact locator | Architecture consequence |
| --- | --- | --- |
| FACT | SRC-CMS-TDR-014, §3.1, PDF 25: outer tracker modules span approximately r=0.21–1.12 m; barrel \|z\|<1.20 m; endcap double-discs 1.20<\|z\|<2.70 m. | ODD's outer radial scale and barrel length have an experimentally motivated analogue; occupied structures/services extend beyond module centres. |
| FACT | SRC-CMS-TDR-014, §2.2, PDF 19 and §4.1, PDF 71: target tracking acceptance about \|η\|=4; forward coverage helps pile-up mitigation in the endcap calorimeters. | Forward pixel geometry and calorimeter association require a joint requirement. |
| FACT | SRC-CMS-TDR-014, §3.1, PDF 25: nominal six crossed outer-tracker module layers within \|η\|<2.4, with a transition region near \|η\|≈1 averaging five; luminous-region assumption \|z\|<0.070 m. | Even an engineered design can have transition weaknesses. A single advertised coverage number hides important structure. |
| FACT | SRC-ATLAS-TDR-030, §2.1, PDF 25–26 / printed 3–4: pixel coverage to \|η\|<4, strips to \|η\|<2.7; physical pixel/strip support-tube separation. | Separate pixel and outer-tracker coverage and mechanical boundaries. |
| FACT | SRC-ATLAS-TDR-030, §2.1.1–2.1.2, PDF 27–29 / printed 5–7: layout iteration uses field/material-aware fast estimates followed by Geant4; inclined modules and ring layout relocate services and improve forward coverage. | Service routing and hit redundancy must inform envelopes, not be added afterward. |
| FACT | SRC-CMS-TDR-014, §5.1, PDF 89: outer support tube has a 0.030 m sandwich wall, and the inner tracker/beam pipe depend on the outer-tracker support hierarchy. | A realistic tracker needs space for supports and explicit mechanical ownership. This CMS wall thickness is not an nODD requirement. |
| FACT | SRC-CMS-TDR-014, §4.1, PDF 72: four barrel pixel layers, eight small and four large double-discs per side; staggered modules and asymmetric longitudinal assembly avoid projective gaps. | Envelopes alone cannot establish hermeticity or independent hit counts. |

## Pinned ODD allocation

**FACT:** SRC-ODD-UPSTREAM at `c167363f3d4ad1540a577af99071283caf54f3a6`,
`xml/OpenDataDetectorEnvelopes.xml`, defines the following constants. The tracker
detector XML files consume `*_env_*` in their top-level Tube shapes and the
barrel/endcap dimensions. These are inspected source definitions, not a newly
executed DD4hep construction or validated occupied-volume bounds.

| Region | r interval [m] | \|z\| extent [m] | Symbols |
| --- | --- | --- | --- |
| Pixel allocation | 0.025–0.200 | ≤2.400 | `pix_env_rmin/rmax/dz` |
| Pixel barrel subdivision | same allocation | ≤0.580 | `pix_b_dz` |
| Pixel endcap subdivision, each side | same allocation | 0.580–2.380 | `pix_e_pz=1.480 m`, `pix_e_dz=0.900 m` |
| Short strips | 0.204–0.720 | ≤3.150 | `ss_env_rmin/rmax/dz` |
| Long strips | 0.720–1.140 | ≤3.150 | `ls_env_rmin/rmax/dz` |
| Strip barrel / endcap subdivisions | respective strip allocation | ≤1.200 / 1.200–3.150 | `ss_b_dz`, `ls_b_dz`, `ss_e_pz/ls_e_pz=2.175 m`, `ss_e_dz/ls_e_dz=0.975 m` |

The source separately annotates `tracker_region_rmax=1.080 m` and
`tracker_region_zmax=3.030 m` as tracking sensitivity. **Do not substitute these
for the assembly envelope.** The support tube occupies r=0.202–0.204 m
(`pst_rmin/rmax`); the intervening allocation is not proven spare service space.

**INFERENCE:** simple boundary differences give only **0.020 m** between the
outer strip allocation and the solenoid inner radius (`sol_rmin=1.160 m`), and
**0.050 m** between the strip longitudinal end and ECal endcap start
(`ecal_e_min_z=3.200 m`). These differences do not establish usable continuous
corridors, manufacturing clearance or timing fit. Preserve the tracker allocation
initially, then expand the surrounding integration space or reduce it through an
explicit coupled trade study; do not silently squeeze services into empty drawing
space.

## Alternatives and interfaces

- **NODD DESIGN CHOICE — proposed option:** retain the 0.200 m pixel outer
  allocation as an ODD-continuity hypothesis. Compare a larger pixel allocation
  before freezing the boundary; RD53 module tiling, extra pixel redundancy and
  realistic supports may consume outer-tracker space. Neither ATLAS's nor CMS's
  module/layer arrangement should be copied without comparison.
- **Beam pipe:** System Architect owns the profile, transitions and support
  handoffs. ODD's central outer pipe radius is 0.0244 m (`bp_rmax`), leaving a
  nominal **INFERENCE** of 0.0006 m to the pixel allocation. This is not a sensor
  clearance or credible installation margin. Resolve first-layer active radius
  separately from the container boundary.
- **Timing:** tracker technician supplies technology/coverage options; System
  Architect reserves a named barrel and/or forward volume with the calorimeter
  owner. No timing thickness is supported by the present tracker envelope study.
- **Services:** separate local module/support material from shared outgoing cable,
  coolant and power corridors. Define where ownership and material accounting
  transfer. Preserve azimuthal routing and barrel/endcap transition questions.
- **Magnetic field:** SW and magnet owners must supply a common field identity and
  gradients over the complete tracking allocation, including forward disks.

## Required follow-up before envelope acceptance

1. Agree luminous-region distribution, transverse-momentum range, displaced-track
   scope, redundancy and forward-physics use cases; do not inherit different
   ATLAS/CMS study assumptions unnoticed.
2. Specify active surfaces within the allocation and count crossings versus η,
   φ, vertex and momentum. A ray with η=4 has r=z/sinh(4), approximately **0.088 m
   at z=2.400 m** (**INFERENCE**, prompt straight-line geometry). It can enter the
   pixel box; this proves neither several hits nor reconstructibility.
3. Reconcile overlap, module gaps, paired strip sensors versus independent
   measurements, and barrel/endcap transition coverage.
4. Compare plausible material scenarios for supports, cooling and outgoing
   services; no whole-tracker X0 target is justified by this envelope pass.
5. Negotiate timing, cryostat/coil and service reservations together, including
   their effects on upstream calorimeter material and forward cracks.

## Research record and limitations

Read local source passages above with the existing PyMuPDF environment and
inspected pinned XML definitions. No geometry build or simulation was run. CMS
public record access encountered its existing bot challenge; local identified TDR
remains available, so no required evidence is inaccessible.

A current web cross-check used the official ATLAS feature
[A new ATLAS for the high-luminosity era](https://atlas.cern/Updates/Feature/High-Luminosity-ATLAS),
§“State-of-the-art tracking”, by Stefan Guindon, Christian Ohm and Caterina Vernieri,
2023-01-18, accessed 2026-09-16. It independently describes the extended pixel
coverage and the role of forward timing. Suggested catalogue ID:
`SRC-ATLAS-HLLHC-OVERVIEW-2023`; HTML, no local copy/hash, redistribution rights
not checked. The numerical envelope recommendation relies on the registered ODD
and local TDR sources above, not an uncatalogued web parameter.
