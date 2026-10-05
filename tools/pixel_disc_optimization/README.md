# DES016 pixel disc optimization — isolated PROTOTYPE

This executable study responds to issue38's excessive silicon overlap, using the
user's10% limit. It writes review evidence and ACTS-sensitive-plane fixtures;
it does not modify the DD4hep compact or any baseline/historical artifact.
[The design](../../docs/design/DES-016-pixel-disc-module-optimization.md) governs
choices and scope; [the retained results](../../docs/validation/DES-016/results.md)
include the failed service-space estimates and guard control.

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
