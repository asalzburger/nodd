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

Protocol assessment completed: [PhysVal-01](SESSION-2026-10-31-strixel-gbts-crosscheck/PhysVal-01-result.md) supports the qualified scan, with pairing/precision/model gates. Execution in progress. No detector or accepted baseline change.

## Token accounting

Exact disjoint client-reported counters are not exposed in this client/tool
surface. Usage stays empty; no estimates or private client state are collected.
The current coordinator turn is incomplete. Final session validation and summary
remain to be run; observed sums are unknown, not zero.


### Coordinator regression checks

The pre-existing DES042 suite passed22 tests. Analysis runtime imports passed
NumPy2.4.6, uproot5.7.7, Matplotlib3.11.2 and unrooted. ACTS supplier checkout
remains clean at355ea68493b326956756c9386d2fd9eaf9328568. Token dashboard validation
passed309 disjoint observed turns; these pre-existing totals are not task usage.
Initial project/session validation failed due to new record fields (`in_progress`
instead of `active`, incomplete activity schema); corrected records then passed
81tasks/42documents/23reviews and217session records. No check was weakened.


### Native implementation and bridge pilot

[SoftEng-01](SESSION-2026-10-31-strixel-gbts-crosscheck/SoftEng-01-result.md)
reports9focused tests and8completed2-event smokes. Coordinator independently
ran the unchanged classifier and [bridge](../../../software/analysis/strixel_reconstruction/bridge.py)
for the three0.5mm smoke populations (Fatrasmuon/electron, Geant4electron):
every original portable observable and NaN mask matches the same two retained
reference events exactly. [Bridge pilot evidence](SESSION-2026-10-31-strixel-gbts-crosscheck/smoke-baseline-bridge.json).
Two adversarial bridge tests pass. Native [smoke summary](SESSION-2026-10-31-strixel-gbts-crosscheck/native-smoke-summary.json)
is a development check with dirty-source hashes; full campaign must run at the
new committed source freeze. Physical hit/pixel/seed pairing is separately audited.
