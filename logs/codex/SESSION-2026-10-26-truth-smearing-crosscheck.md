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

Pooledtable atcee84b8:699273measurements,52volumes/90coordinates, SHA256
1b1abb51667a72ad3cf293b65545824c4a145fc87e16af525a97080f5cfdedf8. Reducerfd0daa4
checksROOT/digitizationhashes andretainsmean/centeredSD/uncenteredRMS. Two scientific
mixture/invalidinputcontrols pass. SoftEng verified nativeGauss JSON andnative
bounds rejection(defaultmaxRetries0); DES amended beforeproduction toretain
losseswithouttuning. Existingruntime importsverified; no shared changes.

Pilot100events:100fits,0invalidcovariance,1443measurements(4071D/10362D),all7
systems/90coordinates;2479marginals exactfloat32sigmaSquared, no clusters, no
bounds losses. Generated31particlebranches equaloriginalpT1first100. Sixnew
controls pass inportableandactualnativePython3.14.5. Mainportable37total:32PASS/
5expectednative-onlySKIP. Exactlaunchpin dc9a9272153a4dcf9b06901911195527b5c64f50
committedbeforeexplicitproductionauthorization. Allthree20kFatrascases launched
concurrentlyatthatpinandunchangedtable; native source/config/inputbytes frozen.
