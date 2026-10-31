# STRIXEL-GBTS-PhysVal-03 — independent full-evidence assessment

Independent read-only PhysVal child `/root/strixel_gbts_physval` assessed exact
commit `a9867564c4ebaeac774aa350e0f440f887916067` under the explicit role fallback
and nodd-review-validation procedure. The reviewer did not author this
implementation. Native profile loading is not claimed. See the
[assignment](physval-03-assignment.json) for the 105 pinned inputs and boundaries.

## Findings and disposition

**Zero unresolved material findings.** The documented prototype interpretation
is supported at the reviewed revision. This is an AI technical assessment,
not human design sign-off or acceptance.

Both PhysVal-02 findings are resolved: zero-discordance contrasts carry
conservative finite-sample bounds without an equivalence claim, and net
measurement-count deficits/excesses are distinguished from exhaustive hit
losses/gains. The ROOT wrapper's serialized-byte binding correctly handles the
44 JSON key-order round-trip differences without weakening the numerical,
classifier or ROOT gates (`root_audit.py`, lines 112–126 at the reviewed commit).

## Actual independent checks

- All 105 pinned objects match their SHA-256 records and reviewed revision.
  All 80 NPZs contain 1,000 unique event identities and 79 arrays.
- All 240 retained case artifacts, all 80 original serialized-summary bindings,
  common native source maps, configuration gates and report hashes agree.
- Independently reconstructed 1,278,653 exact point values across cases,
  regions and stages: counts, rates, residuals, pulls, widths, biases, tails,
  common-success ratios and pairing diagnostics. No discrepancy; no width is
  defined below 30 finite entries.
- Independently reproduced all 80 global Wilson intervals and 400-resample
  paired efficiency intervals, plus first-principles central 100 GeV muon
  z0/theta width and ratio bootstrap intervals.
- Focused unittest discovery for `software/analysis/strixel_reconstruction`:
  49 tests passed. `bridge.py --verify`: all 20 baseline bridges passed,
  covering the 812 original observables and NaN masks.
- Verified all recorded ROOT case bindings/counts totaling 5,406,814 covariance
  marginals. Additionally re-ran the frozen ROOT auditor on three actual
  100 GeV cases: 303,741 marginals, complete event/raw-candidate counts and
  representative tuples passed. This includes the Geant4 electron case with
  455,022 CKF candidates.
- All 40 figure hashes agree; all 20 PDFs are one page. Four rendered figure
  families have consistent interval endpoints, units and low-count handling.
- Session validation passed for 217 records; session summary completed.

The reviewer used only permitted ephemeral scratch under `/private/tmp` for
independent offline calculations and PDF rendering. No canonical source/data
file changed, native job launched, commit created, publication performed or
further agent delegated.

## Reproduced observations and limits

The central 100 GeV muon z0 ratios at 2 mm are 1.106 in Fatras and 1.151 in
Geant4. The same 254 Fatras and 267 Geant4 matched central events supply every
pitch. Endpoint all-generated efficiency changes span 0 to +3.6 percentage
points over the full matrix. The high-momentum charge and momentum tails also
reproduce.

Non-target realized inputs change in 12–167 events per group at 2 mm, including
two central muon events per transport. Unique longitudinal causation is
therefore not established. Intervals are pointwise and statistical; sparse-bin
bootstrap coverage remains limited. The study establishes neither physical
coarse-sensor calibration, statistical equivalence, occupancy performance nor
detector acceptance. Geometry and material remain fixed.

Scientific input remains `4ea4af17727020bac2ba8f5e2f6172378711c15a`; native
execution remains `8c45136098d1e4d407c4d2f96e3590bb78eb6b75`; retained analyzer
SHA-256 is `503bd05aa6fff1164dda466eba8a34dfa2852f3f6888db3e5c3b082cca7d4fd8`.
Frozen helpers and baseline evidence are unchanged. The reviewer did not repeat
the entire bootstrap/export campaign or all 80 raw ROOT audits: their bound
records were checked, supplemented by the independent calculations above.
The coordinator's full exact replays remain separately recorded in
[verification.json](../../../docs/validation/DES-042/gbts/verification.json).

## Coordinator reconciliation

No scientific remediation is required. Source, data, figures and summary stay
exactly at the assessed commit; only the assignment, this curated result,
session closeout and task disposition are added afterward. The local prototype
task is complete. Physical calibration, occupancy, material redesign and fitter
quality remain conditions for any later detector-selection claim.
