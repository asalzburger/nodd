# OBJ-R1 — Actual colored artifact assessment

**Exact revision:** `8b24dc692713d27bbfbfac04209e095437cc8c13`.
**Outcome:** no material findings within the requested visualization-only scope. No repository changes, new ACTS execution or human approval.

The independent parser/math checker inspected the actual immutable OBJ, MTL and ZIP without importing the exporter. It confirms:

- Exactly **1,560 blue chamber objects and 36 grey toroid warm-envelope objects**, with no frame, world, entrance, solenoid or track objects. There are 46,800 quads and 187,200 face-local vertices. Material values agree with the documented ACTS RGB/256 conversion.
- A relative sibling `mtllib chambers-and-coils.mtl`; the ZIP contains exactly the byte-identical OBJ and MTL. Coordinates match metre-scale source geometry with right-handed axes and beam along z.
- All chamber faces match the hashed actual native inspection corners exactly and source corners within 3.67e−15 m. Each chamber has six outward faces, eight geometrically distinct corners and the correct prism volume; maximum volume discrepancy is 6.21e−14 m³.
- All 36 coil sweeps match the source warm cross-section, complete radial/axial extents and twelvefold placement, without clipping at the propagation world. Every coil-face normal agrees with the analytic outward direction. Measured maximum curve chord deviation is **94.123 µm**, below the documented 0.1 mm bound; analytic polygon-volume deficits also agree.
- All 1,596 meshes close with consistent opposing edge directions **after coincident-coordinate welding at 1 nm**. Raw OBJ vertex indices remain face-local, as emitted by ACTS. Chamber Euler characteristic is 2; coil characteristic is 0. This does not claim a shared-index manifold mesh.
- All 91 original scientific source/artifact files checked against the prior frozen revision are unchanged. Export source/output fingerprints agree with the recorded source revision. The preview was visually inspected; its chamber transparency is explicitly preview-only.

Warm sleeves remain separately named, potentially overlapping allocation envelopes, not detailed windings or a Boolean union of cases. Mesh closure does not certify physical construction, collision freedom, magnetic behavior or performance. Prior PhysVal planning/reviews are disclosed; I did not author this exporter. The new checker is reviewer-authored and is not itself independently reviewed.

Portable evidence: `pr90-obj-R1-check.py` and paired `.json` in `/private/tmp`; optional hashed native-corner CSV input was used for this assessment. No shared dependency changes or transport tests were needed.
