# DES-022 long-strip barrel — isolated PROTOTYPE

This is a continuous cooled structural sandwich, with separately identified true
1D stereo sensors on both faces. Production geometry is unchanged.

```sh
python3 -B -m unittest discover -s tools/long_strip_barrel -p 'test_*.py' -v
python3 -B tools/long_strip_barrel/export.py --output build/long-strip-barrel/compact
```

For native work first use the acts-spack skill/preflight and verify this node's
DD4hep/DDG4 imports and all Geant4 datasets. Activate setup_spack, thisdd4hep.sh
and geant4.sh in the SAME shell as these commands:

```sh
cmake -S prototypes/long_strip_barrel -B build/long-strip-barrel/native -DCMAKE_BUILD_TYPE=Release
cmake --build build/long-strip-barrel/native -j 6
ctest --test-dir build/long-strip-barrel/native --output-on-failure
python3 -B tools/long_strip_barrel/check_root.py \
  --root build/long-strip-barrel/native/native.root \
  --expected build/long-strip-barrel/native/compact/expected.json \
  --output build/long-strip-barrel/root-roundtrip.json
```

Expose the build directory on DD4HEP_LIBRARY_PATH, LD_LIBRARY_PATH and
DYLD_LIBRARY_PATH before DDSim (CTest sets those locally). Each stave has a
separate assembly to bound ROOT voxel memory without changing physical solids.

```sh
python3 "$(command -v ddsim)" --compactFile build/long-strip-barrel/native/compact/long-strip.xml \
  --runType batch --numberOfEvents 1 --enableGun --gun.particle mu- --gun.direction '1,0,0' \
  --gun.energy '10*GeV' --physics.list FTFP_BERT --random.seed 42 \
  --outputFile build/long-strip-barrel/geant4.root > build/long-strip-barrel/geant4.log 2>&1
```

Using a Python with NumPy/uproot/Matplotlib, inspect the saved hits with
`check_geant4.py --root ... --log ... --native ... --expected ... --output ...`.
Run `coverage.py --output build/long-strip-barrel/coverage.json` and
`draw.py --expected ... --output docs/design/figures`. Coverage requires BOTH
faces of the SAME module. Its software PASS checks a fast solver against the
independent finite-plane oracle; engineering/coverage failures remain separate.
The anchor search uses full constituent gravity loads and bending plus core
shear; E/G and joint allocation need measurement/FEA. Input files are unsigned
fixtures, pinned source hashes reject silent drift. Raw XML/expected inventories,
ROOT files and runtime logs remain ignored under build/; curated reports/hashes
are retained under docs/validation/DES-022. Never replace historical DES-008/011
artifacts or equate an enclosing Git commit with a dirty native execution.

For the PR #52 transverse mounting view, use the retained inventory directly;
no native rebuild or new compact export is needed:

```sh
python3 -B tools/long_strip_barrel/draw_xy.py \
  --inventory docs/validation/DES-022/inventory.json.gz \
  --output docs/design/figures/DES-022-barrel-xy \
  --receipt docs/validation/DES-022/xy-drawing.json
```

This requires NumPy and Matplotlib. It generates SVG and PNG with a separate
drawing receipt, preserving the older figures and scientific receipts. All three
panels are equal-scale x-y sections at z166.50 mm, within the first positive-z
bearing station. The section includes one potted fastener, its tangent shoe/web,
the bearing ring and cooling legs; it does not project remote z components into
the section or claim manufactured slot details. The producer checks the complete
194-stave/388-sensor section, both rings, four pipe legs and one bolt per stave.

The [review figure and caption](../../docs/validation/DES-022/xy-view.md) are a
companion to the immutable design input. The original DES-022 document remains
byte-identical so the DES-023 input pin and native execution receipts stay valid.
