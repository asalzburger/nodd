# LAYOUT-002 isolated ALLEGRO-style LAr prototypes

DES032 is DRAFT / PROTOTYPE. Production geometry and SiW LAYOUT-001 are
untouched. Python standard library exports and tests the own geometry; native
checks use the verified existing DD4hep/Geant4 runtime. Public k4geo sources
supply parameters, with explicit nODD deviations; no external factory/package
is imported.

```sh
python3 -B -m unittest discover -s tools/lar_calorimeter -p 'test*.py' -v
python3 -B tools/lar_calorimeter/services.py --output build/lar-services.json
python3 -B tools/lar_calorimeter/barrel_export.py --output build/lar-barrel \
  --services tools/lar_calorimeter/barrel_services.py
# Activate verified acts-spack, thisdd4hep.sh and geant4.sh in the same shell.
cmake -S prototypes/calorimeter -B build/lar-native
cmake --build build/lar-native --target nODDLArBarrelPrototype
python3 -B tools/lar_calorimeter/barrel_native.py \
  --compact build/lar-barrel/barrel.xml --expected build/lar-barrel/expected.json \
  --library build/lar-native/libnODDLArBarrelPrototype.dylib \
  --output build/lar-barrel/native.json
```

Linux uses .so. Core-only export omits --services. Native material mass uses
actual native polygon/circular boundaries, explicit mother displacement and
material fractions; stochastic ROOT Boolean Capacity is not exact evidence.
All raw volume IDs are separate from canonical merged cells. Signed theta bins
support the longer nODD barrel and are not the source's unsigned10-bit scheme.
All2,976 shared reference keys are checked inside actual active LAr; symmetry
derives the full2.286million count. TGeoTubeSeg is accepted only for full360°
tubes; native extrusions must have exactly two unshifted, unit-scale sections.

External cables, jackets and FCal space are empty planning reservations. Board
and coolant material proxies are explicit and do not qualify thermal/structural
behaviour. Endcaps and complete LAYOUT-002 are the dependent DES033 PR.

## Turbine endcaps and actual ECAL union (DES033)

```sh
python3 -B tools/lar_calorimeter/endcap_export.py --output build/lar-endcaps \
  --services tools/lar_calorimeter/endcap_services.py
cmake --build build/lar-native  # Includes DD4hep component-map targets for DDSim
python3 -B tools/lar_calorimeter/endcap_native.py \
  --compact build/lar-endcaps/endcaps.xml --expected build/lar-endcaps/expected.json \
  --library build/lar-native/libnODDLArEndcapPrototype.dylib \
  --output build/lar-endcaps/native.json
python3 -B tools/lar_calorimeter/endcap_transport.py fixtures \
  --compact build/lar-endcaps/endcaps.xml --expected build/lar-endcaps/expected.json \
  --output build/endcap-smoke
# Add build/lar-native to the active runtime's library search path.
python3 -B tools/lar_calorimeter/endcap_transport.py run --directory build/endcap-smoke/side1
python3 -B tools/lar_calorimeter/endcap_transport.py check \
  --directory build/endcap-smoke/side1 --output build/endcap-smoke/side1/transport.json
# Repeat run/check for side2.
python3 -B tools/lar_calorimeter/combined_native.py build \
  --barrel-compact build/lar-barrel/barrel.xml --barrel-expected build/lar-barrel/expected.json \
  --endcap-compact build/lar-endcaps/endcaps.xml --endcap-expected build/lar-endcaps/expected.json \
  --directory build/combined-ecal
python3 -B tools/lar_calorimeter/combined_native.py audit --directory build/combined-ecal \
  --barrel-library build/lar-native/libnODDLArBarrelPrototype.dylib \
  --endcap-library build/lar-native/libnODDLArEndcapPrototype.dylib \
  --output build/combined-ecal/native.json
```

Turbine lead1.1mm is the source1.3mm total absorber minus glue/steel, followed
by nODD's explicit thicker steel amendment. The native ray reference intersects
actual expected face planes/circles independently of ROOT navigation. The
complete ECAL-only audit includes405 rays and physical services; there is no
tracker/magnet/HCAL/FCal construction or field. Sparse saved-hit fixtures retain
all three wheels with one physical period per wheel, on each proper signed end.
Cartesian lead taper, equivalent walls/unported rear support, cold-board proxies
and adverse heat limits remain explicit. No charge-response/ACTS/jet claim.

```sh
python3 -B tools/lar_calorimeter/plot_endcaps.py --combined build/combined-ecal/native.json \
  --expected build/lar-endcaps/expected.json --output docs/design/figures/DES-033
python3 -B tools/layout_overview/draw002.py
python3 -B tools/layout_overview/draw002.py --check
```
