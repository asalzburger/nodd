# DES-003 calorimeter review 1: forward reach and service interfaces

- Date: 2026-09-17
- Status: DRAFT; subsystem recommendation, no human technical sign-off
- Scope: global envelopes and interfaces for 14 TeV HL-LHC studies
- Parent: [DES-003](../DES-003-global-envelopes.md)
- Supersedes: the earlier input's open question on whether coverage beyond absolute eta 3 is wanted. The user now requests absolute eta below 5, with extension where feasible.

## 1. What the experiments establish

**FACT — SRC-ATLAS-JINST-2008**, §5.3.3.1–2, printed pp. 129–130 / PDF pp. 159–160,
Table 5.4 and Fig. 5.19: ATLAS integrates forward calorimeters with the endcap
cryostats, covering `3.1 < |eta| < 4.9`, approximately 4.7 m from the interaction
point. Three 0.45 m modules use copper then tungsten absorbers. Their quoted
interaction lengths are 2.66, 3.68 and 3.60; the electromagnetic module gives
27.6 radiation lengths. A shielding plug follows the final module to reduce muon
backgrounds. This supports a compact, dense forward option, not use of ordinary
barrel sampling geometry arbitrarily close to the beam.

**FACT — SRC-CMS-JINST-2008**, §5.4, printed pp. 145–147 / PDF pp. 172–174,
Fig. 5.28: CMS HF's absorber front is at 11.2 m, inner radius 0.125 m, outer radius
1.30 m and absorber length 1.65 m (approximately ten interaction lengths).
Steel/quartz-fibre calorimetry provides two longitudinal readout channels by using
full-length fibres and fibres beginning 0.22 m into the absorber. Its surrounding
shielding, rear readout, supporting table and services are additional volumes;
the absorber dimensions do not define the whole installed system.

**FACT — SRC-CMS-HCAL-CALIBRATION-2020**, abstract of
[arXiv:1910.00079v2](https://arxiv.org/abs/1910.00079v2), JINST 15 (2020) P05002:
the later collision-data calibration paper reports HF coverage to absolute eta
5.19. Its §2, printed p. 4 / PDF p. 6, describes the 2016 operating detector with
front faces at **11.150 m**, inner/outer radii **0.125/1.570 m**, coverage
**2.85–5.19**, and long/short quartz fibres **1.649/1.426 m**. It demonstrates
operational use of that coverage; it does not establish that all forward showers
are contained or transfer HF response to nODD.

**Source discrepancy retained:** the 2008 text explicitly calls 1.300 m the outer
radius of the steel structure; its Fig. 5.28 caption (PDF p. 174) identifies
0.125–1.300 m as the sensitive radial extent, and Table 5.8 (PDF p. 175) ends the
outer tower at 1.300 m. The 2020 paper instead explicitly gives 1.570 m as the
calorimeter outer radius. These excerpts do not resolve whether this is a
boundary-definition distinction, physical change or documentation inconsistency.
Do not merge them into one historical geometry or assert an upgrade without
evidence. The front-face difference is also retained rather than silently rounded
away. Both papers support the scale of a detached forward detector; neither fixes
our enclosure. Resolving the exact CMS boundary is necessary only if a later
comparison reproduces that detector. It does not block an independently specified
nODD envelope.

**INFERENCE:** reaching eta 5 is a credible reference-detector objective. A separate
forward calorimeter with technology suited to high flux is better motivated than
merely shrinking every current endcap hole. A compact ATLAS-like location and a
detached CMS-like location are both precedents, with different integration costs.

## 2. Recommended envelope option: detached forward calorimetry

**NODD DESIGN CHOICE — proposed, approving humans: none.** Reserve on each side
an instrumented forward-calorimeter study envelope:

| Quantity | Proposed allocation | Rationale |
| --- | --- | --- |
| Absolute z | 11.2–13.2 m | Retain CMS-like distance; allow 2.0 m axial allocation versus historical 1.65 m absorber |
| Inner radius | 0.120 m | Prompt eta 5 reach with room to investigate approximately 5.2 |
| Outer radius | 1.500 m | Angular overlap with existing endcap calorimetry through its transition |
| Separate upstream endcap ECal aperture option | reduce 0.315 to 0.180 m | Preserve calorimeter depth before proposed muon eta 3.5 stations |
| Separate upstream endcap HCal aperture option | reduce 0.355 to 0.200 m | Same reason; retain current axial ranges pending depth studies |

The 1.500 m outer radius is an **independent nODD allocation**, not a copied CMS
outer boundary or a resolution of the 1.300/1.570 m source discrepancy.
The forward allocation is **not a complete enclosure**: shielding, rear readout,
support and service routes require separate reservations, possibly extending beyond
13.2 m and radius 1.5 m. Extending the simulation world is an explicit consequence.
The 0.35 m axial increment over CMS HF is a planning allowance, not a demonstrated
services budget. No absorber technology, number of layers or material recipe is
selected here. Minimal support must still carry its intended role in material
accounting; a CAD structure is unnecessary in this round.

**INFERENCE — prompt straight rays:** `r = |z| / sinh(|eta|)`. Crossing the complete
axial depth of an annular cylinder requires
`asinh(z_back/r_outer) <= |eta| <= asinh(z_front/r_inner)`.
The proposed forward box therefore has a full-axial-depth geometric band
**2.871–5.229**, before passive skins, dead rims, shower spread and vertex offsets.
At eta 5, radius grows from 0.15094 to 0.17789 m; at eta 5.2 it grows from
0.12357 to 0.14564 m. Only **3.57 mm** separates the eta 5.2 ray from the proposed
inner face at entry: this is an exploratory edge, not robust accepted coverage.
Eta 5 is the working objective; extension needs beam-pipe/shielding dimensions,
vertex-envelope and shower-edge studies. A front-face intersection alone is insufficient.

The detached option avoids overlap with the present muon allocation ending at
absolute z 10.27 m, leaving 0.93 m before the calorimeter front; that interval is
not pre-approved for shielding. However, **a calorimeter downstream of muon
stations cannot filter hadrons before those stations**. The muon technician agrees
this is a physics-interface constraint, despite non-overlapping boxes.

For eta 3.5, the proposed smaller upstream apertures give entrance reach 3.647
(ECal, z=3.45 m) and 3.679 (HCal, z=3.96 m), allowing the prompt ray to traverse
the full axial stack before the muons. These values request an inner endcap
extension, not a validated sensor technology or shielding solution. Their beam-line
clearance and mass must be reconciled with tracking to eta 4. The radial overlap
between central and detached calorimetry provides redundancy but requires combined
response accounting; do not count the same energy twice.

## 3. Compact alternative and why it is not the default

**NODD DESIGN CHOICE — proposed alternative:** a forward calorimeter at
absolute z **6.2–8.2 m**, radius **0.080–0.900 m**, has a prompt full-depth geometric
band **2.906–5.043**. Eta 5 enters at radius 0.08355 m, again with only millimetres
of aperture margin. Achieving ten interaction lengths in this allocation requires
an explicit dense absorber/active-medium choice; ATLAS establishes a possible
technology class, not the adequacy of this design.

This box overlaps the existing muon envelope starting at z=7.2 m, including
trajectories for eta 3–3.5. It requires moving early muon stations behind it or
partitioning the radial/axial volumes and accepting a revised station sequence.
No shared empty box can solve that overlap. A genuinely integrated ATLAS-like
insert farther upstream would require reshaping the current ECal/HCal inner
boundaries and their supports. Keep this alternative for a deliberate compactness
tradeoff; the detached option disrupts fewer existing global interfaces.

## 4. Service exits: replace empty gaps with named routes

**FACT — SRC-ATLAS-JINST-2008**, §5.5, printed p. 136 / PDF p. 166:
the barrel/endcap cryostat gap contains inner-detector and barrel-LAr services;
gap scintillators help correct energy lost in inactive material. Services and
recoverable calorimeter response coexist; the gap is not empty acceptance.

**FACT — SRC-CMS-JINST-2008**, §4.2, printed p. 92 / PDF p. 119:
barrel ECal services converge to patch panels at supermodule external ends.
**FACT — SRC-CMS-TDR-019**, §4.5, PDF/printed pp. 64–65, Figs. 4.6–4.7:
HGCAL services follow its outer surface and leave through the outer circumference
of the rear thermal-screen disk. The design explicitly shares constrained exits
with timing and muon services and preserves ME1/1 access; technical coordination
owns the joint route. These are dated design examples, not nODD load estimates.

**NODD DESIGN CHOICE — proposed route topology:** retain the present barrel/endcap
axial gaps as integration reservations, but route barrel bundles toward outer/end
patch regions and endcap bundles along the outside toward a rear annular handoff.
Give tracker, calorimeter and muon routes named owners and azimuthal sectors;
reserve local penetrations and stagger projective gaps where possible. Do not fill
an entire annular gap with a uniform cable material without documenting what it
represents. First validation needs minimum path depth versus eta/phi, service mass
ranges and continuity to off-detector handoffs, not detailed cable CAD.

## 5. Depth and immediate decisions

Historical **24–30 radiation-length ECal** and roughly **9–11 interaction-length
combined-calorimeter** screening bands remain useful comparison hypotheses from
the earlier input. Operational papers validate particular calibration/response,
not a universal depth rule. At 14 TeV, define energies and acceptable leakage for
single particles and jets before freezing depth. Scan transition/beam-hole edges,
leakage into muons and uninstrumented material separately. Dense-PCB inventory is
deferred as requested; it must remain counted in any inherited depth estimate.

Decide now: detached versus compact forward location; reserve the smaller upstream
apertures for muon filtering; nominal eta 5 versus conditional stretch 5.2; and
service handoff ownership. Later close shielding, beam-line aperture and energy/
angle-dependent containment. This pass used source inspection and explicit ray
arithmetic; no detector construction or shower simulation was run.
