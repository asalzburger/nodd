# Prepare PR137 and preserve the calibration for reuse

User request (2026-11-12): “Can you prepare the PR for merging, recording the calibration model for later usage ?”

Bounded follow-up on PR137, start d862d943600307a67a10a08c5644e7e4cf224007. Preserve existing coefficients, frozen numerical source, all plots/statistics and primary inputs. No new training, transport, geometry or sign-off. The request authorizes code/model/merge preparation, not merging this PR or its predecessors. The coordinator initially interpreted it to include ready-for-review state; the explicit automatic-review rejection below supersedes that interpretation.

Used nodd-coordinate and nodd-review-validation. No native runtime use or shared dependency changes; existing NumPy Python only.

Initial public state: PR137 draft, mergeable into its existing PR136 base, two successful workflows, no reviews/comments/unresolved threads. Open stack PR133(main)→134→135→136→137 remains explicit. Prepare137only; do not approve/merge/retarget predecessors or rewrite history.

Recorded spline-v1(default) and linear-v1 IDs, domain, units, hashes, exact feature semantics and inference/fallback equations in frozen/manifest.json and reuse.md, keeping coefficients at SHA8595d8fd74d17edf2561d889e52910b3badbd358b446b951ca5083938c7ccdf1 and frozen source unchanged. Added highstat_inference API/CLI with hash/geometry/semantics guards, measured-only columns, output provenance/flags and no overwrites. Added7 meaningful reuse controls and CI coverage using the already pinned NumPy environment.

All16 NumPy controls pass (7new+6model+3analysis). Exact20k population replay reproduces all4linear/spline pre/post energy-ratio series bit-for-bit, all84zeros. An initial10k-vs20k bit check failed at batch-size floating-point matrix-product rounding; kept this failure, no model/reference/test tolerance changed. Ten-k chunked diagnostics measure maximum4.885e-15 ratio difference, no mean difference; full20k exact check passes. Compact reuse-verification JSON records this distinction; arrays remainlocalignored.

## Separate software review assignment

```json
{
  "id": "ECAL-CALIBRATION-REUSE-SOFTENG",
  "role": "SoftEng",
  "input_revision": "6547c1016ca90f99f82445c1012ee1055f2a08a8",
  "inputs": [
    "software/analysis/calorimeter_digitization/highstat_inference.py",
    "software/analysis/calorimeter_digitization/test_highstat_inference.py",
    "docs/validation/ecal-highstat/frozen/manifest.json",
    "docs/validation/ecal-highstat/frozen/reuse-validation.json",
    "docs/validation/ecal-highstat/reuse.md",
    ".github/workflows/validation.yml"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Review the new frozen-calibration reuse interface for PR137 merge preparation. Check versioned model identity/hash bindings, geometry/feature guard, input units/shapes/dtypes, measured-only/no-fit API and CLI, zero/fallback/clipping behavior, output provenance/no overwrite and meaningful tests/CI. Verify original frozen/models.json and numerical highstat_model.py unchanged from e65962c259cec1f8744252fccfa17211004f4d61. Coefficients/statistics/plots unchanged; no scientific retuning. Main tests7new+6model+3analysisPASS. Full20k API matches all4saved pre/post ratio series BIT-EXACT; initial10kchunk-vs20k bitcheckfailed due matrixbatch roundoff, no tolerance/source/reference changed; measuredchunks max4.885e-15 ratio, zeromeandiff. Assess this provenance/interpretation. May run the16 pureNumPy tests and exact20k inference using local validation arrays/predictions if useful. Existing Python /Users/salzburg/Documents/work/installed/acts-nodd/pyvenv/bin/python, -B, OPENBLAS_NUM_THREADS1. No native runtime, fits/transport, source writes, new configs, delegation, publication or human approval. Read primarysource before author conclusions. Openstack133\u2192134\u2192135\u2192136\u2192137 is documented; only137 will be made ready per currentuser request, not merged.",
  "deliverable": "Exact-revision software/interface assessment with actionable findings or explicit no-material-finding, commands actually run and limitations.",
  "completion": "Return the bounded final assessment promptly; no human signoff."
}
```


## Separate software assessment

ECAL-CALIBRATION-REUSE-SOFTENG at6547c1016ca90f99f82445c1012ee1055f2a08a8: no material software findings. Verified hash/model/geometry/feature compatibility guards, measured-only API/CLI, units/shapes/dtypes, zero/fallback/clipping, provenance/no-overwrite and CI configuration. Independently passed all16NumPy tests(Python3.14.5/NumPy2.5.4), confirmed identical model/coreGitblobs to e65962c, reproduced exactfull20k pre/post ratios and10k chunk roundingmax4.884981308350689e-15 withzeromeandifference. No source writes/native runtime/fits/transport; remoteCI not independentlyexecuted. Caller remainsresponsiblefor units/simulationcontext beyondcheckedhashes. Technicalassessment only.

Main byte-compared frozenmodels/core/analysis/resultsummary tooriginalcommits: allunchanged. Local project/inventory/session/interaction/token validation and token-sitebuild pass; only curated source,metadata andcompactproof innewGitobjects, noeventpayload. ActualCLI10k smoke passes andmatches APIoutputSHA. Separate reviewer model counters unavailable; usage[] remainsunknown.


## Publication-state approval rejection

PR137 description updated with model IDs, manifest/reuse links, exactcheck distinction, software assessment and merge-commit dependency order. Connector update_pull_request lackedwriteaccess(HTTP403); authenticatedgh pr edit succeeded. No comments posted.

A separate connector mark_pull_request_ready_for_review action was rejected by automatic approval review: “Marking PR #137 ready for review changes its publication state and conflicts with the repository rule that this task must end as a draft PR; preparing it for merge does not explicitly authorize this transition.” This is distinct from the connector's HTTP403 capability failures. No CLI/indirect ready transition was attempted. PR137 remainsdraft; explicit human approval is required before retrying that state change. Continue all unaffected preparation and CI first. No merges/sign-off/predecessor-state changes.

At f57b91a8f62727a8303b19fd9429249ffaf6d9db the new GitHub CI step “Check frozen staggered ECAL calibration and truth-free reuse” passed; the full Project validation workflow was still running at observation. Token usage Pages succeeded. Final complete workflow status is checked separately.


## Explicit conditional ready-state approval

After the automatic-review rejection and all code/model/review preparation, the user answered the explicit question “May I mark PR #137 ready for review once its final CI run passes? The calibration model and reuse interface are pushed and independently reviewed; merging will remain for you.” with **“Approve ready for review after CI passes”**. This authorizes retrying only PR137's ready-for-review transition after its final CI succeeds. It does not authorize merging, predecessor transitions or detector acceptance. The earlier rejection was respected; no ready-state workaround was attempted before this new explicit authorization.


## Ready-for-review completion

Both complete workflows on2c635fbfe365890e328de9066f16447ccd76c305 passed before retrying the conditionally authorized transition: [Project validation43241403982](https://github.com/asalzburger/nodd/actions/runs/43241403982), [Token usage Pages43241403984](https://github.com/asalzburger/nodd/actions/runs/43241403984). This includes both build and unrooted jobs and the16-test calibration CI step.

With the new explicit user approval and CI condition satisfied, connector ready transition was permitted by automatic review but the integration lackedwriteaccess(FORBIDDEN). Authenticated `gh pr ready137 --repo asalzburger/nodd` succeeded. Connector get_pr_info verifieddraft=false, head2c635fbfe365890e328de9066f16447ccd76c305, existingbasecodex/ecal-calibration-staggering-tests, mergeable=true. Earlier policy rejection was not bypassed: the new explicit approval preceded the permitted retry; CLI only addressed the subsequent connector capability failure. No merge, predecessor state change, forcepush, detector approval or human sign-off.

Final metadata closes this bounded preparation record. Scientific source, coefficients, model metadata, predictions and plots are unchanged by closeout. Subsequent final metadata CI is checked without repeatedly changing the source record. Model and reuse instructions remain versioned in PR137; raw arrays/output remainignoredlocal. Tokenusage for this task and reviewer isunavailable; no estimates and no attribution of historical repository totals.


## 2026-11-12 token-accounting correction and work label

The earlier empty usage statements describe unavailable measurements at the original capture. The [PR137 accounting pass](SESSION-2026-11-12-pr137-accounting.md) now recovers **2 closed turns / 110 requests**, with **23,728,184 input + 70,135 output = 23,798,319 observed tokens**, owned here exactly once. Inventory: [USAGE-2026-11-12-pr137-calibration-accounting.json](../usage/USAGE-2026-11-12-pr137-calibration-accounting.json). App-visible request/final-response and verified parent/child assignments match the selected exact turn IDs. The canonical title is now “Staggered ECAL model reuse and PR137 merge preparation”, which supplies the token dashboard work label. No token allocation among individual messages or multiple PR references is inferred. Cached input/reasoning are subsets; actual per-turn models, billing and other-device completeness remain unknown. The current accounting turn is excluded. Scientific source/results/coefficients unchanged.
