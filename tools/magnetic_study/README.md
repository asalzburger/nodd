# Magnetic studies — PROTOTYPE

Governed by [DES-004](../../docs/design/DES-004-magnetic-configurations.md).
These tools are isolated research fixtures. They do not supply a production
DD4hep field, magnet material or detector performance estimate.

## Vacuum current-sheet benchmark

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
