# SESSION-2026-11-05-calorimeter-digitization117 — Issue 117 calorimeter digitization model selection and prototype

## Scope and evidence

Contemporaneous curated record for issue #117. Started from clean task worktree
`codex/issue117-calorimeter-digitization` at main
`96dbf57d0da7f3027e59109c1846d992d68d4d44`. The original `nodd` checkout has
unrelated changes; it was preserved. The issue explicitly authorizes an unsigned
Si-W PROTOTYPE. No production detector parameters or shared software were changed.

## Selected conversation

- User, exact request: “There’s an issue #117 - address it, request what you need to do so”.
- Assistant: identified the calorimeter digitization issue through GitHub, read
  governing instructions and created an isolated worktree from fetched main.
- Assistant: warned that the Spack preflight fingerprints changed, then checked
  actual runtime imports, packages, datasets, compilation and execution.
- Assistant requested an existing Marlin/Key4hep setup command or remote
  host/path for the missing original-framework comparison. The user subsequently deferred the Marlin study until appropriate software is
  installed; no further runtime request or Marlin study was pursued.
- Assistant reported source-reuse boundaries, native test results and the
  calibration/held-out distinction without claiming design sign-off.

## Decisions and outcomes

CaloTech prepared DES-044 before physical implementation, surveying six pinned
primary software sources and recommending chains for all four technologies.
The main agent integrated source records and CALICE comparator evidence into
the canonical source manifest. SoftEng reused original Marlin silicon energy
methods in a separate GPL executable, leaving the ACTS library interface MPL.
The explicit prototype includes cell aggregation, signed Gaussian noise checks,
strict thresholds, deterministic event seeds, opt-in stored cell positions and
noise-only output without fabricated truth. The absence of a full original
runtime remains a blocker for the issue's reference gate, not for preparing
reviewable code or running the available ODD simulation.

The first half of 500 central 10GeV muons freezes a 148.75keV empirical binned
MIP scale; the second half is held out. No fitted/path-aware MIP acceptance is
claimed. Shower generation uses full unchanged ODD. Only compact binwise
counts, plots and reproduction recipes are intended for Git.

## Commands and validation

- `git fetch origin main`; task worktree creation: passed.
- `acts-spack/scripts/preflight.py`: exit2, changed setup/lockfile fingerprints.
- `software/env/run.sh python3 software/env/doctor.py`: exit0; DD4hep/DDG4,
  Geant4 version and twelve dataset presence checks passed.
- Standalone ODD configure/build against pinned d70556f3: passed.
- Initial `ddsim` pilot: exit2 due to unsupported explicit boolean value;
  corrected to the flag form. Three-event photon pilot then passed.
- Two 500-event muon generation points: passed; calibration script passed.
- Native build and five CTest suites passed, including eight silicon cases;
  noise criterion was strengthened from six to the validation plan's five
  standard errors after separate review. Full original-processor comparison
  remains NOT RUN.
- SciPy probe: import failed; no SciPy dependency added and no fitted-MIP claim.
- First token-site output location was rejected because repo output must be
  under `_site/`; corrected `_site/issue117` build passed.
- Detailed final campaign results and checks are retained in the paired JSON
  and issue117 validation report once available.

## Changes and revision links

Implementation: `1deb638b626d2fb9f608f221879a069a9cc2da41`.
Numerical-range correction: `fc28d2edb34f828496354a7344d754ffbae51f52`.
Review-remediation commit: `26335fcb381143bc5d29aad0fb405d0d9e22efb9`.
The paired JSON carries the full changed-file inventory. Later report/log commits
can reference these real revisions without a self-referential hash.

## Token accounting

No exact disjoint client-reported per-turn input/output counters were exposed
for the active parent or child turns. `usage` stays empty. Observed task input
and output totals are unknown, not zero; historical global totals are not
attributed to this task. No estimates, raw rollouts or private reasoning were
collected. Client version and stable thread/turn IDs remain unknown.

## Follow-up

The user deferred the Marlin study until appropriate software is installed.
Retain the preparation and add the full original-framework study in that later
phase. Complete path-aware fitted MIP validation, physical
active-plus-passive sampling scoring, noise-free paired controls and reviewed
shower interpretation. DES-044 lists follow-up drafts for LAr, tile HCAL and
quartz-fibre FCAL. No human design sign-off was supplied or inferred.

## Specialist assignments

Explicit role instructions via saved workflow prompts; native profile loading is not claimed. Input revision 96dbf57d0da7f3027e59109c1846d992d68d4d44.

```json
{
  "input_revision": "96dbf57d0da7f3027e59109c1846d992d68d4d44",
  "mode": "write",
  "id": "I117-CaloTech",
  "role": "CaloTech",
  "inputs": [
    "docs/design/DES-031-siw-barrel-prototype.md",
    "docs/design/DES-032-allegro-lar-barrel.md",
    "docs/design/DES-033-allegro-lar-endcaps.md",
    "docs/design/DES-036-hcal-common-readout-module.md",
    "docs/design/DES-039-common-forward-calorimeter.md"
  ],
  "writable_paths": [
    "docs/design/DES-044-calorimeter-digitization.md",
    "reference/issue117-sources.json"
  ],
  "task": "Issue #117: verify primary source implementations and pin exact commits/paths. Survey models for Si-W, LAr, SiPM-on-tile and W/quartz FCAL, recommend one per technology; identify effects, reuse/framework coupling and mu=200 gaps. Read issue via connector. Coordinate first Si-W choice with coordinator and SoftEng promptly. Prefer reusable existing silicon model rather than bespoke model. Write DRAFT DES-044 before implementation. JSON source fragment contains manifest-ready entries. No sign-off or production changes. No further delegation.",
  "deliverable": "DES-044 draft with model table, precise version/source locators, references, open questions, follow-up issue drafts; manifest entries in reference/issue117-sources.json for coordinator integration.",
  "completion": "All technologies covered; actual source inspection distinguished from unverified leads; recommendations, upstream licensing and missing evidence explicit."
}
```

```json
{
  "input_revision": "96dbf57d0da7f3027e59109c1846d992d68d4d44",
  "mode": "write",
  "id": "I117-SoftEng",
  "role": "SoftEng",
  "inputs": [
    "software/source/ActsExamples/Calorimeter/src/CalorimeterDigitizationAlgorithm.cpp",
    "software/source/ActsExamples/Calorimeter/README.md",
    "software/source/ActsExamples/Calorimeter/CMakeLists.txt"
  ],
  "writable_paths": [
    "software/source/ActsExamples/Calorimeter/include/ActsExamples/Calorimeter/CalorimeterDigitizationAlgorithm.hpp",
    "software/source/ActsExamples/Calorimeter/src/CalorimeterDigitizationAlgorithm.cpp",
    "software/source/ActsExamples/Calorimeter/include/ActsExamples/Calorimeter/SiliconDigitization.hpp",
    "software/source/ActsExamples/Calorimeter/src/SiliconDigitization.cpp",
    "software/source/ActsExamples/Calorimeter/tests/AlgorithmSkeletonTests.cpp",
    "software/source/ActsExamples/Calorimeter/tests/SiliconDigitizationTests.cpp",
    "software/source/ActsExamples/Calorimeter/tests/CMakeLists.txt",
    "software/source/ActsExamples/Calorimeter/CMakeLists.txt",
    "software/source/ActsExamples/Calorimeter/EDM4hep/include/ActsExamples/Calorimeter/EDM4hepCalorimeterInputConverter.hpp",
    "software/source/ActsExamples/Calorimeter/EDM4hep/src/EDM4hepCalorimeterInputConverter.cpp",
    "software/source/Calorimeter/tests/CalorimeterEDM4hepReconstructionTests.cpp",
    "software/source/ActsExamples/Calorimeter/README.md"
  ],
  "task": "Issue #117: inspect skeleton and propose implement existing upstream reusable Si-W digitization as explicitly opt-in PROTOTYPE. Contact CaloTech promptly on choice. Start read-only until coordinator confirms draft exists and selected source. Add meaningful tests including noise RMS, threshold statistics, upstream comparison if feasible. Add explicit converter option to use EDM4hep hit cell position with validation and tests (callback default retained). Need explicit all-channel/noise-only support, proper truth/noise semantics and event-deterministic RNG. No bespoke physical model and no claim toy formulas are upstream reference validation. You own listed code paths; request additions if needed. No further delegation. Coordinator handles runtime and samples.",
  "deliverable": "Focused implementation, tests and README recipe; report exact upstream bytes/revision/license, test commands and unavailable checks. Do not modify shared dependencies or sister ACTS.",
  "completion": "Native build/tests pass where runtime permits; explicit PROTOTYPE config, model provenance, no production changes. Unmet issue criteria accurately identified."
}
```

```json
{
  "input_revision": "96dbf57d0da7f3027e59109c1846d992d68d4d44",
  "mode": "write",
  "id": "I117-PhysVal",
  "role": "PhysVal",
  "inputs": [
    "docs/decisions/ADR-003-validation-and-artifact-policy.md",
    "docs/design/DES-031-siw-barrel-prototype.md",
    "software/source/ActsExamples/Calorimeter/README.md"
  ],
  "writable_paths": [
    "docs/validation/issue117/validation-plan.md"
  ],
  "task": "Issue #117: define rigorous noise-only, MIP, independent original-implementation same-hit comparison, electron/photon multi-energy/eta validation. Inspect primary published Si-W performance references and ODD source differences. Write concise validation-plan with observables, required inputs and interpretation limits. Report minimally sufficient required user inputs/runtime if absent. No acceptance claims, retuning or fabricated plots. Separate later review of implementation will target a fixed commit. No further delegation.",
  "deliverable": "Validation matrix and primary source locators with configured-vs-test-fixture numbers explicit. Return suggested actual campaign manageable on local ODD runtime.",
  "completion": "Every issue validation item mapped to commands/inputs/criterion or missing evidence; distinguish downstream cell position from step positions, sparse-hit/noise occupancy pitfalls."
}
```


### Exact implementation review assignment

```json
{
  "id": "I117-PhysVal-implementation",
  "role": "PhysVal",
  "input_revision": "1deb638b626d2fb9f608f221879a069a9cc2da41",
  "inputs": [
    "docs/design/DES-044-calorimeter-digitization.md",
    "docs/validation/issue117/validation-plan.md",
    "software/source/ActsExamples/Calorimeter/src/CalorimeterDigitizationAlgorithm.cpp",
    "software/source/ActsExamples/Calorimeter/src/SiliconDigitization.cpp",
    "software/source/ActsExamples/Calorimeter/upstream/marlin/Backend.cpp",
    "software/source/ActsExamples/Calorimeter/tests/SiliconDigitizationTests.cpp",
    "software/source/ActsExamples/Calorimeter/EDM4hep/SiliconCampaign.cpp",
    "software/analysis/calorimeter_digitization/analyze.py",
    "software/analysis/calorimeter_digitization/calibrate.py",
    "software/analysis/calorimeter_digitization/plot.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Review prototype implementation, scientific assumptions, reproducibility, tests and claim boundaries at this exact commit independently from code authors. Identify correctness bugs and blocking issues; original full-framework comparison remains pending. Do not review your own validation-plan authorship as independent. Actual 3600 shower +1000muon events generating; numerical results reviewed separately later. Read source before author conclusions. No further delegation.",
  "deliverable": "Return cited actionable findings, severity, actual checks and limitations. Main retains in report/session.",
  "completion": "Every material issue has exact locator and remediation; distinguish source/kernel tests from unmet issue gates; no sign-off."
}
```

### Reference comparison preparation

```json
{
  "id": "I117-SoftEng-reference-tool",
  "role": "SoftEng",
  "input_revision": "26335fcb381143bc5d29aad0fb405d0d9e22efb9",
  "inputs": [
    "software/source/ActsExamples/Calorimeter/EDM4hep/SiliconCampaign.cpp",
    "software/source/ActsExamples/Calorimeter/include/ActsExamples/Calorimeter/SiliconDigitization.hpp",
    "docs/validation/issue117/validation-plan.md"
  ],
  "mode": "write",
  "writable_paths": [
    "software/source/ActsExamples/Calorimeter/EDM4hep/SiliconReferenceComparison.cpp",
    "software/source/ActsExamples/Calorimeter/EDM4hep/CMakeLists.txt",
    "software/analysis/calorimeter_digitization/reference.md"
  ],
  "task": "Prepare actual original-framework same-hit comparison capability while external Marlin/Key4hep runtime is unavailable. Add standalone native comparator consuming original ddsim ROOT SimCalorimeterHits plus full-original-processor digitized ROOT output, explicit configs/units and provenance; run native silicon algorithm on identical events and compare matched cell IDs/energy with declared precision tolerances in deterministic pairEnergy=0/noise=0 controls first. Preserve events/IDs/count denominators and reject mismatched collection/event metadata; output compact binwise/mismatch summaries, no event payloads in Git. Document exact original processor steering requirements from pinned source and executable command, marking unavailable runtime recipe unexecuted; inspect source before inventing component/property names. No full-reference pass claims. Do not modify main campaign runner/scripts. No further delegation. Native build/meaningful utility validation where possible; request added file ownership if needed.",
  "deliverable": "Native same-hit comparator and CMake target, concrete original-framework setup/steering recipe with input/output unit contract and limitations, build/check report.",
  "completion": "Capability ready to execute when user supplies runtime; mismatches fail explicitly; no self-comparison described as independent reference validation."
}
```

## User-directed deferral and final preparation disposition

User, exact steering: “Hold on for the Marlin study, we will add that when we the appropriate software is installed”.

The main agent stopped seeking the original runtime and retained source survey,
isolated optional prototype, native tests and prepared comparator/steering.
No additional Marlin study, original-framework execution or installation was
performed after this direction. No final digitized physics-study evidence is
committed in this preparation change. Existing exploratory plots/binwise files
and Geant4 event inputs remain ignored and local.

Docker executable discovery succeeded. The sandbox denied image-inventory
socket access; an escalated read-only inventory request was interrupted by the
user. No successful Docker inventory, container execution or installation is
claimed. This is not recorded as an automatic approval rejection.

Specialist results: CaloTech completed the six-source survey and manifest
fragments; the coordinator merged those and CALICE/method documentation into
the canonical manifest. SoftEng completed the opt-in kernel, provenance/position
handling, tests, then a bounded reference-comparator capability with synthetic
corruption checks. PhysVal reviewed implementation1deb638b and numerical delta
fc28d2ed, verified original-source hashes and Python syntax, and identified two
minor issues: hardcoded figure counts and5-vs6-standard-error criteria. The
coordinator corrected both, rebuilt and ran six passing CTest suites. PhysVal
found no additional campaign-energy blocker but did not grant acceptance,
review its own validation-plan authorship as independent evidence, or execute
an original full-framework benchmark.

File-ownership additions granted during work covered the EDM output
converter/metadata headers and source, native EDM hit comments, NOTICE, the
explicit upstream adapter/license assets, and reference utility registration in
tests/CMakeLists.txt. Actual changed paths are in the paired JSON. Explicit role
assignments were /root/calotech117, /root/softeng117 and /root/physval117; native
profile loading and exact child usage were not claimed.

This bounded preparation record can close while issue117 and its deferred
reference/physics gates remain open. No human design approval was supplied.

At closeout, the independent Geant4 generator manifest records 18/18 successful shower points (3600 events), plus1000 completed muon events. The remaining job, if any, is transport input preparation rather than Marlin execution. No completion beyond that observed manifest is claimed.

Final validation passed: session validate/summary, project-record validation, token-site build and whitespace checks. Task input/output totals remain unknown because no exact per-turn counters were exposed. All18 shower points (3600events) and1000muons finished as independent Geant4 inputs; no further Marlin analysis was run after deferral.

## 2026-11-10 token recovery and work label

Supersedes the earlier unavailable-counter note for the recovered closed turns only. Exact app-visible requests/results, verified parent/child role metadata and this journal's bounded assignments identify 7 previously unowned observations. Imported with session_log.py after a successful dry run; replay adds zero. Observed input 43,056,000 + output 149,149 = 43,205,149; cached input/reasoning are subsets, not additions. See [the scoped inventory](../usage/USAGE-2026-11-10-pr118-prototype.json) and [readiness/accounting record](SESSION-2026-11-10-pr118-merge-readiness.md). This existing session title labels the work in the cumulative usage view. Original task outcomes, gates and source versions remain unchanged; model/client version and excluded active/other-device usage stay unknown.
