# SESSION-2026-10-15-issue38-validation — coverage and material plots

## Scope and evidence

Contemporaneous curated record for issue [#38](https://github.com/asalzburger/nodd/issues/38),
starting at `5b4e5d9e563505aea17e9b792458708c3175ec4a` on a fresh
`codex/issue38-validation-review` worktree. The original `nodd` checkout has unrelated
modified/untracked logs and a TDR submodule; those files were preserved. The two
October 14 forwarded review sets are the requested scope. Prior disc-overlap and
integer-position changes are already merged through PR40/46 and are historical.

## Selected conversation

User request (exact): “Issue #38 has two set of reviewer comments (forwarded
from Susanne Kuehn, Markus Elsing), can you address - answer them and if needed
take action (in separate PRs) ?”

The assistant separated mechanical/editorial actions from native geometric and
material diagnostics, with a separate PR for each. Reviewer answers are to be
posted to the issue once concrete changes and checks are available.

## Coordination and scope

Applied repository `nodd-coordinate`, `nodd-design-evidence` and
`nodd-review-validation` instructions. Generic subagents receive the complete
prepared role mandate; native profile loading is not claimed. PubDoc owns the
mechanical chapter/drawings in the separate mechanics worktree. SoftEng owns the
native scan and retained results in the validation worktree. PhysVal contributes
independent observable definitions and then reviews a fixed implementation
revision. The coordinator owns tracking, logging, integration and external replies.
Assignments below were recorded before dispatch. No agent grants human sign-off.

## Commands and validation

Issue and PR metadata read with `gh`; main fetched normally. A first GitHub read
inside the network sandbox failed, then the authorized read succeeded with network
access. Fresh branches preserve unrelated local changes. Full commands/results
and final changed paths are curated in the paired JSON at closeout.

## Token accounting

No exact client per-turn counters or stable thread/turn usage export were exposed.
This session and child work have no new observed token counters; `usage: []`
means unavailable, not zero. Historical project sums are not attributed to this
session, and counters are not estimated or duplicated between the two task records.

## Outcome and remaining review

In progress. Detector inputs, formal lifecycle and human sign-off remain unchanged.

## Specialist assignment before dispatch

```json
{
  "id": "VAL-SOFTENG",
  "role": "SoftEng",
  "input_revision": "5b4e5d9e563505aea17e9b792458708c3175ec4a",
  "inputs": [
    "tools/tracker_dd4hep/README.md",
    "tools/tracker_dd4hep/validate.py",
    "tools/module_layout/README.md"
  ],
  "mode": "write",
  "writable_paths": [
    "tools/issue38_validation/README.md",
    "tools/issue38_validation/scan.py",
    "tools/issue38_validation/test_scan.py",
    "docs/validation/issue38-review/results.md",
    "docs/validation/issue38-review/summary.json",
    "docs/validation/issue38-review/coverage.png",
    "docs/validation/issue38-review/material.png"
  ],
  "task": "Implement and actually run reviewer-requested nhits and holes versus eta/phi plus stacked X0 and interaction-length versus eta plots for current full tracker prototype. Prefer native DD4hep straight-ray scanning of true active patches and material paths, use existing available runtime after acts-spack preflight. Keep geometry/field/runtime/scientific limits explicit; define holes as missed expected ideal stations separately from active patch hit count, strip sensor pair/station distinction. Zero field rays are geometric coverage not reco efficiency; eta/phi sampling and luminous positions must be explicit. Do not substitute surface-only material for full budget. Inspect expected.json and assembly exporters/config. Preserve input hashes, source SHA, seeds/grid/tolerances and exact commands. Reasonable bounded scan sufficient; no production geometry changes. Own only listed files; ask coordinator if more artifacts needed. No commits or external messages. The source main may predate merged stacked PR80; use current available existing build read-only only if its exact config/hash can be matched to clean source. Return limitations honestly and actual plots if feasible.",
  "deliverable": "Owned files, point-by-point response, evidence locators, actual checks, limitations to coordinator.",
  "completion": "All assigned reviewer points handled or explicit evidence-backed unresolved gaps reported; run narrow checks; no human sign-off claims."
}
```

## Independent scientific definition assignment

```json
{
  "id": "VAL-PHYSVAL-DEFINITIONS",
  "role": "PhysVal",
  "input_revision": "5b4e5d9e563505aea17e9b792458708c3175ec4a",
  "inputs": [
    "docs/design/DES-025-tracker-dd4hep-gen3.md",
    "tools/module_layout/README.md",
    "tools/tracker_dd4hep/README.md",
    "docs/validation/DES-025/results.md"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Independently assess scientifically defensible definitions for issue38 Markus Oct14 request nhits versus eta/phi, holes versus eta/phi and stacked X0/interaction length versus eta of full tracker prototype. Examine source inputs before conclusions. Identify ideal-station oracle, strip doublet counting, seam/overlap distinction and limits of native straight-ray scan. Return compact recommendations and pitfalls; implementation underway separately, this is requirements/definitions input, not implementation review. Do not delegate.",
  "deliverable": "Cited independent requirements-to-observables recommendations to coordinator for session record.",
  "completion": "Definitions, expected denominator, sampling/report limitations, and any misleading claims identified with evidence locators."
}
```

## Ownership amendment

VAL-SOFTENG additionally owns `docs/validation/issue38-review/rays.json.gz` for
compressed per-ray counts/material paths. The coordinator approved scratch files
under `/private/tmp/issue38-native-scan-*`. Coordinator owns the CI unit-control
step, project tracking and session closeout files. Geometry inputs remain fixed.

## Fixed implementation review assignment before dispatch

```json
{
  "id": "VAL-PHYSVAL-IMPLEMENTATION",
  "role": "PhysVal",
  "input_revision": "fbed1779adef22f659152200b9c35d84f2c22d71",
  "inputs": [
    "tools/issue38_validation/scan.py",
    "tools/issue38_validation/test_scan.py",
    "tools/issue38_validation/README.md",
    "docs/validation/issue38-review/results.md",
    "docs/validation/issue38-review/summary.json",
    "docs/design/DES-025-tracker-dd4hep-gen3.md"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Review final native reviewer scan/results at this exact commit, independently of author: counting stations/same-module strip pairs, ideal reference mapping, holes, material integration/units/scope, provenance and interpretation of actual controls. Examine primary implementation and input evidence before author conclusions. Run meaningful narrow checks and inspect retained rays hash/aggregates and figures if useful. Identify actionable errors preventing reviewer response; no human acceptance, no further delegation or writes. Earlier independent definitions input at5b4e5d9 remains recorded.",
  "deliverable": "Exact-revision findings with severity, source locators, actual checks and limitations for coordinator; no formal sign-off.",
  "completion": "Return actionable findings or no findings; distinguish finite geometric characterization from reco/physics efficiency and material-model qualification."
}
```

## Specialist outcomes and independent assessment

VAL-SOFTENG (/root/softeng, explicit SoftEng mandate) re-verified changed Spack
fingerprints with actual DD4hep/DDG4 imports and12Geant4datasets. Existing
DD4hep1.38/Geant4 11.4.2/ROOT6.40.04/Python3.14.5 environment used; fresh compact
is byte-identical and factory sources match the separate clean530080c build
source. Libraries are independently hashed and unchanged. No shared install.
The current producer ran7872main+576offset rays, with all45646native sensitive
transforms/bounds matching and successful material/pipe closure. Repeated full
ray arrays are exactly identical. Figures, compressed per-ray archive and
provenance are retained. Initial probe reference-key typo was corrected before
rays; its scratch output was preserved. A final plot legend correction moved
the material legend outside data; native rerun kept producer hashes exact.

VAL-PHYSVAL-DEFINITIONS (/root/physval) independently established station-ID
set subtraction, same-module paired strip faces and active32.3..181.455mm pixel
ideal annuli rather than service radii. Current disc datums remain explicitly
distinct from historical coverage denominators.
VAL-PHYSVAL-IMPLEMENTATION reviewed fixed
fbed1779adef22f659152200b9c35d84f2c22d71: no actionable findings. It verified all
8448ray count/ideal/material/pipe identities, source/archive hashes and an
independent oriented-box oracle for262selected rays against45646sensitive
patches, with zero differences. It did not rerun ROOT navigation or grant human
acceptance. Reviewer commands were read-only; no reviewer files changed.

## Delivered outcome and limits

Reviewer plots now exist: direct eta/phi maps and projections with patch,
physical-sensor, logical-station and ideal/hole definitions, plus stacked native
X/X0 and L/lambda_I versus eta. Holes average0.07622/max2; offset sampling exposes
gaps missed by one grid. Maximum4.87848X0 is retained, dominated by represented
services. Finite x=y=0,z=−150/0/+150mm and B=0 sampling is not continuous luminous
acceptance or tracking efficiency. No physical parameter tuning, new overlap or
Geant4/ACTS reconstruction test is claimed. Native ROOT material closure does
not validate physical recipes.

Six unit controls pass and are wired into CI. Project records,183session records
and token-site validation/build pass. An initial tracking role/workstream mismatch
was corrected to WS-SOFT; early missing-deliverable validation happened before
the author files existed and is not hidden as a scientific result. No tests,
tolerances or acceptance criteria were weakened. Usage summary was executed;
this task/children have no newly exposed input/output token observations. The
historical project totals cannot be allocated to this task.
