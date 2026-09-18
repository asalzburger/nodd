# First tracker layout study — DES-006

**PROTOTYPE / DRAFT.** This directory studies ideal layers for
[DES-006](../../docs/design/DES-006-first-tracker-layouts.md). It creates no
DD4hep geometry and is isolated from production detector/reconstruction settings.
The fixed host and `abs(eta)<4` investigation are inherited from DES-005; all
active dimensions, response and material scenarios require human review.

## Reproduce the public geometric screen

Run from the repository root, Python 3.10 or later for the geometric screen.
The complete covariance checks use Python 3.12+ and the pinned NumPy control
dependency (`requirements-controls.txt`); the executed local environment is
Python 3.14.6. CI installs that dependency and runs all prototype tests, without
requiring external IdRes access.

```sh
python3 -B -m unittest discover -s tools/tracker_layout -p 'test_*.py' -v
python3 -B tools/tracker_layout/study.py docs/design/DES-006-layouts.json --output docs/validation/DES-006-layout-screen.json
```

The input has explicit signed disks and SI units. A stereo pair is represented
by one effective surface and its paired material, not two independent 2D hits.
`study.py` derives the first outward crossing of each ideal cylinder/annulus
in a uniform axial field. With `rho=pT/(0.299792458*abs(B))`, the transverse arc
to a cylinder is `sT=2*rho*asin(r/(2*rho))`; a disk uses
`sT=(z_disk-z_vertex)/sinh(eta)` and `r=2*rho*sin(sT/(2*rho))`.
The zero-field limit is evaluated separately. Return/curling intersections and
exact cylinder turning-point tangencies are excluded. No supplied pT/field case
requires them. Both signs of eta and reflected vertices are sampled.

Local radiation length is the normal surface fixture divided by incidence
cosine. Cylinder cosine is `sqrt(1-(r/(2*rho))^2)/cosh(eta)`; disk cosine is
`abs(tanh(eta))`. Exact active edges count, without safety margin. This is a
thin-surface sum, not material transport or a complete material budget. The
geometric report applies nominal material only; half/double runs belong to the
IdRes study. No beam pipe, remote services or finite support structures exist.

The signed eta grid is .01 for extrema; retained plotting profiles are .05.
The independent PhysVal straight-ray scan uses .001 near transition weaknesses.
No grid establishes continuous hermeticity. Test fixtures exercise zero-field
known answers, incidence corrections, curvature/sign reflection, holes, stereo
station counting and invalid inputs. They are not physics acceptance tests.

## IdRes and independent covariance

See [IdRes installation, interface audit and runs](IDRES.md). Its native hit
intersections are straight-ray approximations; do not describe them as ACTS or
the independent helix model above. Its upstream source is not vendored. The
public nODD inputs and analytic controls remain usable when upstream access is
unavailable; complete public IdRes distribution/licensing remains an intake item.

The [PhysVal input](../../docs/design/inputs/DES-006-physval.md) explains the
free three-parameter measurement-only transverse covariance control and why a
large inverse-pT error cannot be reported as Gaussian momentum precision.
NumPy for this control is already pinned in the envelope-study environment.

```sh
reference/cache/envelope-venv/bin/python -B tools/tracker_layout/covariance_control.py --idres-results docs/validation/DES-006-idres-results.json
```

This also audits retained baseline station counts and thin-layer material sums
against independent straight-ray calculations. Print-rounding agreement is a
numerical consistency check, not a physical acceptance threshold.

## Figures and two-page proposal briefs

Reuse the existing environments documented in
[envelope study](../envelope_study/README.md) and
[reference reading](../reference_reading/README.md):

```sh
MPLCONFIGDIR=/tmp/nodd-mpl reference/cache/envelope-venv/bin/python -B tools/tracker_layout/plot.py
reference/cache/venv/bin/python -B tools/tracker_layout/render_briefs.py
```

The first uses Matplotlib 3.11.2 / NumPy 2.5.3; the second PyMuPDF 1.28.2 in
this local execution. The Markdown brief sources contain explicit page breaks;
the renderer requires exactly two A4 pages and fails on overfull text boxes.
The output PDFs and small figures are retained alongside the review documents.
Raster appearance and font metrics are platform-dependent. A PDF page count is
checked programmatically and pages are rendered for visual inspection.

## Provenance and exclusions

Reports record input/code hashes, pre-generation Git HEAD, dirty-tree state,
versions, commands, units and deterministic sampling. A dirty pre-commit SHA
does not claim the new files already belonged to that commit. Final publication
revision is carried by normal Git history and PR review records. No random seed
is needed for these deterministic studies.

ODD XML placement extraction is documented in the TrackTech input at the exact
public source revision; it is not a converted full-ODD comparison benchmark.
Missing module masks, scalar stereo geometry, beam pipe, material ownership,
field maps, occupancy/radiation conditions, luminous distribution and numerical
performance thresholds prevent final layout selection. DD4hep/Geant4, ACTS
module conversion, efficiency/fake-rate reconstruction and timing benefit are
explicit later stages, not tests passed by this tool.

## PR #13 review: inclined C and double-sided strips

The [C proposal](../../docs/design/DES-006-proposal-C.md) retains A/B as historical
controls and adds an axisymmetric envelope of tilted planar module rows. C uses
an independent public geometric/material screen; the IdRes adapter rejects
unsupported surfaces. No C IdRes or scattering-fit result is claimed.

```sh
python3 -B tools/tracker_layout/inclined_study.py
python3 -B tools/tracker_layout/audit_inclined.py
MPLCONFIGDIR=/tmp/nodd-pr13-mpl python3 -B tools/tracker_layout/plot_inclined.py
python3 -B -m unittest discover -s tools/tracker_layout -p 'test_*.py'
```

The first writes the C layer table and comparison with A, including 0/5/10 mm
row-extension controls, input/code hashes and execution provenance. The second
retains the independent solver and denser straight-ray coverage audit. The third
uses Matplotlib to draw C, compare material/coverage and render a two-page A4
brief; local execution used Matplotlib 3.11.0 and NumPy 2.4.3. PDF page count and
visual inspection accompany publication.

Each long-strip pair contributes two scalar faces but one parent station. Its
paired normal material is not doubled. Overlap contributes every crossed row's
material and faces; distinct parent groups are reported separately from physical
crossings. The conical envelope intersection uses the helix's local direction
and the surface normal. Bisection tolerance/iterations and the restricted outward
branch are explicit in code; opposite-facing unsupported roots fail rather than
silently disappearing. Future tilted pixel/barrel geometries need their own
validated domain extension.
