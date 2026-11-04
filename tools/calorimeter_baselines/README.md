# Two ECAL working baselines

Select the ECAL while keeping the maintained DES043 tracker:

```sh
python3 -B tools/calorimeter_baselines/export.py --layout LAYOUT-001 --output build/baselines/01
python3 -B tools/calorimeter_baselines/export.py --layout LAYOUT-002 --output build/baselines/02 \
  --tracker-compact build/baselines/01/components/tracker/tracker.xml
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
