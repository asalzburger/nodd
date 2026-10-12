# DES-024 native implementation checks

- Date: 2026-10-08
- Scope: DRAFT user-authorized simulation baseline.

The built DD4hep wall has inner/outer radii27/27.8 mm and half length4000 mm,
pure Be (Z=4), density1.848 g/cm³, mass2036.162205863 g and native
radiation length352.759820463 mm. The vacuum bore is explicit.
Two component CTests passed. ROOT found zero overlaps at1e-5 mm;15 rays
from the origin at η=−4,−2,0,2,4 and three azimuths reproduce0.8 cosh(η)
mm wall paths to1e-7 mm. The transverse wall contributes0.002268 X0 (rounded).
A seeded transverse geantino DDSim event completed successfully with FTFP_BERT.
The passive-only fixture has no sensitive collections and disables the tracker
hit-truth handler. It is a conversion/transport smoke test, not a physics result.

The exact dirty execution revision and compact, expected, factory and validator
hashes are in [native.json](native.json); enclosing PR commits are result revisions.

Failed attempts retained: validator initially used a TGeoMedium as a material;
ROOT singleton cleanup needed the established explicit manager deletion; DDSim
first missed plugin discovery because the components target was not built, and
invocation through `/usr/bin/env` stripped macOS loader paths. An explicit-load
steering attempt failed a DD4hep plugin cast. The passive fixture also needed
its hit-truth handler disabled because it contains no tracker readouts. The final
command uses the active Python interpreter, generated plugin registry and proper
loader paths. No tolerances or physical inputs were weakened.

Tracker clearance and Gen3 conversion are subsequent assembly checks. Mechanical,
vacuum, support and forward-transition qualification remains absent.
