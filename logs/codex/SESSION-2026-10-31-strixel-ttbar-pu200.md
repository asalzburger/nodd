# SESSION-2026-10-31-strixel-ttbar-pu200

## Scope and selected request

User: “Reconstruction of ttbar with 200 pileup, Fatras only, with the 4 strixel
configurations, 100 events each, focus on efficiency/fake rates.” The requested
guide resolves to ACTS `Examples/Scripts/Python/full_chain_odd.py`, inspected at
matching installed revision355ea68493b326956756c9386d2fd9eaf9328568.

Start90a3a753473255281b8bcf2d659a336150e16e97, clean worktree, existing branch
codex/strixel-pitch-truth-study. DES042 protocol amendment precedes implementation.
This is an isolated local prototype; no publication or shared dependency changes.

## Environment and initial checks

acts-spack preflight exits2 with unverified setup/lock fingerprints and missing
fullDD4hep/G4source warnings. User warned. Actual runtime activates Python3.14
fromnodd-software-layout/build/pyvenv and importsACTS/ROOT/DD4hep. Pythia binding
is absent (native import exits1); installed SpackPythia8@8.317 exists. Investigate
task-owned binding against the existing matching source/build before production.
The authorized ACTS sister development checkout is now555c66e71d0639665c2fa3d5574a0fe7f3f62cde
with unrelated local modifications, preserved; it is not the executing runtime.

## Protocol

Four0.5/1/1.5/2mm lengths,100events each, exactly200pileup vertices plus one
hardscatter. Guide physics/beam/vertex/generator cuts, frozennODD3T/geometry/
material/response/GBTS/CKF/ambiguity, no retuning. Production seed153042 and
smoke153043 fixed before execution. Independent event-block uncertainties;
allgenerated charged fiducial and conditional efficiencies, matched out-of-scope
truth, secondaries, duplicates and unmatched fakes remain distinct. SeeDES042.

## Assignments and checks

Explicit role fallback through repository mandates; no native profile loading
claimed. Bounded assignments will pin the committed protocol/source, own disjoint
files and prohibit native production, shared changes, delegation or publication.
Coordinator owns scientific integration, production launch and final closeout.

## Token coverage

Exact disjoint client-reported counters are unavailable. Usage is empty/unknown;
no estimates or private client-state collection. Active coordinator turn excluded.


Assignments recorded before dispatch: TTBAR-PU200-SoftEng-01 owns isolated
native/generation/runtime sources and small smoke; SoftEng-02 owns multiparticle
analysis/tests/plots; PhysVal-01 independently assesses protocol read-only.
All targeta734cf0, with exact fullSHA/objecthashes in prepared prompts and
assignmentJSON files. No child production launch/shared change/delegation/commit.


### Protocol assessment and sample architecture

[PhysVal-01](SESSION-2026-10-31-strixel-ttbar-pu200/PhysVal-01-result.md)
supports the qualified fixed-response study, with three high implementation
gates: selected collection must reach SafeFatras while fulltruth stays retained;
201producer origins must map demonstrably through HepMC conversion; generated
initialposition/ct must be retained for fiducial/HS/PUscoring. Peers notified.
Guidehardprocess is qqbar-onlyttbar; upstreamPythia disables FPE monitoring
inside generation, while Fatras/reconstruction monitoring must remain intact.

Native peer proposed task-owned lossless gzipJSON fullparticle/simhit replay,
approved to avoid ROOTfloat32and finalstate loss. Require actual native field
roundtrip comparison, not only common filehash. Generate/transport once, then
reconstruct4variants. Disk observed69GiBfree; measure actual1-eventfootprint
before production, prefer compact/stream-compressed audit. No old evidence removal.
Coordinator adds boundedcampaign.py and5adversarial tests, allpass (0.034s),
covering output tamper, sample rebinding, failed/wrongseed cases, path escape
and preserved failednative logs. Defaultonecaseprocess; no100eventlaunch yet.


Preflight exit-code correction: initial combined preflight+cat shell ended0
fromcat, incorrectly attributed to preflight in initial metadata. A standalone
rerun confirms exit2, matching nativepeer. Corrected check/status; unverified
warning and actual runtime boundary unchanged. PhysVal-01 originally reported0;
its historical report remains explicit, with this coordinator correction.


### Native generation smoke and bounded controller

Task-owned Pythia/sample/audit module built against matching ACTS355ea,
installedPythia8.317 and exactpreinstalledpybind3.0.4/ABI11. Initial development
build exposed defaultviewpybind3.1/ABI12 include precedence; taskCMake corrected,
sharedinstallunchanged. First generation attempt used protected/usr/bin/time,
which stripped DYLD paths and failedbeforeevents; failedreport retained. Fresh
zshbuiltin-time retry sample2 succeeds47.38s atsmokeseed153043:24908fullgenerated,
7586selected,8364transported,59624hits,201primaryvertices/origins0..200.
Losslesssamplegzip9463133bytes/event, wholedevelopmentdir67MiB. Every source,
runtime/preparedhash unchanged. Reconstructionroundtrip and4variant smoke pending.

Coordinator tightened campaign to<=jobs pendingcases and submitnewwork only
after success;6adversarialtests pass, including nolaterlaunch after firstfailure.
Nativepeer confirmed previoussmoke stopped before this executing source edit.
Nativeguard counts sharedlink usage byunique tracks while preserving pertrack
occurrences, matching frozenalgorithm. Analyzer preserves old uniqueinlier>=7
quality then accepted-only countidentity gate; rejectedraw mismatches retained
asdiagnostics, never silently promoted toacceptedtracks.


### Reconstruction development smoke

First0.5mm reconstruction completed nativework in51.51s:20896pixelSP,
601GBTSseeds, strictambiguitymaximumshared2 and exactfullfieldnative sample
roundtrip. Report failedonly sourceguard because coordinator campaign tightening
overlapped child startup after its generation-stop message. Preserve that
attempt and repeatbaseline withstableexecuting source; no test weakened.
Nativepeer measuredpeakRSS6.24GB, eventaudit5.6MiB pluscombined5.4MiB,
wholecase70MiB. Estimated100-event sample/audits fit observed69GiBfree disk;
this is a footprint estimate, not completed production. Runtime/campaign/native
sources nowstable forremaining4lengthsmokes. Shared dependencies unchanged.


### Native source ready and final smoke plan

All4same-runtime development smokes pass at52.546/52.260/52.487/52.541s and
peakRSS6.187/6.106/6.200/6.178GB; all ambiguitymaxshared2, source/native/prepared/
samplehash gates pass. Independent analysisretention/replay checks105960native
variance marginals,20896measuredpixelSPtransforms and3816muonhypotheses in0.5case;
all4fullsource/config/sample invariants andparticle/hitpairing pass. Pixels/SP/
orderedseeds/estimatedseeds identical, non-target realizednoise changes1/1event
at each nonbaselinepitch. Nativegeneratedselection independently recomputed by
coordinator:7586selected IDs/fullpayloads exact from24908generated,201producer
origin labels/convertedPVmapping andinitialpositionct checks pass.
[Generationcheck](SESSION-2026-10-31-strixel-ttbar-pu200/generation-smoke-check.json).

After allnativejobs stopped, strengthened only observation/provenance: full
reserialization byteequality preserves signedzero, explicitsameinstalledPythiaXML
binding/hash, dynamicnative/buildninja dependencies, resource/timing records and
failedFPE diagnostics. Tasksidecar rebuilt;13runtimeprotocoltests pass. Runtime
SHA8a9f2c6d74e04e9a8244c12db6bcaf892fcf384a6820df7f0f5d64ec720fcc14,
AuditCppSHA09b4927ec7b057bbe158baebec4149d9fa4ae6eafb840fbd82773e699ec49c6b,
moduleSHA7a1a98faac8a5bff042eb4776f5d2a79629c776ca1294cc547cbfccc7757bef6.
Freeze native/controller source next; child paused until committed revision for
onefinalbaseline smoke and independent exactsource review before100-event run.

Offline analyzer remains owned/inprogress, outside executingnative sourceguards.
It retains bounded per-event chunks, immutable sanitized source/config binding
and joint2000eventbootstrap; native0.5chunk1.32MB andexactreplay0.357s. Fixed
NpzFile repeated-decompression development bottleneck by readingeacharrayonce,
with regression. Added rawrejectedmeasurementcountmismatch diagnostics while
preserving accepted-only frozen gate. Coordinator authorized small pure/estimated
seedcoverage diagnostic+links forreplay beforeproduction, without native retuning.


Native source freeze aacf2ba0ab6c42e675959a8cb25c43c0ba7b477f.13runtime and6campaign tests independently pass; project/session/diff checks pass. PhysVal-02 exactsource assignment recorded beforedispatch; finalbaseline native smoke atcommittedsource delegated toexistingSoftEng child. Offline4ownedanalysis/plotfiles remainuntracked andexcludedfromexecutingnativeguards; HEADstaysfixed throughproduction.


Finalcommittedbaseline smoke at aacf2ba passes54.918swhole/21.343ssequencer,
peakRSS6210174976bytes, signedzero-sensitive fullnative roundtrip/allhashgates.
Its twoauditfiles are byte-identical to earlier0.5smoke. PhysVal-02 reports no
native blocker atC,19tests andindependentselected/origin/variance/SP/hypothesis/
convergence checks pass. Itflags frozenGBTSz0±15mm versusvertexsigma55.5mm as
an important efficiencyqualification. Optionalhumanpreference requested whether
to retainexactsingleparticle settings or widen to guide-selected±1m; no100event
reconstruction yet. Coordinator still progressing independentinputprovenance.

Nativepeer noted upstreamPythia ignores next()bool and existingproducerorigin
inventory doesnot explicitlyprove all201contributeconvertedtruth. SoftEng-03
boundedcorrection assignment recordedbeforedispatch: failonunsuccessfulgeneration,
requireallconverted origins, no retry/filter/resampling, same-seedvalidpayload
regression, no seeder/configchanges. Allnativejobsstoppedbeforeedits.


### Common ttbar vertex-window assumption before production

Optional preference question gave the human an opportunity to select the exact
single-particle±15mm control or a guide-compatible±1m window. With no reply
exposed after several minutes, coordinator stated the recommended±1m default
under the authorized isolated ttbar study. This is an implementation/scenario
assumption, not recorded human approval. Explicit later human steering overrides
it. Physical rationale: guidevertexsigma55.5mm versusorigincontrol±15mm;
±1m comes directly fromguideselectedvertexregion. No100-eventvalidation sample
has been generated or inspected. Common geometryROI/graph minmax/filter limits
will agree atallpitches; otherseeder/fitsettings unchanged. Existingnarrowwindow
smokes remainhistoricalcontrols. DES042/README updatedbeforeimplementation.


### Complete preproduction source freeze

SoftEng-03 success/origin guards pass17runtime andactualnative adversechecks;
seed153043generatedsample is byte-identical topriorfullgzip nativepayload,
provingvalid-eventphysics/draws unchanged. Proofs andcuratedhandoff retained.
Allnativejobsstopped beforecoordinator implemented thecommon±1m window. The
newttbarcampaign derivesallthree GBTSwindow controls directly fromgenerator
abs_z_max_mm1000; regression verifies everyotherprofile/CKF/matching/quality/
parameter/ambiguitysetting unchanged acrossall4pitches. This is preproduction
physics-scenario adaptation, not a validationperformance scan orhumanapproval.

All52focusedtests pass1.480s, including4newgenerationtests andcommonwindow
invariant. Session218/project82tasks42docs23reviews/diffchecks pass. Offline
source ready: boundedfullmatching/seed replay, sanitizedprovenance and2000paired
bootstrap. Coordinator only added explicitbenchmarkmetadata/qqbar/windowlabels;
currentanalyzer603bba8fe09a9e3fa9474dc0a4bf8f63bd5dd115bb9fe5e654df3809754dde86
replaysall4historicalnarrowwindow cases andall2000bootstrap/Markdown exactly
at/private/tmp/nodd-strixel-ttbar/analysis-development-smoke-v5. Metadata correctly
reportsnativeactual±15mm control, notnewintended±1m. Newsourcecommit will bind
allnative/offlinesources beforeupdatedwindow nativepilot+independentreview.


Complete sourcefreeze6edcbe5fc5a3edb612e0d5d584ab584444b7e815. Parentlaunched
committed±1mbaselinepilot inbuild/strixel-ttbar-smoke/reco05-wide-committed,
execsession44408 atobserved09:06:01UTC; existing153043sample3successguard.
Source/native/controller stayfixed. PhysVal-03 fullsource/updatedpilot assignment
recordedbeforedispatch; bothnative andofflineimplementation assessed, plusknown
READMEunchanged-upstream wording correction tofollowwithoutsciencechange.


### Wide pilot and graph-cap observability

Committed6edwidepilot passed61.635swhole/27.342ssequencer, peakRSS6816956416bytes;
4547seeds/4526estimated,20986rawCKF/937ambi, same59624hits/measurements. Allfour
effectivewindowcontrols±1000mm, fullnative roundtrip/convergence/immutability.
PhysVal-03 independentlyclassifies acceptedpartitions/HS/PUrates, reproduces2000
explicit-event-indexbootstrap intervals andwideportablematching replay;52tests
pass. Materialfinding: native2milliongraphedgecap reached. Keep cap unchanged,
recordeventincidence/edge/linkcounts; capped_seeds is unrelatedoutputcap.

Coordinator adds process-localnativefdstdout/stderr capture duringreconstruction,
sequencer+GBTSDEBUG logging andstrictsinglethread event-boundary/graphwarning
parser. No insertedalgorithm, seed/fitcut/RNGslot change. Fournewadversetests
cover completeIDs, missing/duplicate/unbounddiagnostics, warningcountmismatch,
zeroedgeevents and descriptorrestorationonexception; total56tests pass1.513s.
READMEminimalPythiasuccessguard wording corrected. Fresh committedsource pilot
and byteidentical scientificaudit proof required beforeproduction. Diskfree
47GiBobserved09:07UTC; currenttasksmokes633MiB, not the externalvolume growth.


Graphdiagnostic sourcefreeze1000edb212287c3638f96e3a0c2eec0a6292cb18.
Parentlaunchedoneeventobservationalpilotexec71475 inreco05-graph-logged at
observed09:11:26UTC. PhysVal-04 boundedread-only deltaassignmentrecordedbefore
dispatch. No furtherphysics/configchanges; allsources/HEADfixedthroughnativework.


Final observational pilot passed62.060s. Scientific event payload/audit byte-identical to prior wide pilot; strict graph audit event0 has2,000,000edges/48,283links/one cap warning. PhysVal-04 independently verified all17hashes, parser replay and22runtime tests at1000edb; no remaining preproduction blocker. Full100event campaign starts at this frozen commit, jobs4. Disk37GiB free observed09:14UTC; monitor external volume growth and fail safely without deleting evidence.


### Production attempt1: numerical failure retained

At09:33:32UTC the100event generation process ended failed after1144.776s. All100event files were written, but finalsequencer audit found oneunmasked FLTUND in pow within existingFpeSafeGammaDistribution, called bySafeBetheHeitler. No reconstruction launched. Separate6low-momentum particle step-limit failures were logged at events8,31,36,42,63,93. No event is removed or failure hidden. Full failedsample/log/stack retained; hashes inproduction-attempt-01.json. SoftEng-04 read-only diagnosis assigned beforeanynewsourcechange. Disk~12GiBfree and continuingexternalvolume growth; human capacity question pending.


PhysVal-05 correction09:37UTC: logged5PU belowpT1+1secondary does not establishactualfailedparticleidentity. MatchingACTS MultiParticleSimulation.hpp137–153 erasesqueuedinitialParticle before copying its nowinvalidatedreference intoFailedParticle. Parent withdrewpreliminaryuserclaim andupdateddraftreport/tracking. Actualselected-vs-simulatedinventory andobservationalcopy-before-erase diagnostic underassessment; no assertionthatallheadlineeligibleparticlestransported.


### Isolated numerical repair preproduction controls

SoftEng-05 implements distinct task-owned Fatras types/module inStrixelPileupSafeFatras, preserving frozen/sharedsources. NativeO2/strict controls pass originalpow-underflowpositivefixture,378threshold/highprecisioncontrols,1572432bitwiselosscomparisons,20000fullparent/photon/RNGcomparisons(activeFPE),127229guardedhardware/nativeFPEchecks pertarget; forcedprimary/end andsecondary/middlefailuretests preservequeue/RNG/correctfailureidentity. Parent60Python tests pass1.657s (24runtime/8campaign/24analysis/4plot). Oneevent153043sample4 passes47.258s/8.359ssequencer/6190235648bytesRSS, completezero-failureaudit; fullgzipbyte-identical tosample2. Currentartifactcb32b961 is historicalbeforeadditionalcompiled-local-sourcehashbinding; source-ready rebuild andcommittedsmoke/review stillrequired. Full100attempt remainsfailed/notused.


Finalnumericalrepair source-ready: moduledfd4e5d2 embeds all6local sourcehashes plus7upstream/generated inputs/compiler flags; staleownsource rejection tested. Parentall60tests pass1.579s; session218/project82tasks42docs23reviews validate. SoftEng04/05 andPhysVal05 handoffs curated. Sourcefreezecommit nowbindscompleteisolatedfix; thenparent committedsource1eventpilot+separatePhysVal06 beforefull100rerun. No source/module changesduringnativework.


Sourcefreeze250a211ff71be2ce7339cc043766f0d839470411. Committed1event153043sample5-gamma-committed launchedexec33428 atobserved09:48UTC; allsources/controller/nativeartifacts stable. PhysVal06 read-onlyexactrevisionassignmentrecordedbeforedispatch, CTest/Pythonadversererunspermitted butnogeneration/reconstruction/builds. Nativefull100payloadreplayremainsrequiredafterpilot/review.


### Staged corrected100event replay

PhysVal06 exact250a211 closespreproduction source/pilotgates: independent3CTest/60Python tests, allcompiledown/upstream/generated/compiler/ABIbindings, observedcommittedpilot11hashes/fullgzipbitidentity/zero-failureaudit pass. Parentinitializedfreshcampaignplan-v2 usingexistingcampaign.plan/write_json at250a, events100/seed153042/jobs4/defaultsupplier/runtime/native/fatrasdirs, thenlaunch_process ofruntimegenerate only. Exec2853 launchedobserved09:50:10UTC. Noautomaticreconstruction: firstverifyFPE-cleanfullgeneration, compareall100gzipSHAagainstfailed-sample-inventory andinspectcorrectedtransportfailureaudit. Onlythen campaign.py resume identplan launches4cases. No executingcode/head/artifactchanges untilallnativeworkfinishes. Failedv1 remainspreserved. Disk~16GiBfree atlaunch; capacityquestionremainsunanswered.


### Corrected100event gate passed; reconstruction active

Correctedv2generationcompleted1325.402swhole/1083.321ssequencer, peakRSS7786135552bytes. Parent ranrecordedverify-numerical-replay.py: all100original+correctednativegzipSHA andcounts exact, completedreport/output/provenance/origin/immutability checks pass. Correctedfull100failureaudit has6maxstep losses:5generatedPU belowpT1 and1Fatras e+secondary pT0.450487GeV; affected6eventfullgeneratedeligible-vs-simulated inventorieszeroomissions, failedIDszerohits/simoutputs. Proof +fullfailureaudit retainedunderDES042/ttbar-pu200. Originalfailedv1remainsinvalid. Existingcampaign.py resume identical250aplan/events100/seed153042/jobs4 launchedexec62711 observed10:12:33UTC. All4caseprocessesstarted; source/head/module/controllerfixed. Firsteventcomplete ineachat10:13:53; all4recordoriginal2milliongraphedgecap asprotocolrequires. No eff/fakeproductionanalysisyet.


### Reconstruction attempt1: final GBTS numerical audit failure

At observed11:10:04UTC controller62711 exited1. Allfour native loops wrote100eventauditfiles andfinished100events; finalsequencer audit rejectedoneunmasked FLTDIV inGbtsTrackingFilter::update at eachlength. No successful reconstructionreport/eventscombined or performanceevidenceisclaimed. NonfatalCKFSurface/Navigatorerrorsremainseparate. Eachlength logged99graphcapwarnings/100events. Source/head250a211andnativeartifactswerefixedduringallruns. Wholewalls3437.924/3448.774/3445.418/3441.881s; peakwholeprocessRSS6.82–6.91GB. Allrawreports/logs/auditfilespreserved, hashesinreconstruction-attempt-01.json. Validatedv2Fatras sample remainsusableandunchanged. SoftEng06 boundedread-onlynumericdiagnosisassignedbeforeanynewnativeedit. Parentwilladdexplicitboundexternal-samplereuse forfreshreconstructiononlycampaigns, preservingoriginalgenerationrevisionandreporthash; norelabelingorretransport.


SoftEng06 read-onlysourceanalysis identifies candidate endcaplenCorr, curvaturelimit andinnovation divisions; exactrealstate stillrequired. SoftEng07 assignedownednewStrixelPileupSafeGbts diagnosticclasscopies/replaybuild withsameCoreflags/compilerandcompiledprovenance. Shared/frozenhelperspreserved. PhysVal07 independentlysets exactsingularity/finitepath/differentialseedquality requirements andpasses10external-samplereusecontrollertests; dirtyhashesretainedinresult. Parentaddedgraphcapcounts/ranges toofflinebenchmark/Markdown/PDFcanvasfooteronly; classifiers/cuts/bootstrap unchanged. Full63Python tests pass1.653s; project/session/diffchecks pass. No productionnativejobsactive; allfailedreportsremainfailed.


### Proven unselected-division compiler fault

SoftEng07 all100savedpixel-input events matchallorderedseedIDs/qualitybits insharedCore/renamed/instrumented copies; only57FLTDIV. ActualO2Corefdiv0x23a714 precedesbarrelfcsel0x23a71c. Capturev2 directlyidentifiesevent57/update1369234, twoBarrelpoints samez169.1857452392578mm, initialslope-0.0bits0x80000000/tau²+0, curvature0; endcapdivision is source-unselected butspeculativelyexecuted. Capturedrelativefault0x69514 inmodule52efb2f8 aligns withactualinstruction. All4889event57seed IDs/qualitybits remainexact. No outputseedcontainsbothpoints; thisisnotchainancestryproof. Original4sources/exactdriver andsanitized100report/state nowretained. Diagnosticmodules/rawreplay preservedlocally.

PhysVal08 separatelyverifies4local/10upstream/20generated sourcebindings, nativeO2assembly/fault, independentlyreplaysevent57all3variants andoriginalrawseeds exactly. Itrequiresactualdenominator-firstassembly/boundaryFPEgates/full100seed and4lengthauditidentity, notbranchrejection. ParentrecordedSoftEng08 authorization foronly selected-denominator rewrite, sameNoddNativeGbts slot/settings/RNG, newproductionmodulewithcompleteper-eventobservationalaudit. Nocut/floor/rejection/mask changes. Parentruntime/controllerintegration fingerprints compiledGBTS local/upstream/generated/nativeconfiguration andguards per-eventauditcoverage; preliminary66Python tests pass1.572s (fixturetestgroupingthenfixed; focused11campaignpass). No newproductionlaunchorperformanceclaim.


### Denominator-first source-ready gates

SoftEng08 finalmodule1be2d1d2c3caf2174d32594b8fc9448b40de8db0bcd1ce08a52940549ccec3b2 passesnative+strict2CTest, each522254expression-bit/36actualfilter comparisons; genuine selectedendcap/innovation FPEs retained. Full100fourvariant replay227.178545s:485545orderedseedIDs/qualitybits exacttooriginal/Shared/Renamed/Observed/Guarded; controlsone57FLTDIVeach, Guardedzeroall100. Complete0..99numericalaudit andexactlyoneaffected57update pass parentruntimeparser. Actualassemblyselectdenominator0x7a1bc beforefdiv0x7a1c0. EarliernativeunitfixtureFMAissuepreserved; onlysyntheticexactzero widthchanged. Allfiveownedsource/nativeartifactcopiesfrozenandsnapshottedbeforehandoff.

Parentactual3.14moduleimport/compiledlocal5/upstream10/generated30/native50fingerprints/pybind3.0.4internals11 pass. Final66Python tests pass1.577s, campaign11focusedaftertestgroupingcorrectionpass. Source-readycode+curatedproof nowcommittedbeforefullchainpilot/pinnedPhysVal09/freshv3fourreco. Validatedgenerationoriginal250a reportSHAfdb1e2d4 remainsunchanged. No performanceanalysisfromfailedv2.


### Corrected GBTS committed-source pilot/review gate passed

Sourcefreeze46926ce90074d44b4a4ad42bbca0f318c6a68449. Committeddistinctseed153043fullchainpilot launchedexec84331 observed11:29:53UTC andexited0 at11:31:05UTC. Whole61.558926s/seq27.592115s/6863323136bytesRSS, all17outputhashes/immutability/fullnative roundtrip/ambiguity/numericalcoveragepass. Bothper-eventnativeauditgzipandcombinedevents scientificgzip byte-identicaltooriginalreco05-graph-logged. Parentproofgbts-committed-smoke.json.

PhysVal09 exact46926ce/11pinnedhashes independentlypasses2CTest/66Python, compiled5local10upstream30generated/nativeflags/ABI, all400diagnosticvariantfiles/485545seedbitidentity/GuardedzeroFPE/oneaffected57update andcommittedpilotfullhash/payload checks. No unresolvedsource/pilotblockerforfresh4x100; final400fullpayloadcomparison/classification/statistics/plots/reviewstillrequired. Originalfailedv2rawremainsfailed; validatedv2samplegeneration250a/SHAfdb1e2d4retained. Parentlaunchesfreshv3with--sample explicitly, jobs4. Sources/HEAD/module/artifactsfrozenuntilnativeprocessesfinish.


### Fresh v3 native campaign and full scientific identity passed

Controller21878 at46926ce launchedobserved11:32:07UTC with--samplev2/sample/jobs4, exited0 at12:33:27UTC. Allfour100eventcasescompleted afterFPE-cleannative loops+finalfullroundtrip/ambiguity/hash/immutabilitygates. Perlengthwall/sequence/RSS(bytes):.5=3672.274304/3415.641228/8487223296;1=3668.683120/3410.823922/8603910144;1.5=3660.397694/3402.875749/8492630016;2=3664.364450/3407.026238/8597356544. Each116outputhashes, maxshared2, graphcap99of100, completenumericaleventaudit/exactlyoneaffectedsource-unselectedupdatein57,0FPE. Canonicalsanitizednative-campaign.jsonretains actualreports/provenance.

ParentCLIcheck86348 exits0. Recordedverify-gbts-reconstruction-replay.py31509 completes12:34:48UTC:all400original+freshscientificpayloads byte-identical, originalfailedreport/log/auditinventory hashes unchanged, freshcampaign/hash/source gatespass. Native v2reportsremainfailed; freshv3acceptednumericalexecutionalone isnotfinalperformanceacceptance. Partialearlier32events+four57payloads alsoexact, butcomplete400gate supersedespartialcontrols.

Parentlaunched4portable retentionprocesses39114 at12:35:02UTC, boundedoneeventatatime; all21chunks/casecompletedby12:35:57withnoreportederrors. NativeHEAD/code/modulefrozen46926ce remainsunchanged. Fullvariance/SP/hypothesis/matching controls, exactportable replay/2000pairedbootstrap/figures/finalcommittedevidencereviewremainpending.


### Full portable inference and figure evidence passed

Four retention processes exited0 at12:39:24UTC, all400event chunks; largest4,687,538bytes. Response audit passes55,903,986 variance marginals,10,837,452 measured-pixel transforms,10,736,705 muon hypotheses. All7systems CKF andstrictshared<3 pass. Baseline7907248measurements; coarser lengths lose1/2/2EC strixel measurements. Pixels/SP/seeds/estimatedseeds invariant, realized non-target response differs inall100coarser events via bounded-retry coupling.

Full statistics2000jointlypaired event-bootstrap exited0 at12:43:54UTC, followed by full exact classification/statistics/Markdown --verify exited0 observed12:49:19UTC. Guide-selected HS efficiency80.36/80.40/80.40/80.36%, fake.195/.181/.204/.230%; frozen fake3.460/3.646/3.944/4.236%. 2mm guide fake delta+.034pp[+.005,+.064], HS0pp[-.211,+.202]; no equivalence claim. Denominators89342inclusive/4797HS/84545PU unchanged.

Unrooted six PNG/PDFpairs exported and all12files+manifest byte-identical in fresh directory. PDF authoring marker invoked once12:45:14UTC; all6pages rendered/requiredcaption text checked; contact sheet andtwofullpages visually inspected, noclipping/overlap. figure-verification.json bindsQA. Final report keeps99/100graphcap, qqbar-only, constant3T, Gaussian/no-merging/fixedmaterial and6low-particletransportloss qualifications. Final independent evidence review at committed input remains pending.


Final independent assignment TTBAR-PU200-PhysVal-10 recorded before dispatch, exact evidence commitd93063a9e4827e9f9a66fc0f175c16c3cc1dbc64; read-only, profile .codex/agents/PhysVal.toml supplied explicitly by prepared prompt. Full400case evidence/inference/plots reviewed independently; no human acceptance.


### Final independent assessment and local closeout

PhysVal-10 reviewed evidence commit d93063a9e4827e9f9a66fc0f175c16c3cc1dbc64 with no unresolved blocker for the qualified prototype comparison. It independently rehashed 1,500 files, verified all 400 reconstruction and 100 Fatras original/corrected gzip identities, and reproduced all 1,864 metrics and absolute/paired intervals by 2,000 explicit event-index resamples. Its independent classifier matches 10,920 representative counts and all candidate identities for events 0/57/99 at each length. Separate response checks cover 979,452 measurements and 335,456 pixel space points; all six transport-loss identities/eligibility inventories and figure integrity/render checks pass. Exact assessment in PhysVal-10-result.md. No human design acceptance.

The final report records the review and clarifies the already enforced native finite/symmetric/positive-definite covariance flag, in addition to positive finite diagonals; portable replay stores the flag, not the full matrix. No scientific source/data/statistic/figure changed after review. DES-042 adds a report cross-reference; task state completed denotes only this local study.

Preserved the independent integrity and classifier checkers with only their absolute root locator replaced by the retained file's repository-relative root; original/retained SHA and adaptation are explicit. Parent reruns both pass: 1,500 file hashes and 12 raw/portable pairs / 10,920 counts. Final session/project/token-dashboard/workflow/diff checks pass; historical accounting has 309 recorded disjoint turns, whereas this task has no exposed exact usage counters. Empty usage is missing coverage, not zero. No private client state recovered or token estimate entered.

Task bounded closeout time observed 2026-10-31T13:00:10Z. Session closed with partial coverage because its exact start and client usage/model/turn identifiers remain unavailable. Raw failed and valid runs stay preserved; no push, PR, publication, detector baseline change or shared dependency change. Scientific source freeze remains46926ce; generated sample original250a; final data commitd93063a.


Closeout metadata correction: the session validator initially rejected the independent review recorded as a command PASS without an observed exit code. The recommendation is now an activity, with its findings unchanged; no synthetic shell result entered. Dependent dashboard checks also refused that intermediate record. Final corrected validators/build are rerun below. The initial science-closeout time above precedes this record correction; ended_at records the later final closeout.

Final corrected closeout checks all pass; final ended_at 2026-10-31T13:00:49Z. Session218/project82tasks42documents23reviewrounds/workflow8roles3skills validate. Dashboard builds locally with309historical disjoint recorded turns; currenttask usage remainsunavailable.

Final checklist serialization also needed explicit No findings text for the successful silent diff check; schema rejection retained and corrected. Final record closeout timestamp2026-10-31T13:00:52Z; subsequent validators rerun on this complete record before commit.
