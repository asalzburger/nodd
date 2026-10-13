# DES-030 — Custom ECAL edge sensors and optimized endcap

- Status: **DRAFT**
- Type: **PROTOTYPE**
- Date: 2026-10-13
- Parent: DES028/DES029; no production integration
- Human instruction: design custom edge sensors, update the prototype layout,
  compare ODD, first nODD, optimized squares and squares with edge sensors.
- Human clarification: extend optimized layouts toward |eta|=4 as a prototype target.
- Engineering approval: pending. Implementation permission is not design sign-off.
- Aperture/carrier decision: [ADR008](../decisions/ADR-008-prototype-ecal-forward-aperture.md)

## Scope and provenance

**FACT:** Existing ODD ECAL sources at c167363 use continuous sensitive sheets;
DES029's actual first cassette packer gives31.85% active absorber-plate area.
Those historical geometries/evidence remain unchanged. Their apertures do not
provide front-face coverage to|eta|4. **INFERENCE:** at z=3950mm, that direction
reaches r=3950/sinh(4), approximately144.75mm.

**FACT / architectural precedent:** SRC-CMS-HGCAL-PARTIAL-2025, latest inspected
arXiv2510.17280v4 §2/Figs1–3, describes manufactured partial sensors with
dedicated dicing/HV/guard structures. SRC-CALICE-SIW-2022 PDF4/6 describes
compact sensor boards, quarter endcaps and shared interfaces. Their geometries
and operating modes are not transferred as approved nODD parameters.

All new parameters in `tools/calorimeter_hardware/edge_sensors.json` are unsigned
**NODD DESIGN CHOICE** proposals. Retain90mm sensor blanks,0.5mm silicon,
5.5mm nominal pad pitch,1.9mm tungsten,48 layers and10.9mm layer pitch from
DES028/029. Preserve the outer sixteen-sided ECAL envelope and front z.
Replace sixteen narrow cassette-packing boundaries by four physical quadrants;
logical/physical carrier IDs remain explicit.

The new aperture is a90mm-apothem square, surrounded by5mm inner support;
its supported corner reaches134.35mm, below the eta4 front radius. This is a
prototype aperture contract requiring beam-pipe, shielding and forward-service
integration review. It is not a claim that the present machine interface fits.
Five-mm side reserves and a25mm outer service band retain explicit dead space.

## Custom sensor and electrode design

The complete sensor blank, matching PCB, active inset and pad mask are separate
polygons. Boundary outlines are generated as convex intersections of90mm blank
windows with the reserved carrier face. These specify **new manufactured masks
and dicing profiles**; standard silicon sensors are not clipped in the simulation.
Full squares keep their inherited1mm guard. New boundary sensors reserve2mm
along all edges for dicing/HV termination, subject to electrical qualification.
Triangular profiles contain acute corners; tip bevel/radius, dicing damage and
guard termination require process review. The polygon proposal is not a claim
of established wafer yield or breakdown voltage.

Reject less than1200mm2 sensor area, less than20mm minimum Feret width, or
boards that cannot hold the necessary10×12mm readout packages with1mm clearance.
Every retained profile fits inside its90mm blank and hence a6-inch wafer.
Record profile count, family, outline and discarded remainders; mask/procurement
complexity is a result, not hidden by calling all partials one sensor.

Clip the nominal pad lattice to the **active** mask to form custom electrode
outlines. Merge pads smaller than20% of a nominal pad with connected neighbours;
record channel mapping and the representative point inside each electrode.
Some merged pads are nonrectangular. A dedicated segmentation returns these
points and merged IDs; it must not return positions outside the physical mask.
This is geometry/readout topology, not an electric-field or charge-sharing model.
Module IDs use the linearized grid address, preserving square sensor IDs when
edge variants are added. Closed boundaries that coincide with a grid edge map
to an existing interior electrode; no positions outside the active mask are
returned. Tiny-pad merging preserves active area and connected electrode groups.

## Hardware and validation boundaries

PCBs and package/thermal-contact footprints remain behind the sensor face.
The carrier owns absorber/cooling material once per layer; readout interfaces
are shared at its peripheral service zone. Continuous-power/channel and bias
hypotheses remain those of DES028. A3mm copper cooling plate can contain2mm
outer-diameter Ti/water runs; preserve material displaced by the channels.
External manifold/connector details, hydraulic flow/thermal analysis, stiffness,
HV breakdown, wafer yield and radiation response remain unqualified.
The10mm DES029 rear cover is retained. Straight cooling runs account for tube,
water and displaced copper; their external hydraulic connections are not
implemented. The new3mm plate is a layout proposal, not thermal qualification.

Shared interface capacity is a proposed8192 logical channels/interface at the
inherited2W interface hypothesis. Continuous ASIC power counts every channel of
every installed64-channel package, including unbonded channels. No unverified
power saving is credited to those channels; bias current counts sensor pads.

Publish deterministic square-only and square-plus-edge layouts, native geometry
checks, mass/material/channel/power ledgers and eta/phi active-layer counts.
Use the same new aperture, carrier, pitch and reservations for the two optimized
panels, isolating the contribution of custom edge sensors. Show historical
aperture/size differences and denominator definitions on the SVG.
High active area does not mean100% efficiency or an absence of narrow cracks.

## Delivered layouts

| Single layer, one quadrant | Compact squares | Squares + edge sensors |
| --- | ---: | ---: |
| Sensors | 423 | 462 (39 custom) |
| Logical pad channels | 108288 | 114813 |
| ASIC packages | 1692 | 1812 |
| Unbonded powered ASIC channels | 0 | 1155 |
| Nominal face active fraction | 83.47% | 88.12% |

There are22 distinct oriented edge profiles: trapezoidal, chamfered and
triangular variants, with6 small/narrow remainder candidates rejected. The
catalogue records every outline, guard, PCB, channel count and package count.
The phase optimizer enumerates0/2/4/6mm equal x/y offsets, prioritizes eta4
front-plane azimuth coverage, then active area; it selects0mm. This is an
optimization within that declared search/family, not a global packing optimum.

![Four requested ECAL packing stages](figures/DES-030/four-stage-coverage.svg)

Historical ODD and nODD use their own dimensions and denominators. C/D retain
the same new envelope, aperture and reservations; their4.65 percentage-point
difference isolates edge sensors. Their denominator includes support/services:
outer sixteen-sided polygon minus the90mm-apothem square aperture. The separate
eta4 fiducial-face denominator subtracts a144.742mm-radius disc and gives
83.49%/88.15%. These area fractions are not particle efficiencies.

The360 azimuth samples at eta4 have43.58 active layers on average;95.56% cross
at least one layer and80% cross at least40 of48 layers in both optimized masks.
Some rays along seams have zero crossings. The improvement at the inner edge
comes from the aperture/carrier/grid change; these custom edge sensors recover
the outer perimeter. No layer staggering or uniform eta4 acceptance is claimed.

[Profile catalogue](inputs/DES-030-edge-profiles.json),
[directional masks](../validation/DES-030/directional-coverage.json) and
[validation report](../validation/DES-030/results.md) retain exact inputs,
coverage limits and the completed native checks.
