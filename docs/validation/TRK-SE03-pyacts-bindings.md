# TRK-SE03 — pyacts module surfaces and Gen-3 geometry capability

- Date: 2026-09-21; role: `SoftEng`, with independent source inspection and runtime checks.
- Status: completed software capability assessment; isolated **PROTOTYPE** fixtures.
- Governing work: [DES-005](../design/DES-005-tracker-system-plan.md), TRK-SE03;
  [ADR-003](../decisions/ADR-003-validation-and-artifact-policy.md).
- User direction: leave tracker proposals on hold; assess the latest pip release.
- No nODD placement proposal, production detector, review or sign-off is advanced.

## Finding

**Yes, pyacts 47.7.0 has enough bindings to place finite sensitive modules into
barrel/endcap layer blueprints and build a Gen-3 tracking geometry, using the
wheel's JSON surface reader and existing blueprint API.** A custom C++ extension
or DD4hep is not required for this demonstrated prototype route. Direct Python
construction has defects and missing setters that must be worked around.

The live PyPI JSON endpoint and `pip index versions pyacts` both identify
**47.7.0** as the latest release checked on 2026-09-21; its wheels were uploaded
2026-09-07. A fresh isolated install selected
`pyacts-47.7.0-cp314-cp314-macosx_26_0_arm64.whl`. The existing project ACTS
environment was not modified. A cached web rendering of PyPI still displayed
46.8.1; the live index/JSON and installed distribution govern this result.

The [executable probe](../../tools/acts_binding_probe/probe.py),
[reproduction guide](../../tools/acts_binding_probe/README.md) and
[retained execution report](TRK-SE03-pyacts-bindings.json) contain commands,
versions, source/input hashes, numerical checks and actual outcomes. This is a
software-readiness result, not evidence of detector coverage or tracking efficiency.

## Verified capability boundary

| Operation | Result on installed wheel | API / qualification |
| --- | --- | --- |
| Place finite planar modules with bounds and transforms | Yes | `Surface.createPlane`, `RectangleBounds`, `Transform3`, `AngleAxis3`; use the safe composition described below |
| Create genuinely sensitive modules entirely through Python-accessible APIs | Yes, via JSON | `acts.json.readSurfaceVectorFromJson`, with `kind: PlaneRectangle`, `sensitive: true`, explicit transform and bounds |
| Group module lists into barrel and endcap layers | Yes | `LayerBlueprintNode.surfaces`, `.layerType = Cylinder / Disc`, `.envelope` |
| Combine layers into a coherent Gen-3 geometry | Yes | `Blueprint`, `addCylinderContainer(AxisR / AxisZ)`, `addLayer`, `addStaticVolume`, `construct` |
| Assign/query sensitive geometry identifiers | Yes | Blueprint construction produced 32 unique nonzero sensitive IDs; `visitSurfaces`, `geoIdSurfaceMap`, `findVolumeByName` usable |
| Use navigation policies with portals | Yes | TryAll and SurfaceArray policies tested; array cylinder bins `(8,1)`, disc bins `(1,8)`, plus TryAll portals-only |
| Navigate finite modules in both barrel and endcaps | Yes, diagnostic straight rays | Seeded `pseudoNavigation` results matched independent ray/rectangle intersections |
| Instantiate standard Navigator against this geometry | Yes | `Navigator(trackingGeometry=..., resolveSensitive=True, ...)` constructed |
| Run field-dependent propagation, hits, material interaction, fits or pattern recognition | Not tested here | These remain separate integration/physics checks; pseudo-navigation is not the Propagator |
| Arbitrarily edit a low-level TrackingVolume or implement a Python SurfacePlacementBase | Insufficient direct bindings | `TrackingVolume.addSurface` not exposed; placement base has no Python constructor/trampoline. Use the higher-level blueprint/JSON route |

Gen-3 “layers” here are module-bearing volumes created by `LayerBlueprintNode`
with portal connections and navigation policies. They are not the old
`CylinderLayer`/`DiscLayer` construction chain, nor the separate experimental
`Detector` API. The result type is `TrackingGeometry`; generation is established
by the release-pinned blueprint construction implementation and portal navigation,
not by the name of that result type alone.

## Actual fixture and checks

All dimensions are **synthetic test values**, isolated from detector descriptions:
two eight-module barrel rings at radii 50 and 100 mm, and eight modules on each
of two disks at z = -100 / +100 mm, centered at radius 70 mm. Planes have local
half-widths 10 and 20 mm. Barrel local axes are tangential / longitudinal;
disk axes are tangential / inward radial. No material or response is assigned.

Empty central volumes close the cylindrical container topology and contain the
origin. The module-layer envelopes are 1 mm; the root envelope is 5 mm. These
are numerical fixture margins, not engineering clearances. The first mixed
attempt combined hollow disks with a solid central barrel and failed portal
construction; adding explicit empty inner volumes made the stack consistent.
An earlier navigation attempt without an origin-containing volume hit an
upstream assertion; the final fixture deliberately supplies that volume.

For **each** navigation policy, the retained execution verifies:

- 32 sensitive modules, two cylinder and two disc layer nodes, 32 unique IDs;
- all module centers within 1e-9 mm and normals within 1e-12 of the JSON fixture;
  these tolerances test floating-point transforms, not detector alignment;
- 200 straight rays over diagnostic eta range [-3,3], internal fixed seed 42;
- 2,406 finite CSV records and 45 module intersections: 31 barrel, 4 negative
  endcap, 10 positive endcap, touching 19 distinct modules;
- exact agreement of module-ID sets with independent ray/rectangle intersections
  for all 200 rays, without duplicate module crossings;
- identical navigation CSV SHA-256 for TryAll and SurfaceArray policies.

This gives 400 policy/ray comparisons, **not 400 independent ray directions**:
the same 200 seeded rays are deliberately used for both policies. The sample is
not a uniform-eta physics distribution or an acceptance sample. A preliminary
barrel-only control also ran successfully (100 rays, 72 module intersections);
the retained mixed fixture is the reproducible assessment artifact.

## Binding limitations and safe paths

**1. The two-argument Transform3 constructor is defective in this build.**
`Transform3(translation, rotation)` returned nonfinite values in the tested
macOS wheel, even for an identity rotation. Pinned `Definitions.cpp` creates an
uninitialized `Transform3 t` then calls `prerotate` and `pretranslate`.
Use a valid transform followed by angle-axis composition, for example:

```python
transform = (
    acts.Transform3(translation)
    * acts.AngleAxis3(phi + math.pi / 2, acts.Vector3(0, 0, 1))
    * acts.AngleAxis3(math.pi / 2, acts.Vector3(1, 0, 0))
)
```

This produces the tested barrel basis. Alternatively, the JSON reader accepts
the complete finite transform. The small upstream correction would initialize
`t` to `Transform3::Identity()` before applying the operations. No upstream
source or installed wheel was patched by this assessment.

**2. Sensitive identifiers are not sensitivity flags.** Direct `createPlane`
surfaces remain `isSensitive == False` after
`assignGeometryId(GeometryIdentifier(sensitive=1))`. `isSensitive` is read-only
and the C++ `assignIsSensitive` method is not bound. JSON import with
`sensitive: true` sets the underlying flag; all 32 imported modules were checked
explicitly. No detector-element wrapper or lifetime workaround is needed for
this route. A small direct sensitivity binding would simplify future adapters.

**3. Blueprint child enumeration fails.** Reading `.children` raised a
return-value-policy runtime error in this wheel. Retain the handles returned by
`addLayer`/`addCylinderContainer`; construction and final geometry queries work.

**4. Low-level APIs remain partial.** `LayerBlueprintNode.setProtoLayer` and
`TrackingVolume.addSurface` are not exposed, and the placement base cannot be
implemented through a Python trampoline. These omissions do not block the tested
JSON-to-blueprint path, but prevent assuming every C++ builder is available.

**5. The diagnostic CSV header is inconsistent.** `pseudoNavigation` writes
eight values per row, including a leading run number, but names only seven
columns. The probe checks and parses the actual structure explicitly. The helper
also assumes an origin-containing geometry and is not a robust general tracking
runner; use normal propagation infrastructure for subsequent field studies.

## Recommendation and follow-up

**NODD DESIGN CHOICE — proposed software route, no human approval implied:** use
a versioned module JSON adapter feeding `readSurfaceVectorFromJson`, then Gen-3
blueprint layers/containers and tested navigation policies. Pin the wheel and
keep transform, sensitivity, ID and navigation checks at the adapter boundary.
There is no need to start a custom C++ bridge merely to place modules in layers.

When the user resumes tracker work, the next bounded software task is to convert
one module family, verify inactive masks and scalar stereo semantics, then run
the existing straight/uniform-field Propagator controls against the module
geometry. Real material, alignment/conditions, field maps, curved crossings,
holes/edge cases, detector identifiers and detector performance remain open.
Optional upstream binding fixes should be separate from that detector work.
No issue, comment or review request was sent to upstream maintainers here.

## Primary-source provenance

Source ID **SRC-PYACTS-4770-BINDINGS** in the
[catalogue](../../reference/manifest.yaml). Public facts are the package metadata
and exposed C++ binding definitions. Runtime observations and independent
comparisons are retained measurements; the recommended adapter route is a
proposed nODD software choice. Test dimensions are not normative detector facts.

- [Live PyPI metadata](https://pypi.org/pypi/pyacts/json), queried 2026-09-21;
  [versioned release page](https://pypi.org/project/pyacts/47.7.0/).
- Release `v47.7.0`, commit `2790f1b05c0c94cb3b569cbb18262b24867c7855`:
  [Gen-3 bindings](https://github.com/acts-project/acts/blob/2790f1b05c0c94cb3b569cbb18262b24867c7855/Python/Core/src/GeometryGen3.cpp),
  especially `LayerBlueprintNode`, `Blueprint::construct`, policies and pseudo-navigation.
- [Transform bindings, lines 294–318](https://github.com/acts-project/acts/blob/2790f1b05c0c94cb3b569cbb18262b24867c7855/Python/Core/src/Definitions.cpp#L294),
  [surface bindings](https://github.com/acts-project/acts/blob/2790f1b05c0c94cb3b569cbb18262b24867c7855/Python/Core/src/Surfaces.cpp),
  [JSON reader bindings](https://github.com/acts-project/acts/blob/2790f1b05c0c94cb3b569cbb18262b24867c7855/Python/Plugins/src/Json.cpp).
- [Layer implementation](https://github.com/acts-project/acts/blob/2790f1b05c0c94cb3b569cbb18262b24867c7855/Core/src/Geometry/LayerBlueprintNode.cpp)
  and [blueprint tests](https://github.com/acts-project/acts/blob/2790f1b05c0c94cb3b569cbb18262b24867c7855/Python/Core/tests/test_blueprint.py).
- [Surface JSON conversion](https://github.com/acts-project/acts/blob/2790f1b05c0c94cb3b569cbb18262b24867c7855/Plugins/Json/src/SurfaceJsonConverter.cpp) and
  [transform JSON conversion](https://github.com/acts-project/acts/blob/2790f1b05c0c94cb3b569cbb18262b24867c7855/Plugins/Json/src/AlgebraJsonConverter.cpp):
  sensitivity setter and row-major rotation import used by the workaround.
