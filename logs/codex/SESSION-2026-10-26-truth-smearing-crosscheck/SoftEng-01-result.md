SMEAR-SoftEng-01 complete. Input revision `c9be04caf58fc7e458c518fd7cb1566662db9ad4`; all production runs used frozen pin `dc9a9272153a4dcf9b06901911195527b5c64f50`.

| Fatras pT | Generated | Selected / fitted | Measurements | Coordinate checks | Seconds |
|---|---:|---:|---:|---:|---:|
| 1 GeV | 20,000 | 19,992 | 280,368 | 486,521 | 313.33 |
| 10 GeV | 20,000 | 19,998 | 279,217 | 484,735 | 312.29 |
| 100 GeV | 20,000 | 19,999 | 279,930 | 485,772 | 311.43 |

All three exited 0 with no invalid covariance, fit losses, native unmatched tracks or simhit-to-measurement losses. Every system and all 90 width groups are represented. Every measured marginal equals float32 of frozen sigma² exactly.

The pooled measurement standardized residual means are `0.002226`, `0.002389`, `0.001913`; population SDs are `1.000165`, `0.999683`, `1.000024`. All finite tails remain: respectively 1277/1266/1268 coordinates exceed |3|, one per case exceeds |5|, none exceed |10|.

Changed only:

- `software/running/nodd_truth_tracking_smearing.py`
- `software/analysis/truth_tracking/smearing.py`
- `software/analysis/truth_tracking/test_smearing.py`

Six meaningful controls passed under both portable and activated native Python; compilation passed. The 100-event native pilot passed with 100 fits, all dimensions/groups covered and exact marginal variances. Strict analysis identity/cohort checks passed for all final cases. All 31 generated-particle branches equal their respective geometric baseline arrays exactly. Session validation passed: 207 records.

No baseline source/output, shared installation or native C++ extension changed. Native Gaussian smearing uses no geometric response, merging or covariance replacement. Reused native truth/selection/fitter adapters remain unchanged. Native sensitive-bound rejection remains enabled; these samples observed no rejected measurements.

Frozen pooled-table SHA256:
`1b1abb51667a72ad3cf293b65545824c4a145fc87e16af525a97080f5cfdedf8`

Complete startup source/runtime/input hashes, all seven native output hashes, dimensions and residual diagnostics are retained in each `build/truth-tracking-smearing/fatras-pt*/run-report.json`. Report SHA256:

- pT1: `73e1767be5504710ebff8a8a525c2dad435e762e4ef27012828e32d75d9ffb22`
- pT10: `cd3ba88e64cf02d4dcf3c00a2e975d4c573e3af3df7010d44ae7b188df941c18`
- pT100: `644d1725454ef16bef94a863171d6ee2626e2992e2e8a0607396d1c81c0d0d50`

Independent PhysVal assessment and interpretation remain coordinator-owned; no human acceptance claimed.
