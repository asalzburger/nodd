# Tracker sensitive-crossing profiles

This repeatable **PROTOTYPE** study uses the current DES-025 DD4hep tracker,
its native ACTS TrackingGeometry conversion, the DES-026 finite-annular-winding
vacuum field map normalized to 3 T at the origin, and the ACTS propagation
example algorithms. It characterizes sensitive-plane crossings, including
overlapping pixel chips and both strip faces. It does not count reconstructed
hits, independent layers or stations, and does not measure tracking efficiency.

The default study is specified in [study.json](study.json): fixed pT of
1, 10 and 100 GeV; 8,192 generated muons per momentum; uniform η in [−4,4]
and full azimuth; origin vertex; seeded random charge signs; no energy loss or
multiple scattering. Each momentum uses the same seed so initial directions
can be paired. The profile includes zero crossings. Shading shows the
population standard error of the mean in each of 80 η bins; it excludes field,
alignment, material, response and reconstruction uncertainty.

## Run

On the supported ACTS node, run the acts-spack preflight and verify the installed
runtime as documented in [AGENTS.md](../../AGENTS.md#node-specific-software-workflows).
Install the pinned [unrooted plotting environment](../../software/analysis/README.md)
once. From the repository root:

```sh
make tracker-propagation
```

This builds the DD4hep factories/compact in `build/dd4hep`, generates and checks
the map, propagates all three momentum samples, compares converted surfaces to
the native source inventory, and writes profiles/plots under
`build/tracker-propagation/plots`. The node wrapper uses the existing
`acts run acts-nodd` runtime and never builds or changes shared dependencies.
`ACTS_SETUP_SCRIPT` and `ACTS_RUNTIME_NAME` can explicitly select another already
verified compatible installation; changing a path does not qualify another node.

Make variables `BUILD_DIR`, `PROPAGATION_OUTPUT`, `PLOT_PYTHON` and
`PROPAGATION_ARGS` select task-owned outputs and sampling overrides. For example:

```sh
make tracker-propagation PROPAGATION_OUTPUT="$PWD/build/another-profile" PROPAGATION_ARGS="--tracks 8192"
```

The orchestrator [run.py](run.py) also supports `--stage field`, `propagate`,
`plot` and `all`. Native stages require the activated ACTS environment. The
executed configuration is saved as `<output>/study.json`; per-case and stage
logs remain beside the data. A failed native stage stops the pipeline.

## Replot without ACTS

Once native `counts.csv` tables exist:

```sh
make tracker-propagation-plot
```

Or run the analysis environment directly:

```sh
software/build/unrooted-venv/bin/python -I tools/tracker_propagation/plot.py \
  --directory build/tracker-propagation \
  --config build/tracker-propagation/study.json \
  --output build/tracker-propagation/plots
```

The output contains standard ROOT TProfiles and the underlying per-track trees,
JSON bin populations/means/standard errors, compressed per-track tables, SVG/PDF/PNG
figures and a self-contained interactive HTML full-tracker view. ROOT TProfiles,
unrooted branch profiles and independent bin sums must agree before figures are
written. The main figure groups pixel, short-strip, long-strip and full tracker;
the second resolves all seven DD4hep system IDs.

## Numerical and data contracts

The field generator requires the retained DES-026 sizing solution to match the
current baseline/model/tracker source hashes. Eight-point radial Gauss quadrature
represents the uniform-J annular pack as ACTS finite solenoid sheets, each with
1,000 axial coils. The signed-z RZ text map has r-fastest columns
`r_mm z_mm Br_T Bz_T`. Its 10 mm × 20 mm grid covers r≤1,300 mm and |z|≤4,200 mm.
Axis values are checked against the independent continuous-winding expression;
sampled off-grid interpolation, doubled axial-coil and doubled radial-order
comparisons must remain within the declared 1 mT software check tolerance.
Those sample differences are not a global error bound or magnet qualification.
No ODD map, uniform-field substitution or ferromagnetic return structure is used.

One generated probe per event gives a stable `(event_nr, track_nr=0)` identity.
Native summaries and steps must account for the complete generated identity set.
Every sensitive GeometryIdentifier is mapped back to a native DD4hep system;
the per-system counts must sum to the native summary `nSensitives` for every
probe. Missing/failed propagations are errors rather than silently omitted
profile entries. Each requested transverse momentum, generated kinematics and
zero-crossing contribution must remain explicit.

The three technology groups sum systems 1–3, 4–5 and 6–7 respectively; the full
tracker sums 1–7. This grouping follows the retained DES-025 system translation.
Fixed random seeds establish reproduction, while independent seeds, charge/η/φ
diagnostics and numerical refinements assess finite sampling and navigation.

Meaningful pure controls can run without ACTS:

```sh
software/build/unrooted-venv/bin/python -B -m unittest discover -s tools/tracker_propagation -p 'test_*.py' -v
```

Large native step ROOT files, maps and detailed converted-surface arrays remain
in ignored build outputs. The scientific report should retain source/runtime
identities, configuration, count/profile tables, checks and artifact hashes.
