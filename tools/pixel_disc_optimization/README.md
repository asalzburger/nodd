# DES016 pixel disc optimization — isolated PROTOTYPE

This executable study responds to issue38's excessive silicon overlap, using the
user's revised 15% preferred / 20% maximum limit and radial/tangential axes.
The original 10% Cartesian study remains a superseded control. It writes review evidence and ACTS-sensitive-plane fixtures;
it does not modify the DD4hep compact or any baseline/historical artifact.
[The design](../../docs/design/DES-016-pixel-disc-module-optimization.md) governs
choices and scope; [the retained results](../../docs/validation/DES-016/results.md)
include the failed service-space estimates and guard control.

## Superseded Cartesian control and shared environment

Use Python3.12+ with NumPy and the pinned Shapely dependency. For native audit and
plots, activate the verified acts-nodd installation in the same shell, following
the repository's node preflight/acts-spack skill. Do not install into a shared ACTS
or Spack environment. A local ignored dependency target can be populated with:

```sh
python3 -m pip install --no-deps --target build/disc-optimization/python -r tools/pixel_disc_optimization/requirements.txt
```

The interpreter/wheel ABI must match the ACTS Python runtime. The verified local
run used Python3.14 with Shapely2.1.2. Preserve the activated ACTS PYTHONPATH when
prepending the local target, then run:

```sh
export PYTHONPATH="$PWD/build/disc-optimization/python:$PYTHONPATH"
python -B tools/pixel_disc_optimization/study.py --output build/disc-optimization/final
python -B -m unittest discover -s tools/pixel_disc_optimization -p 'test_*.py' -v
python -B tools/pixel_disc_optimization/audit.py --screening build/disc-optimization/final/screening.json --output build/disc-optimization/acts --acts-source /path/to/acts-nodd/source
MPLCONFIGDIR=build/disc-optimization/matplotlib python -B tools/pixel_disc_optimization/report.py --run build/disc-optimization/final --audit build/disc-optimization/acts --output docs/validation/DES-016
```

Matplotlib is needed only for the report drawings. ACTS's actual extension hash,
source SHA, source working-tree changes and guide-state fallback are recorded by
the existing native audit. No ACTS source file is edited by these tools.

`inputs.json` centralizes active dimensions, new slim-guard/body choices, numerical
controls and scenario references. Every new physical parameter is an unqualified
NODD DESIGN CHOICE under DES016; matrix/pitch/material facts are inherited from
DES001. `baseline_sha256` protects the source scene; report hashes pin all
consumed service inputs and executable code. NumPy/Shapely/Python versions are
retained. No random sampling or seed is used.

The objective is whole projected sensor silicon: `(ΣA−union A)/union A`, with
annulus-only overlap also≤10% and overhang reported. Active rectangles alone
must cover the unchanged annulus. DSATUR colours padded occupied-body footprints;
final actual bodies are then checked without that padding, including periphery,
beam aperture and0.2mm separation. Counts/IDs in this prototype have a separate
namespace; existing production identifiers remain unchanged.

The first-disc lattice uses a0.45mm reduction in both active pitches. For farther
discs the reduction scales as `0.45×615.2/abs(z)`; the same328 module indices are
retained, with slightly adjusted centres. This avoids unnecessary far-disc
silicon overlap. Axial centre compensation uses the mean inverse distance to
vertices±150mm. Neither operation changes sensor shape, matrix dimensions,
disc positions or the nominal acceptance annulus.

Coverage certificates adaptively subdivide the continuous on-axis vertex
interval. On each accepted interval, the union of intersections of endpoint
footprints contains a polygon superset of the true annulus. Because each finite
plane footprint is a monotone homothety, every intervening vertex is covered.
This is a straight-ray certificate, not a helix or transverse-vertex proof.
324 matched native tracks and an exhaustive small control audit finite-plane
transport separately. Service estimates retain full module/link counts,
local spatial grouping, both feed/return legs, barrel traffic and failed adverse
cases. They cannot qualify manufacture, thermal contacts or hydraulics.

## Superseded nine-ring radial revision

The user rejected global x/y alignment, particularly for rectangular pixels.
`radial.py` keeps the 18-single inner polar ring and explores further concentric
single, tangential-double, radial-double, quad and mixed-family rings. The axes
are tangential/radial at each assembly centre. Shared sensors are counted once;
individual active matrices retain the inherited 0.2 mm inactive seam. Whole
physical assemblies share one axial level, with occupied-body checks including
periphery. The configured scan is bounded, not a global optimum claim.

After the same verified ACTS environment activation above, run:

```sh
python -B tools/pixel_disc_optimization/radial.py --output build/disc-optimization/radial-final
python -B -m unittest discover -s tools/pixel_disc_optimization -p 'test_*.py' -v
python -B tools/pixel_disc_optimization/radial_audit.py --screening build/disc-optimization/radial-final/screening.json --output build/disc-optimization/radial-acts --acts-source /path/to/acts-nodd/source
MPLCONFIGDIR=build/disc-optimization/matplotlib python -B tools/pixel_disc_optimization/radial_report.py --run build/disc-optimization/radial-final --audit build/disc-optimization/radial-acts --output docs/validation/DES-016/radial-revision
```

[Revised results](../../docs/validation/DES-016/radial-revision/results.md) and
`radial-inputs.json` retain the full family scan, continuous straight-ray
certificates, per-distance body/silicon screens, matched native ACTS audit,
orientation covariance control and recomputed half-ring services. The source
scene and original Cartesian report/code remain intact. The double/quad controls
are rejected where their actual active seams leave holes; their shared silicon
cannot be treated as one seamless active matrix.

The rectangular 25 × 100 micrometre pixel control uses pitch/sqrt(12) to show
measurement-axis dependence; it is a test hypothesis rather than changed RD53i
hardware. Finite rectangles still have corner departures from the local
radial/tangential basis. No fitted track resolution, global navigation or
continuous helical hermeticity is asserted. Source datum pairing accepts only
1e-9 mm binary-float roundoff; actual native transport uses the unchanged source
datums, including the original first-disc position. Guard, support, cooling and
shared service qualification remain open.

## Current service-radius revision

The user required the radial module file to remain within the existing cable
and service bounds. `service_radius.py` removes the complete outer ring and
retains every surviving transform/ID/level. It reads pinned DES014/DES015
interfaces: r188.5 mm local plate, r190 mm collector boundary, r192..231.7 mm
trunk and r222 mm flange neck. Tube and provisional pickup-land reservations are
screened too. The earlier Cartesian and nine-ring radial outputs stay intact.

After the verified ACTS dependency/runtime activation above, run:

```sh
python -B tools/pixel_disc_optimization/service_radius.py screen --output build/disc-optimization/service-radius-final
python -B -m unittest discover -s tools/pixel_disc_optimization -p 'test_*.py' -v
python -B tools/pixel_disc_optimization/service_radius.py audit --run build/disc-optimization/service-radius-final --output build/disc-optimization/service-radius-acts --acts-source /path/to/acts-nodd/source
MPLCONFIGDIR=build/disc-optimization/matplotlib python -B tools/pixel_disc_optimization/service_radius.py report --run build/disc-optimization/service-radius-final --audit build/disc-optimization/service-radius-acts --output docs/validation/DES-016/service-radius
```

[Current results](../../docs/validation/DES-016/service-radius/results.md) and
`layout.json` retain 296 singles in eight rings and a maximum reserved radius of
183.388628 mm. Original-annulus coverage explicitly fails after outer-ring
removal; its comparison target and numerical tolerances are unchanged. Native
ACTS includes 54 added edge probes and retains actual target-disc misses.
The report requires finite-plane/oracle agreement, radial interfaces, body
separation, orientation and overlap checks; it does not require or falsely claim
hermeticity for the user-authorized trimmed proposal. Fixed service capacities
and all failing scenarios remain visible. Pickup lands are bounding reservations,
not qualified contacts, flex artwork or swept pipes.
