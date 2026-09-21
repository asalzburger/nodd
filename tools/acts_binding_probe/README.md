# pyacts module / Gen-3 binding probe

**PROTOTYPE: synthetic software fixtures only.** This check belongs to DES-005
TRK-SE03 and does not resume the held tracker-placement proposals or construct
a production nODD detector. Every module dimension below is a test value.

Install in a separate, ignored environment from the repository root:

```sh
python3 -m venv reference/cache/pyacts-bindings-venv
reference/cache/pyacts-bindings-venv/bin/python -m pip install -r tools/acts_binding_probe/requirements.txt
reference/cache/pyacts-bindings-venv/bin/python -B tools/acts_binding_probe/probe.py --work reference/cache/pyacts-binding-probe --report docs/validation/TRK-SE03-pyacts-bindings.json
```

The release was checked against the live package index on 2026-09-21. Installation
and execution were tested on CPython 3.14.6 / macOS arm64; this is not a promise
that every Python/platform combination has a wheel. No source build, DD4hep,
Geant4, ROOT or custom extension is needed for the retained fixture.

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
