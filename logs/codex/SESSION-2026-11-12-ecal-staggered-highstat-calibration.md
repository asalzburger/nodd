# Staggered ECAL high-statistics calibration

User: “ok, let's do this”, then “Let's focus on the staggered geometry, as it gives some improvement already”. This authorizes existing10k learning curves, revised training-only closure/calibration,100k newtraining and20k newindependent validation,12DDSimthreads, diskplanning, onlystaggeredgeometry. Existing source/results remainunchanged. Isolated PROTOTYPE, no geometrychanges or designacceptance. Start e9aabc83d3c8aa4127d1bcd824db0a134e69e7b0; dedicatedbranch codex/ecal-staggered-highstat-calibration. Current exacttoken counters unavailable; usageempty,notzero.

Using nodd-coordinate, nodd-design-evidence, nodd-review-validation and acts-spack skills. Preflight changed setup/lock fingerprints disclosed before dependentwork; runtime doctor underway.375GiBavailable, conservative2x120koutput+30GiBreserve fits. RawROOT/features/ledgers remainlocalignored. MandatorydraftPR publication follows accepted projectworkflow; user previouslyexplicitlyapproved publicationofcalibration source,compactresultsandplots toasalzburger/nodd.

## Recorded specialist contracts before dispatch

```json
{
  "id": "ECAL-HIGHSTAT-PHYSVAL-PROTOCOL",
  "role": "PhysVal",
  "input_revision": "e9aabc83d3c8aa4127d1bcd824db0a134e69e7b0",
  "inputs": [
    "docs/validation/ecal-staggering/protocol.md",
    "docs/validation/ecal-staggering/results/summary.json",
    "software/analysis/calorimeter_digitization/staggered_calibration.py",
    "software/analysis/calorimeter_digitization/staggered_features.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "User authorizes learning curve, improved train-only-closure calibration,100k training+20k fresh independent validation electrons and steers staggered geometry ONLY. Freeze practical prospective protocol before fit/new validation inspection. Advise model family with no new dependencies (NumPy additive splines/interactions ridge is likely), learning curves on old10k with same heldoutfolds, hyperparameter selection on new train only, separately heldout closure subset, untouched fresh20kvalidation. Consider keeping100kuniform E10-80 eta-3..3 phi full; optionalgap oversampling only if accounted and declared in advance. Primary vs frozen original10featuremodel and raw, allinclusive means/CV/tails/zeros/clipping, energy-slices,10eta/10foldphi, finitefixed-energy checks not intrinsicresolution. Need feasible training+test uncertainty accounting without enormous repeatedmodelsearch. Return early constraints/recommendations; later exact-source/result review. No fits/simulation/writes/delegation/publication.",
  "deliverable": "Prospective statistical/model/sample protocol and independent review boundaries.",
  "completion": "Return concrete choices/risks promptly; no human acceptance."
}
```

```json
{
  "id": "ECAL-HIGHSTAT-SOFTENG-PIPELINE",
  "role": "SoftEng",
  "input_revision": "e9aabc83d3c8aa4127d1bcd824db0a134e69e7b0",
  "inputs": [
    "software/analysis/calorimeter_digitization/angular_sample.py",
    "software/analysis/calorimeter_digitization/angular_analyze.py",
    "software/analysis/calorimeter_digitization/staggered_features.py",
    "build/ecal-staggering/production-input/sample.json",
    "build/ecal-staggering/production12/readback.json"
  ],
  "mode": "write",
  "writable_paths": [
    "software/analysis/calorimeter_digitization/highstat_sample.py",
    "software/analysis/calorimeter_digitization/highstat_readback.py",
    "software/analysis/calorimeter_digitization/test_highstat_pipeline.py"
  ],
  "task": "Implement bounded reproducible large-sample pipeline ONLY for unchanged frozenstaggered geometry. Need100ktraining+20knewindependentvalidation,12DDSimworkers,375GiBavailable; measured1.26MB/event allows2x120k+30GiB~312GiB. Prefer12 separate10kbatches, freshsample manifests/inputs, disjoint seeds and campaignglobalIDs, uniformE10-80 eta-3..3 phi full; no old10kreuse in newtrain/test. No geometrychange; pinXMLd78ece.../libraries. Reuse angular_sample.run for each10k with distinct seed; preserve allraw artifacts and diskguard. Implement generator/manifest first and message main promptly so simulation starts. Then fast combined nativeC++ hit audit plus feature accumulation/probes perbatch to avoid Python per-hit loops and duplicateROOT passes (originalreadback6min/10k). Could reuse staggered_features.NATIVE cells/masks and C++ supplemental audit to validateIDunique/system/finitepositiveenergy/layer/positions, retain exact primary/worker/audit/input checks and ledger to match original. Output samefeatureNPZkeys per10k and receiptboundJSON, plus event-summary/readback compatible original; fieldsno truthinference. Add meaningfulcontrols including fast/old audit equivalence on existing24pilot/current10k or boundedsubset; do not weakenchecks. Main ownsprotocol/newcalibration/LC/results/docs and runs. Do not edit shared angular_*/staggered_* sources, no runs until runtime doctor mainconfirmation. No delegation/publication/signoff. Deliver generatorfirst, then auditable fastreadback withactualtests. Caninspect ROOTinstalledheaders after existingacts-spack preflight only; no new deps.",
  "deliverable": "Batch primary preparation, efficient full native audit/features and narrow regression controls; exact commands/hashes/limitations.",
  "completion": "Source plus tests and ready-to-run recipe, within ownedfiles only."
}
```


SoftEng contract corrected before dispatch: local build inputs are supplemental, committed input set uses docs/validation/ecal-staggering/geometry-and-run.json. Runtime doctor exit0.
```json
{
  "id": "ECAL-HIGHSTAT-SOFTENG-PIPELINE",
  "role": "SoftEng",
  "input_revision": "e9aabc83d3c8aa4127d1bcd824db0a134e69e7b0",
  "inputs": [
    "software/analysis/calorimeter_digitization/angular_sample.py",
    "software/analysis/calorimeter_digitization/angular_analyze.py",
    "software/analysis/calorimeter_digitization/staggered_features.py",
    "docs/validation/ecal-staggering/geometry-and-run.json"
  ],
  "mode": "write",
  "writable_paths": [
    "software/analysis/calorimeter_digitization/highstat_sample.py",
    "software/analysis/calorimeter_digitization/highstat_readback.py",
    "software/analysis/calorimeter_digitization/test_highstat_pipeline.py"
  ],
  "task": "Implement bounded reproducible large-sample pipeline ONLY for unchanged frozenstaggered geometry. Need100ktraining+20knewindependentvalidation,12DDSimworkers,375GiBavailable; measured1.26MB/event allows2x120k+30GiB~312GiB. Prefer12 separate10kbatches, freshsample manifests/inputs, disjoint seeds and campaignglobalIDs, uniformE10-80 eta-3..3 phi full; no old10kreuse in newtrain/test. No geometrychange; pinXMLd78ece.../libraries. Reuse angular_sample.run for each10k with distinct seed; preserve allraw artifacts and diskguard. Implement generator/manifest first and message main promptly so simulation starts. Then fast combined nativeC++ hit audit plus feature accumulation/probes perbatch to avoid Python per-hit loops and duplicateROOT passes (originalreadback6min/10k). Could reuse staggered_features.NATIVE cells/masks and C++ supplemental audit to validateIDunique/system/finitepositiveenergy/layer/positions, retain exact primary/worker/audit/input checks and ledger to match original. Output samefeatureNPZkeys per10k and receiptboundJSON, plus event-summary/readback compatible original; fieldsno truthinference. Add meaningfulcontrols including fast/old audit equivalence on existing24pilot/current10k or boundedsubset; do not weakenchecks. Main ownsprotocol/newcalibration/LC/results/docs and runs. Do not edit shared angular_*/staggered_* sources, no runs until runtime doctor mainconfirmation. No delegation/publication/signoff. Deliver generatorfirst, then auditable fastreadback withactualtests. Caninspect ROOTinstalledheaders after existingacts-spack preflight only; no new deps. Existing local source files build/ecal-staggering/production-input and production12 are supplemental hash-bound inputs from committed geometry-and-run.json. Runtime doctor nowPASS 2026-11-12; mainauthorizes dependent runtimechecks.",
  "deliverable": "Batch primary preparation, efficient full native audit/features and narrow regression controls; exact commands/hashes/limitations.",
  "completion": "Source plus tests and ready-to-run recipe, within ownedfiles only."
}
```
