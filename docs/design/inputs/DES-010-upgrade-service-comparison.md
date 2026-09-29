# DES-010 input — Service spaces in ATLAS and CMS upgrade designs

- Date: 2026-09-29; **DRAFT / PROTOTYPE comparison, no geometry approval**.
- Responds to [PR #25's expert question](https://github.com/asalzburger/nodd/pull/25#issuecomment-5890301780).
- Governing [DES-010](../DES-010-tracker-service-corridors.md); original
  [service-gap report](../../validation/DES-010-tracker-services.md).

The nODD reservations are broad compared with the published engineering scales,
especially the 170 mm short-strip route. They should not be treated as required
upgrade-tracker gaps. ATLAS/CMS distribute and aggregate services differently,
and a difference between active detector radii is not the same as an available
cable corridor. The present comparison adds context and exposes opportunities
for the later routing/position optimization; it does not select narrower gaps.

## Source editions and verification

**FACT — source identities:** SRC-ATLAS-TDR-030 is the public ATLAS Pixel TDR,
CERN-LHCC-2017-021 / ATLAS-TDR-030, catalogue edition dated 2018-07-10; its cover
was created 2018-06-15. [Official public page](https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/UPGRADE/CERN-LHCC-2017-021/).
SRC-ATLAS-TDR-025 is the Strip TDR, CERN-LHCC-2017-005, local cover 2017-04-15.
[Public record](https://cds.cern.ch/record/2257755). SRC-CMS-TDR-014 is the CMS
Phase-2 Tracker TDR, CERN-LHCC-2017-009, local cover 2017-07-01 with a later CERN
stamp. [Official CMS index](https://cms-results.web.cern.ch/cms-results/public-results/preliminary-results/TDR-17-001/index.html),
[public record](https://cds.cern.ch/record/2272264).

Catalogue PDF SHA-256 values, respectively:

- ATLAS Pixel: `14ec26bfb376c7a7a6fba2d06819a30b3ef6dc378508911ae7e90c3a8833dd12`.
- ATLAS Strip: `f1ce247fb807a37b0e9065c02764f39f041fc66d266c824828cad9b2915d2bff`.
- CMS Tracker: `642f37707fbe2654c99ae3e9c116297c537d2f048370602ca7de92e5d79a1f54`.

Local public catalogue copies were checked and the dimensioned figures rendered
and visually inspected. CDS record/PDF browsing returned access challenges;
current public/local byte equality remains unverified. These historical
engineering envelopes are not assertions about final construction. The ATLAS
Fig. 15.1 drawing is ITk Envelope Model v1.5, 2017-11-29, explicitly marked
**For Discussion / Not Valid for Execution**. Its public reproduction is the
source; no internal CAD document is used as a normative reference.

A later primary public presentation, SRC-ATLAS-ITK-PIXEL-OVERVIEW-2021,
Francisca Muñoz Sánchez for ATLAS ITk Pixel, *ATLAS ITk Pixel Detector Overview*,
TIPP2021, 2021-05-27, ATL-ITK-SLIDE-2021-214, supplies a local ring-shell example.
[Public PDF, slide 15](https://cds.cern.ch/record/2772175/files/ATL-ITK-SLIDE-2021-214.pdf#page=15).
Its unauthenticated download was checked (26 pages, 75,835,729 bytes), SHA-256
`ed02cd2c6d7804876bc3380c2fdc6d44da7d5f4b0b3589e08bc1ae4a161973bc`.
Cover and slide 15 were inspected. Redistribution is unestablished; all source
PDFs remain ignored and are not committed. Printed / one-based PDF pages follow.

## Dimensioned facts and derived widths

Coordinates and labels in the third column are **FACT**; every subtraction or
comparison in the fourth is **INFERENCE**. No source specifies the nODD packing
or azimuth factors. All lengths are mm and all radial coordinates are radii.

| ID | Source / object | FACT: labelled boundaries or statement | INFERENCE: width and limits |
| --- | --- | --- | --- |
| UG-F01 / UG-I01 | ATLAS Pixel TDR Fig. 15.1, p322 / PDF344; strip-barrel service bypass outside endcaps | Strip Barrel Services r=1015–1061 | 46 radial. Carries barrel services past endcaps, not the full combined strip endcap+barrel inventory. A service-labelled envelope, without a published all-phi packing allowance. |
| UG-F02 / UG-I02 | Same figure; strip-barrel radial escape | Barrel layer endpoint z=1372; service band endpoint z=1475; strip endcap starts z=1478 | 103 axial for the labelled service band, plus 3 to the endcap envelope. This is a historical envelope drawing, not a qualified bundle bend radius. |
| UG-F03 / UG-I03 | Same figure; pixel/endcap support interface | Pixel endcap outer r=330; PST inner r=346, outer r=361.75; strip endcap inner r=367.45 | Pixel-to-strip difference 37.45 includes 16 to PST, 15.75 PST allocation and 5.70 separation. **Not 37.45 of free cable space.** The endcap-side PST inner boundary is 346; the barrel-side label 345 is distinct. |
| UG-F04 | ATLAS overview 2021 slide 15; outer pixel ring-layer services | Services follow shells at half-ring outer rims; limiting Layer 2 last half-ring has reported local accommodation 6.6 and fits its services | Retain the reported local accommodation; the slide does not give independent radial CAD bounds/tolerances. It is one ring-layer route, not all pixel services in a combined trunk. |
| UG-F05 / UG-I05 | CMS TDR Fig. 5.1, p89 / PDF89; outer barrel-service bypass | Barrel services inner r=1155; thermal-screen inner boundary r=1175; TEDD with services outer r=1145 | Nominal bypass allocation 20 radial. The separate 10 installation clearance between TEDD and barrel services is **not payload space**. No full-azimuth packing claim. |
| UG-F06 / UG-I06 | Same figure; barrel radial escapes | TBPS structure ends z=1224.5, services end 1265; TB2S ladders end 1202, services end 1245 | Axial allocations 40.5 and 43 respectively. TEDD starts 1275, giving separate 10 installation clearance after TBPS services. |
| UG-F07 / UG-I07 | Same figure; barrel package boundaries | TBPS outer r=577; TB2S inner r=621 | 44 mechanical-envelope separation, **not labelled a dedicated PS-service annulus**. |
| UG-F08 / UG-I08 | CMS Table 10.1 p236 / PDF236 plus Fig. 5.1 p89 | Pixel TFPX outer module radius 160 and TEPX 254; corresponding OT inner allocations 210 and 310; IT support-tube boundaries 200 and 300 | Pixel-module-to-OT differences 50 and 56 include support/services/clearances. Only 10 remains between the stated IT support tube and OT allocations. Neither subtraction measures usable cable space. |

The ATLAS TDR's 1512−1400=112 nominal first-disc/barrel-end separation
(Strip §3.2.1/Table 3.1 p27–28 / PDF53–54) is an active-layout comparison, not the
same boundaries or edition as the later dimensioned service band. It is not
silently substituted for the 103 mm service-labelled allocation.

## What is comparable with nODD

All nODD dimensions below remain **NODD DESIGN CHOICE, unapproved**, SC-C10–19.

| nODD fixed reservation | ATLAS reference scale | CMS reference scale | Interpretation |
| --- | --- | --- | --- |
| Pixel axial trunk 72 radial, r170–242 | Reported 6.6 local ring-layer accommodation; 37.45 pixel-to-strip envelope difference |50/56 pixel-module-to-OT envelope differences | nODD collects the entire pixel subsystem in one route. ATLAS distributes services over shells; boundary subtractions include structures. No direct capacity ratio follows. |
| Short-strip axial trunk 170 radial, r635–805 | No separate nested short/long-strip endcap corridor | No separate nested PS/2S endcap corridor; 44 is only a barrel mechanical gap | Largest architectural difference. Neither experiment establishes 170 as a necessary inter-endcap gap. |
| Long-strip external trunk 76 radial, r1144–1220 |46 strip-barrel service bypass |20 outer barrel-service bypass, plus separate 10 installation clearance | Similar outer routing function, different transported loads and sector/access architecture. Published widths are smaller; nODD includes its endcap load in the trunk. |
| Pixel/short/long barrel bays 50/80/90 axial |103 strip-barrel radial service band |40.5 TBPS and 43 TB2S radial service allocations | nODD strip bays are of the same order as ATLAS and about twice these CMS allocations; pixel architecture differs. Width agreement does not qualify connectors or bends. |

**FACT — routing topology:** ATLAS Strip §11.4.2–3 p262–267 / PDF288–293 places
service modules/trays outside the endcap, with electrical, optical and cooling
exits arranged differently. CMS PS and 2S share TEDD dees/rings (§3.1.1 pp27–28,
Fig. 3.5), while TBPS/TB2S barrel services are connected and routed to the OT support
tube ends before TEDD installation (§11.2 p266). Thus neither has nODD's proposed
separate nested short/long endcap packages and its uniform 170 mm gap.

**INFERENCE — comparison limits:** route cross-section depends on radius as well
as width, on available azimuth, packing, supports/access and actual chains/links/
pipes. ATLAS's 46 mm bypass has mean radius 1038, while the nODD short-strip trunk
has mean radius 720 and also collects short-strip endcaps. The widths cannot
establish a relative capacity or material mass. CMS PS/2S trigger modules and
ATLAS conventional strips also have different readout loads from nODD strixels
and stereo pairs. The existing budget remains a declared engineering comparator.

## Does the cable bundle grow along the endcaps?

**FACT — public precedent:** ATLAS Pixel §2.2.1 p16 / PDF38 accounts for material
build-up along cylindrical endcap service volumes fed by radial barrel/endcap
annuli. ATLAS Strip §3.3 p31 / PDF57 varies pixel barrel cable material with z
because the number of cables changes. The later slide 15 identifies the last
half-ring as limiting. These support a position-dependent load calculation.

**INFERENCE — original nODD implementation:** individual disc collectors carry
only their selected layers. Barrel radial segments accumulate inner layers; rear
collectors accumulate subsystem owners. However, each original **axial trunk
carries the final entire signed-end inventory at every z**. The constant gap is
therefore an upper-envelope reservation, not a claim that its full payload is
needed before the outermost endcap.

SC-C19 adds a separate cumulative diagnostic. Every feeder contributes the whole
retained local groups once at the near edge of its finite trunk intersection.
Chains, harnesses and per-layer cooling manifolds are counted before summing;
demand is not scaled linearly by a module fraction. Supply/return and coolant
feed/exhaust occupy the same route even when flows run in opposite directions.
Substantial barrel services are already present at the first endcap. Final load
is reached at the last pickup and continues to the common exit under this
routing hypothesis. Connector/manifold pockets can still limit capacity earlier.

The [review response results](../../validation/DES-010-service-gap-review.md)
show the actual per-section inventory, equivalent widths and plots. No gap,
module row, layer radius or disc position is changed here. Tapering and row
recovery require the separate constrained optimization and interface review.
