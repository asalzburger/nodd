# Native ACTS chamber-boundary engine — PROTOTYPE

This standalone C++20 executable uses the existing installed `Acts::Core`.
It does not build, patch or install ACTS, DD4hep or Geant4. The governing
DES040 propagation amendment was committed at
`a4d3788f89a79af8b31ff694e811b543af792d3c` before implementation. It changes
validation only; the retained chamber geometry and joint vacuum field are inputs.
The revised native face-audit method was committed before its implementation at
`faa544a1fa424906c68b27bcf37db181d783b84e` after the finite-portal adverse control
missed a curved entry and exposed a native portal assertion at looser targeting.
The correction-retention and curvature-guard amendment was committed before its
implementation at `008ae5b6ab673de5504fe9ea55ab6378312d4d0a`, following failed
refinement controls on the first audit binary. Preserve those failed controls.
The independent native near-limit correction was documented before its
implementation at `cf7997d78d3e5058345d979f77969f980401e37e`.
Bounded exhaustive discovery and independent RK accuracy were committed before
implementation at `cbef091d19984e475efe3b59f148ea676de8e90b`, after unbounded
supports stalled on remote faces and grazing hit coordinates failed refinement.

Build in a task-owned directory after verifying the local ACTS environment:

```sh
cmake -S tools/muon_layout/acts -B /private/tmp/pr90-acts-build \
  -DActs_DIR=/Users/salzburg/Documents/work/installed/acts-nodd/lib/cmake/Acts \
  -DCMAKE_BUILD_TYPE=Release
cmake --build /private/tmp/pr90-acts-build --parallel 2
```

The optional `ACTS_CORE_PREFIX` mode imports only the installed Core target and
finds its Boost/Eigen interfaces. It was used during initial compilation when
the previous aggregate ActsConfig pinned vecmem 1.27 but the updated environment
provided 1.28. The subsequent complete ACTS rebuild regenerated that configuration
with vecmem 1.28 and DD4hep 1.38. Normal `find_package(Acts)` discovery is now the
primary build path; the optional Core import remains an explicit limited-scope
mode and does not relax aggregate dependency requirements or install dependencies.

The source HEAD is `555c66e71d0639665c2fa3d5574a0fe7f3f62cde`, with preserved local
patches. The installed header's commit string describes its source configuration;
the reported version `999.999.999` is not release provenance. Record actual
headers/library hashes, compiler, configuration and command alongside each run.
The executable reads `VersionInfo::fromHeader()` and `fromLibrary()`, refuses
a numeric-version mismatch and compares commit hashes only when both APIs
provide one. This ACTS source deliberately returns no library commit from
`fromLibrary()`; metadata records that unavailability and the header commit.
The separately pinned dylib SHA remains the library-identity evidence.

The coordinator rebuilt and installed the complete ACTS configuration against the
updated Spack environment before resuming this engine. The rebuilt
`libActsCore.dylib` SHA256 is
`f4c040fa6c331fca6180dc75589fbc95ec30fc485c2edbefb891fda46cdf7088`;
this supersedes the library used in the initial Core-only compile. The
coordinator reports 385/385 C++ unit tests, three integration suites, 28 Python
passes with two optional-input skips, runtime imports and 12 dataset presence
checks passing. These are ACTS installation checks; engine navigation controls
and the engine's rebuilt executable require their own executed evidence.

No Python ACTS bindings, ROOT
files, material transport or detector response are used by the engine.

## Input and output

All external lengths are **metres**, momenta **GeV**, fields **tesla**. ACTS
positions use `UnitConstants::m`, and returned fields multiply `UnitConstants::T`
(which is not 1 in ACTS internal units). IDs and directions are dimensionless.

- `--geometry`: whitespace text. First token unsigned panel count; then each
  row is `id station depth origin[3] basis[9] vertices[8]`. IDs contain no
  whitespace. Basis is row-major with columns local x/y/normal. Vertices are
  four counterclockwise local `(x,y)` pairs. Preserve the pinned JSON values.
- `--map`: binary `NODDMAP1`, then three little-endian uint64 dimensions,
  float64 R/z/phi axes, float32 `(Br,Bphi,Bz)` in C `(R,z,phi,component)` order,
  then uint8 node validity. This is an unchanged-value export of the pinned NPZ,
  not a regenerated field. Hash both input NPZ and binary export.
- `--tracks`: first unsigned count; rows `id p q x y z dx dy dz`. Directions
  must be unit vectors, q is ±1. The caller owns sampling, seed and entrance.
- `--output-dir`: writes `hits.csv`, `tracks.csv`, `geometry.csv`,
  `geometry-corners.csv` and `metadata.json` for propagation mode.
  Optional `--audit-roots` also writes native `root-audit.csv` and
  `step-audit.csv` diagnostics, including current/target IDs, native remaining
  step constraints, positions and finite matches. It changes no propagation.

`hits.csv` records actual native surface-root actor positions, all six finite
faces, with panel/face ownership and a computed `is_large` flag. In audit mode,
one ACTS supporting root can match several finite owning faces; all are recorded
at that same native position. Geometry IDs are
**uint64**, above 2^53; never import them through a float64 CSV column. Raw
entry/exit/reentry events remain separate. Count only the two large faces as
provisional segment proxies, then apply the analysis protocol for unique faces,
paired same-chamber traversals, distinct stations and border-inset results.
The engine does not manufacture measurement-plane intersections.

`tracks.csv` has exactly one row per successfully parsed input track, including
failures. A shared external capture retains already reached native faces and
last completed-step position/path when ACTS returns an error. Field lookup
errors retain their first failure reason and position. Statuses are `completed`,
`field_masked`, `outside_map`, `navigation_error`, `step_limit`, `path_limit`
or `returned_to_entrance`.
Additional per-track columns retain native negative-correction count, guard-cap
count, distinct near-tolerance parallel face ambiguities and the minimum guard
step. A near-tolerance parallel ambiguity supplies no fabricated hit; retain it
when qualifying the completeness of the boundary-event accounting.
Three native virtual entrance surfaces (R=4.35 m, half-z=6.50 m) stop on the
first native inward crossing, status `returned_to_entrance`. These are study
surfaces with no material and are excluded from muon hits. In audit mode the
world boundary also uses native surface targets and a strict finite actor check;
an outward crossing sets `completed` and aborts. A malformed
input file or impossible geometry is a fatal setup error, exit 2, rather than
a successfully executed zero-track run.

```sh
/private/tmp/pr90-acts-build/nodd-muon-propagate \
  --geometry GEOMETRY.txt --map MAP.bin --tracks TRACKS.txt --output-dir OUTPUT
```

Controls:

```sh
# Geometry closure, counts, actual native face centres/normals/corners only
nodd-muon-propagate --geometry GEOMETRY.txt --field zero --inspect-only --output-dir INSPECT
# Field reader only: points file has N followed by xyz rows; geometry not needed
nodd-muon-propagate --map MAP.bin --query-field POINTS.txt --output-dir FIELD_CHECK
# Analytic straight/helix controls, with exhaustive candidate refresh
nodd-muon-propagate --geometry GEOMETRY.txt --tracks TRACKS.txt --field constant \
  --bz 3 --policy exhaustive --output-dir HELIX_CHECK
```

Field modes are `map` (default), `zero`, and `constant`; constant uses `--bz T`.
Boundary modes are `--mode surface-audit` (default) and `--mode finite-portals`
(the original adverse negative control). The equivalent
`--boundary-mode support-plane|finite-portals` spelling is also accepted.
The strict map reader rejects outside-domain positions and **any** invalid
interpolation corner, even with zero interpolation weight. It rotates the
periodic cylindrical field using the original global phi, preserving both z
signs. No invalid value becomes zero and no extrapolation is performed.

## Native geometry and navigation

Each retained panel becomes an exact `GenericCuboidVolumeBounds` leaf
`TrackingVolume`: the first four vertices are its negative-depth face and the
next four its positive-depth face. Every leaf has six actual finite portals,
shared with the vacuum world, with links to the leaf and world on opposing
sides. The world is a cylinder R=9.1 m and half-z=11.5 m, contains all chamber
corners, and lies inside the supplied field-map domain. No frames/coils/chamber
internals or material are inserted as additional volumes.

Complete IDs use world volume=1 and chamber volume=2/layer=(panel+1), then
boundary=(face+1). This respects ACTS's 8-bit volume and 12-bit layer fields.
Geometry closure preserves these explicit IDs, checks uniqueness and visits
all native volumes/portals. `is_large` is calculated from the native face
normal's absolute dot product with the JSON prism normal; every panel must
have exactly two. All six sides remain available for navigation audit.

Native `EigenStepper` and `Navigator` perform the propagation. A local stateful
policy invalidates after position/direction changes except while ACTS has a
pending negative Navigator correction to its active target. That target is
retained until native correction converges; otherwise refreshing would discard
the just-overshot root as behind the track. Refresh resumes after the native root.
The independent native `navigation.nearLimit` is explicitly zero: its default
100 nm cutoff would otherwise discard a refreshed forward target only a few
nanometres away, despite a tighter configured surface tolerance. ACTS still skips
already-on-surface candidates; finite containment and hit tolerances are unchanged.
In audit mode
it proposes the actual finite portal surfaces as surface targets with infinite
candidate-boundary tolerance. ACTS finds the supporting-plane roots; an actor
then tests the unchanged native finite faces with `BoundaryTolerance::None()`
and the configured normal-distance tolerance. Outside-footprint roots are
discarded. The actor audits all nearby finite owners at that ACTS root, including
coplanar faces that ACTS would otherwise skip at zero path distance. No trajectory
segment is intersected afterward and no root is manufactured or moved.

The same global audit policy is installed in the world and every leaf, covering
native renavigation into a leaf. Chamber portal volume switching is deliberately
not used in audit mode. World and virtual entrance targets likewise use native
surface roots followed by actual finite bounds and direction checks. All finite
volumes, portals, links and native IDs remain present for geometry inspection.
This validates finite-face crossings with an explicit audit policy; it does not
establish correct stock portal transitions through the chamber network.

A locally parallel or moving-away tangent can have no forward plane root even
when curvature reaches the face during the next step. For planar faces the actor
uses the constant-momentum vacuum bound `kappa=0.299792458*abs(q)*Bmax/p` in
inverse metres. `Bmax` is the maximum valid-node field norm, with a small floating
arithmetic margin; positive trilinear weights and the cylindrical-to-Cartesian
rotation preserve that bound. Constant controls use `abs(Bz)`. No field value is
changed. When `g*vn>=0`, `abs(g)` exceeds targeting tolerance, and
`abs(g)+abs(vn)*maxStep <= kappa*maxStep^2/2`, the next native Actor step is capped
at `0.8*2*abs(g)/(sqrt(vn^2+2*kappa*abs(g))+abs(vn))`. Here `g` is signed normal
distance to the actual planar face and `vn` its direction component. The bound
follows `abs(g(s)-g-vn*s)<=kappa*s^2/2`. If the lower bound stays positive across
the whole maximum step, no cap is needed. Once a forward tangent root exists,
ACTS targeting finds it. Pending native negative corrections are never capped by
this guard. The public `ConstrainedStep::Type::Actor` constraint changes only
integration step sizes and creates no event or interpolated position.

The actor recomputes the guard before the first step and after completed steps.
Metadata records the field/curvature bound, native corrections, guard checks,
cap count/minimum and near-tolerance parallel ambiguities. The guard covers
planar chamber faces and planar entrance/world boundaries; cylindrical native
targets retain their native intersection behavior. Grazing cases within the
normal tolerance remain explicitly ambiguous, and path/step budgets still apply.

`--policy indexed` uses 1 m Cartesian cells containing complete chamber AABBs,
then a conservative distance-to-AABB filter with radius
`2*max_step + 2*surface_tolerance`. It includes every face of selected chambers
and always keeps world outer surfaces plus the three native virtual entrance
surfaces. Any point reached within one allowed
step is inside that search ball; the second step budget is conservative extra
candidate space. `--policy exhaustive` scans every chamber AABB without the grid
and applies the same conservative distance bound. It independently validates grid
enumeration while retaining the same physical reach rule. Its candidate set and
ordering must agree with the indexed selector. `--policy unbounded` retains all
infinite supports as an explicit adverse negative control: remote supports can
oscillate at unreachable roots and hide real finite faces. It is not a reference
for the scan. Unreached infinite-bound targets are not carried between
refreshes. The target-skip budget covers every finite face plus world/entrance
surfaces, allowing coplanar candidates to be skipped after the common root has
already been audited. It changes no integration step or finite containment test.

**Numerical scope:** finite-portal mode relies on finite tangent intersections
and missed the adverse curved entry even with exhaustive candidates. It is
retained as a negative control. Audit mode addresses that discovery failure;
require adverse curved-edge recovery, exact straight/helix roots, strict native
residual/bounds checks and indexed/exhaustive plus step/tolerance refinements
before a broad scan. Candidate index conservatism alone proves no root accuracy.
The
unmodified ACTS `TryAllNavigator` helper does not enumerate dense child volumes
and dereferences absent layer arrays; it is not silently substituted here.

Numerical defaults: `--max-step-m 0.05`, `--tolerance-m 1e-8` (10 nm),
`--rk-tolerance-m 1e-11` (10 pm), `--max-steps 20000`, `--path-limit-m 100`.
The first tolerance controls surface targeting and normal containment. The
independent RK tolerance controls native RKN local integration error; its
acceptance permits an error estimate up to four times that parameter. A local
error target is not achieved global accuracy. Grazing crossings amplify small
trajectory differences, so refine RK to 1 pm independently of surface tolerance
and maximum step, keeping the 10 micrometre coordinate gate unchanged. Loop protection
is disabled to preserve explicit path/step accounting. Refine step and tolerance
independently, check actual native face residuals/bounds, and preserve failures
in denominators. Every full physics result needs the accompanying executed
controls; a compile, nonzero hit count or successful propagation is insufficient.

The implementation is deliberately single-threaded: field and navigation
capture pointers are track-local within its serial loop. Parallelize independent
executables with separate output directories if needed. No density, scattering,
energy loss, alignment, chamber efficiency or reconstructed performance follows
from these vacuum envelope crossings.
