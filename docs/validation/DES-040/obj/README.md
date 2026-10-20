# Current chamber and toroid OBJ — PROTOTYPE

The [OBJ](chambers-and-coils.obj) and [MTL](chambers-and-coils.mtl) are also
packaged together in a [ZIP](chambers-and-coils.zip). Keep the material file
beside the OBJ when importing it. Coordinates are metres, with right-handed
Cartesian axes and the beam along z.

Blue objects are the 1,560 finite chamber envelopes from PR90's actual ACTS
TrackingGeometry. Grey objects are the 36 fixed toroid **warm envelopes**
(12 barrel and 12 per endcap), including their allocated case space. These
are empty envelope surfaces: no chamber internals, support frame, world,
entrance cylinder or trajectories are exported. The central solenoid is
outside this muon-layout export. Neither chamber placement nor coil geometry
is changed, and no new coverage study is performed.

The [exporter](../../../../tools/muon_layout/export_obj.py) calls the unchanged
native propagation executable in inspection mode, takes its actual finite-face
vertices, corrects polygon winding for outward-facing display and writes them
through `Acts::ObjVisualization3D`. The two large faces and all four side faces
close each chamber envelope; they are not internal MDT layers.

Toroid sweeps follow the existing analytic rounded-rectangle centreline and
rectangular warm cross-section. Curves use 64 segments per quadrant; maximum
chord deviation is below 0.1 mm. Overlapping warm sleeves remain separately
named allocation objects; their summed mesh volume is not a Boolean union.
Colours use standard OBJ material assignments. The installed ACTS writer divides
RGB integers by 256 and emits repeated identical material definitions; the
export retains that colour conversion and removes only duplicate definitions.
The `mtllib` reference is a portable sibling filename.

The native OBJ writer stores face-local vertices. Closure and orientation checks
identify coincident positions on a 1 nm grid within each object; they do not claim
that the raw OBJ indices already form a shared-vertex manifold mesh.

Reproduce from the repository root after the prescribed ACTS/Spack setup:

```sh
cmake -S tools/muon_layout/obj_writer -B reference/cache/pr90-obj/build -G Ninja \
  -DCMAKE_PREFIX_PATH=/path/to/verified/acts/install -DCMAKE_BUILD_TYPE=Release
cmake --build reference/cache/pr90-obj/build --parallel 2
python3 -B tools/muon_layout/export_obj.py \
  --propagator reference/cache/pr90-acts/build/nodd-muon-propagate \
  --writer reference/cache/pr90-obj/build/nodd-muon-obj \
  --acts-library /path/to/verified/acts/install/lib/libActsCore.dylib
```

Build the native propagation executable using its
[existing instructions](../../../../tools/muon_layout/acts/README.md) if needed.
The library filename is platform dependent. Commit export sources before
capturing final provenance. [Export evidence](export.json) records source/input,
executable/library and output hashes, native geometry metadata, mesh and material
checks. [Preview](chambers-and-coils.png) uses transparent chambers for visibility;
the OBJ materials are opaque. This visualization grants no engineering approval.

The separate [technical assessment](review.md), [check results](independent-check.json)
and [portable checker](independent-check.py) assess the exact artifact revision
`8b24dc692713d27bbfbfac04209e095437cc8c13`. They confirm the object colours,
native/source chamber corners, coil dimensions and placement, portable materials
and ZIP payload, geometric closure and curve approximation. No material findings
were reported within this visualization scope; this is not human design approval.
