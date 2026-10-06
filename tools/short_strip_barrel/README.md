# Detailed short-strip barrel — DES-020 prototype

This independent model does not replace the pixel compact or modify production
geometry. Read [DES-020](../../docs/design/DES-020-short-strip-barrel.md) and the
[results](../../docs/validation/DES-020/results.md) before treating a software
pass as detector feasibility.

The frozen tangential layout is compared without rewriting it: structure,
identifiers and discrete values are exact; serialized floats allow8 ULPs of
libm rounding across macOS/Linux (≤9.1e−13 mm at660 mm). This is stricter than
the existing1e−7 mm native transform gate. A negative control rejects a1e−8 mm
placement shift while accepting a one-ULP perturbation. Native overlap and
engineering tolerances are unchanged.

The **working baseline**, selected by the user on2026-10-06, is
`inputs-phi-tilted.json`: same-radius staves at+15° about global+z, unchanged
local components, and beveled ring-contact webs. The model, compact exporter and
coverage CLI select this input when `--input` is omitted. It has44/56/80/108
staves and8,064 modules. `inputs.json` remains the byte-preserved historical
tangential control, selected explicitly with `--input`. Historical drawings
also explicitly load that control; the comparison figure retains its original
labels. Read [the baseline selection checks](../../docs/validation/DES-020/baseline-selection.md)
and [tilted evidence](../../docs/validation/DES-020/phi-tilted/results.md).

The standalone CMake project's default `compact/` and `native.json` now describe
the tilted baseline. `compact-control/` and `native-control.json` describe the
explicit tangential control; CTest audits both. This replaces the earlier
`compact-phi/` alternative naming for fresh builds. Existing build products and
historical retained reports are not rewritten by this selection.

For a separate control export:

```sh
python3 -B tools/short_strip_barrel/export.py --input tools/short_strip_barrel/inputs.json --output build/short-strip-control/compact
```

Coverage uses the same nominal-cylinder denominator for both layouts. The12/18°
controls and the12° collision failure remain retained separately. Neither finite
sampled coverage nor zero overlaps establishes detector acceptance.

From the repository root:

```sh
python3 -B -m unittest discover -s tools/short_strip_barrel -p 'test_*.py' -v
python3 -B tools/short_strip_barrel/model.py --output build/short-strip-barrel
python3 -B tools/short_strip_barrel/export.py --output build/short-strip-barrel/compact
python3 -B tools/short_strip_barrel/check_layout.py --refined \
  --expected build/short-strip-barrel/compact/expected.json \
  --output build/short-strip-barrel/layout-check.json
python3 -B tools/short_strip_barrel/compare_phi.py --output build/short-strip-barrel/comparison.json
MPLCONFIGDIR=/tmp/nodd-strip-mpl python3 -B tools/short_strip_barrel/draw_phi.py --output build/short-strip-barrel/figures
```

The model/export/controls use Python's standard library. Coverage uses NumPy and
the existing finite-plane oracle. Figures use Matplotlib. The retained local run
used NumPy2.5.3/Matplotlib3.11.2 in the existing ACTS Python environment; no package
installation was performed. The input pins governing documents, the unchanged
selected DES-011 layout and reused pixel material definitions. Stale pins fail.

For native construction, follow the acts-spack skill and verify the runtime in
the same shell. On the verified local node:

```sh
source /Users/salzburg/cernbox/configs/acts/acts_setup.sh
unset ACTS_SPACK_SETUP
setup_spack
source /Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view/bin/thisdd4hep.sh
source /Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view/bin/geant4.sh
cmake -S prototypes/short_strip_barrel -B build/short-strip-barrel/native -G Ninja
cmake --build build/short-strip-barrel/native --parallel 4
ctest --test-dir build/short-strip-barrel/native --output-on-failure
python3 -B tools/short_strip_barrel/check_root.py \
  --root build/short-strip-barrel/native/native.root \
  --expected build/short-strip-barrel/native/compact/expected.json \
  --output build/short-strip-barrel/root-roundtrip.json
```

The standalone library is `libnODDShortStripBarrel.dylib` on macOS or `.so` on
Linux. Compact XML, expanded expected inventories, ROOT files and raw runtime
logs belong under ignored `build/`. Native CTest audits every physical entity,
anisotropic strixel IDs/cells, material inventories and overlaps, then exports
the ROOT geometry. Persistence is checked in a fresh process without loading the
factory. DD4hep units in native ROOT are cm; persisted checks explicitly convert
to the model's mm. This is not ACTS tracking-geometry conversion.

Geant4 smoke, after the same runtime setup:

```sh
export DD4HEP_LIBRARY_PATH="$PWD/build/short-strip-barrel/native:${DD4HEP_LIBRARY_PATH:-}"
export DYLD_LIBRARY_PATH="$PWD/build/short-strip-barrel/native:${DYLD_LIBRARY_PATH:-}"
python3 "$(command -v ddsim)" \
  --compactFile build/short-strip-barrel/native/compact/short-strip-barrel.xml \
  --runType batch --numberOfEvents 1 --enableGun --gun.particle mu- --gun.direction '1,0,0' \
  --gun.energy '10*GeV' --physics.list FTFP_BERT --random.seed 42 \
  --outputFile build/short-strip-barrel/geant4.root
```

Inspect the saved event using Python with `uproot` installed:

```sh
python3 -B tools/short_strip_barrel/check_geant4.py \
  --root build/short-strip-barrel/geant4.root \
  --log build/short-strip-barrel/geant4.log \
  --native build/short-strip-barrel/native/native.json \
  --expected build/short-strip-barrel/native/compact/expected.json \
  --output build/short-strip-barrel/geant4-check.json
```

Save the DDSim stdout/stderr as `geant4.log` when running the smoke command.
The original and tilted retained executions use separate `geant4-transverse`
reports in DES-020 and DES-020/phi-tilted/. Both saved eight positive-energy hits
in all four layers. Supplying the baseline expected inventory makes the checker
use its tilted sensor normal, rather than the tangential0.2mm fallback.
No field is defined in this simulation compact.

Retain the failed30 mm collector using `inputs-30mm-control.json`: the compact
export is required to reject excess constituent volume. The final65 mm proposal
changes the axial endcap interface; it cannot be integrated into the old disc
schedule unchanged. Engineering capacity, thermal, data, bend and coverage
screens are separate from native software PASS. The gross cable inventory is a
benchmark; its effective composition is not a manufactured cable specification.
