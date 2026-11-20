# DES-045 — Deep, segmented HCAL around the restored LAr ECAL

2026-11-20. **DRAFT / PROTOTYPE**, requested by the project user. No engineering
sign-off or detector acceptance. Parents: DES-035–038 and the
[November 18 ECAL selection](inputs/ECAL-baseline-selection-2026-11-18.md).
The historical 36-layer studies and maintained tracker/ECAL exporter remain
reproducible; this is an isolated full-HCAL simulation proposal.

## Physical basis

**FACT — public technology precedent:** SRC-CALICE-AHCAL-2022, sections 2.1–2.2,
describes individually read out SiPM-on-tile scintillators with 30 mm transverse
granularity and 3 mm scintillator thickness. It does not establish a proton
collider rate, radiation or lifetime qualification for nODD.

**FACT — retained project hardware:** DES-036 supplies the complete
380 × 240 × 12 mm carrier, two 184 mm boards, 72 separate
29.7 × 29.7 × 3 mm scintillator cores on 30 mm pitch, reflectors, sensor recesses,
SiPM and electronics proxies, skins, cold plate and cooling material. Preserve
the physical gaps, including the 6.3 mm inter-board core seam and service bay.
The optional module test's reference absorber is omitted: regional plates own
the steel once per layer. No uninterrupted sensitive plane substitutes for tiles.

**NODD DESIGN CHOICE — transport hierarchy:** the full assembly has about21million
logical tile channels. On the measured64GiB host, avoid a separate native
volume-manager context for every tile: compound the72 disjoint, unchanged core
CSG solids into one sensitive union in each carrier. Keep their actual recesses,
gaps, passive components and material. A custom segmentation maps carrier-local
positions to the original module/sensor addresses and returns exact core centres.
This changes the logical hierarchy only. Check all72 channel centres and union
capacity against the original solids; optical boundary behavior is outside this
raw-deposit model. A carrier context, rather than a tile context, supplies the
coordinate transform. No sensitive material fills any gap.

**NODD DESIGN CHOICE — depth:** increase 36 to **60 layers**, retaining 30 mm
Steel235 per layer, the unchanged 12 mm carrier, 1 mm installation allowance and
10 mm rear cover. The choice is made before shower results, to give substantial
standalone depth after removing the ECAL. Adding sampling layers preserves the
existing sampling structure; adding copper to an electronics proxy would not.
The alternative 48-layer stack is smaller but has less standalone depth.

**FACT — screening reference:** SRC-PDG-FE-2026, iron property table, lists
167.7 mm nuclear interaction length and 204.1 mm pion interaction length.
**INFERENCE:** 1800 mm steel corresponds approximately to 10.733 nuclear or
8.819 pion interaction lengths using pure iron. These are distinct quantities;
native Steel235 material/path checks must replace the screening approximation.
The complete mechanical depth is `60 × (30 + 12 + 1) + 10 = 2590 mm`.
This arithmetic is not a claim that all showers or all directions are contained.

## Fit to the selected ECAL

**FACT — selected project envelope:** the restored LAr barrel warm radius is
2641.7 mm and half-length is 4100 mm. Endcaps occupy R=301–2949 mm and
|z|=5100–6260 mm. The selected context reserves HCAL front apothem3130 mm,
barrel half-length6260 mm and endcap front |z|6760 mm.

**NODD DESIGN CHOICE:** retain these front coordinates, the 500 mm rear ECAL
service break and 300 mm endcap bore apothem. Amend the outer/rear HCAL bounds:

| Coordinate | Proposed value [mm] |
| --- | ---: |
| Barrel inner / outer apothem | 3130 / 5720 |
| Barrel half-length | 6260 |
| Barrel 16-gon maximum corner radius | 5832.061 |
| Endcap inner / outer apothem | 300 / 5710 |
| Endcap front / back | |z|=6760 / 9350 |
| Outer service handoff reservation | R=5950 |

**INFERENCE:** radial allocations are 488.3 mm outside the barrel and181 mm
outside the endcap cylinder. They include services. The retained R3029 mm
external route plus50 mm radius and20 mm clearance leaves31 mm to the HCAL
face. A5950 mm outer handoff leaves47.939 mm beyond corner+50+20; this is an
allocation only, with no newly installed pipe. The older R4800 handoff is
superseded for this proposal.

The enlarged HCAL requires subsequent magnet/muon and FCAL interface work.
Historical FCAL rear-route proofs do not transfer. Full-depth barrel and
endcap traversals leave a transition around |eta|0.947–1.269; quantify the
combined path and shower response there instead of adding separate maxima.
Whole carrier packing, staggered layers, fixed sector seams, support edges and
the bore remain real losses. This proposal does not close thermal, hydraulic,
structural, extraction, pressure-vessel, high-rate or radiation questions.

## First transport and validation

Use the predeclared [50 GeV pion protocol](../validation/hcal50/protocol.md).
First validate deterministic export, layer/placement/identifier capacity,
unchanged common materials, native construction and overlaps. Audit native
material interaction lengths and finite rays, worker configuration, all primary
and cell IDs, and accepted sensitive-step energy against native and saved hits.
Run serial/MT controls and a pilot before the10k production sample.

Report raw visible response, width, distributions, longitudinal activity and
terminal-layer fractions. Include all valid primaries, zeros and tails. A single
50 GeV sample cannot establish multi-TeV containment or calibrated resolution.
No optical statistics, Birks quenching, SiPM saturation, noise, threshold,
timing electronics, digitization or calorimetric reconstruction is included.
