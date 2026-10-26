# Gen3 truth-tracking baseline

Human requests both Geant4 and Fatras single-muon truth-associated ACTS tracking
at fixed transverse momenta 1,10,100 GeV, PR100 map and Gen3 geometry, geometric
50x50 micrometre pixels and module-default strips, resolutions/pulls versus eta
and pT. Interpret ODD as the exact PR100 Gen3 tracker so map IDs match.

Start clean merged main709d7fe5e5620305812aff502c3e02b9e7be3347 on branch
codex/tracker-truth-baseline, reusing the previous material worktree/runtime.
DES025 amended before implementation; all characterization remains PROTOTYPE.
Main owns campaign, reduction/plots, records and integration. Delegate native
full-chain implementation/execution to SoftEng, then a separate exact-revision
PhysVal assessment. Assignments prepared and retained before dispatch.

Read repository AGENTS/PROJECT, coordinate/review/evidence skills, DES007/008/025
and ADR008. acts-spack preflight warns changed setup/lock fingerprints. A direct
authorized acts run acts-nodd imports ACTS, Geant4, DD4hep and DDG4; Geant4
11.4.3 reports all12 datasets installed. The helper attempts shared ODD asset
copies, denied by sandbox; do not retry that mutation with escalated permission.
ROOT setup also warns about shell detection. Use the already working isolated
nODD native runtime with explicit activation and hashes for actual campaigns;
an import alone is not a native simulation pass.

Draft configuration:20k one-muon events per backend/momentum, uniform eta[-4,4],
full phi, origin, random charge; deterministic seeds. Field optional clarification
requested:2T ODD example,3T ideal fixture,or finite DES026 field. Default2T if no
preference, with sufficient reply time before final generation.
Short strips75umx0.5mm from DES007C01;long strips80um and one measurement per
physical face from DES008C05/measurement contract. No synthetic stereo.

TRUTH-SoftEng-01: source675612ef5a2c5b23b7c1bcf7456f278a4447b819;
write ownership is the native CLI, runtime/digitizer helpers/controls, safe shell
wrapper, optional isolated native sidecar and eight declared case outputs.
Assignment JSON retains the full task and completion conditions before dispatch.

Before production, ideal digital cell-centre response made explicit in DES025
and campaign: exact path-length charge,zero threshold,no added drift/diffusion
or empirical variance table. Native cluster covariance formula must be retained.
SoftEng ownership expanded for per-event audit/selected-particle ROOT outputs
and task-local native compiler artifacts; no shared build changes authorized.

Human field clarification: Constant3T, as an ideal-field nODD baseline.
Campaign and DES025 updated before production; SoftEng notified immediately.
Both simulation and fitter use the same3T constant field. Any2T pilot is a
separate historical control and cannot supply retained production evidence.

Fatras3T100-event pilot succeeds with100fits,zero native invalid covariances.
Geant4 pilot exposed default Silicon-only sensitive mapper missing namespaced
pixel_Silicon; corrected explicit material list. Initial control excluded from
baseline and retained separately after native output closes; no geometry or
shared install patch. Exact both-material mapping is required for production.
Seven main analytic metric controls pass,including wrappedphi,charge symmetry,
full theta/qOverP cross term,uncut tails,empty bins and event bootstrap.

Further native-pilot check found long-strip1D digitizer needs two physical
segmentation axes even when indices=[0]. Initial one-axis configuration made no
long-strip cells; all100fits alone did not validate subsystem coverage. First
Fatraspilot retained separately as excluded one-axis control. Correct native
contract adds one full-length unmeasured-axis bin, preserving1D measurement.
Both corrected pilots must demonstrate actual1D/2D measurement coverage before
production; no initial pilot is retained as baseline evidence.

Human adds Fatras-derived hit-error parameterization via existing ACTS script,
and permits long-strip smearing only if native1D geometry is unavailable.
Corrected pilot has4071D+10362D measurements across all7systems, so keep geometric.
Training now independent50kFatras events with loguniformpT1..100GeV,seed142042;
freeze one hit-error table for both performance backends. Pinned script uses
British error_parameterisation.py spelling. Its pooled-tail RMS append precedes
recalculation; audit rawtable overflow before adopting, with source unchanged.

G4pilot exposes pinnedTruthTrackFinder double-index lookup; measurement-map
values already name simhits,unlike measurements. Authorize isolated adapter
repair within ownedTruthTracking.cpp before production,with original/corrected
counts and direct-map control; simulation/nativeKalman unchanged. Earlier G4
pilot without repair isexcluded diagnostic. Full sourceevidence retained later.

Native source inspection confirms ModuleClusters::squash recalculates geometric
variance from weightedcellwidths and discards pre-cluster varianceMap. Authorize
isolated post-cluster calibrated covariance adapter: unchanged IDs/positions/
associations,diagonal RMS² byvolume/cluster size,lastentryoverflow,zero measured
offdiagonals as table carries no correlations. Native truthadapter deduplicates
physicalmeasurement perprimary beforetimeordering. Both documentedbeforecode.

TRUTH-PhysVal-01 prepared before dispatch: read-only preliminary benchmark/
analysis assessment ateb86998ad5d42c37bf7d244063c575f93b0c42a3, plus exact
ACTS355ea primarysources. No concurrent dirtynative implementation assessed.
Later fixed-revision finalresults assessment remains required.

G4runtime profiling identifies repeatedBeamOn(1) cut-couple construction.
Authorized task-local ordinary-run lifecycle adapter,independentevent processing
and nativephysics unchanged,with mandatorysmall standard-vs-adapter primary/
simhit comparison beforeproduction. This avoids changing sample size or packing
muons intooneevent. No sharedsource/install edits.

Preliminary independentPhysVal at eb86998 confirms metrics/denominators and
reproduces upstream hiterror pooled-tail/cap/NaN defects. Result retained. Main
calibrationwrapper will preserve rawACTS output and independently recompute exact
groups plus finalpooledoverflow; explicitunsupportedtailmerge.11main analytic
controls pass (7metrics+4calibration). Newtaskanalysisvenv installs pinned existing
plotpackages plus pandas2.3.3; sandboxDNSfailure retried network-enabled, no shared
installation change. Later finalnative/results review still required.

First baseline parent01a17858-7fb6-7b61-b726-8199715ccd69 has a verifiedclosed
boundary/clientstatusfailed when later usersteering continuedwork. Its exact
5,549,160input+25,630output=5,574,790tokens are recorded once in this baseline
account;statusdoesnotmeanthis ongoingtask ended. Active follow-up01a17864-5f5d-7140-9b37-3445edfdbebb remains excluded. PriorPR10020,489,109tokens imported
only into original cumulativeaccount;completedvisible/approval/merge refreshed.

Dedup amendment beforeimplementation: native7measurement selection andtruth
matching also consume unique(primary,measurement)pairs; fullmeasurement-simhit
map stays unchangedfortruthaverages. Otherwise mergedG4steps could overcount
selection/tracktruthmatches. OldclosedunfixedG4diagnostic moved toexcludedcontrol.

Independent50kFatras training completed:699,273simhits/measurements,49,999
selected/attempted/fitted,onebelow7unique;0nativeinvalidcovariance. All7systems
covered. RootinventoryinitiallyselectedoldTTreecycle,correctedbyhighestcycle
control;rawROOTunchanged. TrainingobserverC++/binary endhashes arepost-run
inventorybecauseadapterdevelopedwhiletrainingran; executedtransport/digitizer
libraries andPythonstartuphashes arestable, measurementpositions unaffected.
Finalproductioncapturesallsource/binaryhashesatstartupandwillremainfrozen.

Five-event G4lifecycle control passesfullpayload equality:31particlebranches,
25simhitbranches/95hits,42measurementbranches/80measurements,99tracksummary
branches,13auditbranches. PairedNaNsallowed;nootherdifference. Persistent123.87s
versusstandard203.55s. Nativeoldfinder63 versusdirect-index65primarymeasurement
uses exposesactualbadlookup. Controlsuseidenticaloldsourcebytes; laterunique-map
repair doesnotinvalidate lifecyclephysics comparison.

Untouched pinnedACTS hiterror script ran on all699273trainingmeasurements.
RawJSONretained; audited106cluster groups with correctednativeclampedtails.
FrozenRMSfile SHA2564d637137a64ae5854fc795634a4fdffae8ece4d081220ef143de907f219b460c.
Nativeoutput map cache is now content-checked and atomically replaced so parallel
casescannotreadpartialJSON. Nativeenvironment12tests pass includingimmutable-map
conflict/latestROOTcycle guards; mainanalysis18pass4nativeskips before IOguard.
Finalcalibratedpilots/production use newsourcepin andfrozentable, not controls.
