# Reusable LAr periods: placement and initialization investigation

**DRAFT / PROTOTYPE**, requested on 2026-11-13 before continuing the 10k response
comparison. Governing inputs are DES032/DES033 and the
[placement investigation](../../design/inputs/DES-032-lar-placement-initialization.md).
The legacy assembly hierarchy remains the default.

The optional `--real-periods` export replaces the repeated assembly with a real
logical mother for each inclined barrel or turbine period. The envelope follows
the existing outer absorber faces and annular/axial clipping. All existing
material pieces fill it. Its material is the actual enclosing material; it adds
no intended material layer. The same logical mother is reused for all matching
periods. This is the LAr counterpart of the
[Si–W real-wedge investigation](../siw-real-wedge-default/README.md).

## Evidence and measured scope

The matched first-event timings and exact run receipts are retained in
[results.json](results.json), with [runtime identities](environment.json).

| Quantity | Assembly reference | Real-period candidate |
| --- | ---: | ---: |
| Time to first actual event | 522.258 s | 67.383 s |
| DDG4 volume-map build | 3.858 s | 0.195 s |
| Whole seven-event probe, including audit/shutdown | 529.554 s | 70.844 s |
| Peak child RSS | 5.538 GiB | 2.417 GiB |
| Geant4 physical-volume objects | 283,751 | 115,735 |
| Assembly imprints | 174,644 | 6,516 |

The observed time-to-first-event ratio is **7.75**; the volume-map ratio is
**19.79**. These are measurements from one sequential pair on the same node.
Implementation source is `8d74a4c1221a19d314881c4deccb2b5986ff425d`; the matched
probe source is `f91578eb3b39e1e2ba52d76af38368bd38501128`. Documentation was in
progress, and each run verified its launch source/configuration/library hashes
were unchanged at exit.

The primary metric
is **child launch to first ParticleHandler event-begin message in the audited,
ECAL-only serial probe**. It includes the same fixed inventory/native-map audit
overhead for both geometries. It is not isolated voxelization or shower throughput.
The seven identical gun cases cover the barrel and each turbine wheel on both
ends, using 20 GeV momentum electrons from the origin, phi0.123, eta0.5 and
±3.0/±2.2/±1.6. Both models use the same two factory libraries, one worker,
FTFP_BERT, 0.7 mm range cut, output and seed policy.

Completed geometry checks:

- Removing only four optional envelope declarations restores the complete
  original XML tree, including all readouts, pieces, services and replica poses.
- All **43,648 raw sensitive IDs** and **274,689 terminal material-leaf records**
  have identical full-dump hashes between assembly and real-period Geant4 trees.
  Dumps include poses and material names/densities; the separate native shape
  and material checks cover what those dumps do not serialize.
- Native barrel/endcap checks preserve **3,488,768 logical cells**, all canonical
  reference keys and the checked raw/canonical inverse mappings.
- Barrel, endcaps and complete ECAL union pass ROOT containment/overlap checks
  at **10 nm**, with zero reported overlaps or extrusions. The union retains
  **405** material/active-path rays; the component checks retain their own rays.
- A separate matched **65-ray** comparison has zero differences in per-material
  path length, radiation lengths and interaction lengths.
- Seven real-period electron events pass saved-primary, canonical-ID and aimed
  barrel/wheel/side hit checks. Full event data remain local.

Both members of the final pair passed all seven saved-event checks. Their cell
counts and summed sensitive energies also agree exactly in these smoke cases;
that observation does not establish general shower-response equivalence.

The new pure-Python controls check envelope partition, face adjacency, XML
preservation and invalid/missing geometry inputs. The existing LAr controls are
also retained: all **37** standard-library controls pass. Mother-minus-daughter volume residuals are numerical, with the
largest relative residual about7e-14; they are not an added material allowance.

## Timing interpretation

The DDG4 map-build interval is parsed from its actual begin/end messages.
Calling the map getter later is a cached access and is reported separately.
Likewise `/run/initialize` and a zero-event `/run/beamOn 0` do not capture the
large delay observed before the first actual event. The actual-event pair is
therefore required for the primary initialization comparison.

One clean sequential pair supports a descriptive measured comparison, with no
timing confidence interval or claim of stable production speedup. Earlier zero-
event setup probes and a preliminary candidate smoke are diagnostic runs,
separate from that pair. The failed twelve-worker response pilot is a different
configuration and is not used as the baseline. Twelve-worker initialization,
shower-response equivalence and the 10k campaign remain later work.

New mother boundaries can alter stochastic shower histories even when material,
poses and readout are equivalent. This study supplies no digitization, response
calibration, engineering acceptance or human design sign-off.

## Reproduce

Use the existing node-verified Spack runtime through `software/env/run.sh`.
Recheck the node preflight and actual imports/datasets; recorded fingerprint
drift was resolved by runtime verification, without changing shared software.
The measured runtime is DD4hep1.38, Geant411.4.3 and ROOT6.40.04.

Start with a fresh output directory. The maintained LAYOUT002 export is the
assembly reference; the probe removes only tracker/beam-pipe detector roots and
unused readouts to make the ECAL-only fixture.

```sh
work=build/lar-placement-repeat
python3 -B tools/calorimeter_baselines/export.py --layout LAYOUT-002 --output "$work/layout002"
software/env/run.sh cmake -S prototypes/calorimeter -B "$work/factories" -G Ninja -DCMAKE_BUILD_TYPE=Release
software/env/run.sh cmake --build "$work/factories" --parallel 3 --target Components_nODDLArBarrelPrototype Components_nODDLArEndcapPrototype
libs=(--library "$work/factories/libnODDLArBarrelPrototype.dylib" --library "$work/factories/libnODDLArEndcapPrototype.dylib")
software/env/run.sh python3 -B tools/lar_calorimeter/placement_probe.py --compact "$work/layout002/detector.xml" "${libs[@]}" --output "$work/stock-smoke1" --smoke
software/env/run.sh python3 -B tools/lar_calorimeter/placement_smoke.py "$work/stock-smoke1"
python3 -B tools/lar_calorimeter/barrel_export.py --output "$work/barrel-final" --services tools/lar_calorimeter/barrel_services.py --real-periods
python3 -B tools/lar_calorimeter/endcap_export.py --output "$work/endcaps-final" --services tools/lar_calorimeter/endcap_services.py --real-periods
python3 -B tools/lar_calorimeter/placement_variant.py --source "$work/stock-smoke1/detector.xml" --barrel "$work/barrel-final/barrel.xml" --endcaps "$work/endcaps-final/endcaps.xml" --output "$work/candidate-v2"
software/env/run.sh python3 -B tools/lar_calorimeter/placement_probe.py --compact "$work/candidate-v2/detector.xml" "${libs[@]}" --output "$work/candidate-smoke2" --smoke
software/env/run.sh python3 -B tools/lar_calorimeter/placement_smoke.py "$work/candidate-smoke2"
python3 -B -m unittest discover -s tools/lar_calorimeter -p 'test*.py' -v
```

Use the platform's shared-library suffix. Complete the component/union native
checks and matched [material rays](../siw-real-wedge-default/material_rays.py):

```sh
software/env/run.sh python3 -B tools/lar_calorimeter/barrel_native.py --compact "$work/barrel-final/barrel.xml" --expected "$work/barrel-final/expected.json" --library "$work/factories/libnODDLArBarrelPrototype.dylib" --output "$work/barrel-final/native.json"
software/env/run.sh python3 -B tools/lar_calorimeter/endcap_native.py --compact "$work/endcaps-final/endcaps.xml" --expected "$work/endcaps-final/expected.json" --library "$work/factories/libnODDLArEndcapPrototype.dylib" --output "$work/endcaps-final/native.json"
python3 -B tools/lar_calorimeter/combined_native.py build --barrel-compact "$work/barrel-final/barrel.xml" --barrel-expected "$work/barrel-final/expected.json" --endcap-compact "$work/endcaps-final/endcaps.xml" --endcap-expected "$work/endcaps-final/expected.json" --directory "$work/combined-final"
software/env/run.sh python3 -B tools/lar_calorimeter/combined_native.py audit --directory "$work/combined-final" --barrel-library "$work/factories/libnODDLArBarrelPrototype.dylib" --endcap-library "$work/factories/libnODDLArEndcapPrototype.dylib" --output "$work/combined-final/native.json"
software/env/run.sh python3 -B docs/validation/siw-real-wedge-default/material_rays.py trace "$work/stock-smoke1/detector.xml" "$work/stock-rays.json" "$work/factories/libnODDLArBarrelPrototype.dylib" "$work/factories/libnODDLArEndcapPrototype.dylib"
software/env/run.sh python3 -B docs/validation/siw-real-wedge-default/material_rays.py trace "$work/candidate-v2/detector.xml" "$work/candidate-rays.json" "$work/factories/libnODDLArBarrelPrototype.dylib" "$work/factories/libnODDLArEndcapPrototype.dylib"
python3 -B docs/validation/siw-real-wedge-default/material_rays.py compare "$work/stock-rays.json" "$work/candidate-rays.json" "$work/ray-comparison.json"
```

Then collect:

```sh
python3 -B tools/lar_calorimeter/placement_report.py --work "$work" --output "$work/results.json"
```

The collector rehashes logs, inventories and all smoke ROOT files, requires
matching primary cases/configuration/library identities, checks native/ray
gates, and binds the exact compact variant. Full compacts, ROOT, per-leaf dumps
and full logs stay ignored locally; compact receipts, counts and hashes support
review without committing those payloads.
