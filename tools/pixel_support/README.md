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
