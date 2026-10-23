# SESSION-2026-10-23-tracker-propagation — Tracker sensitive-crossing profiles in the 3 T field

## Scope and selected requests

Contemporaneous, curated record of a new bounded task after merged PR96, starting
from main `fbf81c4c72469c1bda0cd6122f9912af6f17228d` in a clean isolated worktree
on `codex/tracker-sensitive-propagation`. The user requested the current Tracker
through DD4hep → ACTS TrackingGeometry, propagation in the 3 T field map at
pT 1/10/100 GeV, nSensitives versus eta profiles split by subdetector and full
tracker, attractive unrooted plots and a repeatable process. On clarification,
the user explicitly selected generation from the current 3 T solenoid model.
DES-025 and DES-026 remain DRAFT/PROTOTYPE; this is a software characterization,
with no geometry change, detector qualification or human sign-off.

The existing acts-spack and nODD coordination/review skills were read and applied.
Spack preflight reported changed setup/lockfile fingerprints; the user was warned
before dependent work. Current DD4hep 1.38, Geant4 11.4.3, DD4hep/DDG4 imports,
12 datasets and native ACTS modules were then checked directly. The installed
ACTS version is the development placeholder `(999,999,999)`; retained binary
hashes identify execution. The sister checkout was already dirty at
`555c66e71d0639665c2fa3d5574a0fe7f3f62cde` and was neither edited nor rebuilt.

## Decisions and results

The map represents the retained finite uniform-J annular DES-026 vacuum winding,
with eight radial Gauss sheets and 1,000 axial coils per sheet. Signed-z RZ data
uses explicit mm/T units, 10/20 mm spacing, r≤1300 mm and |z|≤4200 mm. Source
hashes and declared 3 T normalization are enforced. Off-grid and radial/axial
refinements are sampled checks, not whole-domain bounds or magnet acceptance.

One generated muon per event avoids the native example's survivor-renumbering
ambiguity. Complete unique identities, momentum components, origin, charge,
seven-system source-ID sums, final World-portal exits and map support are checked.
All 24,576 nominal probes passed at 8,192 per momentum, uniform eta/phi and both
charges, with material effects disabled. All 45,646 native sensitive elements
match the converted geometry in 117 volumes. Overlaps and both strip faces count;
these are plane crossings rather than reconstructed hits or efficiency.

ROOT TProfiles, unrooted branch profiles and independent sums agree. Zero entries
remain in all denominators. The main and seven-system figures are exported as
SVG/PDF/PNG; self-contained HTML and ROOT remain in ignored build outputs.
Compressed counts, bin statistics, field/native reports and figures are retained
under `docs/validation/tracker-propagation`. Restoring those compressed counts
and replotting without ACTS passed. Full sample bin populations are 79–131.

## Implementation, independent assessment and corrections

SoftEng01 supplied useful source/API findings but produced no files or native
run: its runtime escalation waited about 36 minutes and was interrupted. The
coordinator explicitly suspended that write ownership and implemented the native
job, accounting and controls. Do not count that assignment as separate implemented
or runtime-tested work. Subsequent SoftEng02 is a read-only review of actual
coordinator code and 128-probe output; role instructions were passed in prepared
prompts, not claimed as natively loaded profiles.

PhysVal01 independently checked the field construction and ROOT profile errors,
and demonstrated missing identity/kinematic checks and unenforced declared field
strength at the preliminary revision. Both were corrected. SoftEng02 found the
venv executable `.resolve()` bypass and lack of saved-run verification in replot.
The first full native sample completed, but the initial analysis subprocess
failed to import awkward through the dereferenced interpreter. Using `.absolute()`
preserves the venv. Plotting now requires PASS, matching count hashes/configuration
and common geometry/field/runtime identities. Native runs invalidate prior PASS
before work. A later world-bound check initially used a nonconstructible ACTS
GeometryContext; it was corrected to the detector's nominal context and all three
nominal samples rerun at 7f65054. These adverse results and remedies are retained;
no tests or tolerances were weakened.

## Relevant commands and actual checks

- Fresh CMake/Ninja DD4hep factory/compact build: 24 steps succeeded.
- Native eight-probe diagnostic and 128-probe complete-accounting smoke passed;
  the initial eight used the older example's default eta distribution and is
  excluded from final uniform-eta evidence.
- `/bin/zsh software/running/tracker_profiles.sh --stage propagate`: all three
  nominal samples passed, then `make tracker-propagation-plot` passed.
- `controls.py`: paired half-step, finer-map and independent-seed runs are
  recorded separately in the final report; no unrun control is claimed here.
- Eight pure profile/accounting controls passed, including missing/duplicate IDs,
  unknown source IDs, zero denominators, interrupted/mixed plotting and endpoint aborts.
- Six tracker conversion tests and 12 solenoid tests passed.
- 33 session/recovery tests and 28 project-record tests passed.
- Project, session and token validators passed before closeout; final results
  are retained in the paired JSON checks.

## Token ownership

Usage-only recovery read selected token_count metadata and explicit parent/child
relationships, without retaining conversation items or private model state.
Five closed/interrupted specialist turns contribute 6,186,162 input + 30,747 output
= 6,216,909 observed tokens under this task. The parent scientific turn remains
active and excluded from finalized totals. Cached 5,968,896 and reasoning 8,795 are
subsets. No model, billing or complete-task total is inferred.

A separate correction observes the prior issue95/PR96 accounting follow-up now
closed. It is imported under its existing accounting session. Original installation
and accounting together contain 14,400,520 input + 42,672 output = 14,443,192 tokens;
this tracker task is excluded from that total. Prior provisional snapshots remain
historical evidence and are not counted again.

## Changes and review boundary

The paired JSON lists actual files and commits. The source/data report and bounded
technical assessments are review evidence, not human engineering approval. A new
Software PR carries this task separately from merged PR96.

## Specialist assignments

```json
{
  "id": "TRKPROP-SoftEng-01",
  "role": "SoftEng",
  "input_revision": "fbf81c4c72469c1bda0cd6122f9912af6f17228d",
  "inputs": [
    "AGENTS.md",
    "docs/design/DES-025-tracker-dd4hep-gen3.md",
    "tools/tracker_dd4hep/README.md",
    "tools/tracker_dd4hep/check_navigation.py",
    "docs/validation/DES-025/gen3.json",
    "software/README.md"
  ],
  "mode": "write",
  "writable_paths": [
    "software/running/tracker_propagation.py",
    "tools/tracker_propagation/counts.py",
    "tools/tracker_propagation/test_counts.py"
  ],
  "task": "Implement a repeatable native ACTS propagation job for the current DD4hep-backed Tracker converted via getNoddDetector to Acts::TrackingGeometry. User requests pT exactly 1,10,100 GeV in the current 3T field map and nSensitives versus generated eta profiles per subdetector and full tracker. Implement run CLI and robust per-track count extraction/tests; parent owns map selection/generation, sampling config, orchestration, plotting, docs and final runs. Read local acts-spack skill and preflight before runtime. Known local ACTS sister source /Users/salzburg/Documents/work/dev/acts-nodd at dirty555c66e71d0639665c2fa3d5574a0fe7f3f62cde; preserve all changes and do not edit/build there. Installed runtime imports verified via acts run acts-nodd using its pyvenv. Use actual ACTS PropagationAlgorithm, EigenStepper and Navigator with material effects off for geometry crossing study. Coordinate supported map-loading format and output table schema with parent early. Match summary and steps by stable identifiers, include every generated probe including zeros; explicitly fail/report dropped/failed tracks rather than silently profile survivors. Reconstruct full GeometryIdentifier and map to DD4hep source systems1..7 via geometryReport; verify per-track split sums equal summary nSensitives; no fabricated geometry or ODD map. Distinguish sensitive-plane crossings from reconstructed hits/stations or unique layers. Support small smoke CLI and scalable full job with reproducible seed/count/eta/pT, report configuration/source/install hashes. Keep dependencies in existing ACTS environment and test pure extraction controls with synthetic fixtures. Do not modify shared dependencies, geometry or existing files beyond owned new paths. Do not commit or spawn nested agents. Send parent schema and runtime/source findings promptly.",
  "deliverable": "Three owned files implementing runnable ACTS job, pure count extraction and meaningful tests. Return supported field map interface, per-track/output schema, actual checks and limitations.",
  "completion": "Parent can supply current DD4hep build and field map, run a smoke/full sample and plot all subdetector/full profile counts without survivor bias or silent field substitution."
}
```

```json
{
  "id": "TRKPROP-PhysVal-01",
  "role": "PhysVal",
  "input_revision": "7b02e7eb88196d1dd0282e32a12a3d7b3db4dc5a",
  "inputs": [
    "AGENTS.md",
    "docs/design/DES-025-tracker-dd4hep-gen3.md",
    "docs/design/DES-026-tracker-solenoid-baseline.md",
    "tools/solenoid_baseline/baseline.json",
    "docs/validation/DES-026/sizing.json",
    "tools/tracker_propagation/field_map.py",
    "tools/tracker_propagation/plot.py",
    "tools/tracker_propagation/study.json",
    "tools/tracker_propagation/test_profiles.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Independently assess the scientific definition and implementation of the requested current-tracker nSensitives versus generated eta profile study at pT1,10,100GeV, origin vertex, phi uniform, seeded both charges, material effects off. Review exact committed field/plot/config code and source DES025/026 before author claims. Field uses 8 Gauss-radial ACTS finite SolenoidBField sheets with1000axialcoils each to represent the retained uniform-J annular pack, normalized3T, textRZmap r[0,1300]z[-4200,4200]mm dr10dz20. Parent actual map report at build/tracker-propagation/field/field-report.json is supplementary dirty output whose scriptSHA should be matched; generation central3T, max sampled maperror0.000305T, axialrefinement3.4e-6T. Native propagation implementation/output not yet fixed: SoftEng is assigned; scope now is definition/field/profile correctness and meaningful validation criteria before full runs. Check trueTProfile population variance/errors, inclusion of zero crossing probes, grouping seven DD4hep systems into pixel/short/long/full, sensor-plane versus layer/hit semantics, pT nottotalp, potential survivorbias, map support, finitewinding approximations and any unsupported physical claims. Identify corrections needed and practical convergence/statistical controls. Read-only; do not edit files, install dependencies, spawn agents or assume approval. Parent will send a later exact revision and measured outputs for final assessment.",
  "deliverable": "Return bounded PhysVal findings with exact revision/file locators, actual checks and specific corrections or conditions. Parent curates response in docs/validation/tracker-propagation/physval.md and journal.",
  "completion": "Provide actionable pre-run assessment of this fixed study definition and field/profile code; distinguish verified statements from native propagation evidence still pending."
}
```

## Preliminary execution evidence (superseded by final samples above)

User explicitly confirmed generating the map from the current3T DES026solenoid model. The Spack registry fingerprints are stale; current installed DD4hep1.38/Geant4 11.4.3 and DD4hep/DDG4 imports/datasets were reverified, then installed acts-nodd Python runtime, getNoddDetector and ROOT propagation writers imported successfully in its pyvenv. Sister source is dirty555c66e71d0639665c2fa3d5574a0fe7f3f62cde and was preserved. Fresh tracker factories built at the new worktree/build/dd4hep. Initial eight-probe EigenStepper/3Tmap smoke completed; all45646 surfaces and117 volumes match native inventory; independent per-system step reconstruction closes to summary nSensitives for all8 probes. This smoke reused the older example's eta sampling and is diagnostic only, not the final uniform-eta sample.

Initial field generation:131x421grid, radial Gauss order8,1000axialcoils, Bz(0)=3T. Sample interpolation difference0.000304987755T, coil refinement3.434306e-6T, radial refinement2.09e-14T; all below declared0.001T software tolerance. Field script later gained explicit normalization/config consistency enforcement; regenerate for final source snapshot.

PhysVal preliminary assessment at7b02e7eb88196d1dd0282e32a12a3d7b3db4dc5a confirmed field construction and profile population errors independently, and identified missing input-identity/kinematic checks plus unenforced declaredfieldstrength. Main corrected both and added duplicate-ID/profile-zero controls; native completeness checks remain assigned toSoftEng. Main ownsfieldmap, plotting, run orchestration, Make targets and reports.

## Follow-up implementation review assignment

```json
{
  "id": "TRKPROP-SoftEng-02",
  "role": "SoftEng",
  "input_revision": "b78f754dc15eaa408492aae3e50e8e9fed0ce443",
  "inputs": [
    "AGENTS.md",
    "software/running/tracker_propagation.py",
    "tools/tracker_propagation/run.py",
    "tools/tracker_propagation/counts.py",
    "tools/tracker_propagation/plot.py",
    "tools/tracker_propagation/field_map.py",
    "tools/tracker_propagation/test_counts.py",
    "tools/tracker_propagation/test_profiles.py",
    "tools/tracker_propagation/README.md"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Read-only implementation review of the exact committed native propagation and accounting pipeline, now implemented by the coordinator after suspended assignment01. Inspect primary code before claims. Assess failure and duplicate detection, ROOT identity/kinematics matching, source-ID crossing counting, runtime provenance and repeatability. Run pure unit controls in software/build/unrooted-venv/bin/python -I; no native activation, shared dependency changes or installs. Supplementary measured smoke run under build/tracker-propagation-smoke/pt_1GeV accounts for128 probes; final8192-per-pT run ongoing. Identify concrete bugs, severity and fixes. Do not write files or spawn agents.",
  "deliverable": "Return exact-revision findings, actual commands/results and limitations. Coordinator curates review and any fixes.",
  "completion": "Complete bounded code assessment and report actionable findings."
}
```

## Final measured scientific assessment assignment

```json
{
  "id": "TRKPROP-PhysVal-02",
  "role": "PhysVal",
  "input_revision": "5181bd317e6b369388805e1567d695a22a4e33aa",
  "inputs": [
    "AGENTS.md",
    "docs/design/DES-025-tracker-dd4hep-gen3.md",
    "docs/design/DES-026-tracker-solenoid-baseline.md",
    "software/running/tracker_propagation.py",
    "tools/tracker_propagation/counts.py",
    "tools/tracker_propagation/plot.py",
    "tools/tracker_propagation/field_map.py",
    "tools/tracker_propagation/diagnostics.py",
    "docs/validation/tracker-propagation/README.md",
    "docs/validation/tracker-propagation/study.json",
    "docs/validation/tracker-propagation/profiles.json",
    "docs/validation/tracker-propagation/field-report.json",
    "docs/validation/tracker-propagation/pt-1GeV-run.json",
    "docs/validation/tracker-propagation/pt-10GeV-run.json",
    "docs/validation/tracker-propagation/pt-100GeV-run.json",
    "docs/validation/tracker-propagation/controls/diagnostics.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Assess the final committed measured study and corrections at the exact supplied revision, read-only. Independently inspect retained compressed counts/run/geometry/field/profile reports before author prose; pure checks may use software/build/unrooted-venv/bin/python -I. All24576 nominal probes have complete IDs and native World exits, all source sums close, TProfiles/unrooted/sums agree, N80bins79..131. Reduced step25vs50mm gives no per-system changes in512 paired probes at1/10/100GeV. Refined map5x10vs10x20mm changes7 of 512 probes at1GeV by one sensitive each (delta full mean +1/512), none at10/100GeV; all affected forward trajectories are near finite pixel/strip sensor edges, with saved-step common-position shifts 0.029..0.066mm. diagnostics retains changed source paths and local edge clearances via explicitly approximate interpolation. Refined sampled field discrepancy0.061mT vs nominal0.305mT; tolerance1mT is a sampled numerical check, not exact acceptance convergence. Independentseed2048perpt retained. Assess whether evidence and wording are sound for requested prototype overview; identify any remaining scientific blocker or unsupported claim. Verify prior P2 identity/kinematics/normalization corrections; distinguish all-probe completeness, map support, native termination and uncertainty from tracking performance. No native runtime activation, installs, writes or nested agents. Large original ROOT and surface arrays remain supplementary in build/tracker-propagation and may be inspected without ACTS if needed, but retained Git evidence is the primary revision target.",
  "deliverable": "Return assignment ID/review revision, findings, actual commands/results and limits. Explicitly assess the seven refined-map edge flips and the retained non-convergence qualification; do not grant human approval.",
  "completion": "Complete separate scientific assessment of final measured evidence and flag required fixes or appropriate remaining qualifications."
}
```

## Final controls and review outcome

All paired and independent-seed runs completed. The fine map changes seven of 512
1 GeV probes (1.37%) by one crossing each, four gains/three losses. Source-local
edge diagnostics reproduce finite pixel/strip boundary flips; common-surface
shifts 0.029–0.066 mm. The signed full mean +1/512 is supplemented by absolute
change 7/512 and maximum affected control-bin shift 0.2. Per-track map convergence
is explicitly unestablished. Half-step and fine-map 10/100 GeV comparisons show
no count changes. Separate PhysVal02 at `5181bd317e6b369388805e1567d695a22a4e33aa`
reproduced all 24,576 native rows and 33 profiles and found no remaining blocker
for a prototype overview under retained qualifications. See curated scientific
and software assessments; no human approval is inferred.

The documented `make tracker-propagation` command completed end-to-end with 2,048 probes per momentum in a fresh output directory. All 6,144 saved CSV rows exactly match the nominal prefix, including path lengths; regenerated map bytes are identical. Retained replay.json records hashes and actual execution revision.

## Delivery

[Software PR97](https://github.com/asalzburger/nodd/pull/97) opened and attached,
published evidence head `7675d4b2cd40692664aa4ae5fe10aaebb0fdab58`. Metadata-only
closeout follows. Both figures were visually inspected; overview image opening
was queued by the app. Sandboxed push/API DNS failures were retried successfully
through normal escalation. No merge or engineering approval was performed.
