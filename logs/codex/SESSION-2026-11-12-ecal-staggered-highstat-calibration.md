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

Learningcurve rerun withunchangedseeds/sourceprocedure toretain pairedsizecontrasts and joint4global/80angularwidth covariance. Existingpointmetrics,intervals,predictions bitidentical; priorversion retained inGit. Sixthmodelcontrol comparesfull weightedbootstrapfit againstexplicitduplicatepopulations forbotharchitectures;PASS. Fullsynthetic100k70/15/15software smoke forbothmodels passesmeanclosure andzeroinvariants; thisis softwareverification, notdetector performance.

## Learning-contrast assessment

```json
{
  "id": "ECAL-HIGHSTAT-PHYSVAL-LC-CONTRAST",
  "role": "PhysVal",
  "input_revision": "99eb9ed0587180873ca75e52a03e2dccf5440185",
  "inputs": [
    "software/analysis/calorimeter_digitization/highstat_learning.py",
    "docs/validation/ecal-highstat/learning/learning-curve.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Nonfitting assessment of addedLCpaired-size contrasts/jointcovariance. Rerununchanged200bootstrapseeds/method; alloldpointmetrics/intervals/predictions bitidentical. Addedglobal8x8 andangular80x80covariance, widthNminus8k percentile ranges. At1k pointdifference0.001317, fullprocedurebootstrap95%range[.001570,.005869] excludespoint, suggesting finite-training/bootstrapshift; existingLC isexploratory200replica, notcertification. Advise truthfulinterpretation (retainrange, donotposthocadjust/drop); checkwhethermaterialstatisticalissue requirescodechange beforecampaign eval. Primarynew100kfit/20kvalidationnotinspected. No fits/newbootstrap/runs/writes/publication/delegation.",
  "deliverable": "Bounded interpretation/covariance review and actualchecks.",
  "completion": "Return materialissue or explicitcautionwithlimits."
}
```

LCcontrast review: pairedformulas/ordercorrect;1kpoint.001317 versus shiftedpercentilerange[.001570,.005869] retainedandexplicitlyexploratory,nosignificanceclaim. Beforeanyfreshvalidation, primaryintervalreports nowretain bootstrapmean/median−point,fractionbelowpoint, withunchanged draws/intervalmethod; tuning/closure variation alreadyretained. Thirdanalysiscontrol verifies noCIrecentering;PASS. No calibrationmethod/model-gridchange.

Coordinator pipeline smoke without NODD_HIGHSTAT_NATIVE flag ran9lightweight controlsand skipped4native controls, asdesigned. Recipecorrected toexplicitlysetflag; fullnative coordinator rerun follows. PriorSoftEng13/nativePASS and full10k native regression alreadyobserved.

Prepared-primary input-only QC (no responseperformance): all1400E×|eta|×foldphi cells occupied; training46–96inputs/cell,avg71.43;validation4–29,avg14.29. MeansE45.0008/45.0408GeV. Fullnative coordinator flag-enabled suite13/13PASS in6.280s, withno skips. All22distinct narrowcases nowpass(13pipeline+6model+3analysis); repeat executions notcounted as additional cases.

## Prospective grid fairness assessment

```json
{
  "id": "ECAL-HIGHSTAT-PHYSVAL-GRID-FAIRNESS",
  "role": "PhysVal",
  "input_revision": "ca38408d765fdce2cbc14d3d597d6b9b7a89bfa9",
  "inputs": [
    "docs/validation/ecal-highstat/protocol.md",
    "software/analysis/calorimeter_digitization/highstat_model.py",
    "docs/validation/ecal-highstat/learning/learning-curve.json",
    "docs/validation/ecal-staggering/results/summary.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Prospective comparator fairness check beforeanynew100kresponsemodel fit or20kvalidationperformance. Currentneworiginal-architecture grid(.01,1,100), newspline(.0001,.01,1). Old10kmodels allselectedlowest.01. Complete-recipecomparison isvalidiflabelled, but strongerbaselinecouldusecommonunion(.0001,.01,1,100) forbothnewlinear/spline withsame70/15/15/refit85/C chain, preservinghistoricalold10kensemble andoriginalLC unchanged. Advise whether amendgridprospectivelynow toavoidregularizationsearch confound/weakbaseline orkeeporiginaldeclaredrecipewithexplicitattributionlimit. No freshtrainingperformanceapartfromnativeQAcountshasbeeninspected; MC~60k/120k ongoing. No sourcewrites/fits/newbootstrap/simulation/publication/delegation.",
  "deliverable": "Bounded scientific recommendation about fair prospectivehypergrid and requiredlabelling.",
  "completion": "Return decisionrationale/limits promptly; nohumanacceptance."
}
```

Prospectivegridamendmentbeforeanynew100kfit/fresh20kperformance: accept PhysVal recommendation commonunion{.0001,.01,1,100} forbothnewmethods, removesprescribedsearch-rangeconfound. Old10khistoricalensemble/LC unchanged. Newlinear isretunedten-featurearchitecture, notidenticalhistoricalrecipe; bases/interactions/clipping stilldiffer, noisolatednonlinearityclaim. All10oldstaggeredfits selected priorendpoint.01. No changes tosampling,MC,roles,bounds,closureorresampling.

Beforeanynewmodel fit/freshvalidation, the complete numerical dependency graph isalso frozen: angular_sample/angular_analyze/staggered_results helper hashes recordedinmodel snapshot andcheckedbeforevalidationload, alongsidecore/analysis hashes. Sourcehelpers remainbyte-unchanged; this addsprovenance enforcement only. ThreeanalysiscontrolsPASS.

## Frozen training chain review

```json
{
  "id": "ECAL-HIGHSTAT-PHYSVAL-FROZEN-MODELS",
  "role": "PhysVal",
  "input_revision": "e65962c259cec1f8744252fccfa17211004f4d61",
  "inputs": [
    "docs/validation/ecal-highstat/frozen/models.json",
    "docs/validation/ecal-highstat/protocol.md",
    "software/analysis/calorimeter_digitization/highstat_model.py",
    "software/analysis/calorimeter_digitization/highstat_analysis.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Pre-validation review of actual100k-trained frozen chain. Commit e65962... created2026-11-12T13:41:48Z; nofresh20kperformance inspected, MCvalidation000 stillrunning. Verify declaredcommonlambda{.0001,.01,1,100},70/15/15roles,85krefit/Cclosure,bounds andfrozenfeature/helper/core/source/campaign bindings. Supplemental localbuild/ecal-highstat/campaign TRAINfeature receipts only; you MAYreproduce both frozen fits on these100k training rows withdeclaredprocedure, no alternativeconfigs, compare savedcoefficients/basis/closure exactly orwithjustifiedroundoff. DO NOTopen validation feature arrays,inspect anyvalidationresponseperformance,modifyfiles,runsimulation,retune,delegate orpublish. Usepython-B/OPENBLAS_NUM_THREADS1. Reportactualchecks and anymaterialfinding promptly; final20kresultsreview later.",
  "deliverable": "Exact-revision frozenmodel/data/source reproduction assessment before unblinding.",
  "completion": "Return findings/noactionablefinding withactualchecks, nohumanacceptance."
}
```

## Actual100k training freeze

All10trainingbatches passedtransport/native/readback. Automaticdeclaredchain fitbothmodels andcommittedfrozen/models.json ate65962c259cec1f8744252fccfa17211004f4d61 on2026-11-12T13:41:48Z, beforefresh20kperformanceinspection. Source/core/helper/campaign/featuresemantic hashesverifiedagainstcurrentfiles. Linearregionalλ=.0001/.01; spline7knots/.0001both,80/82coefficients, C1.0854609; linearC1.0857735. No validationperformanceclaim yet.

Frozenchain reviewerresult: e65962c259cec1f8744252fccfa17211004f4d61 completepointmodelrecords reproduce BIT-EXACTLY fromall10training batches(maxdifference0), includingcandidateMSEs/choices/quantiles/centres/coeffs/fallback/C. Explicitloaderguardallowedonlytrain paths; NOvalidationarraysopened. Verifiedrole/source/core/helper/campaign/featurehashes andglobalclosuremean1/CVinvariance/zeros/gainlimits. No materialfinding. Independent20kperformance stillpending.


## Final results assessment assignment

```json
{
  "id": "ECAL-HIGHSTAT-PHYSVAL-FINAL",
  "role": "PhysVal",
  "input_revision": "83eb6a8828eea3cfd54da07650ca226a88f7c2e9",
  "inputs": [
    "docs/validation/ecal-highstat/results/summary.json",
    "docs/validation/ecal-highstat/frozen/models.json",
    "docs/validation/ecal-highstat/campaign-and-run.json",
    "docs/validation/ecal-highstat/README.md",
    "software/analysis/calorimeter_digitization/highstat_analysis.py",
    "software/analysis/calorimeter_digitization/highstat_plots.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Final exact-revision independent scientific assessment of the completed 120k staggered-only campaign. Inspect primary compact results before author conclusions. Review fresh20k points/controls/histogram populations, residual mean/tail/seam/energy bias, conditional1000/full200 within-role bootstrap interpretation and correlated contrasts/covariance, source/freeze/hash bindings, and all nine rendered PNG families. Supplemental local campaign train/validation feature receipts/arrays and build/ecal-highstat/validation-predictions.npz may now be read; all MC complete. You may reproduce frozen inference and the declared unchanged bootstrap if useful, no alternative fits/configuration or retuning. Coordinator checked all120angularhist populations, global point metrics,84zeros,CVinvariance,120/60covariances PSD and A\u03a3A\u1d40, render hashes and vectorSVG. All22narrow tests pass; old10k native regression passes. Report material issues and truthful limits; no writing, new simulation, source/model changes, delegation or publication. Python-B, numerical threads1; no native imports required unless following acts-spack preflight.",
  "deliverable": "Exact-revision final result/control/uncertainty/figure assessment with actual checks and actionable findings or explicit no-material-finding.",
  "completion": "Return bounded final assessment and actual evidence; technical assessment only, no human sign-off."
}
```

All120k transport/readback complete; immutable training freeze precedes validation. Fresh20k widths raw38.313%, historical31.338%, retunedlinear31.322%, spline30.209%; closed means1.00287/1.00300. Full200refits and1000conditional resamples complete. Coordinator numerical/count/zero/CV/covariance/hash/vectorSVG checks pass. Residual energy/local bias, seam tails and84zeros retained; no retuning. Final specialist assessment follows at exact results commit.


## Completed independent evidence and verification

The final numerical source is unchanged after the training freeze. Twelve 10k batches, each with12DDSimworkers, yield120000 audited primaries and76941173 silicon cell hits. ROOT occupies152.506GB; summed transport wall118.6min, elapsed118.8min,20.93CPUh, peak transport child2.672GiB; minimum recorded free232.7GiB. No input/output deletion or trimming. All source/config/library/worker hash checks pass.

On the same fresh20k, raw/historicalensemble/retunedlinear/spline widths are38.313/31.338/31.322/30.209%. Global scale closure restoresmean1.00300for spline but does not changeCV and raises its RMS28.929→30.301%; closed linear RMS31.412%. All84zeros, clipping and219spline feature-extrapolated events remain. Spline energy-slice means0.96975..1.02622; local foldedphi means0.61376..1.10597; sector-edge widths73.23/75.06% versus11.01..12.65% interiors. Results do not establish an intrinsic resolution, a pure statistics-size effect or engineering acceptance. The validation cohort has now been inspected and is no longer untouched for future tuning.

1000conditional whole-event and200complete within-role training/selection/refit/closure+validation resamples finish. Allglobalpoint statistics reproduce from localpredictions;120angular hist populations and all84zeros retained; closureCV identity passes.120×120width covariance has expectedrank80;60×60contrasts rank60; symmetry/PSD/AΣAᵀ pass. Bothuncertainty sets retaincentering/tie diagnostics; ranges are approximatepointwise, no posthoc recentering.

All27render hashes and9SVG vector structures pass. Standaloneplotting using onlycompactstatistics reproduces all18PNG/SVG byte-for-byte;9PDFs regenerated with variablecreation metadata. All9families visually inspected, legible/no cropped content. NewGitobject inspection finds no ROOT/NPZ/HEPEvt/JSONL/buildpayload. Largestnewblob is2.993MB compactbinwise summary including required correlatedstatistics.

Task token counters remain unavailable, including separate specialist turns; usage[] means unobserved, not zero. No estimates or historicalproject totals are attributed tothis task.


## Final separate PhysVal assessment

Assignment ECAL-HIGHSTAT-PHYSVAL-FINAL examined83eb6a8828eea3cfd54da07650ca226a88f7c2e9 read-only. No material scientific or implementation finding. The reviewer reproduced all6frozen-inference series and438population summaries (120angular,84energy,228controls,6global), including all120inclusive histograms,84zeros, tails/RMS/clipping/extrapolation. Bothcovariance sets have expectedwidthrank80 and contrastAΣAᵀ discrepancy atmost5.8e-19. All1680metricinterval and120contrastdiagnostics are internallyconsistent; no metricpoint falls outside itspercentilerange. Largest angular-width bootstrapmean offset0.16SD; no conspicuous analogousLCcenteringissue, but200fullrefit ranges remain approximate. All27renderhashes/all12provenancechains covering120000events/76941173hits andall9PNGfamilies assessed. Source/bindings reviewed; neither ROOTreadback nor fullbootstrapgeneration was repeated. No retuning/writes/simulation/publication byreviewer andnohumanacceptance.

## Draft publication

Published dedicatedbranch and opened [draft PR137](https://github.com/asalzburger/nodd/pull/137), stacked on codex/ecal-calibration-staggering-tests (PR136). Connectorcreate_pull_request returnedHTTP403 Resource not accessible by integration; authenticatedgh pr create succeeded. This was a connectorcapability failure, not an automatic approval-policy rejection. User's earlier explicit source/compactresults/PNG/PDF/SVG publicationapproval and authorizedfollow-up remain the publicationbasis. No comments posted; no ready/merge/sign-off action. Connector metadata verifiesdraft=true andcorrectbase/head. BothPR136and137 publicdiscussion snapshots refreshed andsanitized. RawMC/eventpayload remainslocal/ignored.

Final report, protocol, exactrecipe, coefficients, compactbinwise correlatedstatistics andall9figurefamilies retained. Requiredrepository validators and token-sitebuild run forcloseout; taskusage isunknown, neverzero or estimated.

Final closeout checks PASS: project107tasks/54documents/24reviewrounds; inventory68components/101families/52inputs/12pins;287pairedsessionrecords;116PRinteractionrecords; tokenvalidator and sitebuild(_site). Summary generated locally, taskusage remains[]/unknown; repositoryhistorical totals are not attributed tothis task. Final session associations forPR136and137 synchronized, whitespace clean. Only curatedmetadata changes after the assessed scientific result; source/model/statistics/plotbytes unchanged.


## 2026-11-12 token-accounting correction and work label

The earlier empty usage statements describe unavailable measurements at the original capture. The [PR137 accounting pass](SESSION-2026-11-12-pr137-accounting.md) now recovers **13 closed turns / 321 requests**, with **83,941,695 input + 303,876 output = 84,245,571 observed tokens**, owned here exactly once. Inventory: [USAGE-2026-11-12-pr137-calibration-accounting.json](../usage/USAGE-2026-11-12-pr137-calibration-accounting.json). App-visible request/final-response and verified parent/child assignments match the selected exact turn IDs. The canonical title is now “Staggered ECAL: 100k training and 20k independent validation”, which supplies the token dashboard work label. No token allocation among individual messages or multiple PR references is inferred. Cached input/reasoning are subsets; actual per-turn models, billing and other-device completeness remain unknown. The current accounting turn is excluded. Scientific source/results/coefficients unchanged.
