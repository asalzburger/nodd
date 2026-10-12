# Long-strip sandwich screen — PROTOTYPE

[DES-008](../../docs/design/DES-008-long-strip-modules.md) governs this isolated
analytical comparison. It is not wired into production detector geometry.
The convex polygon helpers originate in PR21 / DES-007 at
`17d84a4c92916a49929db3c5e75684e51bf613b7`; they are copied locally to keep this
study independent of that unmerged branch. The stereo transforms, same-module
pair coverage, row masks, 3D body checks and cooling/gap scans are added here.

Requires Python 3.10+ and NumPy; Matplotlib only for the figure. No DD4hep,
Geant4 or ACTS installation is used. From the repository root:

```sh
python3 -B -m unittest discover -s tools/long_strip -p 'test_*.py' -v
python3 -B tools/long_strip/study.py --refined --sweeps \
  --figure docs/design/figures/DES-008-rings.svg
```

The local study used `reference/cache/envelope-venv/bin/python` and
`MPLCONFIGDIR=/tmp/nodd-long-strip-mpl` for NumPy/Matplotlib. This ignored
local environment is optional, not a dependency shipped with the repository.
`--input` and `--output` select alternate configuration/result paths. The tool
writes the requested output; use a fresh path for exploratory scenarios and
preserve retained evidence when intentionally replacing a report.

All dimensions are mm, angles radians. Inputs are unsigned scenarios with
rationale in DES-008 C01–C09. `separation` means sensor mid-plane separation;
free silicon-face gap is separation minus one sensor thickness. Ring centre
and sensor rotations are independent. Active polygons are physically rotated
about each module centre; two-row candidates remove a central dead band from
each sensor separately. Die guard space is outside the active polygon.

A counted pair requires the same ray in both sensors of the same module. Normal
projection and finite-z rays are separate results. The fast nearest-three-module
search checks an angular containment bound and is tested against independent
full enumeration in global coordinates. Body collisions use convex SAT and
intersecting normal intervals. Occupied boxes are conservative screening
fixtures, not assemblies of real solids. The cooling test subtracts an explicit
one-dimensional stack, not a thermal or hydraulic simulation.

The retained run has 250×720 and 500×1440 polar grids, area weights proportional
to radius; boundary epsilon 1e-9; no random numbers. Scans use 100×360 and do not
establish fine-grained coverage. The JSON records inputs, hashes, Git revision
and dirty paths, package versions and numerical tolerance. Counts and body
intersections are deterministic; Git metadata will differ on replay.

Tests cover transforms, containment, independent full-enumeration pairing,
false cross-module pairs, 3D collision controls, cooling failure, covariance
inversion, singular zero stereo and invalid input. No continuous coverage proof,
barrel tiling, curved tracks, detailed readout masks or full services are modeled.

## PR13 A/C1 compatibility

The current default uses the shared **710–1100 mm** disk target and first-disk
**z=1430 mm** from PR13 A/C1, pinned in `pr13-layouts.json` with the full
source revision/file hash and signed layer identities. The earlier 700 mm /
1320 mm fixture remains in Git at `68932692fc61bb25d21e55a915a12eb929b2b316`.
This is a geometry-only extraction of a DRAFT proposal, not a merged dependency.

```sh
python3 -B tools/long_strip/compatibility.py
```

This compares five/six square-module rings at every |z| in both proposals on the
same two grids, preserving failed controls. It also tests points directly on
both target-radius circles with full module enumeration. Negative disks reflect the complete
module stack and vertex; the ray factors are identical and tested explicitly.
The script fails if either layout's annulus/first disk drifts from the study, if
the A/C1 positions differ, or if six rings fail sampled pair/body checks. Source
field equality and the original-file hash were verified against the fetched
PR13 revision. Running this tool needs no other branch or network access.

The [compatibility report](../../docs/validation/DES-008-layout-compatibility.md)
distinguishes target-radius compatibility from actual silicon/body extensions.
Axial interface estimates use PR21's 11 mm short-strip trial depth and PR13's
ideal barrel end/host boundary; full carriers and barrel end structures remain
unknown. A nominal 10 mm band separation is not a free radial service corridor.
