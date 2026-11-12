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

