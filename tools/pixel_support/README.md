# Pixel support and cooling screening

Isolated **PROTOTYPE** for [DES-002](../../docs/design/DES-002-pixel-barrel-support-cooling.md).
No detector generation or production integration. Python plus the repository's
existing NumPy (finite-box test) and Matplotlib (drawings) are required.

```sh
python3 -B tools/pixel_support/screen.py --output docs/validation/DES-002/screening.json
MPLCONFIGDIR=/tmp/nodd-des002-mpl python3 -B tools/pixel_support/draw.py
python3 -B -m unittest discover -s tools/pixel_support -p 'test_*.py' -v
```

`inputs.json` centralizes proposed dimensions, property assumptions and the exact
baseline geometry hash. Review the baseline hash, family/grouping assumptions,
measured module mass and power before rerunning for new shapes. The program
refuses stale identity, mixed-family staves or changed pixel tilt/z-staggering.
Results record input/script hashes and Python version. Drawings are dimensioned
cross-sections and labelled longitudinal routing concepts, exported as PNG/PDF/SVG.
Their file and source hashes are recorded in the retained artifact manifest.

This is an energy balance, simple beam and material screen. It does not solve
boiling, pressure drop, laminate shear/torsion, global supports or thermal runaway.
The zero-clearance cross-section test uses all82 repeated stave columns; shared
ribs, joints, tolerances and end routing need separate full geometry checks.
Never interpret nominal heat-capacity or static-sag targets as engineering approval.

## Candidate A, sensor inward / support outward

```sh
MPLCONFIGDIR=/tmp/nodd-des002-mpl python3 -B tools/pixel_support/outward.py
```

This separate generator writes four complete barrel x–y sections and a combined
view in PNG/PDF/SVG, plus a nominal-clearance screen and artifact manifest, to
`docs/validation/DES-002/outward-A/`. `--output PATH` selects another directory.
It retains the earlier inward-support evidence. The shared stack and exact
baseline come from `inputs.json`; `outward.json` selects z = +25 mm and the
numerical overlap tolerance. The tolerance is not a manufacturing allowance.

Sections use actual body and active-patch intersections with that plane. They
refuse a cut missing modules/active silicon, a changed baseline checksum or
nonuniform/tilted stave columns. The clearance screen uses two enclosing boxes
per stave (full-width thin plate, narrow spine), checks all other module and
support boxes, and computes Euclidean polygon gaps and corner-based outer radii.
Tube circles are contained within the spine. Own-module and internal-layer
contacts are intentional. No global frame, bearings, end joints or flex is tested.
Review the assembly report when changing sensor/module shapes or orientation;
never carry the previous fit or service handoff forward automatically.

## Candidate A with mounting and stiffening rings

```sh
MPLCONFIGDIR=/tmp/nodd-des002-mpl python3 -B tools/pixel_support/mounting.py
```

`mounting.json` selects six proposed ring centres per barrel, the axial locator,
nominal ring separation and bearing-foot width. Ring radial/axial sizes and CFRP
properties reuse `inputs.json`. The output directory defaults to
`docs/validation/DES-002/outward-A-mounted/`; `--output PATH` overrides it.
Five x–y sections through a ring and one combined |r|–z projection are exported
in PNG/PDF/SVG, alongside numerical results and a producer/artifact hash manifest.
Earlier inward and between-ring outward evidence remains unchanged.

Ring/body and ring/service checks use conservative radial–axial projections;
feet are screened against all module bodies, other feet/staves, other rings,
existing support reservations and routes. Curved feet end on the inner ring
surface; their bounding boxes are used conservatively, with intentional contact
at their own ring excluded. New rings are treated as continuous annuli for
clearance and mass: a segmented assembly's joint hardware remains unmodeled.
Tests include a ring deliberately moved into the service bay and a numerical
cross-check of the curved-foot volume. No global cage stiffness follows from
the ring count or a passing nominal clearance screen.

## Cumulative cable bundles and sector cooling

```sh
MPLCONFIGDIR=/tmp/nodd-des002-mpl python3 -B tools/pixel_support/services.py
```

`services.json` defines the separate additive service proposal. The generator
reuses the pinned baseline, mounting geometry and DES-010 cable footprint/scenario
inputs. It writes `docs/validation/DES-002/outward-A-services/` (or `--output PATH`):
five x–y sections, |r|–z, cable accumulation and dedicated radial extraction views
in PNG/PDF/SVG; a numerical screen; compressed machine-readable routing records;
and hashes of all producers and artifacts. Previous evidence is preserved.

Module pickups grow each half-stave's electrical bundle. Twelve phi sectors at
each end collect the actual stave populations into supply/exhaust pairs without
changing the two local counterflow evaporators per stave. Radial/axial capacity
is checked sector by sector. The reference scenario fits these screens; adverse
scenarios fail and are retained explicitly. The exit screen is barrel-only;
downstream barrel plus endcap traffic remains owned by DES-010.

The export separates cable outer-footprint volume from material composition.
Composition/mass are null pending a cable bill of materials. Packing and spare
space are not solid material. Transport-tube mass is a provisional wall/length
screen; branch gathering uses idealized centrelines and the drawing omits bends.
It is not a complete DD4hep solid model, pressure design or overlap proof. A
future implementation must partition/union turn volumes, normalize constituent
mass, add flex/connectors/manifold/clip inventory and run full material scans.
