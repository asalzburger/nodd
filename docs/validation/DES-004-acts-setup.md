# DES-004 — ACTS wheel setup and propagation fixtures

- Date: 2026-09-17; status: **PROTOTYPE**, executed infrastructure checks.
- Scope: approved magnetic research first increment; no production integration or
  human detector-design sign-off.
- Environment: macOS 26.6.2 arm64, CPython 3.14.6, `pyacts==47.7.0`.
- Source context: SRC-ACTS-REPO; package catalogue entry SRC-PYPI-PYACTS.

## Installation and provenance correction

The official [ACTS repository](https://github.com/acts-project/acts) recommends
`pip install pyacts`. [PyPI pyacts 47.7.0](https://pypi.org/project/pyacts/47.7.0/)
provides the tracking toolkit; its installed metadata links the official repository.
The selected binary was `pyacts-47.7.0-cp314-cp314-macosx_26_0_arm64.whl`.
`import acts`, `acts.examples`, straight-line/Eigen propagation, particle generation
and `SolenoidBField` worked in this environment. This is a concrete wheel result,
not a claim that every ACTS plugin or every macOS/Python combination is supported.

The earlier plan missed this ready-made distribution:
the public package called `acts` belongs to Android, but **`pyacts` is the correct
tracking ACTS distribution**. No Android package was installed. An initial official
source-clone attempt failed sandbox DNS; its escalation was interrupted. The user
then requested `pyacts`; source-build work was abandoned. The first pip attempt
also failed sandbox DNS, then succeeded with approved network access. No compiler
build or system package installation was needed.

Executed setup:

```sh
python3 -m venv reference/cache/acts-venv
reference/cache/acts-venv/bin/python -m pip install pyacts
```

The resolved dependency pin is retained in
[acts-requirements.txt](../../tools/magnetic_study/acts-requirements.txt).
For reproduction, use `python -m pip install -r tools/magnetic_study/acts-requirements.txt`
with the isolated environment's Python. Wheel availability on another platform
must be checked; it is not assumed.

## Actual checks

Run from the repository root:

```sh
reference/cache/acts-venv/bin/python -B tools/magnetic_study/acts_checks.py --output reference/cache/acts-propagation-checks --report docs/validation/DES-004-acts-checks.json
```

[Harness](../../tools/magnetic_study/acts_checks.py) and
[retained result](DES-004-acts-checks.json) record seven successful propagation cases:

1. `StraightLineStepper` against an analytic straight line.
2. `EigenStepper` in zero field against the same analytic line.
3. `EigenStepper` in uniform 3 T against the analytic helix.
4. Reversed field against the corresponding helix.
5. Reversed particle charge against the corresponding helix.
6. Half maximum step size against the analytic helix again.
7. Both charge and field reversed, preserving the analytic bending direction.

These use ACTS's GenericDetector only as a synthetic navigation fixture, with
material energy loss, scattering and material recording disabled. A deterministic
particle gun generates a 10 GeV muon or antimuon at η=0.5, φ=0, vertex zero, seed
228. CSV output verifies the generated charge. These are **test values**, not
nODD requirements. The wheel's examples algorithms perform actual propagation;
the Python wrapper does not substitute its own equation-of-motion integrator.

The maximum coordinate/helix radial residual must remain below **0.02 mm** in this
fixture. The OBJ writer retains limited decimal precision despite a requested
precision of 16, so this is a serialization-aware check, not a measurement of
intrinsic ACTS integration precision. The half-step case does not replace a full
adaptive-tolerance convergence study. Floating-point trap tracking is disabled in
this isolated examples sequence; explicit finite analytic residual checks determine
success. No existing production test setting was changed.

Five additional axis points compare `SolenoidBField` with a continuous thin-current
sheet: radius 1.415 m, length 6.600 m, central field 3 T, 1000 discrete ACTS coils.
The largest discrepancy is approximately **1.06×10⁻⁶ T**, below the synthetic
**10⁻⁵ T** threshold; the centre normalization and positive/negative-z symmetry
are included. This tests an ideal current-only provider, not a yoke, winding pack,
cryostat fit or achievable engineering field.

The report records package/Python/platform versions, starting revision, dirty-state
flag, script hash, command, settings, residuals and raw OBJ hashes. Raw OBJ/CSV
and timing outputs remain in ignored `reference/cache/acts-propagation-checks`.
The generated generic geometry is fixed by the pinned package/default configuration.

## Remaining work

No nODD active-surface conversion, spatial field-map adapter, candidate-specific
propagation grid, material transport, ferromagnetic field solve or performance
measurement was executed. Those remain FIELD-V01/PROP-V01/MU-V03 follow-up work
in the [study catalogue](DES-003-study-catalogue.md). The fixtures establish a
working toolchain and basic numerical behavior; they do not close those studies.
