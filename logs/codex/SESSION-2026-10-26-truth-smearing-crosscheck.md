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

Allthree productioncases complete/exited0 atdc9a927:20000generated each,
19992/19998/19999selectedandfitted;0fitloss/invalid6D/nativeFake/finalmeasurement
loss. All31generatedbranches exactlyequalgeometric counterparts. Measurements
280368/279217/279930; coordinatechecks486521/484735/485772. All1457028marginals
exactfloat32sigma2. PoolednormalizedresidualSD1.00016544/0.99968292/1.00002377.
Originalgeometric/nativegeometry/runtime retained;27commoninputfiles exact.
SevenPNG/PDF/SVGZsets+42CSVrows/fullcounts retained. Mainviewedcomparisoncore/
fullandmeasurementcore atoriginalresolution; labels/legends/tails legible.

CSVwriter defaultCRLF triggered gitdiffwhitespacecheck; fixedwriterLF andreduced/
renderedagain, no numericalchange. Nativeproduction notrerun. Initialsource/data
reviewpin c547db045b78ed8816863ff97da1a32779a810fc. SeparatePhysVal01recomputed
all90traininggroups (max2.78e-17mm),all1457028marginals,270groups,15aggregates,
all42histograms/CSV,59989CholeskyPD6Dcovs,21newROOT hashes/27commonidentities.

BLOCKINGfactualfinding: mainandSoftEng initiallymisread per-smearermaxRetries0
as effectiveoneattempt. PinnedACTS355ea684 DigitizationAlgorithmConfig default
minMaxRetries10 overridesit; Fatrasloopallows maxRetries+1=11attempts. Actual
runs usednative10retrydefault throughout. Preserveallrawreportsandoutputs;
addexplicitpercase/top-levelcorrectionannotations,correctDES/README/7figure
footers/futureCLImetadata. No physicalsettings/response/source schedulingchange,
no reruns. MainASTcomparison of5physicalfunctions exactvsdc9a927. Actual
executedsoftwarehashes nowauditedatlaunchcommit via gitshow; CI fetches history.
NewhelperhandlesunexposedPythonfield byexplicitpinnedC++default, no falsely
claimedruntime introspection. IndependentPhysVal02correctionreview assigned
at7c9340b99447959cc2efcab17340292d83304c32; allnumericdata/nativehashes exactly
unchanged. All39portablecontrols:34PASS/5expectednative-onlySKIP.

Originalbaselineclosedparentusage finalized onlyinoriginalaccount,106885503
observedtokens. NewSoftEngclosedturn01a178c9-7b18-7f52-961f-f247b0d5f6e2 adds
6040316input+21171output=6061487observedtokens tothisnewaccount only, notprior
SoftEngbaseline turn. Cached5966208/reasoning5037 subsets. Currentcoordinator
01a178c7 activeandexcluded; finalseparatereviewerusage importedwhenclosed.

FinalseparatePhysValcombined01/02report: originalpin c547db0 andcorrectedpin
7c9340b99447959cc2efcab17340292d83304c32. Retryblocker resolved; no scientific/
provenanceblocker remains. All2985scalarstats maxdiff2.22e-16, all462CSVfields,
all7PNGoriginals,21ROOT hashes,90traininggroups/1457028variances/270groups/15
aggregates independentlychecked. MinorREADMEtestcount corrected toeightnew
controls,39portabletotal/34PASS/5expectednative-onlySKIP. Mainactualnative
Config.minMaxRetries field IS exposedand10, all8newnativecontrols pass. Earlier
sourcegrepabsence didnot establishabsence ofPythonbinding; no suchclaim retained
asactualobservation. Fallbackgenericbranch coveredbymocks.

PhysValclosedturn01a178d6-5469-7f93-8fae-aafcc56a98fc recordedonceforcombined
assignments:8133378input+20789output=8154167tokens;8013184cached/6321reasoning
subsets. Newboundedaccounttwo disjointclosedturns:14173694input+41960output
=14215654observedtokens,13979392cached/11358reasoning subsets. Rootcurrent
01a178c7activeandexcluded; whole-taskcostpartial. Safe15activevisiblemessages
andtwochildfinals retained, allreasoning/toolargs/results excluded. Freshpublic
PRdiscussioncapture andsynchronizedledgers accompanycloseout. FinalCIruns at
pushedhead checkedseparately; no mergeorhumanacceptance.

## 2026-10-27 closeout reconciliation

The smearing coordinator turn01a178c7-5878-7141-befd-49e06fdfdd43 is now
completed. Its89 reconciled requests report18,015,766input+69,395output
=18,085,161tokens, imported once into this original smearing account. Three
disjoint finalized turns now total32,189,460input+111,355output=32,300,815
observedtokens;31,849,856cachedinput and37,115reasoning are subsets. This does
not allocate the separate active merge-preparation turn. Twenty safely curated
visible messages, including the final response, replace the provisional active
snapshot. No private reasoning or tool arguments/results were retained.

At reviewed headffd1cb9, both Project validation jobs and Token usage Pages
completed successfully. Public discussion was refreshed during merge preparation.
The user says the result looks good and requests preparation for merging; this
is recorded as merge-preparation authorization, not formal detector sign-off.
