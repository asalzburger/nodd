# Standalone segmented HCAL around the restored LAr ECAL

This is the isolated DRAFT/PROTOTYPE implementation of [DES045](../../docs/design/DES-045-hcal-restored-ecal-pion50.md). It does not change the maintained tracker+ECAL entry point or regenerate historical DES036–038 evidence.

```sh
python3 -B tools/hcal_response/export.py --output build/hcal-response/geometry
python3 -B -m unittest discover -s tools/hcal_response -p 'test_*.py' -v
# In the reverified DD4hep environment:
cmake -S prototypes/hcal_response -B build/hcal-response/factories -G Ninja
cmake --build build/hcal-response/factories --parallel 3
python3 -B tools/hcal_response/native.py \
  --directory build/hcal-response/geometry \
  --library build/hcal-response/factories/libnODDHCALResponsePrototype.dylib \
  --output build/hcal-response/native.json
```

Use the actual platform library suffix. Exported XML, placements CSV, expected manifest, native report, simulation and ROOT files remain ignored under `build/`. Production run/analysis recipes are in [software/analysis/hcal_response](../../software/analysis/hcal_response/README.md).

The 60 repeats preserve 30 mm sector-owned Steel235, the unchanged 12 mm common carrier, a 1 mm installation allowance, and a 10 mm rear cover: 2590 mm normal depth. Barrel front/outer apothems are 3130/5720 mm, half-length 6260 mm; endcaps span abs(z)=6760–9350 mm with inner/outer apothems 300/5710 mm. The 5950 mm radial handoff is an empty allocation. Whole carriers and all source material/part shapes are retained; board/tile clipping is not used. Collector gaps remain empty and external services are unimplemented.

The complete arrangement has 292112 carriers and 21032064 logical tiles. A balanced boolean union combines the 72 **disjoint, individually recessed original scintillator cores** in each carrier into one sensitive solid. Passive skins, reflectors, SiPM/LED packages, boards, cooling, contacts and the copper plate retain their original shapes, materials and poses. This is an exact geometry/hierarchy optimization for raw energy transport, not a continuous sensitive sheet or an effective material. Every boolean node uses an identity left transform and a relative right transform, as required by DDG4 native boolean conversion. The final active-volume placement carries the first-core anchor. Custom segmentation maps the actual component at an active-volume-local point to its original module/sensor address and returns its core-plane reference position. The 72 original logical cells remain distinct; the raw volume-context count is 292112. No optical response is simulated.

The descriptor is `system:8,side:2,sector:4,layer:6,carrier:12,module:2,sensor:6,x:-1,y:-1`. Roots are HCALBarrel/system13 and HCALEndcaps/system14; sides are 0 barrel, 1 positive and 2 negative endcap. Sector/layer/carrier are physical-placement fields; module/sensor are segmentation fields; x/y remain zero. The active-volume frame is anchored at the first core: (−168,−87,−4) mm from the carrier Box centre, equivalently (−168,−87,2) mm from the original carrier front. Its module0/sensor0 reference is (0,0,0), module1/sensor0 is (186,0,0), and row/column spacing is 30 mm. Segmentation reference positions are relative to this explicitly placed active frame; absolute tile positions remain unchanged. The placements CSV stores the original front-face origins and row-basis world frames explicitly. Its system/side/sector/layer/carrier fields uniquely identify each raw sensitive volume.

The endcap packing is fourfold: a sixteen-sector address scheme does not imply a sixteenfold physical response symmetry. Negative-end frames have determinant +1 and transform (x,y,z)→(x,−y,−z) relative to their matched positive-end placements.

ROOT checks establish the native geometry and segmentation only. The transport worker audit separately compares converted Geant4 sensitive-solid membership against the original physical tile union; it also checks positive sensitive-step, native-hit and saved-hit energy closure. A ROOT probe pass alone does not establish Geant4 conversion equivalence.

The native auditor binds artifact hashes, checks all 71 boolean nodes for identity left transforms and logarithmic depth, checks every balanced-union leaf against the original DES036 primitive/cut dimensions and pose, compares core/recess/boundary/gap/random containment and cell IDs, checks exact disjoint-core volume, counts expanded raw contexts from the reusable native DAG, runs ROOT overlap tests at 10 nm once per distinct mother, and traces 68 bounded IP material rays through both systems. `--skip-overlaps` and `--skip-rays` create explicitly partial reports. A numerical overlap check is not mechanical or shower-containment qualification. Steel depth in interaction lengths must distinguish the source's pure-Fe screening estimate from actual native Steel235 path results.
