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

TRUTH-PhysVal-02 prepared beforefollow-up: fixed8b7254cfc36e1462088e7d390577a4a29dbf1075
native/source/trainedtable review,independentall106groupROOTreduction andactual
5-eventG4lifecyclepayloadcomparison. Productionperformanceisnotyetassessed.

DraftPR101 createdandattached. Nativecalibrated100pilots bothpassall7systems;
Fatras1443measurements(4071D/10362D),G41663(4481D/12152D). All2479/2878measured
coordinatevariancesrespectivelymatchfrozenRMS²exactly. G4uniqueprimary/proto1459;
rawassociations1461/faultynativeproto1433demonstratefixes. Bothpilots100fits/no
invalidcovariance. All6×20k productioncaseslaunchedatfrozen8b7254source.

Token-site validator initially rejected two newlysavedusage-evidence arrays:
canonicalimportentrieswerecorrect,but evidenceinventorymustbeobjectwithselected
finalizedturns. Converted evidenceonly to existinginventoryshape; counters/owners
unchanged. No dashboardcodemodification or accountingallocation.

Governing issue102 created and linked in DES025/tracking, PR101 remains draft
pending all six samples, figures and final independent assessment. Fatras three
20k samples completed with19992/19998/19999fits, respectively; no attempted-fit
failures or nativeinvalidcovariance. Geant4 samples continue under frozen code.

Two first-pass G4cases(pT10/100)terminated in unusedoriginalTruthTrackFinder
diagnostic sorting invaliddouble-index hitpointers. No completedreport exists
for either; excluded controls. G4pT1 completed19994fits/19998attempts,2selection
losses,4nativefitfailures. DES025 amendedbeforecorrection: removeunsafeoriginal
finder,retainidenticalnativeextraction/smearingseed stages directly. Allsixcases
willrerun atonefixedrevision; no simulation,digitization,tableorfitretuning.

Correction source39cd5185d21a0ef47445023000c0381dc4b5360f frozenfor sixreplacement
20kruns. Main independentlychecked directnative seedconfiguration against pinned
addTruthSmearedSeeding and ran all24controls in actualnative3.14environment:
24PASS,zeroskips. Offlineexport/replaynowretains portablefullnative reports with
originalhashes and checks commonexecutednativebytes,training/table/group identities.
ACTS primarysource catalogueentry addedat exact355ea684 version.

Allsixfinalcases completeandexited0at39cd5185. Initialstrictreduction exposed3
zerobarcode nativeFake fits(G4pT1event2129:3/20hits;G4pT100event27:7/19;
FatraspT1event17622:11/23). IndependentSoftEng sourceassessment confirms default
doublematching50%completeness,not asecondaryidentity. DES025 amendedbeforeanalysis
handling: verifyselectedROOTprimarybarcode/counts,onecandidate/output index0;allow
onlyallzero sentinel+Fakeclass,retainseed-associatedresidualswithgeneratedtruth,
countnativematchingseparately,rejectvalidnonzero conflicts. No nativechanges or
retuning. Newbarcodecontrolandall25native/analyticcontrolsPASS.

Firstfullplotreplay passedsource/count/table audits butfractionrendering caught
Wilsonendpointfloatingroundoff(upper<1byulp forcompletebins). Canonicalinterval
now enclosesobservedfraction exactly; endpointcontrolchecksalln1..2048. Re-export
requiredwithnewmetricshash. Addedcentral68pullwidth panelsalongsidefullSD(logaxis)
to exposecoreandtail differenceswithoutclipping; alltailsretained.

Finalreduction7774037sourcepasses:119982finitefits,14selectionlosses,4G4pT1fit
failures,0positive-definitecovariancefailures. All3199735measurementcoordinate
variances exactRMS²atfloatstorage;90volcoords eachcase. Generatedtruthhashes
identicalacrossbackends ateachpT. TenPNG/PDF/SVGZsets+1440-rowCSV retained.
Main inspectedresolutioneta,fullpullSDeta,centralpullwidthpT asoriginalPNGs:
clearlabels,legends,errors,logscales,footers. Largepulltailsand100GeVforward
charge/resolutionlossesprominentlyreported; no cutsorunitpullacceptance.

TRUTH-PhysVal-03completedread-onlyatf7b14c60c8be613ce9165684d6ef03007ce1a456.
No blockingimplementation/reduction/presentationfinding forqualifiedprototype.
Independent17712scalarstatsmaxdifference7.28e-12;all3199735marginals,1836922
measurementdimensions,119982CholeskyPDcovariances,120keventdenominators,42native
outputhashes/11portablereports verified. All1440CSVrows/21600numericfields exact;
all10originalPNGs readable;688branches/12filepairs exactreference-removal controls.
First400bootstrapreplicates independentlyreproduced. Broadpulltails/forwardhighpT
lossesexplicit; no designapproval.

Finalized observedbaselineusage:5disjointclosedturns,58268635input+164447output
=58433082tokens;57473152cachedinput/57948reasoning are subsets. Includes original
closedfailed-rootboundary and4completedchildturns. Activecoordinator01a17864…
excluded, so task accountingremains partial. PR100 stays80165771observedtokens
in its three original accounts. Freshpublicdiscussioncapture and18activevisible
messages retained safely with noactiveusageallocation; private reasoning/tool
arguments/results notpersisted. Tokenpreview build successful.

FinalPRmergeabilitycheck found newmain2da3a8a (mergedPR97trackerpropagation).
Ordinarypreservationmerge:onlyconflictadjacentnewtaskinsertions inproject/tracking,
resolvedbyretainingboth complete stable-IDrecords; allotherper-IDparentchanges
programmaticallyverifiedpreserved. BothCIjobadditionsretained. No Gen3truth-native
source,numericaldata orfigure changes. Source f7 assessmentremains exact; native
executionpin39cd unchanged. Revalidatecombinedrecords/plots/workflowsbeforehandoff.

Humanfollow-up asks fullpull distributions overalleta,1/10/100GeV overlayper
parameter, explicittruth-minus-reconstructed sign. ContinuationofsamePR/baseline;
activecoordinatorturn remains01a17864,so reopen logicaljournalwithout splitting
usage orreimporting parentcounters. DES025 amendedbeforehistogramimplementation.
Sixboundparameters includingunmeasuredtime(prior diagnostic),plusderivedpT.
Commonlinearcore/logtailbins preserveallfinitepulls;full+coreviews,counts/extrema/
tails retained. Existingnative outputs andearlierprofilebytesremainunchanged.

Fullpullsource d79c77d exported42common-bin distributions:119982entries per
parameter,all6DcovariancesPD,nofinitepullmissing,zerounderflow/overflow. Allη
[-4,4],truth-minus-fit;wrappedphi,derivedpTfullcrosscov. All6boundincludingtime
withunmeasuredprior label. SixPNG/PDF/SVGZfull/coreviews+42-rowCSV. MainQA caught
symlog±1tickcrowding/shortauxframeoverlap, correctedticks/headerlayout and
re-rendered; inspectedcorrectedFatrasfull/G4core/auxpTfull atoriginalresolution.
24portablecontrolsPASS,5native-onlyskips(expected); new4controlsallPASS.
Existingnative outputs/training/map andearlierprofiledata/figuresunchanged.
