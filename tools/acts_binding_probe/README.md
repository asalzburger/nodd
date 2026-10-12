# pyacts module / Gen-3 binding probe

**PROTOTYPE: synthetic software fixtures only.** This check belongs to DES-005
TRK-SE03 and does not construct a production nODD detector. Every module dimension below is a test value.

## Python-first construction after expert review

The current recommendation is to generate module placements and blueprint topology
in Python. JSON is an explicit wheel compatibility/control path, not a required
geometry-design interface. The review response and executed evidence are in
[the assessment](../../docs/validation/TRK-SE03-pyacts-bindings.md#expert-review-response--2026-09-28).

The source-built path needs `Surface.assignIsSensitive`, added by
[ACTS PR #6176](https://github.com/acts-project/acts/pull/6176).
The installed `pyacts==47.7.0` wheel does not expose it. The recorded local
`acts-nodd` installation has the patch; read its instructions and run the
[Spack preflight](../../skills/acts-spack/SKILL.md) before relying on the runtime.
In a shell configured with `acts run acts-nodd`, from this nODD checkout:

```sh
python -B tools/acts_binding_probe/python_construction.py \
  --acts-source /Users/salzburg/Documents/work/dev/acts-nodd \
  --work /tmp/nodd-python-construction-new-run \
  --report /tmp/nodd-python-construction-report.json
```

Use a **new** work directory. The script builds the same 32-module fixture directly
in Python, tests both navigation policies, then repeats with an alternating
barrel z offset of +/-2 mm (synthetic fixture). It compares native construction
with a JSON control on the same ACTS build and checks independent finite-plane
intersections for all rays. Zero/2 T propagation uses 48 tracks per field and
backend, accounting for every generated track. No plotting dependency is required.

`specs()` generates placements in Python, `python_surface()` constructs each
finite plane and marks sensitivity, and `construction()` organizes the Gen-3
blueprint. The plain module dictionaries also feed the independent oracle and
optional JSON control; native construction reads/writes no module JSON file.
Changing staggering edits Python parameters/logic. Changing layer grouping or
container topology edits the Python blueprint builder; a serialization schema
cannot eliminate those structural choices. Missing sensitivity bindings fail
explicitly instead of silently switching backends.

The pinned source build's JSON control uses `type: PlaneSurface`, whereas
v47.7.0 uses `kind: PlaneRectangle`. The comparison runner selects the former
explicitly; the legacy wheel commands below retain the latter. This format
difference does not affect the native construction API. JSON remains useful
for optional snapshots/interchange, not for this placement exercise itself.

## Historical wheel compatibility control

Install in a separate, ignored environment from the repository root:

```sh
python3 -m venv reference/cache/pyacts-bindings-venv
reference/cache/pyacts-bindings-venv/bin/python -m pip install -r tools/acts_binding_probe/requirements.txt
reference/cache/pyacts-bindings-venv/bin/python -B tools/acts_binding_probe/probe.py --backend json --work reference/cache/pyacts-binding-probe --report docs/validation/TRK-SE03-pyacts-bindings.json
```

The release was checked against the live package index on 2026-09-21. Installation
and execution were tested on CPython 3.14.6 / macOS arm64; this is not a promise
that every Python/platform combination has a wheel. No source build, DD4hep,
Geant4, ROOT or custom extension is needed for this historical JSON fixture.

The probe exercises sensitive rectangular module surfaces through the wheel's
JSON reader, module lists in Gen-3 blueprint layer nodes, construction and a
seeded straight-ray navigation smoke test. It compares navigation with independent
ray/rectangle intersections. It also retains the observed direct-constructor
and sensitivity limitations. See the [assessment](../../docs/validation/TRK-SE03-pyacts-bindings.md)
for the capability boundary and pinned official source references.

`pseudoNavigation` is an upstream diagnostic, not the magnetic-field propagator,
simulation, hit generation or track reconstruction. Its fixed internal seed is
42. The v47.7.0 CSV header omits the leading run column even though rows contain
it; the probe checks the eight-column record shape and names the columns itself.
All rays begin at the origin, which must lie in a constructed volume; the fixture
includes an empty central volume for that purpose. Counts do not establish nODD
acceptance, efficiency, material response or field-dependent navigation.

The report records the installed version, wheel receipt when available, fixture
and code hashes, pre-generation Git revision, commands, numerical tolerances,
seed, expected counts and actual outcomes. Generated JSON module inputs and raw
navigation CSVs remain under the ignored work directory. The fixture assumes
no material and assigns no detector performance target.

## Propagation step view

The follow-up uses the official propagation-example sequence with
`EigenStepper`, `Navigator`, `PropagationAlgorithm(sterileLogger=False)` and
`ObjPropagationStepsWriter`. The tested wheel does not include the ROOT writer.
This is actual propagation step output, separate from `pseudoNavigation` above.

```sh
reference/cache/pyacts-bindings-venv/bin/python -m pip install -r tools/acts_binding_probe/requirements-plot.txt
reference/cache/pyacts-bindings-venv/bin/python -B tools/acts_binding_probe/propagation_view.py --backend json --work reference/cache/pyacts-propagation-view --figure reference/cache/pyacts-propagation-view/propagation-xy.png --report reference/cache/pyacts-propagation-view/propagation.json
```

The retained [x–y figure](../../docs/validation/figures/TRK-SE03-propagation-xy.png)
and [execution report](../../docs/validation/TRK-SE03-propagation.json) use 48
identical seeded muons per field case, eta = 0, pT = 0.1 GeV, charge -1 and
synthetic Bz = 0 / 2 T. Step length is limited to 2 mm. All values are test
settings; neither the low momentum nor the field is a detector requirement.
Endcaps remain in the geometry but are outside this central slice.

OBJ contains positions and connectivity, not surface IDs. The plotted markers
are actual written steps associated geometrically with finite module planes;
no line-segment intersections are invented for the picture. All generated
tracks must have written paths, reach the fixture boundary and agree with
independent straight/circular trajectories and finite-plane intersections.
The 0.001 mm trajectory/plane and 0.002 mm intersection tolerances accommodate
the upstream OBJ writer's six-significant-digit coordinates. They are numerical
fixture checks, not alignment or detector-performance tolerances. Material,
response and reconstruction are absent.
