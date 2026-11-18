# Restored LAr EM baseline integration

2026-11-18. The project user selected the restored LAr prototype as the EM
working baseline. [Decision and limits](../../design/inputs/ECAL-baseline-selection-2026-11-18.md).
The selected geometry retains a **1000 mm warm-envelope barrel/endcap gap**;
the requested 400 mm gap is a separate subsequent prototype.

The default tracker+ECAL exporter now selects the explicit restored specification.
Fresh generated barrel/endcap compact and material files are byte-identical to
the validated restored control. Systems0–7/10/11, reusable period hierarchy,
27,456+9,856 raw sensitive contexts and3,182,528 logical ECAL channels are retained.
[Component identity receipt](component-identity.json) binds these claims and the
new union's own compact/material hashes. No old ECAL-only calibration or response
claim is relabelled as validated tracker+ECAL performance.

Eight composition/orchestration tests passed, including default restored
selection, explicit Si–W comparison, namespace/material/ID preservation and
rejection of an unexpected hierarchy. All retained tracker-overlay source
hashes match current source. Current R–Z bounds come from the fresh component
expected manifests; SVG/PNG were visually inspected. Historical FCAL/collar
routing is labelled as needing reassessment for the shifted HCAL context.

Native imports were reverified after the Spack setup/lock fingerprint warning:
ROOT6.40.04, DD4hep/DDG4 and Geant411.4.3. Current tracker factories and their
catalogs built successfully. The exact restored LAr factory libraries were reused.
The full native union audit constructs ten system roots and checks their IDs,
then scans overlaps at1e-5mm with seed114. [Native receipt](native.json): **PASS, ten systems, zero overlaps at1e-5mm**.
The export/run recorded an uncommitted working tree at9720c03a; exact exporter,
compact/material and factory hashes bind the executed source bytes. Those
geometry-producing bytes match the committed baseline implementation. This is
geometry integration evidence, not shower or engineering qualification.

## Reproduction

Use a fresh ignored directory and the existing verified Spack environment. No
dependency installation or particle transport is needed for baseline composition.
Native union checks include tracker+ECAL and local services, without a solenoid
field, HCAL or FCAL. Follow acts-spack preflight/reverification before native use.

```sh
python3 -B tools/calorimeter_baselines/export.py --output build/lar-em-baseline/selected
python3 -B -m unittest discover -s tools/calorimeter_baselines -p 'test_*.py' -v
software/env/run.sh cmake -S . -B build/lar-em-baseline/factories -G Ninja \
  -DBUILD_TESTING=OFF -DCMAKE_BUILD_TYPE=Release
software/env/run.sh cmake --build build/lar-em-baseline/factories --parallel 4 \
  --target Components_nODDPixelBarrel Components_nODDBeamPipe \
  Components_nODDShortStripBarrel Components_nODDShortStripEndcap Components_nODDLongStrip
software/env/run.sh cmake -S prototypes/calorimeter -B build/lar-em-baseline/lar-factories \
  -G Ninja -DCMAKE_BUILD_TYPE=Release
software/env/run.sh cmake --build build/lar-em-baseline/lar-factories --parallel 4 \
  --target Components_nODDLArBarrelPrototype Components_nODDLArEndcapPrototype
software/env/run.sh python3 -B tools/calorimeter_baselines/native.py \
  --directory build/lar-em-baseline/selected \
  --library build/lar-em-baseline/factories/detector/libnODDPixelBarrel.dylib \
  --library build/lar-em-baseline/factories/detector/libnODDBeamPipe.dylib \
  --library build/lar-em-baseline/factories/detector/libnODDShortStripBarrel.dylib \
  --library build/lar-em-baseline/factories/detector/libnODDShortStripEndcap.dylib \
  --library build/lar-em-baseline/factories/detector/libnODDLongStrip.dylib \
  --library build/lar-em-baseline/lar-factories/libnODDLArBarrelPrototype.dylib \
  --library build/lar-em-baseline/lar-factories/libnODDLArEndcapPrototype.dylib \
  --output build/lar-em-baseline/native.json
python3 -B tools/calorimeter_baselines/layout.py --baseline build/lar-em-baseline/selected \
  --input docs/layouts/LAYOUT-002-restored.json --output docs/layouts/figures/LAYOUT-002-restored-rz.svg
rsvg-convert docs/layouts/figures/LAYOUT-002-restored-rz.svg \
  -o docs/layouts/figures/LAYOUT-002-restored-rz.png
```

Use `.so` filenames on Linux. A replot from committed named inputs alone omits
`--baseline`; it does not need native dependencies. The input records actual
component hashes, source-byte maps, selection/specification and generator hashes.
Full model exports, expected inventories, libraries and native runtime logs stay
local. Existing librsvg2.62.3 renders the SVG; font versions can affect PNG pixels.
