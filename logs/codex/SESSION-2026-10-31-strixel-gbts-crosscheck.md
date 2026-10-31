# SESSION-2026-10-31-strixel-gbts-crosscheck — GBTS single-particle reconstruction versus strixel length

## Scope and selected request

Contemporaneous local prototype extends DES-042 using DES-041 reconstruction.
User: “Now cross-check GBTS reconstruction for the single particle cases with the different strixel lengths.”
Start revision `4ea4af17727020bac2ba8f5e2f6172378711c15a`; clean source tree,
with task session pair created before execution. The branch was already two local
commits ahead of its remote. Previous external PR publication was rejected by
automatic approval review; no publication is authorized by this new request.

## Protocol and assignments

The governing DES-042 amendment was saved before implementation. It declares a
PROTOTYPE, complete 80-case matrix, 1,000 generated events/case, frozen Gaussian
response with only strixel local-v sigma scaled, existing pixel-only GBTS,
all-system CKF, fixed geometry/material/3T and hypotheses/cuts. No retuning.
Statistical uncertainty and response-model limitations are required outputs.

Explicit role fallback through repository workflow; native profile loading is
not claimed. Assignments use the full initial revision and pinned Git inputs:

- `STRIXEL-GBTS-SoftEng-01`, child `/root/strixel_gbts_softeng`: runtime/campaign,
  four new owned files, native smoke; [assignment](SESSION-2026-10-31-strixel-gbts-crosscheck/softeng-01-assignment.json).
- `STRIXEL-GBTS-PhysVal-01`, child `/root/strixel_gbts_physval`: separate read-only
  protocol assessment; [assignment](SESSION-2026-10-31-strixel-gbts-crosscheck/physval-01-assignment.json).
- `STRIXEL-GBTS-SoftEng-02`, child `/root/strixel_gbts_analysis`: analysis,
  retention and plots, three disjoint owned files;
  [assignment](SESSION-2026-10-31-strixel-gbts-crosscheck/analysis-01-assignment.json).

Children may not delegate, publish, modify shared dependencies or frozen helpers.
Coordinator owns scientific integration, project tracking and final evidence.
Separate final review must target an exact committed evidence revision.

## Commands and checks

- Node preflight returned exit2: setup script/Spack lock fingerprints differ.
  User warned; shared dependencies were not changed.
- Fresh runtime `source software/env/truth_tracking.sh`, imports `sys, ROOT,
  acts, acts.examples, dd4hep` passed (Python3.14.5, ROOT6.40.04).
- `workflow.py prepare` passed for all three bounded assignments.

## Results and revisions

Execution and assessment in progress. No detector or accepted baseline change.

## Token accounting

Exact disjoint client-reported counters are not exposed in this client/tool
surface. Usage stays empty; no estimates or private client state are collected.
The current coordinator turn is incomplete. Final session validation and summary
remain to be run; observed sums are unknown, not zero.
