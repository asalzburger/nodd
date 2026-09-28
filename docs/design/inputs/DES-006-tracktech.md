# DES-006 input — First tracker placement alternatives

- Status: DRAFT; isolated **PROTOTYPE** study, no production authorization.
- Date: 2026-09-18.
- Role: `TrackTech`; AI-assisted technical contribution, not human review.
- Context: [DES-005](../DES-005-tracker-system-plan.md),
  [prior TrackTech input](DES-005-tracker-system-tracktech.md),
  [DES-003 envelope](../DES-003-envelopes.json),
  [ADR-006](../../decisions/ADR-006-global-envelope-and-field-hypotheses.md).
- Human numerical design approvers: none. Final sign-off remains with
  `asalzburger-review`; named review coverage follows DES-005.

## Recommendation and comparison discipline

**NODD DESIGN CHOICE — proposed:** study two complete, symmetric ideal-surface
layouts with the same barrel and outer tracker. Candidate A extends the ODD-like
pixel train downstream; B adds two pixel stations per side and enlarges the
downstream pixel annuli. This separates the high-priority forward question from
barrel-radius optimization. Start with A as the smaller reference and test B for
measurable additional information and redundancy. This is a study priority,
not selection or demonstrated tracking efficiency.

The inherited technology order remains pixels, short strips/strixels and paired
stereo long strips. Neither candidate assigns the whole `|eta| < 4` requirement
to every technology. Far-forward tracks remain in the inner pixel annuli: moving
an outer strip layer outwards cannot increase their radial lever arm.

## Public ODD control extracted this session

**FACT — TT6-F01:** the existing local ODD checkout is at
`c167363f3d4ad1540a577af99071283caf54f3a6`, matching the recorded study snapshot.
Source `SRC-ODD-UPSTREAM` in the [catalogue](../../../reference/manifest.yaml).
The following are exact XML layer parameters, not reconstructed active surfaces.
All lengths in this table are millimetres.

| Technology | Barrel layer `r` | Positive disk `z_offset` | Disk layer `rmin..rmax` |
| --- | --- | --- | --- |
| Pixels | 34, 70, 116, 172 | 620, 720, 840, 980, 1120, 1320, 1520 | 28..186 |
| Short strips | 260, 360, 500, 660 | 1300, 1550, 1850, 2200, 2550, 2950 | 210..715 |
| Long strips | 820, 1020 | 1300, 1600, 1900, 2250, 2600, 3000 | 720..1095 |

Precise locators: `xml/detectors/TrackerPixels.xml`, `PixelLayer0..3` and
`PixelEndcapP0..6`; `TrackerShortStrips.xml`, `ShortStripLayer0..3` and
`ShortStripEndcapP0..5`; `TrackerLongStrips.xml`, `LongStripLayer0..1` and
`LongStripEndcapP0..5`. Each also declares mirrored negative-endcap layers.
`factory/tracker/ODDPixelEndcap_geo.cpp` and `ODDStripEndcap_geo.cpp`, their
`zeff = x_layer.z_offset() - x_det_dim.z()` placement and parent translation,
confirm that the quoted offsets become global disk reference positions.

**FACT — TT6-F02:** barrel construction in `ODDPixelBarrel_geo.cpp` uses module
length, module count and gap to determine stave length; strip construction uses
its own stave/module implementation. XML disk bounds enclose modules and
supports; rings, azimuthal placement, sensors and inactive parts determine
actual active coverage. The table is therefore an auditable ODD placement
control, not an assertion of continuous sensitive cylinders/disks or an
executed DD4hep geometry extraction. The candidate half-lengths and ideal active
disk limits below are new choices even where a reference radius matches ODD.

## Candidate geometry handoff

Every number in this section is **NODD DESIGN CHOICE — proposed**, with no human
numerical approval. Units are mm. Barrel surfaces are centered at `z = 0`;
every positive disk has a reflected negative counterpart. These are active
surface hypotheses of zero thickness for screening. Occupied volumes, module
stagger, supports, service routes and required clearances remain unknown.

The tracker host is `25 <= r <= 1140`, `|z| <= 3150`, following DES-003; the
shared `1140..1240` service reservation is not additional active-layer space.
Retaining ODD's 34 mm first reference radius avoids interpreting the 25 mm host
as an active sensor. Beam-pipe and installation clearance are still unresolved.

| Common component | Radius or radial interval | Axial extent / positive disk positions | Rationale |
| --- | --- | --- | --- |
| Four pixel barrels | 34, 70, 116, 172 | Half-length 550 | Preserve the ODD radial reference pattern while studying forward additions; provisional continuous active length. |
| Four strixel barrels | 260, 360, 500, 660 | Half-length 1200 | Retain ODD radial scales and bridge to the first disks; no module-length fit claim. |
| Two stereo long-strip barrel stations | 820, 1020 | Half-length 1200 | Preserve long outer lever arm and ODD station count; each station represents one physical stereo pair. |
| Six strixel disks per side | 190..700 | 1320, 1630, 1950, 2320, 2670, 3030 | 10 mm radial overlap with A's pixels and 20 mm with the long-strip annuli are hypotheses for transition coverage, not certified assembly overlaps. |
| Six stereo long-strip disks per side | 680..1100 | 1370, 1700, 2020, 2400, 2780, 3070 | Stagger relative to strixels and retain radial leverage; outer 40 mm and downstream 80 mm to host edges are available geometric differences, not closed engineering margins. |

| Candidate | Pixel disks: positive z | Pixel active radial interval | Argument |
| --- | --- | --- | --- |
| A — extended ODD-like | 650, 850, 1100, 1400, 1750, 2100, 2450, 2800, 3070 | 35..200 on all nine disks | Extend precision measurements almost to the host end without a wide forward pixel system. |
| B — forward pixel rich | 650, 850, 1100 | 35..200 | Keep the first three disks identical to A. |
| B — forward pixel rich | 1250, 1400, 1750, 2100, 2450, 2600, 2800, 3070 | 35..320 | Add two stations and improve pixel/strixel overlap and precision coverage at intermediate forward eta. |

B widens the pixel annuli only after the strixel barrel ends at 1200 mm; a
320 mm disk at 650 mm would intersect the ideal 260 mm barrel surface.
The 1250 mm station leaves only 50 mm to that barrel end and requires explicit
module/support/service fit. Pixel/strixel overlapping radial ranges occur on
different z planes; continuous-surface intersection checks do not prove real
modules and supports fit. A and B deliberately retain identical barrel,
strixel-disk and long-strip-disk choices for controlled comparisons.

## Forward consequences and cost proxies

**INFERENCE — TT6-I01:** for a straight ray emitted on axis,
`r(z) = |z - z_vertex| / sinh(|eta|)` on the outgoing side. Applying this to
the proposed tables, at eta 4 and `z_vertex = 0`, A crosses seven pixel disks
and B nine. At `z_vertex = +150 mm` towards the positive endcap, the counts are
six and eight; the last pixel radius is 106.999 mm at z 3070. For the origin it
is 112.496 mm. Reflection gives the opposite-side counterpart. The `±150 mm`
vertices are explicit stress fixtures, not a measured beamspot distribution or
its tails. Eta 4 is the limiting diagnostic edge of the open `|eta| < 4` target.

The useful radial span in this limiting example is approximately 61.195 mm for
A and 66.691 mm for B at the positive stress vertex. B adds information but
does not acquire the metre-scale barrel lever arm. These calculations ignore
curvature, module masks, scattering and response, and establish neither a
resolution target nor tracking efficiency. Full scans must retain transition
minima rather than reporting only the endpoint. PhysVal's independent ideal-ray
scan finds regions with only three pixel stations in both candidates near the
barrel/endcap transition: approximately eta 1.880–1.894 at the origin and
1.581–1.647 at the positive stress vertex. A has another three-pixel interval
near 1.952–1.965 for that stress vertex, removed by B's added station. Total
station redundancy includes strixels/long strips and must not conceal reduced
pixel seeding information. Revisit first-disk width/position and barrel overlap
once module and support constraints are available; no three-pixel acceptance
threshold has been approved.

**INFERENCE — TT6-I02:** summing `2*pi*(r_max²-r_min²)` over the pixel disks
gives ideal two-sided annular areas 2.192675 m² for A and 5.816502 m² for B,
approximately a factor 2.653. These are sensitive-surface area proxies, not
wafer area, installed module count, channel count, cost or power. Actual tiling,
overlaps, guard rings and readout layouts are missing. B's additional area may
increase power, cooling, service cross-sections and material even in eta regions
where it adds no useful hit; per-track material scaling alone cannot close this
system-level cost.

## Measurement and material scenarios to scrutinize

**NODD DESIGN CHOICE — proposed screening assumptions:** use a 50 micrometre
digital pixel pitch as a response control, giving `50/sqrt(12)` micrometres in
each measured coordinate under uniform intra-pixel impact and binary readout.
This is not measured RD53 module precision. A 20 micrometre fine strixel
coordinate and `5 mm/sqrt(12)` coarse coordinate assume 5 mm physical segments;
the proposed segmentation, readout feasibility and occupancy have no qualified
hardware basis yet. Do not infer them from ODD's readout name.

For long strips, equal independent 20 micrometre strip uncertainties on
symmetric axes at `+/-0.020 rad` give a collapsed pair's fine-coordinate sigma
`20/(sqrt(2)*cos(0.020))` micrometres and coarse-coordinate sigma
`20/(sqrt(2)*sin(0.020))` micrometres. This is an **INFERENCE** from the stated
**NODD DESIGN CHOICE** response/angle scenario. It represents two scalar strip
measurements grouped into one station; it must not be counted as two independent
space points. Pair separation, alignment, unequal response, correlation,
ambiguity and loss of one side are omitted. The paired material is counted once.

**NODD DESIGN CHOICE — sensitivity fixtures:** provisional normal-incidence
material values of 1% X0 per pixel surface, 1.5% per strixel surface and 2% per
collapsed long-strip pair, each tested at half/double scale, can expose ranking
sensitivity. These are rounded hypotheses, not sourced complete layer budgets,
uncertainty bounds or a material sign-off. Any nominal local support allowance
within them is unspecified. Beam pipe, distributed services, cooling manifolds,
end structures and inactive support material remain unclosed and cannot be
silently counted as zero in a physical performance claim. Impact-parameter
estimates without beam-pipe material are particularly optimistic. Replace each
allowance with an explicit owned constituent ledger as interfaces arrive.

## Strengths, weaknesses and engineering gates

| Topic | A | B |
| --- | --- | --- |
| Primary value | Small change from ODD radial architecture with a long downstream pixel train. | More far-forward station redundancy and broader forward pixel/strixel overlap. |
| Principal cost | A new long support/service system for small-radius pixel disks is still required. | Roughly 2.65 times A's ideal pixel-disk area, plus two stations per side; potentially greater service and thermal load. |
| Likely limiting question | Does the short forward radial lever arm and limited redundancy meet actual resolution/efficiency targets? | Is the additional measurement information useful enough to offset added material, power and construction complexity? |
| Shared unresolved weakness | Ideal surfaces with unqualified module tiling, beam-pipe clearance, services, realistic material, beamspot and field; reduced pixel redundancy at the barrel/endcap transition. | Same unresolved interfaces and one shared low-pixel-count transition; added pixels cannot repair an impossible beam-pipe aperture or replace a validated field map. |

The existing [pixel issue #7](https://github.com/asalzburger/nodd/issues/7)
and [PR #8](https://github.com/asalzburger/nodd/pull/8) were inspected on
2026-09-18: both remain open; PR head
`d237f146b578915cc032b30efa50044cf6344d5f`. DES-001 compares A1/A2/B4 RD53i
assemblies and leaves layer placement out of scope. Consume its active matrices,
physical outlines, excluded mounting/cooling interfaces and constituent ledger;
do not duplicate or select its module design here. Its 0.5884% X0 partial local
path is not the 1% scenario above and cannot supply a complete pixel layer.

Short-strip and long-strip module designs, support hierarchy, cooling and
power/data distributions have not supplied qualified interfaces. Ideal annuli
must be replaced with tiled module models before claiming hermeticity. Check
radial corners, disk/stave clearances, flex/bond exits, support joints,
installation/removal sequence and material at technology transitions.

Timing remains an unresolved orthogonal study. First investigate the outermost
tracker station as directed in DES-003; do not label either ordinary spatial
strip station as precision timing. A timing response and its extra material,
readout, power and forward coverage must be supplied before a third candidate is
worth ranking. Preserve no-timing, timing-material-with-time-disabled and full
timing-response controls.

## Priority requests to the team

1. PhysVal: run the declared ray/parametric screens, including conditional
   vertices and transitions, and report fit failures and station counts by
   technology. Set real efficiency/resolution targets before selecting A or B.
2. SysArch: resolve beam-pipe profile/clearance and assign disk support and service
   ownership. Neither the 35 mm aperture nor the end/outer geometric differences
   can become accepted margins without those inputs.
3. SoftEng: audit IdRes disk, material and stereo support. Preserve effective
   station versus physical sensor identities; distinguish an installed program
   from a validated representation. Expand to module-aware ACTS propagation
   once response and geometry contracts are ready.
4. TrackTech/component owners: obtain DES-001 outlines and masks; begin strixel
   and stereo module proposals and the associated power/cooling/service ledger.
   Compare B's extra area with actual loads before recommending its adoption.
5. Jointly: replace the stress vertices with an agreed luminous distribution,
   uniform-field controls with pinned magnet configurations, and illustrative
   material with component-informed inventories. These missing inputs block
   final selection, not the bounded prototype studies authorized now.

No detector construction, overlap test, module-aware coverage or full simulation
was performed for this input. Source extraction and the explicit straight-ray
and annular-area arithmetic above were executed. Parent DES-006 evidence records
the team's executable prototype checks and any further performance estimates.
