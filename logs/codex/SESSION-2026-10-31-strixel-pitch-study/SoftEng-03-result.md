# SoftEng-03 — completed Gaussian native control

Implementation composed frozen geometry/material preparation and all-event
reduction in three new files only. Source pinned58f49b9ce12f24f7e11b1b7a3f85fa48fbad020f
before native launch; all four subprocesses captured that revision before parent
advanced HEAD. Three focused tests and actual46250-sensor/94width-group config
checks pass. A100-event pilot passed100fits/1562simhits-measurements/2682exact
float32 marginal variance checks, no geometric cells or lost measurements.

Four5000-event100GeVcases completed: every case5000finite/native-matched fits,
73907simhits and73907measurements, zero missing measurements and native invalid
covariance. All517888written marginal variance checks pass (129472per case);
actual Gaussian-only/noMerge config, fixed fine-u sigma and one-coordinate long
strips verified. Exact generator/all/primary-hit payload pairing holds across
controls and original geometric first5000events. Every original twelve-case
output hash and55source/binary fingerprints stays unchanged. New source/helper/
metrics fingerprints unchanged at completion. Wall times104.62/104.61/104.61/
100.07seconds with three concurrent single-thread processes.

Native Gaussian has10retry/11draw-attempt contract at edges; raw retry counts
are not persisted. Observed zero lost measurements does not imply zero retries.
Full native reports retain stored-variance and standardized-local-residual audits.
Summary/source-header hashes are retained under docs/validation/DES-042/gaussian-control/
native-summary.json; raw ROOT/full arrays and verification logs remain ignored.
No source outside owned files or shared dependency changed. Native control
source58f49b9 and later parent analysis sources remain distinct; no design approval.
