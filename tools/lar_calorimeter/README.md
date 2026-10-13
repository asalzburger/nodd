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
