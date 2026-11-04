# PhysVal-03 — analysis source assessment

Read-only review of five immutable Git blobs in analysis-review-snapshot.json,
with native source context8b7c147b3b0da4bd40dcd9ad06c98abcb2de58f9. These were
explicit uncommitted source supplements, not falsely attributed to that commit.
All five SHA256 checks and three pinned synthetic tests passed. No files changed.

P1: legitimate no-fit rows break retainer comparison because sign(NaN)!=truth
makes the shared helper wrong-charge flag true. Native deliberately masks that
flag. Apply has_fitted_parameters to recomputed flags/observables. Independently
reproduced; parent corrected and added absent-fit regression.

P2: incomplete momentum set could produce hardcoded twelve-case/240000-event
report. Require exact three-momentum/four-pitch matrix and common canonical
configuration/runtime hashes across all twelve. Parent corrected analysis and
report gates; added missing/duplicate matrix regression.

P2: all(empty balanced comparison values) passes. Require exact selection.json
and material-map.json comparison keys with explicit true values. Parent corrected
analysis/verifier and added regression.

Verifier originally replays point statistics, not uncertainty fields. Parent
added explicit --bootstrap deterministic full uncertainty replay, paired fraction
difference audit, and qualified default success wording.

Paired width algorithm itself is sound: shared all-generated draws, NaNs
preserved, common-success intersection, missing/undefined counts explicit.
Report finite-fit minus valid5parametercovariance count is appropriate if named
explicitly; distinct from native reference-surface/full6covariance audit.
Production numerical results were outside this source assessment.
