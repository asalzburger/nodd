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
