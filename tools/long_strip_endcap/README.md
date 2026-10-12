# DES-023 long-strip endcap — isolated PROTOTYPE

A continuous cooled structural petal carries two independent true1D strip faces.
It is not attached to an unmodelled load-bearing rail. Human approval and full
plate/joint/thermal/hydraulic qualification remain pending; production is unchanged.

```sh
python3 -B -m unittest discover -s tools/long_strip_endcap -p 'test_*.py' -v
python3 -B tools/long_strip_endcap/export.py --output build/long-strip-endcap/compact
```

First apply the acts-spack skill/preflight and verify actual runtime/datasets.
In the SAME activated shell, source thisdd4hep.sh and geant4.sh, then:

```sh
cmake -S prototypes/long_strip_endcap -B build/long-strip-endcap/native -DCMAKE_BUILD_TYPE=Release
cmake --build build/long-strip-endcap/native -j 6
ctest --test-dir build/long-strip-endcap/native --output-on-failure
python3 -B tools/long_strip_barrel/check_root.py \
  --root build/long-strip-endcap/native/native.root \
  --expected build/long-strip-endcap/native/compact/expected.json \
  --output build/long-strip-endcap/root-roundtrip.json
```

Expose the native directory on DD4HEP_LIBRARY_PATH, LD_LIBRARY_PATH and
DYLD_LIBRARY_PATH before DDSim. The shared factory groups physical pieces by
petal to bound ROOT voxel memory; grouping does not change their transforms.

```sh
python3 "$(command -v ddsim)" --compactFile build/long-strip-endcap/native/compact/long-strip.xml \
  --runType batch --numberOfEvents 1 --enableGun --gun.particle mu- \
  --gun.position '1000,0,0' --gun.direction '0,0,1' --gun.energy '10*GeV' \
  --physics.list FTFP_BERT --random.seed 42 --outputFile build/long-strip-endcap/geant4-positive.root \
  > build/long-strip-endcap/geant4-positive.log 2>&1
```

Repeat with direction0,0,-1 and a distinct negative output/log. The displaced
zero-field gun is a transport fixture crossing six discs, not an IP acceptance
sample. Using Python with NumPy/uproot/Matplotlib, use the shared saved-hit
checker with `--layers 0 1 2 3 4 5` or `--layers 6 7 8 9 10 11` for each signed
end; it still requires both faces of one identical pair in EVERY target layer.
Run `coverage.py --output build/long-strip-endcap/coverage.json` and
`draw.py --expected ... --output docs/design/figures`. Coverage uses fixed old
datums/annulus, first traversal in vacuum, BOTH faces of the SAME pair and an
independent finite-plane oracle. Software PASS does not certify coverage.

The service corridor contains the pinned barrel loads PLUS all upstream endcap
loads. The endcap compact REPLACES the standalone barrel trunk representation;
simply overlaying both prototypes double-counts the shared corridor. Reference
packing and adverse/gross-cable controls keep the same service bounds. Raw XML,
ROOT and runtime logs are ignored under build/. Curated reports/hashes retain
both rejected attempts and actual dirty execution revisions. See DES-023 and
its results for the first-disc coverage loss, narrow inner contact, horizontal
handling failure, warm LV and lateral thermal failures and outstanding plate/thermal qualifications.
