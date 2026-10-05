# DES-015 — Preliminary combined pixel detector

- Status: DRAFT — human-selected preliminary baseline; isolated PROTOTYPE implementation.
- Created: 2026-10-01.
- Inputs: [DES-012](DES-012-dd4hep-pixel-barrels.md),
  [DES-013](DES-013-pixel-barrel-z-coverage.md),
  [DES-014](DES-014-pixel-endcap-support.md), issue [#7](https://github.com/asalzburger/nodd/issues/7).

On 2026-10-01 the human maintainer requested: “assume the pixel barrel baseline +
the design of PR #36 - and make this a preliminary baseline. Make the corresponding
dd4hep and nodehammer implementations out of it.” This selects DES014 proposal B
alongside the PR34/35 barrel and authorizes this combined implementation. It does
not supply formal engineering sign-off or acceptance. The original pinned layouts,
PR36 screening evidence and production ODD remain unchanged.

## Implementation contract, recorded before code

| ID | Classification | Choice and consequences |
| --- | --- | --- |
| PD-C01 | NODD DESIGN CHOICE | Preserve the complete current barrel export. Add 18 identical-pattern discs using DES014 B heights, faces and first-disc shift. Preserve endcap x/y, active rectangles, occupied bounds and original module/patch identifiers. Endcap modules retain their original radial periphery; the barrel-only slim-z shape is not applied to them. |
| PD-C02 | NODD DESIGN CHOICE | Reuse the DES012 material and physical module stack. Local module +w points from silicon toward its support, hence opposite the selected mounting face. Flip local v with w where required for a proper rotation. Transform chip offsets as well, preserving their global x/y. This explicitly orients ASICs and contact shims toward the plate. |
| PD-C03 | NODD DESIGN CHOICE | Resolve full annulus plus three rectangular tongues into disjoint solids. Retain 6.3 mm plate, 0.15 mm faces, 16×8 mm raised graphite feet and 0.45 mm pickup stacks. Internal graphite inserts, saddle cuts and skin contact windows use inventory-normalized effective materials: their manufactured routes remain unresolved. Full-ring Ti/CO2 tori represent the summed ten half-ring evaporators; they do not assert hydraulic connectivity. Radial legs and bend inventory remain effective, not swept pipes. |
| PD-C04 | NODD DESIGN CHOICE | Preserve the PR36 per-disc constituent inventory, with foam displacement, liquid CO2, glue, inserts, clips and hardware allowances itemized. Local flex and external bend allowances use an effective annular cell after the module envelope, inside the collector reservation. This relocates material for preliminary transport; it does not validate the two-face flex artwork or thermal conduction. The remaining core inventory is homogenized around explicit evaporators. Effective compositions must normalize by volume then convert to mass fractions. Cable fractions remain configurable. |
| PD-C05 | NODD DESIGN CHOICE | Three 8×8 mm box-rail envelopes follow the carrier curvature (annular-sector walls, nominal radial limits unchanged). Interrupt rails across each tongue's axial interval to represent unresolved coupling pockets. Partition flanges at the shell inner radius and rails at flange faces to avoid counting intersecting solids twice. Record the resulting mass difference from PR36's additive carrier estimate. Couplings are Ti-equivalent mass allowances, not machined cone/slot hardware. |
| PD-C06 | NODD DESIGN CHOICE | External collector/trunk services are explicit effective transport cells in DES010 reservations. Reserve the three 30-degree mounting sectors. They represent reference inventory only; no claim of fixed-sector redistribution, fitted connectors or conservative/stress capacity. The last disc uses a separately labelled adapter/bypass. Maintain the PR36 failed thermal and conservative/stress service screens as unresolved engineering limits. |
| PD-C07 | NODD DESIGN CHOICE | Separate subsystem IDs: barrel 1 unchanged, negative endcap 2, positive endcap 3. Endcap readout uses system:5,layer:4,stave:5,module:16,sensor:16,x:-9,y:-9, with disc index 1..9, stave=phi column, original module/patch IDs and 50 µm pitch. These are stable simulation identifiers, not nodehammer's internal indices. |
| PD-C08 | NODD DESIGN CHOICE | Standalone world half-size 700×700×3400 mm encloses the selected pixel services. No beam pipe, strips, magnet or production-detector integration is implied. Reuse numerical tolerances: ROOT overlap 1e-5 mm, sensitive transform 1e-7 mm, relative inventory 1e-6. Deterministic ray settings are test parameters, not layout constraints. |

The implementation is intended to support geometry/material and subsequent
Geant4 learning. A successful build or overlap check cannot resolve the failed
thermal screen, qualify the carrier, or replace an ACTS coverage re-evaluation
of the shifted endcap sensors. Public source facts remain those catalogued in
DES012 and [DES014's literature dossier](inputs/DES-014-literature.md); this
document adds implementation choices, not new experimentally established facts.

## Validation and use

Commands, actual results, inventory differences and limitations are retained in
[the implementation report](../validation/DES-015/results.md).

## Construction-driven service interface amendment

**PD-C09 — NODD DESIGN CHOICE, 2026-10-01:** the first native construction
exposed trunk/flange intersections at |z|609..611 and 3134..3136 mm (12 overlaps).
Keep the carrier/flange dimensions. Partition the effective trunk at each flange
face and narrow those 2 mm sections from r192..231.7 to r192..222 mm. Preserve
all transported constituent volumes per unit length. This is a material-model
neck, without manufactured bends. Recheck its bare footprint and reference
packing utilization; a failed packing screen stays unresolved, even if the
homogeneous material fits the available volume. No sensor positions or numerical
tolerances change. The corrected local geometry must be tested again.

**PD-C10 — NODD DESIGN CHOICE:** export `tracker_region_rmax=680 mm` and
`tracker_region_zmax=3300 mm`, derived from the rear-service envelope, for DDSim's
standard MC-truth particle handler. They bound this standalone pixel assembly,
not a reconstruction acceptance region or the future full tracker. This closes
an initialization failure from missing constants; the handler is not disabled.
No events, field-transport result or hit-efficiency claim follows from an
initialization-only smoke test.

## Issue #38: whole-millimetre disc datums

**PD-C11 — NODD DESIGN CHOICE, 2026-10-05:** in response to
[the axial-position review](https://github.com/asalzburger/nodd/issues/38#issuecomment-5991197165),
use positive plate datums **615, 795, 1046, 1333, 1645, 1977, 2328, 2692,
3070 mm**, with exact reflection on the negative end. These are the reviewer's
specified positions, not a rounding prescription applied to the old table.
The first datum replaces the old 611.7 + 3.5 mm expression; do not add that shift
a second time. Local support heights, sensor offsets, x/y placement, materials,
module/chip counts and identifiers retain their DES014/015 definitions.

The explicit list is owned by `tools/pixel_endcap_support/inputs.json`; the
combined compact, carrier interfaces and collectors consume the same values.
Frozen DES013/014/015 study artifacts remain historical controls. New validation
belongs in `docs/validation/DES-015/issue38-disc-positions/`.
This amends the human-selected isolated prototype; DRAFT and engineering limits
remain. The comment and this task authorize the amendment, without supplying
formal design acceptance.

Future disc-spacing searches emit integer millimetres: floor proposed positions
and check ordering and service clearance after quantization. A feasibility lower
bound is first moved to the next integer millimetre so flooring cannot place a
disc below that bound. Do not reuse sub-millimetre optimizer outputs as geometry
or reinterpret sensor/support thicknesses as whole-millimetre quantities.
