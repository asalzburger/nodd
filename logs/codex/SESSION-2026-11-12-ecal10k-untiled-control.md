# SESSION-2026-11-12-ecal10k-untiled-control — Continuous silicon control

User requests an un-tiled ECAL with full silicon across sectors, identical 10k electron inputs and an overlaid response-width comparison. Isolated PROTOTYPE under DES-030/031; no production design changes. Baseline source b9f5af38520ea83215587757b02cd090adc8fb8a.

The coordinator owns comparison/analysis, protocol, execution, metadata and publication. Assignments are explicit generic-agent role instructions, not native profile loading.

```json
{
  "id": "UNTILED-SOFTENG",
  "role": "SoftEng",
  "input_revision": "b9f5af38520ea83215587757b02cd090adc8fb8a",
  "inputs": [
    "prototypes/calorimeter/BarrelCalorimeter.cpp",
    "prototypes/calorimeter/EdgeCalorimeter.cpp",
    "tools/calorimeter_hardware/barrel_export.py",
    "tools/calorimeter_hardware/edge_export.py",
    "docs/validation/ecal10k/protocol.md"
  ],
  "mode": "write",
  "writable_paths": [
    "software/analysis/calorimeter_digitization/untiled_geometry.py",
    "software/analysis/calorimeter_digitization/test_untiled_geometry.py"
  ],
  "task": "Implement isolated preparation of continuous 0.5 mm silicon slabs over entire sector faces, barrel and both endcaps, using original retained XML and SAME primary/input files. Investigate existing XML factories; prefer XML-only transformation and unchanged native plugin. Remove original active/guard silicon, fill complete sector planes including tiling gaps, leave absorber and passive geometry unchanged except subtract intersections where necessary to avoid silicon overlaps. Preserve layer pitch, silicon plane, beam aperture, sector geometry, and other physics. Use extended CartesianGridXY 5.5 mm virtual readout IDs if needed. Record exact material changes and geometry differences, validate counts/transforms/plane intersections, fail on unsupported source. Do not run full sample; deliver prep CLI and meaningful geometry checks. Own only two assigned Python files. Coordinate physical boundary choices before implementation. No commits.",
  "deliverable": "Return bounded contribution with source locators, actual checks and limits to coordinator.",
  "completion": "Resolve requested contribution or identify concrete unresolved inputs. Do not delegate or publish."
}
```

```json
{
  "id": "UNTILED-PHYSVAL",
  "role": "PhysVal",
  "input_revision": "b9f5af38520ea83215587757b02cd090adc8fb8a",
  "inputs": [
    "prototypes/calorimeter/BarrelCalorimeter.cpp",
    "prototypes/calorimeter/EdgeCalorimeter.cpp",
    "tools/calorimeter_hardware/barrel_export.py",
    "tools/calorimeter_hardware/edge_export.py",
    "docs/validation/ecal10k/protocol.md"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Assess prospective matched-input control: continuous sector silicon replacing tile/guard/gap losses with rest of structure kept. Determine defensible comparison sigma(R)/meanR using 10k identical primary IDs, 12 workers/seeds and joint paired bootstrap. Identify confounding of added silicon and seam/absorber losses. Return scientific control and uncertainty requirements; later exact source/result review will follow. No edits.",
  "deliverable": "Return bounded contribution with source locators, actual checks and limits to coordinator.",
  "completion": "Resolve requested contribution or identify concrete unresolved inputs. Do not delegate or publish."
}
```

```json
{
  "id": "UNTILED-CALOTECH",
  "role": "CaloTech",
  "input_revision": "b9f5af38520ea83215587757b02cd090adc8fb8a",
  "inputs": [
    "prototypes/calorimeter/BarrelCalorimeter.cpp",
    "prototypes/calorimeter/EdgeCalorimeter.cpp",
    "tools/calorimeter_hardware/barrel_export.py",
    "tools/calorimeter_hardware/edge_export.py",
    "docs/validation/ecal10k/protocol.md"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Inspect retained ECAL compact factories/export source for exact continuous silicon sector boundaries and passive intersections. User explicitly requests fictional full silicon slab across sectors. Recommend minimum physically unambiguous isolated control preserving W/passives except necessary silicon-plane replacement; distinguish module gaps, sector seams, service borders. Supply concrete geometry values/formulas and pitfalls to SoftEng/coordinator. No edits.",
  "deliverable": "Return bounded contribution with source locators, actual checks and limits to coordinator.",
  "completion": "Resolve requested contribution or identify concrete unresolved inputs. Do not delegate or publish."
}
```


## Frozen statistical source review

```json
{
  "id": "UNTILED-PHYSVAL-SOURCE",
  "role": "PhysVal",
  "input_revision": "20ba853eb8c7f0243dd6188b21987a9df4d4b900",
  "inputs": [
    "docs/validation/ecal10k-untiled/protocol.md",
    "software/analysis/calorimeter_digitization/untiled_compare.py",
    "software/analysis/calorimeter_digitization/untiled_native.py",
    "software/analysis/calorimeter_digitization/test_untiled_compare.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Independently review prospective control protocol and paired estimator/uncertainty implementation at exact source revision. Review code and run narrow tests if useful. No edits. Identify material scientific or validation defects before production; geometry preparation is still separate/in progress.",
  "deliverable": "Return bounded contribution with source locators, actual checks and limits to coordinator.",
  "completion": "Resolve requested contribution or identify concrete unresolved inputs. Do not delegate or publish."
}
```

## Prospective contributions and gates

UNTILED-CALOTECH at b9f5af38520ea83215587757b02cd090adc8fb8a derived the inherited full carrier bounds and independent sensitive silicon volume targets. This control preserves the 1 mm half-seam and beam aperture. It replaces active/guard wafers, fills service/module areas and removes only intersecting aluminium at the silicon planes. This is a material/coverage counterfactual, not an electronics threshold or pure virtual segmentation measurement. No cross-system envelope is extended.

UNTILED-PHYSVAL at the same baseline required paired primary identities and whole-event bootstrap indices, separate means/SDs/zeros, wide readout addressing, explicit support subtraction and native geometry gates. Same seeds do not imply identical transported shower histories.

UNTILED-PHYSVAL-SOURCE reviewed 20ba853eb8c7f0243dd6188b21987a9df4d4b900. Estimator and 40-width/20-difference covariance ordering were sound. A P2 null-width/CI plotting/subtraction issue was reproduced; the coordinator corrected it and added an all-zero-bin control. All three comparison tests pass. These technical assessments do not grant design acceptance.

Environment preflight flagged changed recorded setup/lock fingerprints; this was reported before dependent work. The installed-runtime doctor then passed DD4hep1.38/Geant4 11.4.3 and all dataset/import checks. No shared dependencies changed. Initial disk free was397GiB. Native construction on the prepared compact passed2304 sensitive sheets,2304 unique parent IDs,3136 wide-cell roundtrips and zero ROOT overlaps at1e-5mm. The native report pins actual script/library/XML hashes even though script additions were not yet committed.

The first24 matched primaries completed with12 workers in24.118s,30,643,802byte ROOT output and2,146,811,904byte peak RSS. All24 IDs/input truth/hits and all12 worker audits passed. Pilot projection at twice1,276,825.083bytes/event plus30GiB reserve requires53.783GiB, safely below currentfree. Native/input-dev compact SHA256852a6206fda380a40a1e1432aa9823021156bb129e314716bd64f3a18d475825. Pilot inputs remain retained separately.

## Frozen geometry and estimator review

```json
{
  "id": "UNTILED-PHYSVAL-FROZEN",
  "role": "PhysVal",
  "input_revision": "528db706de8a07c3cb39c2d12be758d8223fdd39",
  "inputs": [
    "docs/validation/ecal10k-untiled/protocol.md",
    "software/analysis/calorimeter_digitization/untiled_compare.py",
    "software/analysis/calorimeter_digitization/untiled_native.py",
    "software/analysis/calorimeter_digitization/untiled_geometry.py",
    "software/analysis/calorimeter_digitization/test_untiled_geometry.py",
    "software/analysis/calorimeter_digitization/test_untiled_compare.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Review frozen geometry preparation and paired comparison. Verify previous P2 nullable fix. Inspect retained prepared XML/native-dev.json/pilot12 readback as separately hash-bound runtime evidence (not committed inputs). Confirm full-sector scope, correct axes/identifiers, material changes and scientific limits. No writes. Full run is executing after successful native/pilot gates; report defects promptly.",
  "deliverable": "Return bounded contribution with source locators, actual checks and limits to coordinator.",
  "completion": "Resolve requested contribution or identify concrete unresolved inputs. Do not delegate or publish."
}
```

UNTILED-SOFTENG delivered the two owned Python files, ten passing geometry controls and a hash-identical native compact after a provenance-only preparer correction. The coordinator committed frozen implementation528db706de8a07c3cb39c2d12be758d8223fdd39 and prepared fresh production-input; its compact equals the native/pilot artifact. Full10k execution starts with the measured pilot disk budget and unchanged native libraries.

UNTILED-PHYSVAL-FROZEN independently reviewed528db706de8a07c3cb39c2d12be758d8223fdd39, verified the P2 fix and thirteen narrow controls, independently reproduced full silicon volumes/material changes, and checked native/pilot/production input hash bindings. No actionable material source finding. Native script bytes match the frozen source although its runtime report names precommitHEAD20ba853e, which remains explicit. This is a separate agent assessment, not human expertise/sign-off. Result review remains pending.

## Draft publication during execution

Published dedicated draftPR135 at https://github.com/asalzburger/nodd/pull/135, stacked on PR134. The interim body explicitly states fullproduction inprogress; results are pending readback. Only compact source/geometry evidence is published. Authenticated native Git/gh writes are used because connected GitHub write access was unavailable earlier in this session; connected tools read and refresh both PR discussions. PR134 and PR135 have no public comments at this capture. New Git object inspection finds no raw runs/ROOT/input/event ledgers; largestnewblob is the existing project register at~288kB.

Exact parent and child token counters are not exposed. Usage remains empty, not zero; historical journal totals are never attributed to this control.
