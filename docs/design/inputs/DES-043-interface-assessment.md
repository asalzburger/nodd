# DES-043 input — Short-strip endcap and service interfaces

- Status: **DRAFT / PROTOTYPE; interface assessment, not design acceptance**.
- Date: 2026-11-02.
- Assignment: `DES043-SysArch-01`, explicit SysArch profile fallback.
- Examined source: `b564308fe2e76da42d0d62c6ba33f9c76876119c`.
- Scope: finite endcap bounds, candidate ring layouts and service handoffs;
  long-strip geometry is held fixed. No native dependencies were used.
- Related: [DES-043](../DES-043-short-strip-service-redesign.md),
  [DES-021](../DES-021-short-strip-endcap.md),
  [DES-023](../DES-023-long-strip-endcap.md),
  [human-selected readout](DES-042-strixel-selection.json).

## Source boundary and recommendation

**NODD DESIGN CHOICE, candidate recommendation:** investigate five rings at
`289.5, 381, 472.5, 564, 655.5 mm`, rather than adding a sixth ring at 690 mm
without changing the module support. This retains the 48 × 96 mm active sensor
and 60 mm radial pickup, gives 396 modules/disc and reduces the finite active
radial gap to the unchanged long strips by 31.424 mm. It requires revised
petals, board mounts and service transitions; it is not a placement-only change.

For the coordinator's provisional 8 mm power-cable, at-most-14-module LV
grouping and two-loop/petal service hypothesis, compare a trunk at
`r=717..781.5 mm` with `718..783 mm`. The former leaves 2 mm to the existing
long-strip inner bearing ring, while passing the specified adverse *area*
screen with 25% spare. Retain failures of the 10 mm cable and 725 mm inner-edge
cases. Neither cable's current capacity is qualified by this assessment.

**FACT, recorded human decision:** merged PR109 selected 75 µm × 2 mm readout,
while leaving physical placements, material and service allowances unchanged;
see `DES-042-strixel-selection.json`, `scope` and `pitch_mm`. Its channels are
not authority to remove pipes, fibres, ASIC material or cable space.

The baseline source-model parameters below are inherited **NODD DESIGN
CHOICES**, not measurements of constructed hardware. Derived results are
**INFERENCE**. New dimensions in candidate tables are **NODD DESIGN CHOICE**
proposals with no approving human recorded. No new public engineering fact is
introduced; the existing public-source dossier remains
[DES-010 strip services](DES-010-strip-services.md), particularly SS-F02/07–12.

## Baseline finite bounds

Sources at the examined commit:

| Source | Relevant definition |
| --- | --- |
| `tools/short_strip_endcap/model.py:47–85` | Five ring centres/populations, proper signed-end frames, four normal levels and route groups |
| `tools/short_strip_endcap/inputs.json` | Disc datums; plate236..685; frames236..250 and674..700; board695; fan685..710; trunk710..783 mm |
| `tools/short_strip_endcap/export.py:25–30,94–105,113–151` | Readout, local buses, module/flex/pickup footprints, boards and outer fan |
| `tools/long_strip_endcap/model.py:18–35` | Four long-strip ring centres and actual ±20 mrad sensor axes |
| `tools/long_strip_endcap/export.py:25–28,57–65,68–80,141–147` | Core/skins, inner mounts, complete modules and bearing rings |
| `tools/short_strip_barrel/model.py:145–162` | Half-stave group/sector populations and collector-to-trunk handoff |
| `tools/short_strip_barrel/inputs-phi-tilted.json` | Barrel collector244..750 mm, abs(z)1245..1310; fixed support/cooling inventory |

For the short rectangular active plane, the global minimum radius is `R-48`,
attained inside an edge, and the maximum is `hypot(R+48,24)`. The complete
49 × 103 mm occupied module rectangle has maximum `hypot(R+51.5,24.5)`.
For the innermost long-strip centre `R=835.4105719792313 mm`, the nearest point
on a 96 mm square at 20 mrad lies inside an edge: `R*cos(.02)-48`. Its edge
coordinate is −16.707098 mm, within the ±48 mm edge. A corner-only calculation
would overestimate the minimum by 0.621700 mm.

| Baseline quantity | Derived radial bound [mm] |
| --- | ---: |
| Short-strip active envelope | 241.500000..672.485592 |
| Outermost short module occupied rectangle | outer676.001310 |
| Short cold carrier / outer frame | outer685 /700 |
| Short board corner, r695 with tangential half26/radial half10 | outer705.479270 |
| Short axial trunk | 710..783 |
| Long inner bearing ring / carrier | inner783.5 /784 |
| Long inner guard / active plane, true edge minima | 786.743495 /787.243495 |
| Finite active-envelope radial gap | **114.757904** |

The nominal annulus difference `786.460236-670.057193=116.403043 mm` is a
different quantity from the finite active-envelope gap. Neither is an all-phi
clearance or a tracking inefficiency. The current short trunk has only 0.5 mm
radial separation from the fixed long bearing ring. Existing interface and
assembly qualification is not established by that positive difference.

## Ring candidates and pickup constraints

The baseline centres are
`289.5,373.139298,456.778597,540.417895,624.057193 mm`, with populations
`48,60,72,84,96`. The candidate counts use the original source rule,
`12*ceil([pi/atan(45/(2*(R+48)))]/12)`, not circumference divided by chip size.

| Candidate | Centres [mm] | Populations | Modules/disc | Both EC modules | Active outer / occupied outer [mm] | Finite active gap [mm] |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Retained baseline | as above | 48/60/72/84/96 | 360 | 4320 | 672.486 /676.001 | 114.758 |
| Five,90 mm steps | 289.5/379.5/469.5/559.5/649.5 | 48/60/84/96/108 | 396 | 4752 | 697.913 /701.428 | 89.331 |
| **Five,91.5 mm steps** | **289.5/381/472.5/564/655.5** | **48/60/84/96/108** | **396** | **4752** | **703.909 /707.424** | **83.334** |
| Six, old five plus690 | add690 | add108 | 468 | 5616 | 738.390 /741.905 | 48.853 |
| Six, repeat old83.639298 step | add707.696491 | add108 | 468 | 5616 | 756.078 /759.592 | 31.166 |

The recommended five-ring candidate adds 432 sensors and 1.990656 m² of active
silicon across both ends; its endcap channel count at 2 mm is 145,981,440.
Each petal has 33 modules, distributed4/5/7/8/9. All changed positions and
counts belong to a separate candidate identity; old results are preserved.

**INFERENCE, adverse six-ring result:** the inherited outer-ring 6 × 60 mm
pickups bridge from normal position −1.3 mm to the raised sensor backing.
At a new centre690 mm, the ring separation from624.057193 mm is65.942807 mm,
smaller than the 48 mm inner-sensor half-length plus30 mm pickup half-length.
A finite convex-polygon separating-axis check finds **288 positive-area
pickup/old-outer-sensor pairs per disc** at the actual96/108 phi populations.
Their normal intervals overlap; these are real collision candidates, not merely
an overlap of annular plotting bounds. Moving a sixth ring to704 or707.696491
mm removes those particular pairs, but consumes much more service space.

A separate hypothetical12 × 32 mm pickup at u=±10 mm also removes those
690 mm-ring pairs and retains768 mm² total pickup contact area, versus720 mm²
for the old pair. This would amend the cold-module thermal/spreading/mechanical
contract. Equal or larger area does not qualify its heat path. Keep it as an
aggressive alternative, not a silent fix inside the five-ring candidate.

**INFERENCE, sampled finite-plane coverage:** for both five-ring candidates,
straight rays were intersected with the actual oriented active rectangles at
each sensor's datum+0/1.5/3/4.5 mm normal position. All six disc datums and
vertices z0=−150/0/+150 mm were tested with1440 then2880 midpoint phi samples
(25,920 then51,840 rays/candidate). Unioned radial intervals have no sampled
holes in243.5..695.5 mm for the90 mm case, or243.5..701.5 mm for91.5 mm.
The dense-grid minimum margin beyond the latter outer target is1.110666 mm.
These checks omit curvature, beam-pipe interactions, scattering, material,
sensor inefficiency and alignment. They are not a continuous hermeticity proof.

The ray calculation uses, for module radius R, angular difference d and
`f=(z_module-z0)/(z_datum-z0)`, the interval
`[(R-48)/(f*cos(d)), min((R+48)/(f*cos(d)),24/abs(f*sin(d)))]` when positive
and nonempty. Union these intervals and compare with the stated annulus.
This specifies the normal-offset and finite-phi calculation independently of
the candidate's nominal annulus.

## Radial separation versus projective separation

For a diagnostic of paired short/long station datums, project the innermost
long active edge onto the short datum from a point vertex. Using the upstream
inner-ring long face at `z_long-4.95 mm` gives
`gap = 787.243495*(z_short-z0)/(z_long-4.95-z0)-r_short_outer`.
The extreme envelopes can occur at different phi, so this is an annular
projection diagnostic; it is not the complete two-face tracking acceptance.

| Station, short / long datum [mm] | Baseline projected gap,z0=0 [mm] | Five91.5 projected gap,z0=0 [mm] | Five91.5 range,z0=±150 [mm] |
| --- | ---: | ---: | ---: |
| 1335 /1470 | 44.876 | 13.452 | 5.481..19.942 |
| 1534.173415 /1633.208484 | 69.269 | 37.845 | 33.229..41.682 |
| 1863.164246 /1949.635166 | 81.757 | 50.333 | 47.575..52.696 |
| 2237.835637 /2309.997868 | 91.803 | 60.379 | 58.781..61.782 |
| 2645.640721 /2702.228888 | 99.686 | 68.263 | 67.375..69.057 |
| 3080 /3120 | 105.900 | 74.476 | 74.028..74.883 |

Thus the candidate reduces the physical and projective gaps; it does not close
them. Other stations and barrel layers also contribute to a track. A full
finite-surface crossing study is needed before claiming a hit-count or
efficiency benefit. Long-strip positions are unchanged in every calculation.

## Provisional service cross-sections and failed controls

**NODD DESIGN CHOICE, coordinator-supplied hardware hypothesis:** one LV feed
per at most14 physical modules,8 mm finished power-cable diameter; preserve
the two existing optical bundles per barrel half-stave and at least the
ceil(modules/12) endcap optical grouping, with3.6 mm gross diameter. Preserve
one barrel loop/half-stave and allocate two independent loops/endcap petal.
Retain8/12 mm OD bulk feed/return pairs, aggregate at most8 loops/bank, and
round independently per sector. These are not qualified ratings or a claim
that fibre bandwidth follows channel count.

The proposed five-ring candidate has, per signed end,288 barrel half-staves
and72 endcap petals. One end carries504 power feeds,792 optical bundles and
68 bulk cooling pairs (44 barrel+24 endcap). The bare area is44,504.052858 mm².
The largest sectors contain25 barrel half-staves; four others contain22.
The worst final sector therefore contains43 power feeds,68 optical bundles
and6 cooling pairs. At8 mm power OD its bare area is3833.748347 mm², or
4792.185434 mm² with25% spare.

The adverse screen uses50% azimuth,40% packing,25% spare and0.5 mm radial
walls on both sides. Sector capacity is
`0.5*0.4*pi*((r_out-.5)^2-(r_in+.5)^2)/12`.

| Power OD / candidate trunk [mm] | Worst demand including25% [mm²/sector] | Adverse capacity [mm²/sector] | Utilization | Result |
| --- | ---: | ---: | ---: | --- |
| 8 /725..783 | 4792.185 | 4500.646 | 1.06478 | **FAIL** |
| 8 /720..783 | 4792.185 | 4879.208 | 0.98216 | Area PASS; very small remaining margin |
| 8 /718..783 | 4792.185 | 5029.899 | 0.95274 | Area PASS; long-key separation0.5 mm |
| **8 /717..781.5** | **4792.185** | **4982.291** | **0.96184** | **Area PASS; long-key separation2 mm** |
| 8 /715..781.5 | 4792.185 | 5132.354 | 0.93372 | Less compact fallback |
| 10 /710..783,old corridor | 6311.931 | 5628.477 | 1.12143 | **FAIL even before extension** |

The8 mm case needs inner radius at most721.152444 mm with outer783 mm under
this screen; the10 mm case would need inner radius at most700.754055 mm,
which conflicts with the proposed outer modules. These are area inequalities,
not permission to thin a current-carrying conductor or compress installation
allowances. The tight corridor reclaim is8.5 mm relative to the old73 mm
allocation; the31.424 mm active reach gain also consumes existing local
support/board space. Do not call all31.424 mm a recovered cable-corridor width.

An added sixth690 mm ring has39 modules/petal, four optical groups and still
three14-module LV feeds. With two loops/petal its8 mm worst demand plus25%
is4868.526135 mm²/sector: the proposed752..783 mm annulus supplies only
4520.948178 mm² and fails1.07688. The natural707.696491 mm sixth ring needs
the trunk outside its759.591708 mm body;762..783 fails1.60487 under the
nominal75%/50% packing plus25% spare. Both aggressive options therefore need
additional module or service architecture changes.

## Finite handoffs that must accompany a new trunk

The following dimensions are **NODD DESIGN CHOICE proposals**, intended as
explicit interfaces for TrackTech/SoftEng, not as manufactured tolerances.

| Interface and owners | Proposed occupied-space handoff | Constraint and required check |
| --- | --- | --- |
| Endcap module → cold petal,TrackTech | Keep60 mm radial pickups; extend carrier outer radius to710 mm; retain original thicknesses and upstream13.5 mm frame depth | New module occupied outer707.424 mm; pickup contact reaches685.5 mm. Recheck complete solid, thermal and structural geometry. |
| Cold petal → outer frame,TrackTech/SysArch | Outer frame698..715 mm, normal centre−12 mm; outer mounting contacts near704 mm; inner frame unchanged | Frame outer715 leaves2 mm to717 trunk. New contact/load introduction needs mechanical review. No old frame mass or stiffness may be carried over unchanged. |
| Modules → end board,TrackTech | Keep board radius695 mm; move its8 mm normal envelope to centre w=14 mm (10..18 mm) | Board corner705.479 mm clears717 trunk by11.521 mm; bottom clears front fanout9.5 by0.5 mm; top clears new fan start20 by2 mm. Replace old mounts: they would cross the new outer sensor ring. Supports must enter from peripheral lands outside707.424 mm, not through sensors. |
| Two petal loops → manifolds,TrackTech | Inner three rings16 modules; outer two17; four distinct feed/return ports per petal; provisional port radius712 mm | Last inherited fillet requires port radius greater than685.427 mm; old678 mm port yields a negative terminal straight. Keep tubes disjoint; do not duplicate the old28/29 degree port centreline for both circuits. |
| Board/ports → axial trunk,TrackTech/SysArch | Front collection pocket r690..781.5 mm,w20..100 mm; trunk717..781.5 mm | Radial span91.5 mm can accommodate an individual R50+4 mm power turn as a necessary dimension check. Model all cable/pipe turns, connectors and accumulated traffic; conserve payload and use one shared tray. |
| Barrel collector → trunk,TrackTech/SysArch | Extend collector outer radius from750 to781.5 mm, retaining abs(z)1245..1310 mm; finite continuation at trunk entrance | A shifted trunk alone leaves a throat bottleneck. For718..750 the adverse area is2382.793 mm² against3023.783 mm² barrel demand, **FAIL1.26901**. Enlarged joining area must be checked explicitly. |
| Short services → unchanged long hardware,SysArch/TrackTech | Keep short maximum outer781.5 mm | Leaves2 mm to inner bearing ring783.5,2.5 mm to carrier784, and18.5 mm to long barrel collector inner800. This is a proposed reserve, not installation qualification. |

The front pocket is deliberately in front of modules, fanout and the relocated
board. It must not be represented by moving a radial annulus through active
silicon. Its80 mm depth supplies79 mm after two0.5 mm faces: the conservative
radial section at r690 mm has adverse capacity5708.274 mm²/sector. The final
annular join remains the smaller listed area. Declared connectivity and the
actual sequence of bends/joins must still be checked; a favourable volume or
mean cross-section is insufficient.

The first short frame retains its original11.5 mm axial clearance from the
barrel collector. A front pocket ending at datum+100 mm ends at1435 mm for
the first disc; the long barrel collector also ends at1435 mm, but begins at
r800 mm, radially separated from the proposed short envelope. Later pockets
can overlap long-disc z ranges: the2 mm radial separation must therefore hold
for all their passive constituents, not just active sensor corners.

**INFERENCE, energy-only cooling screen:** with200 J/g latent heat and0.35
usable quality rise,3/7 g/s carry210/490 W. The17-module loop at the
coordinator's16/22 W module-heat examples requires3.886/5.343 g/s before
board and rail loss. Thus3 g/s fails;7 g/s can pass an enthalpy inequality.
Pressure drop, dry-out, leakage at the selected operating point and thermal
contact remain unqualified. Fewer readout channels do not by themselves
establish a smaller pipe or a colder sensor.

## Checks performed and required next evidence

Actual work used exact `git show` source at the examined commit, pure-Python
source-model construction, point-to-segment radial minima, convex-polygon
separating-axis intersection checks, finite-plane straight-ray interval unions
at both phi samplings, and independent sector/throat arithmetic. No native
construction, overlap, Geant4, ACTS navigation or tracking result was produced.

Required before selection/integration: independently implement the new source
model; preserve baseline IDs/evidence under distinct candidate identities;
construct complete cold petals, board supports, four-port plumbing and all
finite barrel/endcap joins; count every LV/HV/data/control endpoint; validate
conductor drop/current and optical throughput; audit each cumulative sector
and throat including adverse failures; construct and overlap-check native
DD4hep geometry; verify sensor/readout/axis counts and Gen3 navigation; compare
directional material and finite curved-track crossings at both charges,
multiple vertices and the established pT samples. TrackTech owns module and
service design; SysArch owns shared bounds/handoffs; SoftEng owns their faithful
representation; PhysVal assesses acceptance/performance claims. Identified
humans retain design approval and acceptance authority.
