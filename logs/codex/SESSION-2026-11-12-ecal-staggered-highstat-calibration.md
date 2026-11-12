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

## Exact source review

```json
{
  "id": "ECAL-HIGHSTAT-PHYSVAL-SOURCE",
  "role": "PhysVal",
  "input_revision": "e8c6dc1c1e46495aa46e1f630ec250120355cf77",
  "inputs": [
    "docs/validation/ecal-highstat/protocol.md",
    "software/analysis/calorimeter_digitization/highstat_model.py",
    "software/analysis/calorimeter_digitization/highstat_learning.py",
    "software/analysis/calorimeter_digitization/test_highstat_model.py",
    "docs/validation/ecal-highstat/learning/learning-curve.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Assess exact prospective spline/closure source and frozen-method LC. No freshvalidationperformance inspected. Verify truth-freeinference, knots/ranges/centering/training-onlyselection,70/15/15+85krefit, globalclosureincludingzeros, weightedquantile/bootstrap support, comparatorfairness. LC1/2/4/8k fixedouterfolds+3nestedsubsets+200fulljointrefits, all8kpredictionsbitidentical; observed32.35\u219232.22% width/mean~.919 flat. Main tests5PASS. Primary100k+20k transportbatchtrain000started after24/12pilotPASS. Noteprotocol now withinrolebootstrap/repeatedsearch, noenergy/logsecondary implemented. Report defects/interpretation limits promptly, no writes/newfits/simulation/publication/delegation.",
  "deliverable": "Exact source/LC independent assessment with actualchecks.",
  "completion": "Return defects or noactionablefinding, sources and limits."
}
```

Source review addendum: d3b20a23 shares identical basis/design moments across tuning penalties, a performance-only refactor; all5modeltests pass. Pipeline source nowfrozen at8cc16f6ab0daebb2c59a9ed6803892c24ff8c8e2; add explicit steering hash and worker seed guards under existing SoftEng ownership before campaign readback. Manifest preparation used priorgenerator d56c1093; laterguard-only changes preserve all default primary bytes/seeds.

## Campaign analysis review

```json
{
  "id": "ECAL-HIGHSTAT-PHYSVAL-ANALYSIS",
  "role": "PhysVal",
  "input_revision": "ab753ec5cea60627e4b09133689b0f27441abf84",
  "inputs": [
    "docs/validation/ecal-highstat/protocol.md",
    "software/analysis/calorimeter_digitization/highstat_analysis.py",
    "software/analysis/calorimeter_digitization/highstat_model.py",
    "software/analysis/calorimeter_digitization/highstat_sample.py",
    "software/analysis/calorimeter_digitization/highstat_readback.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Assess exact campaign merge, train/freeze/unblind and final bootstrap orchestration. Verify fit/tune/closure disjoint roles, originalvsnewmodel comparator fairness, Gitobject+core/campaign/featurehash freeze guard before validation, historical5foldensemble labelling,6series means/SDCV/RMS/tails/zeros/clipping, conditional1000vsfull200withinrole resampling repeatingknots/selection85krefit15kclosure. Check35metriccolumn ordering=global1+eta10+phi10+energy14,120width/60contrastcovariance. Maintransporttrain000~5000events, nofreshvalidation inspected. Mainpending fastnative10kregression; agent13native/pipelinecontrolsPASS. No fits/newdatasets/simulation/ROOTreads/writes/delegation/publication. Initialfindings promptly, finalreviewresults later.",
  "deliverable": "Exact source scientific/integrity assessment and actualnonfitting checks.",
  "completion": "Return materialissues or noactionablefinding pluslimits."
}
```

Analysisreview guard remedy at 62261934588a38437b5e115475c82c99727478ba: frozenfeature semantics signature(feature_names,producer,recipe,geometryhelper) now matchesalltraining/validationbatch receipts beforeanyvalidationNPZis opened; metadata boundary negativecontrol2testsPASS. Analysisproducerhash alsofrozen. Fullretained10k nativeaudit/features rerun afterguard/sourcefreeze:114.4s,6346815hits,9958axes; alleventidentity/worker/primaryerror/rootSHA fields exact, allfeaturearrays match oldrecipe at1e-10. A preliminarypasscompletedwhile guard-only sourcechanged and isretainedlocal; onlyfinalfrozenpass isusedforpublicbinding.

## Guard reassessment

```json
{
  "id": "ECAL-HIGHSTAT-PHYSVAL-GUARD",
  "role": "PhysVal",
  "input_revision": "62261934588a38437b5e115475c82c99727478ba",
  "inputs": [
    "software/analysis/calorimeter_digitization/highstat_analysis.py",
    "software/analysis/calorimeter_digitization/test_highstat_analysis.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Verify remedy for soleP2feature-semantics finding: allreceiptsemantic headers nowchecked acrosssplit andagainst frozen training signature beforeanyvalidationNPZopens; analysisprocedurehashfrozen too. Two meaningfulnegativecontrolsPASS. No scientificmethodchange; nofreshvalidationinspected. No fits/writes/delegation/publication.",
  "deliverable": "Bounded guard reassessment exactrevision.",
  "completion": "Return findingfixed orremainingactionabledefect withactualchecks."
}
```

## Actual early outcomes

Originalfrozen-method learning curve widths32.3518/32.1980/32.1912/32.2201% at1/2/4/8ktraining. Mean~.919,42zeros inclusive. Three8kpredictions equalretainedmodel exactly. Exploratory, weak/nonmonotonic, noasymptotic claim. SeparatePhysVal source/LC/math review found no defect; finalanalysisreviewP2 feature-semanticguard fixed at62261934588a38437b5e115475c82c99727478ba and independently rechecked beforeanynewvalidation. Within-role repeatedselectionbootstrap code assessed; 120widthcovariance expectedstructurallysingular because pre/postCV identical.

Transport campaign and harvest run serial10kbatches with12DDSimworkers and one nativeaudit pass; training-only fitting is queued afterall10trainingreceipts, followed by committedmodel freeze beforevalidationprediction. No20kperformance inspected. Allsource/model/featuresemantic hashes bindthechain. Originaldata retained; no new dependency or geometryintegration.
