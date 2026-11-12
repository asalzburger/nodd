# SESSION-2026-11-12-ecal-calibration-staggering-tests

## Scope and selected request

The user said: “Please go ahead with these tests.” This follows the proposed
local-position calibration and independent module-phase tests in PR135. The
bounded implementation uses identical retained 10,000 electron inputs and
12 DDSim workers, with disk planning and a live guard. Starting revision:
`3af5538faf884d0abce98b0956c0e6d4f45d4527`; clean dedicated branch
`codex/ecal-calibration-staggering-tests`. Earlier samples remain unchanged.
The repository is the canonical record. This is an isolated PROTOTYPE under
DES-030/DES-031; no human sign-off or production integration is inferred.

The coordinator applied `nodd-coordinate`, `nodd-design-evidence`,
`nodd-review-validation` and the local ACTS Spack skill. Changed setup/lock
fingerprints were disclosed before dependent work; the native runtime doctor
passed. Existing dependencies were reused without modifying shared installs.

## Decisions and outcomes

The physical four-phase board layout was frozen before response inspection.
Barrel narrow edge boards preserve envelopes/ASIC capacity; short slabs use a
24 mm quarter-phase to preserve rows/clearance. All area/material changes are
explicit. Native construction/IDs/electrodes/zero-overlap checks, 24-event pilot,
full 10k transport and all saved-primary/hit/12-worker audits pass. The original
sector seams remain. Dense mask screening is geometry only.

The calibration protocol freezes observable-only features, five outer/three
inner ID folds, training-only preprocessing, ridge candidates and gain bounds.
Separate `Model.infer(features, signal)` returns energy without truth inputs;
held-out truth changes leave inferred energy unchanged. No held-out retuning.
The first baseline fit improves global CV from 43.09% to 34.43%, while retaining
mean Ecal/Etrue=0.9136 and 8.99% clipping. This scale bias is a reported limitation,
not removed by an evaluation-derived correction. Final paired analysis follows.

## Commands and validation

Exact reproduction commands are in `docs/validation/ecal-staggering/reproduce.md`.
The runtime doctor, native geometry audit, pilot and full saved-event audits
returned exit 0. The 10k run took 591.953 s with peak RSS 2.469 GiB and a
12.613 GB ROOT file. No disk trimming or disk-guard abort. Nine new geometry,
eight existing edge-packing, five calibration and two statistics tests passed.
An initial edge-test discovery used a nonexistent pattern and ran zero tests
(exit 5); corrected `test_edges.py` runs all eight. An initial public evidence
assembly used the wrong disk-budget path and failed; the curator now uses the
correct root record and rejects unexpectedly large aggregates. Full module/pad
polygons remain local, not in public evidence.

The identical-input report integration control with five full-refit bootstrap
replicas gives exactly zero point/interval layout contrasts. It is a software
control, never presented as new geometry data. Figure export smoke-check passed.

Separate PhysVal source review at `3626953a90ed61b078265ab2cf064d65040ba7b6`
found no material defect. It checked source hashes, 1,536 negative-end inverse
transforms (max residual 1.4e-12 mm), frozen XML and feature/pilot bindings.
A nonblocking energy-return API observation was addressed by Model.infer and
held-out full-energy invariance tests before the primary fit.

Statistical review at `f9e9779512747ad6fce0b8ec1bfb5e442b5cddc7`, plus explicitly
identified histogram/global additions (hash 5278f162…), found no material defect.
Actual non-fitting checks matched weighted moments to duplicated populations and
verified 80-width/80-contrast ordering and A·cov·Aᵀ within 3.6e-15. Reviewer
cautions retained: report primary scale bias and clipping; eta-sign pools both
barrel and endcap; secondary-prior diagnostics have no separate intervals; central
quantile width is (q84−q16)/(2q50). Final results review remains pending.

## Changes and accounting

Physical layout preparation, native checks, reconstructed features, calibration,
paired refitting results, PNG/PDF/SVG plotting and aggregate evidence tools are
under `software/analysis/calorimeter_digitization/staggered_*`. The default
endcap packer gains optional phase controls with unchanged default behavior.
Curated report/protocol/evidence, software inventory and scientific tracking are
updated in this branch. Raw ROOT, event-level features/predictions, exact primary
and event ledgers, bulky geometry/pad/ray audits and logs remain local/ignored.

Exact client parent/child token counters are unavailable. The paired JSON keeps
`usage: []`; this means unknown, not zero. No private rollouts or reasoning are
recorded. Final validators, publication and the bounded final assessment follow.

## Specialist contracts

User authorizes implementation and execution of the proposed calibration/layout tests. Scope: isolated PROTOTYPE real board staggering and reconstructed-position calibration; identicalretained10k primaries,12DDSimworkers, diskguard, held-outcomparison. No production integration/sign-off or full-depthsector-interface redesign. Main owns feature extraction/calibration/protocol/run/audits/plots andrecords. Originaldata remainlocalunchanged.

Explicit generic-agent roleinstructions are prepared below, not nativeprofileloading.

```json
{
  "id": "ECAL-TESTS-SOFTENG",
  "role": "SoftEng",
  "input_revision": "3af5538faf884d0abce98b0956c0e6d4f45d4527",
  "inputs": [
    "docs/validation/ecal10k-untiled/calibration-layout-options.md",
    "tools/calorimeter_hardware/barrel_layout.py",
    "tools/calorimeter_hardware/edge_layout.py",
    "tools/calorimeter_hardware/barrel_export.py",
    "tools/calorimeter_hardware/edge_export.py",
    "docs/validation/ecal10k-untiled/results/comparison.json"
  ],
  "mode": "write",
  "writable_paths": [
    "software/analysis/calorimeter_digitization/staggered_geometry.py",
    "software/analysis/calorimeter_digitization/test_staggered_geometry.py",
    "tools/calorimeter_hardware/edge_layout.py"
  ],
  "task": "Implement isolated physical staggered-board compact preparation for original ECAL-only10k tiled geometry, native library unchanged if feasible. Main owns calibration/features/transport/audits/publication. User authorizes actual tests of priorrecommendations. Retain slab\u00b196joint phases, absorber/skins/support/cooling stack/envelopes/plane locations. Implement independent4layer tangent/axial phases00,48/0,0/48,48/48. Fullslab axial rows move48awayfrombay on halfphasedlayers; repack shortslabs safely. Tangential boardphasing needs real narrowed edgeboard/sensor templates/guards/ASIC stacks, not unbuildable continuousSi or masks-only moves. Suggested feasible family: existing94x94PCB/90x90Si/88x88active; on tangenthalfphasedlayers use(N-1)fullboards+two46x94PCB/42x90Si/40x88active edgeboards, twoASICs each, preserving oldouterPCBspan and ASICcapacity, smallSi-area delta explicit. Check derivation yourself. ExistingmoduleIDs <~560; reservedhalfboardIDs700+2*row+side fit10bits. Newhalf masks simple rectangles canretainEdgeGrid with newreservedmodulemasks. Endcaps need4physicalpacking/maskfamilies; use existingpack/hardware generation with optionaldefault-preserving tangentphase/innerpartialrow parameters in ownededge_layout.py. OffsetmoduleIDsphase*256 (verify each<256). Preserveactualsense/guard/PCB/ASIC geometries and originalmaterials; avoidoverlaps. Newregionsperphase existingreplicaschoosefamily; retainsectorenvelopes. XML-only transformation/generation must hashverify source/material/primarybytes and recordmass/coverage/parts/IDs changes and limitations. Preserve baseline public factories, library and prior artifacts. Can importexistinghardwarehelpers. Use onlyownedfiles; sourcechecksumupdatedwhereexistingexport expectsownedpackerchanges. No full transport or publishing/commits; create meaningful tests and a fresh preparedinput for main nativeaudit.",
  "deliverable": "Return scoped implementation/input, exact source evidence, actualchecks and limitations to coordinator.",
  "completion": "Deliver requested contribution or concrete missinginputs; do not delegate, publish or grant acceptance."
}
```

```json
{
  "id": "ECAL-TESTS-CALOTECH",
  "role": "CaloTech",
  "input_revision": "3af5538faf884d0abce98b0956c0e6d4f45d4527",
  "inputs": [
    "docs/validation/ecal10k-untiled/calibration-layout-options.md",
    "tools/calorimeter_hardware/barrel_layout.py",
    "tools/calorimeter_hardware/edge_layout.py",
    "tools/calorimeter_hardware/barrel_export.py",
    "tools/calorimeter_hardware/edge_export.py",
    "docs/validation/ecal10k-untiled/results/comparison.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Assess physical candidate implementation constraints promptly. Work from priorfourphaseproposal, current source and source geometry. Coordinate with SoftEng. Check feasible tangential narrowedgeboard family46x94PCB/42x90Si/40x88active twoASICs: (N-1)full+2edge preserves originalPCBspan with2mmgaps, smallSi decrease; ASIC/geometricreadout/guard/manufacturing rationale andID budgets. Check axialhalfphaseawaybay and shortslab handling; endcapphasedpack minimumshape/ASIC/sourcefamily constraints. Advise dense coverage screening/no geometry-onlyresolution claim. No edits, no full-depthsector seam redesign in this firstmodule-staggering test. Give concrete constraints, counters andproposedacceptancetests.",
  "deliverable": "Return scoped implementation/input, exact source evidence, actualchecks and limitations to coordinator.",
  "completion": "Deliver requested contribution or concrete missinginputs; do not delegate, publish or grant acceptance."
}
```

```json
{
  "id": "ECAL-TESTS-PHYSVAL",
  "role": "PhysVal",
  "input_revision": "3af5538faf884d0abce98b0956c0e6d4f45d4527",
  "inputs": [
    "docs/validation/ecal10k-untiled/calibration-layout-options.md",
    "tools/calorimeter_hardware/barrel_layout.py",
    "tools/calorimeter_hardware/edge_layout.py",
    "tools/calorimeter_hardware/barrel_export.py",
    "tools/calorimeter_hardware/edge_export.py",
    "docs/validation/ecal10k-untiled/results/comparison.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Freeze a practical prospective calibration/analysis protocol. Need baseline/raw vsbaseline/calibrated andnewphysicalstagger/raw/calibrated onexact10k inputs with12threads. Main implements reconstructedhit-barycentre/axis features (no truth inference), lowdimensional smoothresponsemap, eventIDoutercrossfitting and training-onlyhyperparameterchoice. TrueEtraininglabels/evalonly. Propose robust boundedpredictor, feature choices (localgap/maskexposure, reconstructedeta/phi, longitudinalfractions) and validation including narrowtrueE slices, signedeta/sectors, tails/zeros andtrainingprior bias. Prefer NumPy-onlysmallridge/smoothmap withphysicalgeometryexposure; no newdependenciesneeded. Need practical pairedbootstrap withcalibrationtraininguncertainty (outerbootstrap/refit), immutablefolds, no posthocselection/cuts. Provide early protocol decisions before fitting, then independent exactsource/results reviewlater. Continuous sample remainsdiagnostic. No writes/fits/runs/delegation/publication.",
  "deliverable": "Return scoped implementation/input, exact source evidence, actualchecks and limitations to coordinator.",
  "completion": "Deliver requested contribution or concrete missinginputs; do not delegate, publish or grant acceptance."
}
```

## Frozen source assessment

```json
{
  "id": "ECAL-TESTS-PHYSVAL-SOURCE",
  "role": "PhysVal",
  "input_revision": "3626953a90ed61b078265ab2cf064d65040ba7b6",
  "inputs": [
    "docs/validation/ecal-staggering/protocol.md",
    "software/analysis/calorimeter_digitization/staggered_calibration.py",
    "software/analysis/calorimeter_digitization/staggered_features.py",
    "software/analysis/calorimeter_digitization/staggered_native.py",
    "software/analysis/calorimeter_digitization/staggered_geometry.py",
    "software/analysis/calorimeter_digitization/test_staggered_calibration.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Review exact frozen calibration/features/protocol source before any fit. Check observable-only inference, geometry transforms, nestedfolds/scaling, ridge normalization/gainlimits and bootstrap-refittability. Main will implementstatisticalreport/bootstrap next. Nativeaudit has551520unique sensors,252484referencechecks,zerooverlaps;24event12workerpilotPASS; full10krunstarting on same hash-boundcompact. Independent sourceassessment needed promptly. No writes/fits/reruns; report material defects.",
  "deliverable": "Return scoped implementation/input, exact source evidence, actualchecks and limitations to coordinator.",
  "completion": "Deliver requested contribution or concrete missinginputs; do not delegate, publish or grant acceptance."
}
```

## Statistical implementation review

```json
{
  "id": "ECAL-TESTS-PHYSVAL-STATISTICS",
  "role": "PhysVal",
  "input_revision": "f9e9779512747ad6fce0b8ec1bfb5e442b5cddc7",
  "inputs": [
    "docs/validation/ecal-staggering/protocol.md",
    "software/analysis/calorimeter_digitization/staggered_results.py",
    "software/analysis/calorimeter_digitization/staggered_calibration.py",
    "software/analysis/calorimeter_digitization/test_staggered_calibration.py",
    "software/analysis/calorimeter_digitization/test_staggered_results.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Review nested refitting statistical implementation and separate Model.infer(signal,features) API at exactsource. Verify full inferred-energyheldouttruth invariance test, bootstrapduplicateID folds/refits, weightedmoments, covarianceordering and tail comparators. Current source f9 includescoreAPI andinitialreport; workingtree additions sincecommit are onlyhistogram/globalstats andnullable handling, explicitlyinspect dirtydiff too if useful but distinguish. Fullsimulation~7000/10000 completed; baseline firstfit frozenmodel globalwidth43\u219234%, calibratedmean0.9136, clipping8.99%, retained asdiagnosticbias with no posthocretuning. Finalresult source reviewwillfollow. No writes or newfits.",
  "deliverable": "Return scoped implementation/input, exact source evidence, actualchecks and limitations to coordinator.",
  "completion": "Deliver requested contribution or concrete missinginputs; do not delegate, publish or grant acceptance."
}
```

## Final-results review contract

```json
{
  "id": "ECAL-TESTS-PHYSVAL-FINAL",
  "role": "PhysVal",
  "input_revision": "4bbd9a9bdfd8813804dc8adeaffda07b03a01b0d",
  "inputs": [
    "docs/validation/ecal-staggering/README.md",
    "docs/validation/ecal-staggering/protocol.md",
    "docs/validation/ecal-staggering/results/summary.json",
    "docs/validation/ecal-staggering/results/render.json",
    "docs/validation/ecal-staggering/geometry-and-run.json",
    "software/analysis/calorimeter_digitization/staggered_results.py",
    "software/analysis/calorimeter_digitization/staggered_plots.py",
    "build/ecal-staggering/production-predictions.npz",
    "build/ecal-staggering/baseline-features",
    "build/ecal-staggering/staggered-features"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Independently review exact final 10k results and interpretation. Check local predictions/features against all80angular moments, means/zeros/clipping/tails/histograms; original baseline invariant; input/transport/feature/hash binding, covariance transform/order and inclusive counts. Review all8PNG figure families and labels, calibration bias clearly retained, secondary prior point-only, all20raw vs16/20cal interval claims. No new simulation/fits or full ROOT reread needed; report exact actual checks and material findings. No writes/delegation/publication/signoff.",
  "deliverable": "Bounded independent assessment of final source/results and actual numerical/visual checks.",
  "completion": "Return findings or no actionable finding with limitations and exact revision."
}
```

## Publication state

Curated branch `codex/ecal-calibration-staggering-tests` was pushed successfully
to configured `git@github.com:asalzburger/nodd.git` at
`c6e2cdf91664d7a3272a0e4bb59453628f3aee1c`; a subsequent authenticated read
verified that exact remote head. Only the inspected compact result/plots/source
and curated records are reachable; no raw ROOT/NPZ/HEPEvt/event-ledger objects.
The prepared draft targets `codex/ecal10k-untiled-control` (PR135), title
“Calorimeter: test physical module staggering and held-out calibration”.

The connected GitHub draft-PR creation was rejected by automatic approval review:
only test execution was deemed explicitly authorized. The coordinator checked
the pre-existing human publication instruction at the starting AGENTS.md revision,
the configured destination, PR135's draft/base branch and the exact published
branch, then retried the same connected operation. It was rejected again because
repository instructions were not accepted as user authorization for external
publication. No CLI workaround or further publication was attempted. Explicit
user approval is now required; the prepared concrete PR body and final local
closeout changes remain local pending that approval. No PR number is invented.

Standalone replotting without event files reproduces all sixteen PNG/SVG files
byte for byte. Eight SVG exports pass vector-only XML/security checks and all
24 render hashes match. Covariances are finite/symmetric/PSD; the dependent
contrast covariance agrees with A·cov·Aᵀ. All inclusive histogram totals match.
Initial token-site build ran before ledger synchronization and reported stale
accounting evidence; after refreshed PR135 capture/sync it builds successfully.
Historical observed token totals are repository-wide and are not current-task
usage; current task counters remain unavailable.

## Final-results assessment outcome

PhysVal independently reviewed `4bbd9a9bdfd8813804dc8adeaffda07b03a01b0d`:
no actionable material finding. All 80 angular populations match local arrays
exactly for moments, means, zeros, tails, clipping and inclusive histograms;
original twenty baseline populations retained. Frozen primary/secondary model
inference and training means/scales match records without refitting. Energy and
direction/sector tables, native/run/readback/feature/source bindings and all
24 render hashes agree. All eight PNG families visually inspected. Covariance
transform residual 1.6e-18, width covariance PSD, contrast rank 60 as expected.
Both layouts have 42 zeros, 41 common IDs. Confirmed 20/20 raw and 16/20 calibrated
positive pointwise layout intervals. No new fitting, ROOT reread, simulation,
writes or publication by reviewer. No engineering/design acceptance.

## Explicit publication authorization

The user answered the concrete draft-publication question with
“Approve draft PR publication”. This authorizes publication to asalzburger/nodd
of the prepared source, compact results and PNG/PDF/SVG plots, with raw event
files retained locally. The earlier automatic-review blocker is resolved by
this explicit approval. Publication and final verification proceed under that
authorization; the draft remains a prototype and grants no design sign-off.
