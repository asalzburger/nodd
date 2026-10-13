# Magnetic studies — PROTOTYPE

Governed by [DES-004](../../docs/design/DES-004-magnetic-configurations.md).
These tools are isolated research fixtures. They do not supply a production
DD4hep field, magnet material or detector performance estimate.

## Current study: review-directed energy sizing (2026-09-24)

The [response](../../docs/design/inputs/DES-004-magnet-sizing-review.md) and
`sizing-policy.json` govern all five active main-coil geometries. `sizing.py`
solves winding/current/cold-mass size together using all-space vacuum energy;
`finite_winding.py` and `muon_layouts.py` reject invalid current inputs. CI runs
all magnetic tests, including geometry, energy/volume and 5 T hard-limit checks.
No SciPy or new numerical dependency is required; NumPy suffices for tests.

```sh
python3 -B tools/magnetic_study/sizing.py
python3 -B -m unittest discover -s tools/magnetic_study -p 'test_*.py' -v
MPLCONFIGDIR=/tmp/nodd-mpl XDG_CACHE_HOME=/tmp/nodd-cache python3 -B tools/magnetic_study/finite_winding.py
MPLCONFIGDIR=/tmp/nodd-mpl XDG_CACHE_HOME=/tmp/nodd-cache python3 -B tools/magnetic_study/muon_layouts.py
```

The first command regenerates `windings.json` and the sizing report. Radial host
amendments are explicitly retained in `muon-layouts.json`; changing a sizing
input requires reconciling all affected hosts, and containment checks reject a
stale host. The field command now writes `DES-004-sized-winding-benchmark.json`
and `DES-004-sized-winding-axis.*`, preserving the older finite-pack evidence.
Use the existing envelope plotting environment for figures. The new report
records code/input hashes, versions, root/refinement tolerances and limitations.

Cold lengths and vessel end allowances remain provisional, the outer-gap symbol
interpretation awaits confirmation, and installed iron/toroid energy remains a
blocker to complete-system sizing. Generic vacuum current controls are not a
certificate of conductor margin, total physical field or structural feasibility.

## Historical finite homogeneous windings (2026-09-22)

The following dimensions and command descriptions record the prior study. Current
commands and numerical bounds are those immediately above and in `windings.json`.

The active comparison is MAG-01 through MAG-05. MAG-06 is withdrawn following
[expert review](../../docs/design/inputs/DES-004-magnet-expert-review.md).
`windings.json` supplies the current finite main-winding bounds; `candidates.json`
and `solenoid.py` remain historical thin-sheet controls and a quadrature kernel.

```sh
python3 -B -m unittest discover -s tools/magnetic_study -p 'test_*.py'
MPLCONFIGDIR=/tmp/nodd-mpl XDG_CACHE_HOME=/tmp/nodd-cache python3 -B tools/magnetic_study/finite_winding.py
MPLCONFIGDIR=/tmp/nodd-mpl XDG_CACHE_HOME=/tmp/nodd-cache python3 -B tools/magnetic_study/muon_layouts.py
```

These commands require NumPy and Matplotlib (use the environment instructions
below when unavailable). The finite-winding report records actual versions;
this update does not claim a run of the earlier environment or ACTS fixtures.

`finite_winding.py` integrates constant azimuthal winding-pack J over radius,
z and azimuth, with independent analytic axis normalization. Inner r=1.34–1.44 m,
|z|≤3.30 m and outer r=4.40–4.60 m, |z|≤6.50 m are unsigned design choices.
The pack-average density differs between coils to normalize each to +3 T in
vacuum; there is no current grading within a pack. The historical sheet is
recovered in the thin-pack limit. No physical iron/toroid field is supplied.
The 0.12 m numerical exclusion surrounds the whole pack; no interior or near-pack
accuracy, transport map, conductor margin or structural adequacy is claimed.

The [review response](../../docs/design/inputs/DES-004-magnet-expert-review.md)
contains the full derivation, allocation rationale and unresolved vessel design.
`DES-004-finite-winding-benchmark.json` adds evidence without overwriting the old
sheet benchmark. Current muon drawings show finite pack bounds. The old six-option
host report remains in Git at `2530c5543da6b2c474ccadc6c67ce431d69d2e0f`;
the regenerated report contains five active candidates and winding containment.
`withdrawn_options` preserves MAG-06 input but is excluded from normal generation.

## Historical vacuum current-sheet benchmark

Use the existing plotting environment, or create an ignored environment and
install the exact [plotting requirements](../envelope_study/requirements.txt):

```sh
python3 -m venv reference/cache/magnetic-plot-venv
reference/cache/magnetic-plot-venv/bin/python -m pip install -r tools/envelope_study/requirements.txt
MPLCONFIGDIR=/tmp/nodd-mpl XDG_CACHE_HOME=/tmp/nodd-cache reference/cache/magnetic-plot-venv/bin/python -B tools/magnetic_study/solenoid.py
reference/cache/magnetic-plot-venv/bin/python -B -m unittest discover -s tools/magnetic_study -p 'test_solenoid.py' -v
```

The retained run used `reference/cache/envelope-venv/bin/python`, with versions
recorded in the [benchmark JSON](../../docs/validation/DES-004-solenoid-benchmark.json).
`candidates.json` contains unsigned, explicitly sourced diagnostic dimensions.
Neither control represents steel in the actual calorimeter/support structure.

### Calculation and validation

**INFERENCE — classical Biot–Savart calculation:** integrate uniformly distributed
azimuthal current over an infinitesimally thin cylindrical sheet of radius R and
half-length h. Total ampere-turns are `NI = 2 B0 sqrt(R²+h²)/μ0`. At observation
(r,0,z), integrate a circular source `(R cosφ,R sinφ,z')`; `dl × displacement`
has radial component `R cosφ (z-z')` and axial component `R²-Rr cosφ`.
Use Gauss–Legendre quadrature over z' and periodic trapezoidal quadrature over φ.
The independent analytic axis expression is

`Bz(0,z) = μ0 NI/(4h) [(z+h)/sqrt(R²+(z+h)²) − (z−h)/sqrt(R²+(z−h)²)]`.

Units: metre, tesla, ampere-turn. Positive azimuthal current gives positive Bz.
The classical approximation μ0=4π×10⁻⁷ is adequate for these diagnostic thresholds;
this is not a precision constants measurement. Deterministic calculations need no
random seed. Discrete current turns, winding thickness, iron, ends/shaping and
services are omitted. No stored-energy or structural-feasibility result is inferred.

Checks compare independent axis values, reflection/current reversal, vacuum curl
and divergence away from sources, far-field dipole limit and quadrature refinement.
The benchmark compares 48×64, 96×128 and 192×256 quadrature at six named points.
Screening uses `1e-6 T + 1e-5 norm(B_fine)`; axis agreement additionally uses
1e-10 T. These are numerical test settings, not field-calibration requirements.
Test-suite finite-difference spacing and asymptotic distance are test fixtures.

The matched-scale Br/Bz atlas covers 0≤r≤8 m and −14≤z≤14 m. Every plotted point
is compared against doubled quadrature. White regions are excluded: a 0.12 m
numerical guard around the ideal current sheet/edge, or failed convergence against
the same screening threshold. The guard is **not a physical clearance**. Maxima
before the convergence cut are recorded so poor convergence is not hidden.
The images are sampled displays, **not validated interpolated transport maps**.
They must not be used to propagate tracks across masked cells. Map interpolation,
3D toroids and nonlinear iron fields remain separate work packages.

The report includes source commit, dirty-tree state, script/config hashes,
versions, commands and tolerances. A dirty-tree report is linked to exact script
bytes by hashes; its enclosing Git revision is the retained artifact revision.

## ACTS

Tracking ACTS is distributed as **`pyacts`**, imported as `acts`. Public PyPI
`acts` is a different project. See the [actual setup and verification record](../../docs/validation/DES-004-acts-setup.md)
for the pinned distribution, platform, reproduction commands and executed checks.

## Global system layouts

```sh
MPLCONFIGDIR=/tmp/nodd-mpl XDG_CACHE_HOME=/tmp/nodd-cache reference/cache/envelope-venv/bin/python -B tools/magnetic_study/layouts.py
```

`layouts.json` applies only the DES-004 architect's documented amendments to the
unchanged DES-003 allocation input; current-sheet dimensions come from
`candidates.json`. The script reuses envelope validation/intersection checks,
checks sheet containment, and produces two individual and one matched-scale
comparison drawing in PNG/SVG. The retained `DES-004-system-layouts.json` records
coordinates, source hashes, versions and actual checks. No physical material or
station geometry is generated. Plot extents, colours and labels are display choices.

## Preliminary option resource screen

```sh
python3 -B tools/magnetic_study/option_screen.py
```

This deterministic arithmetic screen records uniform-field flux/energy proxies,
muon-annulus areas, trial return fields and ideal active-return radii in
`docs/validation/DES-004-option-screen.json`. It uses the existing candidate/layout
inputs. Every omitted effect is listed in that report; neither the energy proxy
nor the return-area estimate is a rigorous engineering bound. The 1.5/2 T return
trials are study settings, not selected steel saturation limits. No nonlinear
field, force, material transport or detector performance is computed.

## Adapted muon-envelope proposals

```sh
MPLCONFIGDIR=/tmp/nodd-mpl XDG_CACHE_HOME=/tmp/nodd-cache reference/cache/envelope-venv/bin/python -B tools/magnetic_study/muon_layouts.py
```

`muon-layouts.json` holds five active candidate-specific proposals separately from
E1-R2 and the initial two-option inputs. The script validates top-level host
intersections, finite main-winding containment and nested radial reservations,
records forward gaps and straight-ray aperture samples, and generates five
individual plus one combined PNG/SVG drawing. The retained report is
`docs/validation/DES-004-muon-envelope-proposals.json`. Nested reservations
belong to their composite host; they are not independent overlapping mothers.
The MAG-04 trial bands are area screens only; MAG-06 is archived. No baseline
parameter, station efficiency, steel material or full field is implemented.

### Stepped endcaps (2026-09-18)

`muon-layouts.json` supplies explicit `endcap_sections` for each candidate.
`muon_layouts.py` replaces the reference endcap with their union, validating
all section/host intersections without tying endcap starts to barrel length.
The six single-option figures and combined comparison share the same inputs.
The report records per-section ray entries and provisional axial/radial gaps.
These are composite PROTOTYPE allocations, not physical chamber geometry.

```sh
python3 -B -m unittest discover -s tools/magnetic_study -p 'test_muon_layouts.py'
```

### Coordinated inner-space reuse (2026-09-18)

MAG-03/04/06 in `muon-layouts.json` now apply the coordinated ECal/HCal radial
amendment, with `inner_space_reallocated` recording the optimized scenario.
The plotter no longer marks the removed coil space as unused. The report records
nominal depths, interface gaps and a 5,201-point eta scan over 0–5.2 at 0.001
spacing, with a 1e-10 m numerical path-comparison tolerance. Summed straight-ray
host lengths are geometric proxies, not material depths or shower containment.
Earlier `layouts.json` and field controls retain their original comparison inputs.
