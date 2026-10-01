# DES015 — Preliminary combined pixel implementation

The selected PR34/35 barrel and PR36 proposal B are implemented as an isolated
DD4hep compact and portable nodehammer projects. [DES015](../../design/DES-015-preliminary-pixel-detector.md)
records the human selection, material approximations and construction amendments.
No formal design sign-off or engineering acceptance is inferred.

## Baseline and observed checks

| Quantity | Barrel | Both endcaps | Combined |
| --- | ---: | ---: | ---: |
| Layers / discs | 4 | 18 | 22 |
| Modules | 3050 | 2016 | 5066 |
| Active chip patches | 6794 | 8064 | 14858 |

The original barrel export is compared entity by entity, including materials and
IDs. Endcap x/y, chip bounds and identifiers are compared to the pinned source;
z and support-facing normals are independently checked against DES014's formulas.
The silicon faces away from its local support on both sides of each plate.
Endcap module periphery remains radial; barrel slim-z orientation is not reused.

Native construction passed with zero overlaps at **1e-5 mm** tolerance. All
14,858 sensitive transforms and packed IDs matched; 74,290 pixel-cell centre
checks passed. Ninety-three deterministic ROOT rays exercised all 22 planes from
three luminous origins plus one directed ray per endcap disc. Rays are navigation
and directional-material checks, not a hermeticity measurement. Maximum centre
residual was below 5e-13 mm. All six CTests passed, including both ROOT colour
export/reopen checks and source-based tests.

Nodehammer imported 91,488 nodes with no warnings or errors. All physical
placements, materials, sensitive tags and transforms passed the NHB round trip.
Full, sensitive, barrel, stave, positive-endcap, P1-disc and single-endcap-module
projects were packed and their rendered inventories and GLB units audited.
No interactive GUI usability claim is inferred from these headless checks.

DDSim/Geant4 11.4.2 converted the geometry and populated 14,858 sensitive paths,
configured all three sensitive detector systems and initialized FTFP_BERT.
**Zero events were transported.** The compact defines no magnetic field. This
establishes an initialization starting point for the requested Geant4 follow-up,
not hit response, particle transport or physics-list qualification.

## Effective materials and engineering limits

Each disc preserves PR36's non-air constituent inventory: **594.243189 g** before
adding explicit air in effective packing spaces. The physical sensor/ASIC/module
stack is additional; PR36's separate 4 g module mechanical-load proxy is not added
on top of explicit DD4hep components. Carrier mass changes slightly because rails,
flanges and tongues are partitioned into disjoint solids instead of summing
intersecting bounding volumes. `summary.json` retains native masses by subsystem
and role; `service-accounting.json` records material allocations and service cells.

These representations are deliberately preliminary:

- Thermal inserts, saddle cuts and edge closeouts are homogenized in the plate;
  visible Ti/CO2 tori displace that core. Tori preserve summed half-ring length,
  without asserting hydraulic continuity or manufactured bends.
- Pickup graphite, cradle/films and raised feet are explicit. Skin windows and
  cradle contact cutouts are volume-normalized effective mixtures. Their material
  representation is unsuitable for validating thermal conduction.
- Local flexes, bend allowances and clip/coupling mass allowances are collected in
  a labelled effective annulus at w=8..10 mm. It does not claim routed two-face
  flex artwork. Cable composition remains configurable.
- External collector, trunk, last-disc adapter/bypass and rear-turn cells carry
  explicit reference cable/Ti/liquid inventories. They smear route locations and
  fixed-sector redistribution, including the 2 mm collector/trunk boundary space.
  They are material approximations, not continuous swept cables or pipes.
- The first native check found 12 trunk/flange overlaps. Keeping the flanges and
  narrowing the effective trunk to r192..222 mm across their 2 mm thickness
  removes these intersections. At reference 50% packing, the front neck uses
  **74.4%** of capacity and the rear neck **131.0%**: the rear service interface
  remains **FAILED**. No numerical tolerance was relaxed to obtain zero overlaps.
- PR36's stress thermal failure and conservative/stress trunk failures remain.
  No FEA qualification, ACTS conversion or coverage re-evaluation is claimed.

Full axial service material is included for the first time, up to |z|3300 mm and
r680 mm. Its substantial mass must not be compared with the former barrel-only
or local-disc mass without matching this scope. Full-liquid CO2 is a mass bound;
real two-phase density and detailed harness composition remain configurable inputs.

## Reproduction and retained evidence

Follow [the repeatable workflow](../../../tools/pixel_detector_dd4hep/README.md).
`refresh.py --geant4-init` builds, runs CTest, exports ROOT and portable display
projects, then initializes Geant4 without events. `report.py` retains the reports.
Run the Spack preflight first; the registry fingerprints changed, but actual
DD4hep 1.38 / ROOT 6.40.04 / Geant4 11.4.2 capabilities were verified here.

The evidence bundle records code revision, source/configuration hashes, commands,
versions and tolerances. `native.json` contains actual ROOT navigation/material
segments. `nodehammer.json` includes binary/source provenance and every view's
mesh/unit audits. `workflow.json` records command outcomes, log hashes and the
Geant4 initialization result. The source SHA pins leave PR35/36 historical
artifacts unchanged. `artifacts.json` hashes the retained JSON bundle.

Two tooling failures were diagnosed without weakening checks: the pinned GLB
export rounded long translations during float32 cm-to-m multiplication (maximum
0.143 µm); the workflow verifies that exact operation, rescales JSON translations
in double precision and preserves mesh bytes. On macOS the `ddsim` shebang loses
the dynamic-library path; invoking its script with the active Python fixes plugin
loading. Missing tracker truth-envelope constants were added explicitly in the
compact; the standard particle handler was not disabled.
