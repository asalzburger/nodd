# TTBAR-PU200-PhysVal-10 final independent assessment

- Role: PhysVal, supplied through the explicit fallback mandate in `.codex/agents/PhysVal.toml`.
- Reviewed revision: `d93063a9e4827e9f9a66fc0f175c16c3cc1dbc64`.
- Recommendation: no unresolved blocker for reporting the qualified prototype comparison. No human acceptance or detector-design sign-off.
- Source set: all 18 pinned assignment inputs; executing scientific sources unchanged from `46926ce90074d44b4a4ad42bbca0f318c6a68449`. Source-directory delta is only the documented README wording correction. Dirty inputs at assessment: assignment/session metadata.

## Actual independent checks

All checks passed. Rehashed 1,500 distinct files, including 464 reconstruction outputs (116 per length), 400 portable chunks, 110 sample outputs, summaries, reports and figures. All 400 original/corrected reconstruction gzip payload pairs and all 100 Fatras pairs are byte-identical; every reconstruction binds the valid shared-sample report.

Recomputed all 1,864 reported metrics, absolute intervals and paired intervals using explicit event-index sampling: 2,000 jointly paired resamples, seed 153044. Exact agreement with the retained profiles. Independently checked point values, defined-resample counts, degeneracy/reference flags, Wilson intervals and event-bound semantics.

An independently written classifier reproduced all 910 count columns for events 0, 57 and 99 at every length, from both raw and portable inputs: 12 pairs and 10,920 count checks. Candidate quality/selection/winner/category identities, conditional denominators, profiles, pure-seed coverage and ambiguity convergence match. Independent response checks cover 979,452 measurements and 335,456 pixel space points, including sigma/variance scaling, float32 transforms, all-system CKF inputs and muon hypotheses.

Verified 12 figure hashes and all six single-page PDFs with required scope/resource/uncertainty captions. Inspected the hashed six-page contact sheet and detailed guide overview/candidate renders: no clipping or overlap. Independently rehashed and inspected fresh-directory replay artifacts.

## Independently reconstructed results

Guide-selected ambiguity stage; percentages:

| Length [mm] | Inclusive efficiency | Hard scatter | Pileup | Fake fraction | Duplicates / accepted |
|---:|---:|---:|---:|---:|---:|
| 0.5 | 76.052696 | 80.362727 | 75.808150 | 0.195437 | 2 / 69,076 |
| 1 | 76.101945 | 80.404419 | 75.857827 | 0.180882 | 4 / 69,106 |
| 1.5 | 76.138882 | 80.404419 | 75.896860 | 0.203857 | 3 / 69,166 |
| 2 | 76.145598 | 80.362727 | 75.906322 | 0.229765 | 7 / 69,201 |

Every length has 89,342 eligible generated particles: 4,797 hard-scatter and 84,545 pileup. Denominators precede hit requirements.

For 2 mm minus 0.5 mm, percentage-point changes with paired pointwise 95% intervals:

| Metric | Change [95% interval] |
|---|---:|
| Guide hard-scatter efficiency | 0.000000 [−0.210904, +0.201545] |
| Guide inclusive efficiency | +0.092901 [+0.040939, +0.148161] |
| Guide pileup efficiency | +0.098173 [+0.045343, +0.153565] |
| Guide fake fraction | +0.034329 [+0.005459, +0.063788] |
| Guide duplicate fraction | +0.007220 [+0.001448, +0.013235] |
| Frozen fake fraction | +0.775544 [+0.677107, +0.873418] |

Equal aggregate hard-scatter counts do not establish equivalence. Showing frozen and guide-selected results together preserves the material selection dependence of the fake fraction.

## Scope and qualifications

The evidence describes 100 shared physical events, qqbar-only ttbar, exactly 200 pileup interactions, Fatras, constant 3 T and fixed geometry/material. This uncalibrated Gaussian local-v scan has merging disabled and establishes no physical coarse-cell occupancy, material or hardware-service performance.

Source particles/hits, pixels, space points and both seed collections are invariant. Non-target response changes in 100/100 coarser events through smearing-stream coupling. Endcap measurement totals decrease by one, two and two; differences include that coupling.

The unchanged 2,000,000-edge graph cap is reached in 99/100 events. These are resource-limited chain results, without a causal efficiency-loss estimate. Low-count profile intervals are pointwise; undefined and degenerate cases are retained, without simultaneous-coverage or equivalence claims.

Quality includes the native finite, symmetric, positive-definite covariance flag and positive finite diagonals. Portable matching retains the native validity flag, not the complete covariance matrix.

All six transport failures and eligibility inventories in the affected events were independently checked:

| Event | Initial pT [GeV] | Origin |
|---:|---:|---|
| 8 | 0.404776 | Generated pileup |
| 31 | 0.499237 | Generated pileup |
| 36 | 0.533854 | Generated pileup |
| 42 | 0.487791 | Generated pileup |
| 63 | 0.450487 | Simulation-secondary positron |
| 93 | 0.512550 | Generated pileup |

None is headline-eligible. Every headline-eligible generated particle in those six events is present in selected inputs and simulated outputs. Missing background transport remains a qualification for occupancy and fake rates. All events and truth stay in the analysis.

No repository file was changed by the reviewer. Independent scratch integrity/classifier scripts are retained beside this record with only their absolute root locator replaced by a repository-relative locator. Original and retained hashes and exact adaptation are recorded in `physval10-checker-provenance.json`. Coordinator rerun outcomes are in the session journal. No correction is required for the stated scientific scope. DES-042 remains PROTOTYPE.
