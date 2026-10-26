# Fatras Gaussian-smearing cross-check

User asks to inspect a new PR101 comment. Reviewer asalzburger-review confirms
the requested full pull views and asks whether cluster-size-dependent errors
are used, then requests full Gaussian-smearing Fatras with measured total
cluster RMS for pixels, short strips and long strips. Main confirms the
current baseline applies the independently trained size-dependent covariance
after geometric clustering. Add a separate comparison without altering that
reference. Source comment6419397508,2026-10-26T15:04:45Z.

Start at5d77b72c70a3534d64c729ad77aa39a418a633d7, clean branch. Read applicable
AGENTS/PROJECT and coordinate/review/evidence/acts-spack instructions. Preflight
warns changed setup/lock fingerprints; verify the existing isolated runtime,
no shared install changes or acts run asset-copy helper. DES025 amended before
implementation. Pool all cluster sizes by native volume/coordinate using the
existing50k independent training ROOT; retain centeredSD,mean,uncenteredRMS.
Main owns training reduction, campaign/design, plots, records and integration;
SoftEng owns a new isolated smearing helper/CLI/tests and native3x20k execution.
Separate exact-revision PhysVal follows. All remains PROTOTYPE/DRAFT.
