# IdRes intake and first use — PROTOTYPE

This optional adapter runs the unsigned [DES-006 inputs](../../docs/design/DES-006-layouts.json).
It is isolated from detector construction. No upstream source, example detector,
field table or executable is distributed here. Public reproducibility remains
**blocked**: anonymous access and a redistribution licence have not been
established for the supplied checkout. Local execution was explicitly requested
by the user; the independent analytic screen and covariance control remain runnable
without IdRes. Local tool behaviour is an intake observation, not a public
normative detector fact. All candidate numbers come from the nODD proposal.

## Installation actually exercised on 2026-09-18

The supplied local checkout was built in `/tmp/nodd-des005-idres` and retained
durably at ignored `reference/cache/idres`, pinned at
`d54d0e3c465cc0308becb737b04364ce5c68ce16`. Source files were unchanged.
GSL 2.8 was already installed. Apple clang 17.0.0 (arm64 macOS) compiled it with
warnings for unused variables, deprecated `sprintf` and variable-length arrays;
the build completed successfully. No ROOT installation was required.

```sh
mkdir -p /tmp/nodd-des005-idres/bin
make -C /tmp/nodd-des005-idres/src CPPFLAGS=-I/opt/homebrew/opt/gsl/include LDFLAGS=-L/opt/homebrew/opt/gsl/lib
python3 -m venv reference/cache/idres-venv
reference/cache/idres-venv/bin/python -m pip install -r tools/tracker_layout/requirements-idres-plotting.txt
```

The local checkout must first be obtained through an authorized channel; that
unresolved access step is deliberately not presented as an anonymous public recipe.
The compiler/library paths above are the actual macOS paths, not portable defaults.
The retained package lock records the successful Python 3.14 environment. The
candidate adapter uses only the Python standard library and compiled IdRes;
plotting packages are needed for the supplied example pipeline.

From the checkout's `test` directory, the following smoke invocation passed.
`nodd_root` denotes the absolute path to the nODD checkout; that placeholder was
resolved to the local workspace for execution:

```sh
nodd_root=/absolute/path/to/nodd
MPLCONFIGDIR=/tmp/nodd-idres-mpl MPLBACKEND=Agg "$nodd_root/reference/cache/idres-venv/bin/python" test.py
```

It produced 14 PNG and 4 PDF outputs for the supplied example, retained locally only.
Fontconfig cache warnings were nonfatal. That upstream test checks file creation,
not physics correctness; none of its detector parameters is used in DES-006.

## Reproduce the nODD runs

From the nODD root:

```sh
python3 -B tools/tracker_layout/idres_adapter.py --checkout reference/cache/idres --work reference/cache/idres-study
python3 -B -m unittest discover -s tools/tracker_layout -p 'test_idres_adapter.py'
```

The adapter checks the pinned revision and rejects tracked source changes. The
binary checksum is retained; the user must build that executable from the checked
checkout. The report is [DES-006-idres-results.json](../../docs/validation/DES-006-idres-results.json).
It records configuration/adapter/executable hashes, platform, commands and hashes
of generated geometry, raw `.res`, `.hits`, `.X0` and log files. Those full raw
artifacts remain in the requested local work directory. Compact baseline profiles,
scenario points and denominator counts are committed. Reproduction emits fresh
environment metadata; compare numeric outputs separately from that metadata.

The scan is intentionally fixed in this prototype: each candidate, each uniform
field 2/3/4 T, material factors 0.5/1/2, plus two near-zero-material controls at 3 T;
pT 1/10/100 GeV, vertices -0.15/0/+0.15 m, eta 0..4 in 0.05 steps. This gives 22 runs,
729 result rows each, 16,038 successful finite rows in this execution. Missing keys,
nonfinite values, process failures and reported inversion failures abort the
adapter. Negative-eta geometry is checked independently by `study.py`; IdRes
results here are positive-eta only. This grid is not an efficiency denominator
or proof of continuous acceptance.

## Learned conventions and capability limits

Lengths are metres, pT GeV, field tesla, angles radians. Layer material is input
as **percent** X0 (1 means 1%); it is divided by 100 internally. Cylinders take
radius,zmin,zmax,X0%,sigmaRPhi,sigmaZ. Disks take rmin,rmax,z,X0%,sigmaRPhi,sigmaR.
Signed disks must be provided explicitly. Input comments begin with `!` in the
first column; blocks end with `end`. Plotting expects exactly three vertex values,
including zero. The adapter emits only finite cylinders/disks and one positive
uniform field per input. It refuses zero material because the scattering algebra
contains logarithms and inverse scattering variances; factors 1e-6 and 1e-8 provide
a convergence control instead of falsely labelling a run exact zero material.

The covariance coordinates are d0,z0,phi,cot(theta),q/pT with no vertex prior.
Each supplied surface has independent rphi and second-coordinate uncertainties.
For disks, sigmaR is projected to an effective z uncertainty using cot(theta).
The symmetric stereo pair is represented as one effective two-coordinate station
with diagonal covariance; physical separation and arbitrary stereo correlation
are omitted. It is not two independent pixel-like hits. Report station counts
therefore do not equal silicon-face counts. Upstream `.hits` counts one hit per
pixel surface and two per strip-classified surface (including a strixel): the
central trial has 16 upstream hits but 10 effective stations. The artifact retains
these as `upstream_*_hit_count`; `effective_station_count` is pixels plus half the
upstream strip count. IdRes classifies pixels by second
sigma < 200 micrometres, not by technology metadata; our present input separates the
three families consistently, but this heuristic cannot be assumed for new inputs.

Intersections are straight lines sorted by radius: magnetic curvature does not
change crossings, there is no phi tiling, and only a positive-charge pT parameter
is used. A linearized solenoidal-field covariance and accumulated thin-layer
multiple scattering are evaluated. There is no energy loss, pattern recognition,
inefficiency, fake/duplicate rate or timing observable. Large forward inverse-pT
errors cannot be interpreted as a Gaussian fractional-pT resolution. Material
projection is recorded only for origin tracks and the first pT; the candidate
ledger omits beam pipe and remote services. No numerical material ranking is a
complete engineering budget.

Raw d0/z0 output is micrometres. Raw `Sig_invPt` is TeV^-1; the adapter divides by
1000 to produce GeV^-1. Its printed precision is 1e-6 GeV^-1; d0/z0 precision 0.1 um,
and lever-arm precision 1 mm. Independent geometry gives the finer lever-arm values.
Upstream tabular fields are not qualified here; out-of-range lookups can silently
become zero and no supported arbitrary 3D field claim is made.

## Numerical controls and discovered defect

A first exploratory input containing `B 2 3 4 end` returned identical covariance
values for all three labelled cases, consistent with all using the final 4 T table.
At origin/eta 0/100 GeV and near-zero material, the raw inverse-pT error was
0.102 TeV^-1 in each case, versus 0.136 TeV^-1 for a separate 3 T run. The independent
covariance check exposed the factor 3/4 discrepancy. Source inspection suggests
shared scalar table storage. These multi-field trial results are discarded and
are not included in the scientific result artifact. **Every retained run uses one
field per process.** No upstream patch or claim of a fixed library is made.

The independent exact-zero-material covariance uses the physical conversion
0.299792458 whereas IdRes uses 0.3. After accounting for this 0.0692% convention
difference, the two near-zero-material controls agree with the independent result
at the tested barrel/forward points within half the printed 1e-6 GeV^-1 unit.
See the [PhysVal input](../../docs/design/inputs/DES-006-physval.md) and
[independent control](../../docs/validation/DES-006-covariance-control.json).
This validates a limited transverse covariance/control convention; it does not
validate all material scattering, longitudinal covariance or full tracking.
