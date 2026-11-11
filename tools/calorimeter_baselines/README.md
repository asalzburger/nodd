# Two ECAL working baselines

Select the ECAL while keeping the maintained DES043 tracker:

```sh
python3 -B tools/calorimeter_baselines/export.py --layout LAYOUT-001 --output build/baselines/01
python3 -B tools/calorimeter_baselines/export.py --layout LAYOUT-002 --output build/baselines/02
cmake -S prototypes/calorimeter -B build/baselines/factories -G Ninja
cmake --build build/baselines/factories --parallel 3
python3 -B -m unittest discover -s tools/calorimeter_baselines -p 'test_*.py' -v
```

Run CMake/native jobs in the reverified project Spack environment. The tracker
factory is built separately using its existing recipe. `detector.xml` contains
the tracker and the selected complete ECAL components, including their local
services. `baseline.json` records source compact/material hashes, actual system
mapping and the construction stage of the other systems. Generated XML, expected
manifests and native output stay under ignored `build/`.

LAYOUT-001 places the Si–W hardware inside reusable barrel and endcap wedges.
The new mothers use the enclosing material and preserve the existing replica
poses and cell IDs. Standalone Si–W exports keep the legacy assembly form by
default for the component validation and fixture tools. Pass `--real-wedges`
to either standalone Si–W exporter to select the baseline hierarchy.

The standalone Si–W endcap system8 becomes9 only in the combined output. Beam-pipe0 and tracker
systems1–7, Si–W barrel8 and LAr10/11 remain. FCAL12 and HCAL13/14 are reserved
for later integration, preserving the original standalone proposals. Material
definitions and references receive consistent component namespaces; all maintained tracker material/element names remain unchanged, including hardcoded Beryllium. Component Air/Vacuum are namespaced too; duplicate readouts/root IDs and conflicting recipes fail closed.

The common EDM4hep I/O and algorithm skeletons are built independently under
`software/source/ActsExamples/Calorimeter`. They provide the initial data and
configuration interfaces. Executing digitization/clustering explicitly fails
until physical algorithms are supplied; this restoration does not calibrate
hits or clusters.

See the [integration contract and retained review questions](../../docs/design/inputs/ECAL-baseline-integration-2026-11-04.md).
The shared solenoid allocation, HCAL design options and ROOT-only FCAL design
are recorded honestly rather than inserted as fictitious active detector volumes.
Combined detector response, field and engineering qualification remain later work.

Each CLI invocation regenerates the maintained tracker and records its producer, configuration and compact/material/expected hashes. Reusing an arbitrary pre-exported tracker is unsupported. The lower-level composition helper labels an unverified supplied tracker as such.

## Native union check

Build only the existing tracker factories and audit each complete tracker/ECAL
union at the same10nm numerical tolerance used by the component audits:

```sh
source software/env/truth_tracking.sh
cmake -S . -B build/baselines/tracker-factories -G Ninja -DBUILD_TESTING=OFF
cmake --build build/baselines/tracker-factories --parallel 3 --target \
  nODDPixelBarrel nODDBeamPipe nODDShortStripBarrel nODDShortStripEndcap nODDLongStrip
tracker_libraries=(
  --library build/baselines/tracker-factories/detector/libnODDPixelBarrel.dylib
  --library build/baselines/tracker-factories/detector/libnODDBeamPipe.dylib
  --library build/baselines/tracker-factories/detector/libnODDShortStripBarrel.dylib
  --library build/baselines/tracker-factories/detector/libnODDShortStripEndcap.dylib
  --library build/baselines/tracker-factories/detector/libnODDLongStrip.dylib
)
python3 -B tools/calorimeter_baselines/native.py --directory build/baselines/01 \
  "${tracker_libraries[@]}" \
  --library build/baselines/factories/libnODDCalorimeterPrototype.dylib \
  --output build/baselines/01/native.json
python3 -B tools/calorimeter_baselines/native.py --directory build/baselines/02 \
  "${tracker_libraries[@]}" \
  --library build/baselines/factories/libnODDLArBarrelPrototype.dylib \
  --library build/baselines/factories/libnODDLArEndcapPrototype.dylib \
  --output build/baselines/02/native.json
```

These are the verified macOS library suffixes; use the platform's actual shared
library paths elsewhere. The scans inspect the actual ROOT overlap collection,
check all native root IDs against the integration map, and retain launch source,
compiled-library and compact/material fingerprints. Full scans can take a long
time for these complete assemblies. A construction pass is distinct from an
overlap result, and neither establishes response or engineering acceptance.
