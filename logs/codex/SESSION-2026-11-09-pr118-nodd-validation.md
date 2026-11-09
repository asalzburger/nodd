# SESSION-2026-11-09-pr118-nodd-validation — nODD geometry digitization follow-up

## Scope and selected conversation

User: “More comments in” in the continuing PR118 context. New public request
from asalzburger-review, comment6744059438: “Ok, please add the nODD geometry
validation/comparison as well.”
https://github.com/asalzburger/nodd/pull/118#issuecomment-6744059438
Starting revision29a8632eed6c8aeda554e3327e7242c470594881; clean working tree.
Continue existing draft118 on its dedicated branch. No production geometry,
shared dependency change or human sign-off is inferred. Earlier ODD results and
two public summary comments remain dated evidence, not nODD validation.

## Environment and initial checks

Node preflight exit2 warns setup/lock fingerprints changed; warning communicated
before dependent work. Actual software/env/run.sh python3 software/env/doctor.py
passes DD4hep1.38, Geant411.4.3, DD4hep/DDG4 imports and12dataset paths.
Sandbox sysctl/ps warnings retained; no shared installation was modified.
A first read used nonexistent nodd-tiling-response.md; corrected to existing
tiling-response.md. A read-results formatting typo was corrected; no mutations
or scientific output were involved in either error.

## Bounded assignments

Explicit role instruction fallback, not verified native profile loading.

### I118-NODD-CaloTech

```json
{
  "id": "I118-NODD-CaloTech",
  "role": "CaloTech",
  "input_revision": "29a8632eed6c8aeda554e3327e7242c470594881",
  "inputs": [
    "docs/design/DES-030-ecal-edge-sensors.md",
    "docs/design/DES-031-siw-barrel-prototype.md",
    "docs/design/DES-044-calorimeter-digitization.md",
    "tools/calorimeter_baselines/README.md",
    "tools/calorimeter_baselines/export.py",
    "docs/validation/issue117/tiling-response.md",
    "docs/validation/issue117/digitization-protocol.md"
  ],
  "mode": "write",
  "writable_paths": [
    "docs/validation/issue117/nodd-digitization-protocol.md"
  ],
  "task": "New PR118 comment6744059438 asks to add nODD geometry validation/comparison. Identify actual maintained SiW nODD baseline geometry and executable setup, including barrel/endcaps/tracker/field represented or absent; distinguish integrated source baseline from old isolated +z tiled-endcap samples. Recommend and freeze a concrete scientifically valid extension of original/native same-hit software gates, held-out muon characterization and paired raw/D/PN e/gamma response. Preserve existing ODD results. Specify comparison matrix, seeds and common response/calibration rules before new scientific outputs; do not erase geometry response by independent retuning when comparing. Inspect actual generation/factory/export recipes and existing ignored local provenance where helpful. Scope must use actual nODD geometry, not relabel ODD; report missing integrated runtime instead of asserting full detector. Main handles generation/analysis; return a short implementation handoff early. No geometry/source changes, transport, installs, commits, external messages, further delegation or human approval.",
  "deliverable": "Write sole owned docs/validation/issue117/nodd-digitization-protocol.md, with exact source-pinned geometry boundary, fixed settings/samples/observable/gate definitions, executable recipe sketch and limitations; return early geometry/input handoff.",
  "completion": "Concrete nODD protocol ready for separate PhysVal assessment and coordinator execution; unresolved physical/runtime choices explicit."
}
```

## Token accounting

Exact current-task parent/subagent client counters, stable thread IDs and model
identifiers are unavailable. Canonical usage remains empty, unknown rather than
zero or estimated. No historical observations are duplicated.

## Outcomes and closeout

Pending execution and separate scientific assessment; no new gate pass or detector
acceptance is claimed at task initialization.

### I118-NODD-SoftEng

```json
{
  "id": "I118-NODD-SoftEng",
  "role": "SoftEng",
  "input_revision": "29a8632eed6c8aeda554e3327e7242c470594881",
  "inputs": [
    "software/analysis/calorimeter_digitization/reference_validation.py",
    "software/source/ActsExamples/Calorimeter/EDM4hep/SiliconReferenceComparison.cpp",
    "software/source/ActsExamples/Calorimeter/EDM4hep/SiliconValidation.cpp",
    "docs/validation/issue117/digitization-protocol.md",
    "docs/validation/issue117/digitization-results.md",
    "tools/calorimeter_baselines/README.md"
  ],
  "mode": "write",
  "writable_paths": [
    "software/analysis/calorimeter_digitization/nodd_reference_validation.py",
    "software/analysis/calorimeter_digitization/test_nodd_reference_validation.py",
    "docs/validation/issue117/previews/nodd-digitization-reference.json"
  ],
  "task": "Extend original Key4hep vs actual native same-hit validation to freshly generated maintained full SiW nODD LAYOUT-001 geometry (tracker+BARRELHits system8 + EDGEHits system9, both endcaps; no field/HCAL/FCAL). Main owns new generation and response analysis, CaloTech owns docs/validation/issue117/nodd-digitization-protocol.md frozen before outputs. Own only new reference runner/tests/compact reference result. Preserve old ODD reference source/results unchanged. Reuse tested helpers if appropriate but explicitly anchor every actual loaded helper and runner source, protocol, library, compact/readout and input identities, not just wrapper. Existing native comparator and validation support configurable collections. Adapt actual root-copy GeoSvc compact with BARRELHits/EDGEHits encoding constants, preserving source geometry semantics. Retain full original payload/MC endpoints/EventHeaders and exact deterministic accepted sets/tolerance proof. Run A on all20newnODDmu/showerfiles(4600events) and B4x1000conditional mueta0/gamma20eta2 P/PN replays with original ROOT vs native CLHEP independentstreams, actualseed uniqueness (priorhighbitaliasworkaround), frozen previous mean/CDF/width criteria. New disjointseedfamily125xxx, analysis126xxx; wait for protocol + actual samplemanifestcontract before execution. Can implement general manifest/geometry/library CLI now. Send source-ready handoff so main commits before producing science. No source/geometry/sharedinstall changes, unrelated files, commits, externalmessages, furtherdelegation or approval. Existing runtime /private/tmp/nodd-digitization117-build and siblingnodd-pr123-frameworks are available; mainpreflight exit2stale warned, actualdoctor passesDD4hep1.38/G411.4.3/all12datasets. Follow acts-spack skill for own runtime use.",
  "deliverable": "Source-pinned nODD original/native runner and meaningful controls, executed deterministic/stochastic receipts + compact binwise reference JSON, actual failures/seed/runtime audits and explicit scientific limits.",
  "completion": "All required nODD same-hit gates executed or blockers precisely returned; no claimed physical detector acceptance. All event payloads remain ignoredlocal; do not overwrite previous evidence."
}
```

### I118-NODD-PhysVal-Protocol

```json
{
  "id": "I118-NODD-PhysVal-Protocol",
  "role": "PhysVal",
  "input_revision": "554b087c3c0088773199466a779a580a25841017",
  "inputs": [
    "docs/validation/issue117/nodd-digitization-protocol.md",
    "tools/calorimeter_baselines/export.py",
    "tools/calorimeter_baselines/native.py",
    "docs/validation/issue117/digitization-protocol.md",
    "docs/validation/issue117/tiling-response.md",
    "software/analysis/calorimeter_digitization/muon_response.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Separately assess scientific validity and executable clarity of the newly frozen nODD vszero-fieldODD digitization protocol before new scientific outputs. Inspect source/protocol first, not author conclusions. ReviewerrequestedactualnODDgeometryvalidation/comparison. Geometry is actual maintainedLAYOUT-001 tracker+barrel+bothendcaps, notfullHCAL/FCAL/solenoid. Native fullunion10nmoverlap/rootIDmapping planned beforetransport. Matrix9500total includingnegativeendcapcontrols; fixedMIP/noise/threshold/range, original/nativeAall22nODDfiles4550events, Bfixedconditionalreplays independentROOT/CLHEP; commonindependentODDzeroC_eta andunscaledvisiblefraction preservegeometryeffect. Identify flaws in field/gun/energy matching, denominators/crossings, MIPqualification/fits, calibration/bootstrap/covariance, or claimboundaries. Mainwillimplementnewgenericgeneration/analysis; existingODDmuon_response hardcodedcollections/layerbits mustnot be blindly reused. No source edits, transport, installs, commits, externalmessages, furtherdelegation or sign-off.",
  "deliverable": "Exactrevision protocol assessment with blocking/nonblocking findings and concrete minimal corrections; return promptly before generation.",
  "completion": "Report whether protocol supports a meaningful scoped comparison and what must be fixed/clarified before outputs; no expected conclusion imposed."
}
```

### I118-NODD-PhysVal-Transport

```json
{
  "id": "I118-NODD-PhysVal-Transport",
  "role": "PhysVal",
  "input_revision": "9249ea8bc40bcf3525b9c68494e42c41ce34354a",
  "inputs": [
    "docs/validation/issue117/nodd-digitization-protocol.md",
    "software/analysis/calorimeter_digitization/nodd_generate.py",
    "software/analysis/calorimeter_digitization/nodd_transport.py",
    "software/analysis/calorimeter_digitization/test_nodd_generate.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Assess the pre-output clarifications and newly frozen transport implementation against the prior protocol findings. Main chose an explicit common5mm charged-particle ECAL-sensitive-Si step fixture applied to actualG4logicalvolumes beforeevents, preserving otherlimits and exactTGeo geometry/material/IDs. Audit actualfield/regioncuts/Birks/processes beforefirstevent; technicalpilot willverifycallbacklifecycle. Missing primarylayers remain unknowntransportedcrossings; initialraypredictions separate; targetregion/sidefrozenandimmediateconstructedneighbor rule. Inspect source/spec rather than authoredsuccessclaims; report scientific/implementation blockers. No edits, transport, installs, commits, externalmessages or furtherdelegation.",
  "deliverable": "Exact9249ea8b pre-output clarification/transport assessment, actionable defects and what technicalpilot must verify.",
  "completion": "Clarifications resolve or expose the prior three protocol points; no acceptance inferred."
}
```

### I118-NODD-SoftEng-Muons

```json
{
  "id": "I118-NODD-SoftEng-Muons",
  "role": "SoftEng",
  "input_revision": "e75caf4bbbe16ac0acfaca9940d8dea1f9b17467",
  "inputs": [
    "docs/validation/issue117/nodd-digitization-protocol.md",
    "software/analysis/calorimeter_digitization/muon_response.py",
    "software/analysis/calorimeter_digitization/digitized_response.py",
    "software/analysis/calorimeter_digitization/nodd_generate.py",
    "tools/calorimeter_baselines/export.py",
    "prototypes/calorimeter/BarrelCalorimeter.cpp",
    "prototypes/calorimeter/EdgeCalorimeter.cpp"
  ],
  "mode": "write",
  "writable_paths": [
    "software/analysis/calorimeter_digitization/nodd_muon_response.py",
    "software/analysis/calorimeter_digitization/test_nodd_muon_response.py"
  ],
  "task": "While awaiting fresh transport, implement geometry-aware held-out nODD/ODD muon characterization under frozen protocol. Own only new module/tests; preserve old ODD helpers. Main owns nodd_response.py runner/shower/pedestal/plots. Interface: geometry(args) with args.geometry=nodd|odd-zero, args.transport_manifest=Path(manifest.json),args.samples=Path(samples.json),args.work=responsework; writes muon-geometry-GEOMETRY.json. muon_summary(rows,args,pedestal) returns compact samples for bothgeometries eta0,2,-2; args.fit_workers=8 and fixedMIP=.00014875. Rows schema matches old digitized_response read_events: kind,geometry,sample (fullgeneratedmetadata withpath/sha256/requested_events/eta/particle/truth),diagnostics=JSONLpath,receipt{output_sha256,...}; args.work contains runs.json. Each geometry manifest has compact,libraries,collections,nodd baseline_directory. Generic nativeDD4hepVolumeManager sensitiveID queries: derive descriptor fields/layers0..47nODD vs1..48ODD, region/side, thinaxis fromnativeactualsolid, materialprefixes,transformednormals,and compareactualsegmentation cellrefs. Preserve64bitIDs/custommergedpads. TargetnominalBARRELside0eta0/EDGEside1eta2/EDGEside2eta-2; ODD correspondingdescriptors. Constructedinventorysetsphysicalneighbors; do notbridge missingprimarylayers. Initialraynativegeometry intersections are separateapproximation, missingprimarydeposits unknowntransportedcrossings ratherthan fabricatedzero/efficiency. Recordallnominal/identified/split/contaminated/missing/otherregioncounts; thresholdany identifiedprimarycell above strictthreshold, retainnominalandconditionaldenominators. Spectra thresholdindependent pureprimarysinglecell withimmediatephysicalneighborcentroidchord cosine>=.9, actual.5mmthinaxis; sparse/invalidfitsexplicitnotretuned. Reuse pinned old LandauGaussian fitter and orderedspawnbootstrap,1000wholeeventreplicates; protocolseeds126100/101nODD0/2,126102/103ODD0/2,126104/105negative. Sharedpedestalpassedby main: same schema as originalsummary pedestal, unchangedbackendidentityverifiedmain. Thresholdcurveerrors1000eventbootstrap+covariance,Wilsonconditional,undefinedsplitsnull. Return earlysource/interfacehandoff, source-readybefore scientificanalysis. No transport, installeddependencychange,commits,externalmessages,furtherdelegation orapproval. Newruntimegeometryqueries canrunonly after mainsuppliesactualrawsamples; ownscope expands onlyviaexplicitrecord.",
  "deliverable": "New geometry-aware muon module and meaningful controls for ID/region/side/adjacency/denominator rules; actual native audits/MIP/threshold compact output later aftersourcecommit/datahandoff.",
  "completion": "Module ready for main response integration before source-pinned execution; undefined/sparse/unknown cases retained and no physical acceptance claim."
}
```

## Frozen preparation and prospective corrections

CaloTech established actual maintained LAYOUT-001 scope: DES043 tracker+pipe0–7,
DES031BARREL8 andbothDES030EDGEends9; no field/solenoid/HCAL/FCAL/muon system.
Initial8500matrix expanded beforeoutputs to9500 with negativeendcapcontrols;
old4100/4600counts were clarified (newmuons250versushistorical500perfile).
Protocol554b087c, initialproducer9249ea8b andreference/guard e75caf4b are
separatepre-output commits. PhysVal separately assessed those exactrevisions;
no humanapproval inferred. It requested explicitunknowncrossings,targetside,
immediatephysicalneighbors andcommonstep-policy; these were frozenprospectively.
ActualDDSimsourceaddsG4StepLimiterPhysics. A common5mm ECAL-sensitivecharged
stepfixture is applied to G4only; TGeo/geometry/material/masks/IDs stayunchanged.
Additionalguards nowbindcurrentXML/material/nativehashes,rootmapping,10nmtolerance,
originalauditor, bothECALroles andpersistedfiniteorigin/totalenergy/momentum/
orderedrun/eventboundaries. They were addedbeforebulk, nottolerancerelaxations.

Fresh export and6factorybuilds normal0. Nativefullunion overlap scan is running:
13,506,030physicalnodes,650,387volumeUIDs,16,946,408candidatepairs. At20m37s a
read-onlyprocesscheckshowed100%CPUand7,245,008KiBRSS; stillcomputing, not aPASS.
Sandboxprocessinspectionfailed; explicitescalatedread-onlyretryprovidedonly
thisownedPID31157/resourcefields. No automaticapproval rejection occurred.

Excludedtechnicalprobe01failedbeforeevents: cppyydeleted aweaklyreferenced
initializecallable; process-lifetimePythonreference corrected. Probe02then
failedbeforeevents becauseDDG4's existingUserLimitsproxy forbidsSetMaxAllowedStep;
retain/checkexistingODD5mmlimits andattachonlywhenmissing on nODD.
Preparedprobe03was superseded beforeexecution by the requiredtwo-blocktest.
Probe04transport normal0, both2-eventmacroblocks completed and actualzeroG4field,
0.7mmregioncuts,StepLimiterprocesses, bothECALroles andzeroSiBirks verified.
Post-run1e-7truthguard correctlyrejected a2.0e-7GeVkinematicdifference fromthe
energycommand's9.894899769296881→9.8949roundtrip. Origin andheaderscorrect.
Prospectivelyswitched to native /gun/momentumAmp integerGeV/c without changing
truth tolerances or responseparameters. Probe05thenaborted macro at unsupported
/random/showEngineStatus despiteprocess0; missingoutputs failedclosed. Added
explicitmacro-abortdetection andnative /i118/saveRandomState audit recording
actualengine/effectiveseed andserializedstate immediatelyaftereachreset.
Probe06 nowtests thatcorrectedtwo-blockpath. Everypilot is excludedfromscience;
raw outputs,source snapshots,closedlogs andreceipts remain ignoredlocal.

Initialworkflowprepare invocation used unsupported --output; corrected to stdout
redirection andrecordedassignments beforedispatch. One read-resultsformatting
ReferenceError andone failedpatchcontext changed no scientific file; retried
correctly. No sourceinstall or productiongeometrymutation.

### I118-NODD-PhysVal-Implementation

```json
{
  "id": "I118-NODD-PhysVal-Implementation",
  "role": "PhysVal",
  "input_revision": "5afb019eac6e152608639d02223dda73098a197f",
  "inputs": [
    "docs/validation/issue117/nodd-digitization-protocol.md",
    "software/analysis/calorimeter_digitization/nodd_generate.py",
    "software/analysis/calorimeter_digitization/nodd_transport.py",
    "software/analysis/calorimeter_digitization/nodd_response.py",
    "software/analysis/calorimeter_digitization/nodd_muon_response.py",
    "software/analysis/calorimeter_digitization/nodd_reference_validation.py",
    "software/analysis/calorimeter_digitization/test_nodd_generate.py",
    "software/analysis/calorimeter_digitization/test_nodd_response.py",
    "software/analysis/calorimeter_digitization/test_nodd_muon_response.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Separate pre-analysis source assessment at exact5afb019e. Inspect primarysource/protocol before author conclusions. Main hasnowactualnativefullunionPASS, zerooverlaps10nm on13.5Mnodes10systems; four-eventtwo-blockODDtechnicalprobe07PASS with p residual3.6e-15,origin0,monoE,headersrun0/1event0/1, actualfield0/cuts.7/SiBirks0/step5mm, actualMixMaxRngseeds987000/1distinctserializedstates. Originalkineticmacro rounded9.894899769\u21929.8949, failedunchanged1e-7guard; prospectiveprotocolusesdirectmomentumAmp, noresponsecriterionchange. Rawbulkshowerprocessesstartingnow; no new response/fitoutputs examined. Reviewsource scientificguards/statistics/calibration/covariance/hists/longitudinal/primaryselection/path/nominalvsidentifieddenominators andoriginal/native boundary. Verify earlierguardfindingsclosed, actualsourcepins/receipts/importhelperscoherent, and meaningfulsyntheticcontrolsifhelpful. Do not changefiles,transport,installs,commits,externalmessages, furtherdelegation orapprove. Sourcecorrections before analysis must be returnedpromptly. Source/runtimeprimarychecksread-only arepermitted underactualskillpreflight; no fullGeant4/geometry query needed.",
  "deliverable": "Exact5afb019e source implementation assessment with actionable blockers before response analysis, actualchecks and explicit unexecuted/runtime limits.",
  "completion": "Return evidence-based findings; no expected pass, detector acceptance or humanapproval inferred."
}
```

## Integrated native PASS and production launch

Fullnativeunionnormal0:13,506,030physicalnodes,650,387volumeUIDs;
16,946,408candidatepairs,1372.71s pointfill and35.734s candidatecheckwith24threads.
All10systemroots0–9match, zeroillegaloverlaps/extrusionsat1e-5mm. This is a
constructed tracker+ECAL stage pass, not physicaldesignacceptance.
Probe06failedbeforeevents fromaG4String→filesystempath C++type mismatch; explicit
std::string conversion andcheckedJITdeclaration corrected it. No scientificdata
wereused. AstandaloneactualGeant4JITcompile/registrationcontrol thenpassed.
Probe07normal0in23.61656s, twoblocks×2muons, bothtruthaudits pass: maximum
momentumresidual3.55e-15GeV, origin0,monoenergetictotalE10.000558169GeV;
run0/1,event0/1identitiescorrect. MixMaxRng effectivefirstseeds987000/987001
andserializedpre-eventstatesdistinct, actualG4field0,regioncuts.7mm,SiBirks0,
bothECALidentities andchargedStepLimiter/maxstep5mmverified. These4eventsremain
excludedfromscience. Bulkproducer/protocol/sourcefreeze5afb019e. Complete48-row
manifest9500events preparedagainstnativePASS; newnODD andODDzero showergroups
startedseparately. Pending-nativepreparationpolicyallowsonlyindependentODDwork;
thisbulkpreparationactuallyfoundPASS, andeverynODDrun/finalindexmustbindthat
sameactualsource/library/material/root/tolerancereport. No geometrygateweakened.
Thirtyfocusedcontrols passedbeforefinalVolumeManagerpopulationcontrol; the latter
addsonecontrolandusesDD4hep'sdocumentedpopulationaccessor, notan invalidhandle.

### I118-NODD-CaloTech-Plots

```json
{
  "id": "I118-NODD-CaloTech-Plots",
  "role": "CaloTech",
  "input_revision": "855ccf7886bfb78718d16887b2b39145af5c6293",
  "inputs": [
    "README.md",
    "docs/validation/issue117/nodd-digitization-protocol.md",
    "docs/validation/issue117/nodd-digitization-analysis-notes.md",
    "software/analysis/calorimeter_digitization/nodd_response.py",
    "software/analysis/calorimeter_digitization/nodd_muon_response.py",
    "software/analysis/calorimeter_digitization/nodd_reference_validation.py",
    "software/analysis/calorimeter_digitization/plot_digitized_validation.py"
  ],
  "mode": "write",
  "writable_paths": [
    "software/analysis/calorimeter_digitization/plot_nodd_digitization.py"
  ],
  "task": "Prepare standalone Matplotlib renderer for newactualnODD/zero-fieldODD compact data; do not generate invented scientific outputs. Mainrunningrawsamples, datawillfollow. Soleownedsourceplot_nodd_digitization.py; CLI --response JSON --reference JSON optional --output DIR. Preserveolddata/renderers. UsefixedECAL#cccc00 forcurves/markers;lighterECALshadeODDcomparisonandlinestylelabels forraw/D/PN; no arbitrarysubsystempalette. Produce5figures eventually: nodd-digitized-electron.png andphoton.png (eta0/1/2 columns, primaryunscaledvisibleS/E, commoncalibratedresponse residual, all-eventSD/mean; raw/off/on, 2geoms), nodd-digitized-mip.png (eta0/2/-2, pathnormalizedheldoutprethresholdraw/PN andactualPNoutput, PNnominalvsidentifiedthresholdyield w eventCI, fit/SNR/missing/initialraycounts; fitsparse/Noneexplicit), nodd-digitized-comparison.png (matchednODD/ODDmeanvisible ratios perstage, pairedPN-minus-raw relativechanges wpairedbootstrap; negativee20eta-2 clearlybounded), nodd-digitization-reference.png (detnormalizedresidualfullrange andall22casecountsgates,4stochasticreplayenergydistributions original/nativewithenergy/countCDF,widthinterval/mean gate annotations). NewreferenceJSONsameoldsummarysamples/comparisons layout; existinggenericreference_plot canreuseonlyiflabels/fullbinrangeaccurate anddoesnotchangepreviousfigures. Rendereronlyreadscompactdata andvalidateshistcounts/edges/underflow/overflowclosure, noROOT/rawfiles. Primaryshowerdata showers.populations andgeometry_comparisons schema innewsource. SNR/fitnone cases handledwithoutfabricatedvalues, no48N hardcodedcrossingcounts. Negativecontrolse-20only notfullnegativephoton/grid. Normalize actualthresholdedmuonhistbyallqualifiedcrossings, notacceptedonly. Sourcecaptionsclearlyzero-fieldtracker+ECALstage,common148.75keVMIP/.13noise/.6threshold; nofieldedcomplete-nODD or detectoracceptanceclaim. Keepfigureslegible,modestpanels/legendspacing; mainwillvisualQA. No report/tracking/sourceoutsideownedfile, no commits/installs/delegation/publication. Send source-readyhandoffbeforeactualresults, renderonlywhenmainprovidescompactpaths.",
  "deliverable": "Standalone source-pinned plotter producing five clear scientifically labelled figures fromnewcompactsummary; nofiguregenerationclaimuntilactualdataexist.",
  "completion": "RendererreadyforactualdataandvisualQA, preservesexplicitundefined/rejected/unknowncategories andhistoricalassets."
}
```

## Pre-analysis fixes and unchanged-source transport retry

PhysValreviewat5afb019eindependentlyreproducedthreepre-analysisdefects: ODD
physicalmodule16rejectedby4bitkeyguard, emptylongitudinalarrayIndexError, and
missingconfig/rawidentitybindingsatreadtime. Main/SoftEngfixedthem beforeany
nativeresponseoutput. ODDnormalizationusesactualDD4hepIDDescriptor.encode and
actualdecoder, preservingfullphysical→encodedcrosswalk locally andrejecting
collisions; nativecontrolconfirmsphysical16→encoded0 withoutalteringgeometry.
Mode-seedwordingisclarifiedinnewanalysis-notes, leavingtheactivefrozenraw
protocolunchanged: Dhasnostochasticoutputdependence;PNisthesolestochasticmode
inthepairedraw/D/PNcampaign,collectionoffsets0/1. P/PNreferenceexperimenthas
itsdistinctindependentstreams. Histogram/empty/configcontrolsandnativeIDtest
allpass:35controls,1.488s. Correctionscommit855ccf78. Nativeactualsourcecode
andphysicsgatecriteriaareunchanged. PhysValwithdrewaninitialschemafindingafter
checkingexact5afbbytes: produceralreadyusedartifacts,notolder evidencekey.

FirstnODDproductionlaunchfailedbeforeevents becausebuildtargetswereonlythe
factorylibraries;theirComponents_*registrationtargetsweremissing. Generated
five trackerregistrations, verifiedall6factorybinarySHAunchangedfromnativePASS,
andrecordedthe6registrationhashesinlocalplugin-registration-audit.json.
Retainedfailedgroupbyreversiblemove toraw/../failed-attempts/nodd-showers-01,
with5artifacthashes andoriginal/retainedpaths; noneoverwrittenordiscarded.
Retriedthesamefrozen5afproducer/manifest/nativePASS. No activegen/protocolsource
ormaterial/geometryparameterchanged. G4conversionnowsucceeds24.740s; initial
voxelizationcontinues. At9m18s ownedPID38979showed99.3%CPUand12,441,344KiBRSS.
ODDcontrolisadvancing; its750detailedmuonsnowalsoexecuteasasmallerparalleljob.
AllrawROOT/source/log/RNGpayloadsremainignored. Referenceinputwilladdtheclosed
plugin-registrationproofasanexplicitartifactaftergenerationindexing.

## Runtime mapping diagnosis and completed ODD control

All 4950 zero-field ODD events completed in two normal-exit groups: 4200
showers/reference events plus 750 muons. Both execution receipts report
all_inputs_verified; origin, PDG, momentum/total energy, run/event headers,
raw hashes and actual pre-event random-state resets passed. These populations
are frozen before scientific response analysis. No nODD events had begun at
16:50 UTC: both jobs remained in DDG4 Geant4VolumeManager path population,
following successful geometry conversion (24.740/25.650s). A one-second
read-only process sample showed scanPhysicalVolume with path comparisons,
not a blocked wait. The shower process used 33m58s CPU at 33m59s elapsed,
99.1%CPU and 10,280,608KiB RSS. Host RAM was verified as64GiB. No shared
DD4hep changes or geometry simplifications were made.

Technical ODD native-geometry query, using only the three completed muon
files, passed:2304plane groups,39414queries,3381unique cells; maximum
position residual9.765625e-5mm within.002mm. Actual native encoder maps
physical module16 to encoded0 in144plane groups; zero collisions. Initial
straight rays cross48active planes in each direction; this does not determine
transported-crossing denominators. This technical cache is excluded from the
final combined analysis because it binds a partial input-manifest hash.

Retained the compact nODD native PASS, original report/log hashes, aggregate
node/candidate statistics and registration-proof hashes in
previews/nodd-geometry-validation.json. No raw placements/event histories are
included. The refreshed software inventory records the new study usage and
separate report/protocol; 67components/101families/52reviewed inputs/12pins
check. The sanitized current GitHub capture now includes seven PR comments;
interaction110records and paired-session272records validation pass.

### I118-NODD-PhysVal-Corrections

```json
{
  "id": "I118-NODD-PhysVal-Corrections",
  "role": "PhysVal",
  "input_revision": "5d4262a905932ce73c40915f0516fcf1d17c1254",
  "inputs": [
    "docs/validation/issue117/nodd-digitization-protocol.md",
    "software/analysis/calorimeter_digitization/nodd_generate.py",
    "software/analysis/calorimeter_digitization/nodd_transport.py",
    "software/analysis/calorimeter_digitization/nodd_response.py",
    "software/analysis/calorimeter_digitization/nodd_muon_response.py",
    "software/analysis/calorimeter_digitization/nodd_reference_validation.py",
    "software/analysis/calorimeter_digitization/test_nodd_generate.py",
    "software/analysis/calorimeter_digitization/test_nodd_response.py",
    "software/analysis/calorimeter_digitization/test_nodd_muon_response.py",
    "docs/validation/issue117/nodd-digitization-analysis-notes.md",
    "software/analysis/calorimeter_digitization/test_nodd_reference_validation.py",
    "software/analysis/calorimeter_digitization/plot_nodd_digitization.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Separate source-only follow-up at exact input revision. Read source bytes first; do not read the authored in-progress results report as evidence. Verify the three previously reproduced blockers at 5afb019e are closed: physical ODD module16 normalization using actual IDDescriptor encoder, empty longitudinal population, and config/raw read-time binding. Check the current compact result/plot schema, paired statistics, covariance and fixed MIP/crossing accounting for any remaining consequential error before actual response execution. The raw generator/transport/protocol are frozen5af and two nODD jobs are active in DDG4 path population; do not alter or terminate them. No new native nODD response results exist. You may run focused synthetic/source controls; no full simulation, geometry generation, dependency changes, external messages, commits or delegation. Read-only assignment and existing runtime preflight instructions apply. Report fixes verified, remaining actionable findings and exact checks. Main will request final independent actual-data/figure review separately.",
  "deliverable": "Exact-revision source follow-up confirming or rejecting the three fixes and identifying any remaining consequential analysis/plot issue before real data are processed.",
  "completion": "Return evidence-based source assessment and actual checks; no actual nODD response or detector acceptance claimed."
}
```

## Prospective population-label closure

Follow-up separate PhysVal source assessment at5d4262a9 confirmed the prior
three fixes and identified a fourth guard gap: runs.json outer geometry/kind
labels were trusted after only the nested sample identity was bound. Main
added an explicit equality rejection in verify_runs, before receipt/path access.
A focused control independently changes each outer label while retaining the
bound sample; both are rejected. All36focused controls pass in1.380s in the
verified native runtime. This changes no frozen transport input or statistical
gate and precedes all new native response execution. Pre-analysis notes explain
the additional binding.

Published progress at1299e3b7e88c96ebfdf4633946d397727c4be8be to the existing
draft118, with a clearly marked running nODD section and immutable native proof,
protocol and report links. Exact body/title/head/draft readback succeeded;
all three hosted checks started. The existing completed ODD-only figures remain
visible with their original scope. No new public conversation comment posted.

## Separate correction assessment completed

I118-NODD-PhysVal-Corrections assessed exact5d4262a905932ce73c40915f0516fcf1d17c1254,
verified all12assigned SHA256s and independently passed35controls in1.355s,
including actual DD4hep1.38 IDDescriptor module1..16→1..15/0 without geometry
construction. All three original blockers are closed at that revision.
The reviewer also verified main's prospective outer-label guard and actual
verify_runs tamper control (0.002s), plus the deduplicated cross-column MIP
legend fix. A synthetic no-central/present-endcap control retains both geometry
labels exactly once. Assessed correction hashes:

- nodd_response.py:567dc26005baf1479be9308c572985c0473923bf5037b5a1b7a21b4aec893ae8
- plot_nodd_digitization.py:06e333101c08304d37af6c37737878e0f295582e746819941cc3adae5c563f01
- analysis notes:5e8b845428e3e038a8fcd9cd851a5385c83935a0e98fe2b83c43706bd4dcfb35

No remaining consequential source/schema finding was identified in that
combination. The reviewer inspected no new scientific outputs, ran no transport
or geometry construction and edited nothing. This source assessment does not
replace the still-pending independent actual-data and figure review. Main's
all36controls additionally pass. Matplotlib CLI smoke passes after legend fix.

### I118-NODD-SoftEng-MappingAssessment

```json
{
  "id": "I118-NODD-SoftEng-MappingAssessment",
  "role": "SoftEng",
  "input_revision": "2dd8f38a4a8e714150f5a8cd180760e4ef6b6084",
  "inputs": [
    "software/analysis/calorimeter_digitization/nodd_generate.py",
    "software/analysis/calorimeter_digitization/nodd_transport.py",
    "docs/validation/issue117/nodd-digitization-protocol.md",
    "docs/validation/issue117/nodd-digitization-analysis-notes.md",
    "tools/calorimeter_baselines/native.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Read-only runtime scaling assessment while current frozen jobs continue. Both full LAYOUT-001 Geant4 transports are active, first PID38979 started16:16:25UTC, nowabout17:16UTC; no events. Conversion24.740s, then1CPU in Geant4VolumeManager Populator scanPhysicalVolume and memcmp assembly-imprint path matching. One-second profiles at9min and51min show same path; raw profiles local /private/tmp/nodd-pr118-nodd/nodd-initialization.sample.txt and nodd-initialization-51min.sample.txt. 64GiBhost, firstprocessabout10GiBRSS. Existing official v01-38 source downloaded read-only at /private/tmp/nodd-pr118-nodd/DD4hep-v01-38-Geant4VolumeManager.cpp, but do not assume byte-identical installed source. Installed headers in /Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view/include/DDG4. Determine whether documented existing DD4hep/DDSim configuration/API options could reduce this mapping overhead without changing constructed geometry, sensitive masks, physics or stable hit IDs. Assess options only; do not edit any file, change source/binaries/configuration, stop/attach debugger to jobs, install/acquire dependencies, change frozen inputs, execute new simulations or publish. Primary-source inspections and ordinary native header/source reads allowed after relevant skill. If no safe existing option, report that plainly with exact evidence, uncertainty and whether only a separate task-local performance patch would help. No timing extrapolation presented as fact. Current jobs must keep running unchanged.",
  "deliverable": "Bounded source/runtime assessment of available semantics-preserving mapping options and limits; no implementation or acceptance.",
  "completion": "Return actionable evidence-backed findings or explicit absence of a safe existing option; preserve all active jobs and dependencies."
}
```

## First nODD transport progress and truth-only check

The shower job cleared DDG4 path mapping by17:25UTC, unchanged, about69minutes
after process start. Actual initialized audit passes zero sampled field, both
ECAL roles,0.7mm region cuts, zeroSiBirks and chargedStepLimiter/maxstep5mm.
The first200-event block finished by17:38UTC. A separate early read of that
closed first file through the frozen producer audit_input passed: ordered
run0/events0..199, one correct primary, origin0, maximum p residual
1.7763568394002505e-15GeV, totalE5.000000026111991GeV constant, unique source
cells (31752BARRELHits,10EDGEHits). InputSHA
56de8fde676ded30c2d0cfd1a67f0a248f6cc8e5c7fc2ded460ca30b83457f67.
This checks truth/identity only; no signal sum or scientific response was
examined, and full group/postflight/index verification remains required.
The primary sample is retained in its frozen population, not replaced by a
technical fixture. Interim source/audit/truth hashes and aggregate counts are
added to the compact native proof without event payload.

A one-second process sample during second beamOn,17:39UTC, shows
G4RunManager::RunInitialization → G4ProductionCutsTable::CreateCoupleTables →
ScanAndSetCouple. This is distinct from the earlier DDG4 path-map bottleneck.
Current jobs continue unchanged; no installed dependency, cut or geometry was
modified. At this point only one of19shower blocks had finished; the separate
muon group had not reached its initialized audit. Raw profiles remain local.
Hosted checks all pass on1299e3b7:build9m6s,unrooted4m24s,token-site38s.
Later prospective analysis fixes39e16df0 and2dd8f38a were not part of that
hosted head; their local36controls/source assessment are separately recorded.

## Read-only runtime assessment closeout

I118-NODD-SoftEng-MappingAssessment examined
2dd8f38a4a8e714150f5a8cd180760e4ef6b6084, installed
DDG4/Geant4Mapping.h and DDSim/Helper/Geometry.py, official DD4hep v01-38
Geant4DetectorGeometryConstruction.cpp, Geant4Mapping.cpp and
Geant4VolumeManager.cpp, and the supplied task profiles. No safe existing
mapping bypass was found. HaveVolManager=false prevents subsequent mapping
access; sensitive UseVolumeManager=false returns root IDs and skips segmentation.
Neither is acceptable for the frozen stable-ID/readout contract. Debug/print/dump
options do not supply an alternative indexed or parallel mapper. An indexed
assembly-path lookup would require separate implementation/equivalence work.
Official tag bytes were not proven identical to installed binaries. No runtime
completion-time extrapolation is claimed. No files/jobs/configuration/dependency
were changed by the assessment; main ended further research once its bounded
answer was sufficient. Actual original/native execution receives a separate
handoff only after global closed inputs exist.

At17:50UTC the first three nODD shower blocks had finished (600events reported
by run logs; only the first200 had an additional early truth read). Owned
process38979:elapsed1:33:46,CPU93:43.83,100%,RSS16556736KiB. Owned muon40979:
elapsed1:21:58,CPU81:57.77,100%,RSS5574640KiB; still prior to its initialized
audit. Both active, no failed receipt. Repeated Geant4 material/cut-couple scans
are observed between shower blocks. All original runtime and frozen inputs
remain unchanged. Source/first-truth progress published at
b77d31e365fa028ceb7de9e82886ebe6fcef3c90; exact current PR description and draft
state readback verified. This is not a completed nODD digitizer comparison.

## Independent muon execution order, before new native response

Both muon groups are now closed: nODD normal0 in7215.299s, all750events verified;
ODD750 likewise closed/verified. A separate immutable muon-samples.json gathers
exactly their six original sample records and two closed receipts, bound to the
unchanged frozen global transport manifest. To overlap independent work with
slow remaining shower transport, main added an explicit closed-muon scope to
nodd_response.py. Source/settings/gates and event selections stay fixed. Global
indices38..43 and seeds129300..129800 remain exactly those of the complete
48population inventory; subsets are never renumbered. The default/final scope
still rejects a six-population inventory. Native-PASS, SDK, registration, raw,
closed receipt, RNG and source checks apply before both scopes.

A preserved runs-muons.json and source/settings/row bindings close the independent
muon result. Optional reuse in the final full analysis checks completion/output
hash, source/protocol/notes, pedestal, selected-input digest, preserved native run
snapshot and all six exact native rows after complete verification. Fit model,
1000bootstrap seeds and errors do not change. No new native response/fit outputs
have been examined yet. Analysis notes record this prospective execution-order
clarification; active raw producer/transport/protocol at5af remain unchanged.
All38focused controls pass1.591s, including global subset seeds and changed
cached-output/final-input rejection. Actual six-muon metadata verification passes;
default full scope rejects it. This change receives separate source assessment
before native response execution.

By18:15UTC both initialized G4 audits match (field0,cuts.7,Birks0,maxstep5mm).
All hosted checks pass atb77d31e3:build12m41s,unrooted3m36s,token-site33s.
At18:28UTC disk free159.8GiB; current new raw-data tree4.109GiB. No raw event,
trial, bootstrap draw or profile data is staged for Git.

### I118-NODD-PhysVal-MuonScope

```json
{
  "id": "I118-NODD-PhysVal-MuonScope",
  "role": "PhysVal",
  "input_revision": "7bd0b2ec76f3052a0d6fa73d79b6dee4c55da614",
  "inputs": [
    "docs/validation/issue117/nodd-digitization-protocol.md",
    "docs/validation/issue117/nodd-digitization-analysis-notes.md",
    "software/analysis/calorimeter_digitization/nodd_response.py",
    "software/analysis/calorimeter_digitization/test_nodd_response.py",
    "software/analysis/calorimeter_digitization/nodd_muon_response.py",
    "software/analysis/calorimeter_digitization/nodd_generate.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Bounded separate source review before new native response outputs. Raw transport/protocol frozen5af unchanged; both muon groups now normal0 and all1500events verified, shower groupstillrunning. Main adds explicit six-closed-muon scope to overlap native muon analysis with remaining shower transport. Review exact newcommit, especially globalindices38..43/configseeds unchanged, full-default all48 remains strict, all source/native-PASS/RNG/closedreceipt/raw checks retained, exact scope/sample/order bindings, muon geometry sourcechecks, cached compact-result completion/source/settings/pedestal/input/native-row bindings when later attached to fully verified global run inventory. No new event selection, fit model/gate, response coefficient or bootstrap draw is allowed; all38controls pass and actual ordered_samples on closed6passes whilefullscope rejects it. No new native response/fit outputs exist. Primarysources first, do not read authored result report as validation. Read-only; focused synthetic or closed-metadata checks allowed. No geometry/transport execution, source edits, dependency changes, job interruption, publication or delegation. Return consequential findings promptly; assessment of actual outcomes will follow separately.",
  "deliverable": "Exact-revision source assessment of independent closed-muon execution and later full-result reuse, actual checks and any correction needed before native outputs.",
  "completion": "Return evidence-based source assessment; no actual data/figure or detector validation is inferred."
}
```

## Muon-scope source closure before response execution

Separate PhysVal assessment at7bd0b2ec returned four actionable provenance/
preservation gaps before any new native response: cached reuse skipped pinned
legacy-helper verification; closed raw receipt manifest/protocol/producer were
not explicitly bound to selected transport; final output could overwrite a
closed cache; and a truncated technical transport envelope could redefine the
full inventory/global index. Main closed all four prospectively. Helper hashes
are verified/recorded before any stage and again on reuse; raw receipts match
manifest/protocol/producer/steering; fresh summary/checkpoint output paths protect
inputs/cache/snapshots; canonical48point/order/seed fields precede scope selection
and global-index lookup. Existing mass metadata is retained. No selection,
coefficient, fit, uncertainty or gate changes. Frozen raw code5af is unchanged.

All42focused controls pass1.365s, including cached-helper drift, stale receipt
identity, protected outputs and technical-envelope/global-index controls.
Actual six-muon metadata still verifies with indices38..43; default full scope
rejects the subset. PhysVal independently checked the prior7bd real inputs:
1500events acrosssixpopulations, unchanged native seeds129300..129800, actual
receipt digests already matching selected inputs;8changed-module controls pass
0.121s. No new native/scientific outputs or geometry query were inspected by that
assessment. The final corrected source receives exact-revision confirmation
before execution.

### I118-NODD-PhysVal-MuonScope-Closure

```json
{
  "id": "I118-NODD-PhysVal-MuonScope-Closure",
  "role": "PhysVal",
  "input_revision": "c9f2fa7992391987a46c81f038623a2d14e79990",
  "inputs": [
    "docs/validation/issue117/nodd-digitization-protocol.md",
    "docs/validation/issue117/nodd-digitization-analysis-notes.md",
    "software/analysis/calorimeter_digitization/nodd_response.py",
    "software/analysis/calorimeter_digitization/test_nodd_response.py",
    "software/analysis/calorimeter_digitization/nodd_muon_response.py",
    "software/analysis/calorimeter_digitization/nodd_generate.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Verify exact corrected revision closes the four findings from I118-NODD-PhysVal-MuonScope: helper checks before cached/fresh statistics, raw receipt binding to selected manifest/protocol/frozen producer/steering, fresh/protected output and checkpoint paths, and canonical48-row inventory before scope/global-index lookup. All42controls and actual six-muon metadata pass; full scope rejects subset. No new native response/fit outputs yet. Inspect primarysource and meaningful focused guards; do not inspect authored outcome report as validation. Same read-only boundaries: no source changes, geometry/transport, dependencies, job interruption, publication or delegation. Confirm correction closure or return remaining consequential finding promptly before execution. Actual result/figure assessment is separately pending.",
  "deliverable": "Exact-c9f2fa79 source closure assessment with actual checks and remaining limits before independent muon response execution.",
  "completion": "Return evidence-based source assessment; no actual data/figure or detector validation is inferred."
}
```

### I118-NODD-SoftEng-MuonExecution

Initial prepare rejected ignored runtime paths as revision inputs; corrected
the input list to tracked sources. Runtime artifact paths remain explicit in
the task contract below. No execution occurred before valid preparation.

```json
{
  "id": "I118-NODD-SoftEng-MuonExecution",
  "role": "SoftEng",
  "input_revision": "c9f2fa7992391987a46c81f038623a2d14e79990",
  "inputs": [
    "docs/validation/issue117/nodd-digitization-protocol.md",
    "docs/validation/issue117/nodd-digitization-analysis-notes.md",
    "software/analysis/calorimeter_digitization/nodd_response.py",
    "software/analysis/calorimeter_digitization/nodd_muon_response.py"
  ],
  "mode": "write",
  "writable_paths": [
    "build/issue117/nodd/response"
  ],
  "task": "Execute the newly closed six-muon native diagnostic and fixed-MIP analysis now. Exact source c9f2fa79 confirmed independently by PhysVal: all4scope/provenance findings closed;42controls pass; actual6metadata pass with unchanged globalindices38..43/seeds129300..129800 and fullscope correctlyrejects subset. Bothmuongroups normal0,1500events total, allrawverified. Frozen rawproducer/steering/protocol5af remain unchanged; showertransport stillactive separately. Sole ownedignoredoutput tree build/issue117/nodd/response; do not edit any trackedsource, protocol, notes, geometry, publicreport, commits or sharedinstall. Fresh task shell software/env/run.sh asverifiedexistingruntime; followacts-spack preflight boundary and reportstale fingerprints withoutinstalling. Commands use nodd_response.py run --population muons --transport-manifest build/issue117/nodd/manifest.json --samples build/issue117/nodd/muon-samples.json --work build/issue117/nodd/response --jobs 4. Defaults native_validation/backend paths /private/tmp/nodd-digitization117-build verified. After normal native6closures, run geometry twice in separate nativeprocesses with sameargs --population muons and --geometry nodd/odd-zero; may run2independentprocesses concurrently ifmemorypermits. Then stage muons with sameargs --population muons --fit-workers16 --output build/issue117/nodd/response/muon-summary.json. This uses fixed1000wholeeventbootstrap perstage/population; do not reducefits, alterselection, retuneMIP/noise/threshold/model/range orfixanyfailedfitbycherry-picking. Preserve actualundefined/failedresults. Refuseclosedoutputoverwrites; retainerrorsandreportbeforeanysourcechanges. Runsthissourcebeforeanynewnativeoutput; preserve runs-muons.json and completionproof. Record command exits, source/binary/config/input/output/log hashes, actualgeometryquery counts/residuals/IDs and fixedfit outcomes. No original-framework study yet; that separatehandoff awaitsall22nODDrawfiles. No additional transport, externalmessages, publication, installations, jobinterruptions ordelegation. Main willnotwriteownedresponse tree untilyoureleaseit; reportsource/runtime problems promptly, do not silently retry differentinputs/criteria.",
  "deliverable": "Closed six native jobs, actual nODD/ODD native muon geometry proofs and fixed-statistics muon-summary.json+completion proof, actual commands/checks/numerical outcomes and explicit limits; retain allrawlocal.",
  "completion": "Return measured results and artifact/hash paths with normal-exit evidence, or a concrete retainedfailure. Release response tree oncompletion; no detector/humanapproval implied."
}
```

## Corrected source assessment and native muon execution

Separate PhysVal confirms all four findings closed at
c9f2fa7992391987a46c81f038623a2d14e79990. Independent12/12 changed-module
controls pass0.063s from pinned git-show modules; allsix assignedSHA256s and
legacy helper identities match. Actual six closed populations/1500events
retain indices38..43 and seeds129300..129800. Full scope rejects the subset;
native-pass-binding bytes unchanged. No actual scientific outputs, geometry or
transport were reviewed/executed by this source assessment. Final data review
remains pending. Only after this handoff was SoftEng muon execution triggered.

SoftEng reports fresh runtime probe0 (Python3.14.5,ROOT6.40.04,NumPy2.5.4,
Geant411.4.3 and DD4hep/DDG4/podio imports); known registry fingerprint warning
retained, no installs. Allsix native250event jobs close0 in22.885s with fixed
global seeds. runs.json and preserved runs-muons.json exist.
Actual native geometry queries run in separate processes and both close0:

- nODD36.579s:2304planes,35353references,4963uniquecells; maximum residual
  0.000195312500182mm<.002mm;zero collisions/no changed physical fields.
  CompactSHA902a6c3776d9ebbadf216d9886f8ace90b18c51b83d1b57ef604bd8de071f390.
- ODD7.642s:2304planes,39414references,3381uniquecells; maximum residual
  0.000097656250091mm;144module-field16→encoded0 changes,zero collisions.
  CompactSHA3cf7618a3591df2acc3a0243ededf2751805a3605f730f3bcd1a502a10b30483.

Initial straight rays cross42/43/43active planes in nODD versus48/48/48ODD at
eta0/+2/-2. These remain approximate geometric diagnostics; missing primary
deposits are not reclassified as known transported crossings. Fixed1000-bootstrap
perstage/population muon fits now run with16workers. No source, MIP, noise,
threshold, selection or fit setting changed. No fit result is claimed yet.

### I118-NODD-PhysVal-MuonData

```json
{
  "id": "I118-NODD-PhysVal-MuonData",
  "role": "PhysVal",
  "input_revision": "c9f2fa7992391987a46c81f038623a2d14e79990",
  "inputs": [
    "docs/validation/issue117/nodd-digitization-protocol.md",
    "docs/validation/issue117/nodd-digitization-analysis-notes.md",
    "software/analysis/calorimeter_digitization/nodd_response.py",
    "software/analysis/calorimeter_digitization/nodd_muon_response.py",
    "software/analysis/calorimeter_digitization/muon_response.py",
    "software/analysis/calorimeter_digitization/digitized_response.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Separate scientific review of completed actual six-muon results, numericaldataonly; figuresnotgeneratedyet. First inspect pinned primarysource and actualclosedinputs beforeauthor conclusions or authored report. Runtime data: build/issue117/nodd/muon-samples.json; response/runs-muons.json SHA30841e90b936a2f8c3b36c999cdbbed53259144038ca982279e150e19dded0d9; response/muon-summary.json SHA59540ebdbacff877d01691516120e2687a112692092f48bc6ff4ed0b10f7c44b and its .completion.json SHA43517a5c7becddc1d657dd45c501f0b254b77207bdd51189c040945a1d500e7a. All paths under build/issue117/nodd. Tree released by execution owner. Actualsourcec9, native6jobs andbothnativegeometryprocesses andfixed1000fitbootstrap18stage/populationcombinations closednormal0. Read primary rawROOT/diagnostics/nativegeometrycaches/proofs asneeded; independentlycheck identities/actualscope, source/config/binary/raw/closedreceiptbindings, physicalID/positionclosure evidence, immediate-constructed-neighbour/pureprimaryselection and approximatepath conventions, allnominal/identified/missing-unknown/split/contaminated denominators andactual.6counts, spectra/histogram/thresholdmassclosure andmonotonicity, preservedundefinedrare-categoryuncertainties, fits/conventions/diagnosticflags andeventbootstrap/SNR/pedestalinterpretation. Choose meaningfulactualrecomputations/refits/representativebootstrapchecks asneeded; no need duplicateevery expensive fit absentnewconcerns. Do not accept statedzero flags as substitute forchecking. Report measured findings/limits andwhether \u03bcnumberssupporttheir scoped plots, withoutdetectoracceptance or concludingunexecuted full originalKey4hep/showercomparison. The frozenfullshowertransport remainsactive; neverinterrupt/modify it. Read-onlyrepo/no geometryortransportexecution, no newevents, sourceedits, dependencychanges, externalmessages, commits orfurtherdelegation. Task-owned /private/tmp scratchforchecks permitted. Main willcuratefigures andfulloutcomelater; no expectedpass requested.",
  "deliverable": "Exact-c9 separate actual-muon data assessment with independently checked numerical evidence, consequential findings, measuredchecks andscientific limits before publication.",
  "completion": "Return evidence-based assessment and any blocker; actualfullshower/originalframework/figure review remainsseparate."
}
```

## Closed muon analysis handoff, scientific assessment pending

SoftEng releases response tree after all stages normal0: native22.885s,
nODDgeometry36.579s,ODDgeometry7.642s, muon analysis1172.258s with16workers.
All18point fits available and18000/18000bootstrap fits converged;zero failure,
boundary or shape/deviance flags reported. Main reads actualsummary1,472,988bytes
and verifies its sourcec9 and SHA59540ebdbacff877d01691516120e2687a112692092f48bc6ff4ed0b10f7c44b.
Completion43517a5c7becddc1d657dd45c501f0b254b77207bdd51189c040945a1d500e7a;
preserved runs-muons30841e90b936a2f8c3b36c999cdbbed53259144038ca982279e150e19dded0d9.
Controllercompletebd63632b09bf92f5f326f85883aa705151e52a1df7b972e24eceb72e8439b31d;
post-analysis-auditee3e37c4b9fedf665d6b128efa0f00cba6d05a82d96f92056841cb824b4647b4.
Controller audits57artifacts, exact1500orderedidentities and acceptedcounts,
signed-pulse/eventenergy closure≤5.55e-17GeV; no allzero muonevents.

ReportedPN MPV±event-bootstrapSE ateta0/+2/-2 (MIP):
nODD.957671±.003041/.966695±.003047/.961869±.003038;
ODD.961183±.002804/.958711±.002570/.961877±.002662.
Nominal12000trials each. IdentifiednODD10513/10704/10698, unknownmissing
1487/1296/1302;ODD12000identifiedeach. PN>.6nominalnODD
.872833/.888167/.888083;conditionalidentified.996290/.995703/.996168.
ODD.997000/.997667/.997417forbothdenominators. SNRnODD7.360/7.429/7.392
versusODD7.387/7.368/7.392. These are scoped comparator/model statistics,
not hardware or complete detector efficiency. Rare split-category undefined
bootstrap replicas retainnullerrors (nODD1000/7/128,ODD1000/142/7); no
conditioning away zero-denominator cases. Allfigures and broaderinterpretation
await independent assessment; source μdata assignment precedes these author
conclusions in the reviewer contract. Full shower/original comparison pending.

Renderer caption-only refinement before first new figures explicitly defines
D/PN and distinguishes the nODD tracker+ECAL stage from ODD's complete
comparison geometry atzero field. No plotted statistic or selection changes.
Matplotlib CLI smoke passes. RawROOT/JSONL/trials/bootstrapdraws remain ignored.

### I118-NODD-CaloTech-MuonPreview

```json
{
  "id": "I118-NODD-CaloTech-MuonPreview",
  "role": "CaloTech",
  "input_revision": "e6268f81964dcda6582e03c69cde298d473f9fbf",
  "inputs": [
    "software/analysis/calorimeter_digitization/plot_nodd_digitization.py",
    "docs/validation/issue117/nodd-digitization-protocol.md",
    "docs/validation/issue117/nodd-digitization-analysis-notes.md",
    "README.md"
  ],
  "mode": "write",
  "writable_paths": [
    "build/issue117/nodd/muon-preview",
    "software/analysis/calorimeter_digitization/plot_nodd_digitization.py"
  ],
  "task": "Render and visually assess the actual closed six-muon figure now, before full shower data. Primarydata build/issue117/nodd/response/muon-summary.json SHA59540ebdbacff877d01691516120e2687a112692092f48bc6ff4ed0b10f7c44b, produced by statisticalsourcec9f2fa79; independent PhysVal numericreview is active separately. Currentcommittedrenderer caption explicitly distinguishes nODDtracker+ECAL from full ODDzero-fieldgeometry anddefinesD/PN. Source-only/privatepreview assignment: call existing muon_plot(data,path) directly, not fake shower data or full-five CLI. Use existing Matplotlib3.11.2 interpreter /Users/salzburg/Documents/work/installed/acts-nodd/pyvenv/bin/python withMPLCONFIGDIR=/private/tmp/nodd-issue117-matplotlib; no installs/ROOT needed. Writeinitial committed-source image under build/issue117/nodd/muon-preview/initial.png and retain it. Inspectimageforlegible axes/legend/captions/tables and faithful all-qualified normalization, actualPNoutput, nominalversusidentified denominators, approximateinitialrays/missingunknowncounts, fittedunderlyingMPV versusconvolvedmode, explicitSNR convention (pathnormalizedLandauMPV/signedpedestalRMS), uncertainty availability andprototypeboundary. Preservefullhistogramranges/flowcounts, componentcolorsECAL#cccc00/lighterODD, allnumericaldata, scales/selection/fitsettings. If layout/label fixesneeded, editonlyownedrenderer andreturnsourcereadyfor maincommit beforefinalrerender; do not overwriteoriginalprivatepreview or publishanyfigure. No statisticalsource, report,tracking,library/geometry/transport changes, commits, externalmessages, installation ordelegation. MainwillviewactualPNG; fullfivefigurebatch followsfullshowers/reference separately.",
  "deliverable": "Actual committed-source MIP preview, visualQA findings and any focused renderer-label/layout diff; no inventedscience or publication.",
  "completion": "Returnimagepath/sourceSHA/runtimechecks andclarityfindings; maincommitsanyrendererchangesbeforefinalexport."
}
```

## Actual muon figure preview and label closure

CaloTech renders actual closed six-muon data with committed e6268f81 renderer,
Matplotlib3.11.2 and no ROOT/fake shower input. InitialprivatePNG
build/issue117/nodd/muon-preview/initial.png SHA
e4a5c84aa3cb9365bf16e32706288f121334f1bad60270e1488a6ace9f16577b.
Agent and main independently view this image; all six populations, axes, curves,
flows, legends, tables and prototype scope are visible without cropping. Initial
PNG remains unchanged. Focused source-only refinements explicitly label PN
underlying Landau MPV/convolved mode, table±asSE, the SNR denominator/convention,
fixed10GeV/c andphi.123rad, all plotted raw/PN/selected-output flow counts and
actual selectedN. Missing deposits leave transported-crossing status unknown;
initial rays are geometry diagnostics. No numeric/statistical/source-selection
or scale changes. Source-readySHA
e535056258d61073c8084ef6614db900fd3e6f6831f782ad8cd0bb4798a3b8e9;
syntax/import/CLI/diff controls pass. Main commits before revised export.

### I118-NODD-SoftEng-OriginalExecution

```json
{
  "id": "I118-NODD-SoftEng-OriginalExecution",
  "role": "SoftEng",
  "input_revision": "e43bd0d2d5431237cd50bddb9a593bc1aa01b1df",
  "inputs": [
    "docs/validation/issue117/nodd-digitization-protocol.md",
    "software/analysis/calorimeter_digitization/nodd_reference_validation.py",
    "software/analysis/calorimeter_digitization/reference_validation.py",
    "software/analysis/calorimeter_digitization/test_nodd_reference_validation.py",
    "software/source/ActsExamples/Calorimeter/README.md"
  ],
  "mode": "write",
  "writable_paths": [
    "build/issue117/nodd-reference-validation",
    "docs/validation/issue117/previews/nodd-digitization-reference.json"
  ],
  "task": "Actual full original-Key4hep vs native nODD same-hit execution, only after main sends activation with globallyclosed/indexed/verified input. The latest frozenmatrix has22nODDfiles/4550events (19shower200each plus3muon250each), not earlier20/4600 draftscope. Main owns frozenrawgeneration andwillrun index andstrictfull48/9500verification, retainunaugmentedreferenceinput andappendclosedplugin-registration/full-inventoryproofartifacts; wait forthisexplicitactivation. Readfull source/protocol, preserveoldODDsource/data unchanged. Solewriteownedfreshignoredwork build/issue117/nodd-reference-validation andnewcompactpublicreferenceJSON. Use originalinstallation ../nodd-pr123-frameworks/software/env/key4hep_run.sh, runner nodd_reference_validation.py withdefaultframework/comparator/backend/native_validation paths. Freshactualruntime/source/status checks then stages prepare,pilot,deterministic,replays,stochastic,summarize, sequentialdependentgates. Assertinputexact22distinctNDids/4550events, maintainedfulltracker+BARRELHits8/EDGEHits9bothends; originalwrappergeometry/readoutcanonicalproof, allsource/library/input/closedreceipt/RNGidentityclosure. Aall22files mustrunactualfullGaudiDigitiserSiliconMip andnativecomparison with exactacceptedcellsets andstrictreference-only1e-5+5e-6abs(ref)MIPboundproof; retainallzeroevents andallfailures. Bfixedfirstrealcentralmuon andfirstgamma20eta2event0, two1000eventconditionalreplays P/PN each, independentROOT/CLHEPstreams andactualnonzero/uniqueseeds. Frozen1252xx/1253xxseeds,125800+1000fixture+iheaderidentity,126000+2f+manalysis; unchangedmean\u22645SE,10kpermutationCDFp\u2265.001 and10kbootstrapenergy-SDratio95CIwholly[.85,1.15]. Neverrelaxgates,chooseseeds/eventsafterseeingoutcomes ordiscardfailed/degeneratecases. PreserveallSimHits/contributions/MCendpoints/orderedEventHeaders; no timing/hardwareacceptanceclaim. No newtransport,geometry/model/source/sharedinstallchanges, commits, externalmessages orfurtherdelegation. Ifsource/runtime/gatefailure, retainclosedlogs/payload/receipts andreportmainbeforeanyremediation; do not overwriteexistingevidence. Compactsummaryonlybinwise/gates/moments/provenance, noevent/cell/trialpayload. Return actualcount/outcome/tolerancenorms/gates/versions/commands/hashes andlimits. Mainmayupdateunrelatedmetadataandnative-responseoutputsbutwillnotalterreferenceproducer/helper/protocol oryourworktreeoutputswhileactive.",
  "deliverable": "Newsource-pinned original/native nODD deterministic andfourconditionalstochastic comparisons withcompactnewreferenceJSON, actualclosedexits/hashes/counts/gates andretainedfailures.",
  "completion": "Returnactualallcaseoutcomes/provenance orconcretefailure andreleaseownedpaths; no broadergeometry/hardwareapproval inferred."
}
```

## Independent actual muon assessment and refined figure

PhysVal I118-NODD-PhysVal-MuonData reports no consequential finding at exactc9.
Allsix source/threeartifact hashes match; actual verification covers all1500raw
frames/74767ECAL hit references, source/native/config/backend/helper/completion
bindings, generator endpoints, primary purity/split/depth/chord/path selection,
all18unthresholded+12selected spectra and all1000-resample threshold/category
uncertainties/covariances. Counts reproduce exactly, including unknown crossings
and rare splitundefinedreplicas1000/7/128/1000/142/7 withnull errors retained.
Both2304plane inventories/actualencodercrosswalks close; maximum nativeposition
residual.000195313mm<.002mm. All18centralROOTfits replay exactly withpositive
covariance, no nearbound/devianceflags; diagnosticp.3346–.9347. Acomplete1000fit
nODDeta0PNbootstrap replay matchesMPVSE.00304096484 andCI95
[.951576129,.963625267],zerofailures. Recomputed200kpedestalSD.130119248,
mean−.0000504523MIP,4610above2sigma/0above.6,analyticdeviations<.9SE.
SNRreproduces7.360–7.429. Scratch checks at
/private/tmp/nodd-physval-muon-{audit,fits,additional}.{py,json} remainlocal.
No authored outcome report read, repo edits, geometry build or transport.
Fits characterize selected approximatepathnormalized populations; geometry/model
systematics and detectoroccupancy are excluded. Full shower/originalreference
and allfigure assessment remain separate.

Main exports revisedprivateMIP from committed e43bd0d2 renderer, using the same
rcParams as full-five CLI. RendererSHAe535056258d61073c8084ef6614db900fd3e6f6831f782ad8cd0bb4798a3b8e9;
input59540...unchanged; output build/issue117/nodd/muon-preview/refined.png SHA
fc5aa712969f1cbcf3d18c2540ab1d5b0fdf08871502ff3b11af8375b51561bf.
Matplotlib3.11.2/NumPy2.5.4; normal0. Mainview confirms labels, flowcounts,
qualifying/selectedN, fit/SE/SNRconvention, fixedgunphi/p, tables, captions and
legends visible; no cropping/overlap. Initialpreviewretained. Finalfullbatch
willregenerate this figure andcheck againstthiscandidate aftercached-result
attachment. No statisticalsource/settings changed.

## Full raw/native closure and separate comparison assignment

All four raw groups close normally; 48 populations / 9,500 events pass canonical inventory, truth, ordered headers, unique source-cell IDs, immutable hashes and actual RNG-state checks. nODD showers complete in 12,389.345 s; no technical/failed events enter this inventory. Index exits 0 and produces 22 nODD reference files / 4,550 events. The retained generated reference input is augmented only with closed plugin-registration and full-inventory proof artifacts (10 total); augmented SHA 6c1a3904b9e2b40e992f71baa875d6014e64fea321e66cb20ce8d7e76c4d4db7. Original execution activation follows this full closure. Its pilot exits 0 in 36.790 s: 333 input cells, 279 accepted, zero mismatches and strict normalized upper bound 0.10000005. Full original comparison is running.

All 48 native jobs now close normally, preserving six muon cache identities and global seeds. Full analyze runs with the exact closed muon summary, so expensive fits are reused only after full verification; results remain pending. Hosted checks at published 2fcd47cf all pass (build 9m56s, unrooted 2m18s, token 40s).

### I118-NODD-PhysVal-FullComparison

```json
{
  "id": "I118-NODD-PhysVal-FullComparison",
  "role": "PhysVal",
  "input_revision": "e43bd0d2d5431237cd50bddb9a593bc1aa01b1df",
  "inputs": [
    "docs/validation/issue117/nodd-digitization-protocol.md",
    "docs/validation/issue117/nodd-digitization-analysis-notes.md",
    "software/analysis/calorimeter_digitization/nodd_response.py",
    "software/analysis/calorimeter_digitization/nodd_muon_response.py",
    "software/analysis/calorimeter_digitization/nodd_reference_validation.py",
    "software/analysis/calorimeter_digitization/reference_validation.py",
    "software/analysis/calorimeter_digitization/plot_nodd_digitization.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Separate scientific assessment of actual complete zero-field nODD/ODD comparison, primary inputs first. Previous actual muon review stands; do not duplicate all expensive muon fits absent a new concern. All 48 raw populations / 9500 events and 48 native outputs are now closed normal 0; build/issue117/nodd/{manifest.json,samples.json,response/runs.json,validated-full-inventory.json} are immutable. Statistical producer bytes remain c9f2fa79, current committed source e43bd0d2; raw producer/protocol 5afb019e. Main runs full final analyze to response/summary.json with closed muon cache; this output is still pending, wait for its explicit SHA handoff before conclusions. Original Key4hep full comparison is also running under SoftEng; do not interfere, wait for summary SHA handoff before reviewing gates. Start independently inspecting source/frozen protocol and actual primary raw/native inputs, source/binary/config/receipt bindings and sample plan now. Assess 38 shower populations, 4 independent 100-event ODD D references, true-total-energy denominators, shared calibration, paired stage changes, independent geometry comparisons, 5000 whole-event/reference bootstrap and 114-axis response/width/tail covariance. Choose meaningful independent recomputations from events, not just consistency among authored summaries. Check zero-event/tails/longitudinal normalization/histogram flows and retain failures. Check same closed muon cache and pedestal exact attachment. Then assess full original 22-file/4550-event comparison and four fixed conditional replay gates when handed off, including strict reference-only tolerance, actual cell sets/event identities/payload closure and independent seed identities. Figures will be rendered later and main will hand off actual PNGs for visual/scientific QA; no need wait for figures to report numeric findings. Do not read author's outcome report before primary data. No new transport, geometry/material/source/helper/protocol edits, gate/seed changes, shared installs, repo edits, commits, external messages or further delegation. Private /private/tmp scratch and necessary verified runtime checks permitted. Report adverse geometry response distinctly from digitizer software agreement; no tiling-only, hardware, complete fielded nODD or human acceptance claim.",
  "deliverable": "Exact-revision independent full comparison assessment with actual numeric recomputations, consequential findings, measured checks and interpretation limits. Coordinator curates it in paired session.",
  "completion": "Return source/data/gate assessment or blockers after explicit pending-artifact handoffs; figures may be a separate follow-up."
}
```

## Full response closure and quantile correction

Full analyze exits 0 at source HEAD e43bd0d2d5431237cd50bddb9a593bc1aa01b1df; statistical producer bytes remain c9. Runtime output SHA adbdbe66978e033c415aa6aea905a409b554aacf37758ae69eacd37248abc58d (5,818,881 indented bytes). The public nodd-digitized-response.json uses compact JSON serialization (2,526,638 bytes, SHA ae770b1113ee96df5f9667d8bd590e27ffde0c6f89582cc5a81ddca66ae53fd8); exact decoded-object equality is checked. It stores 38 shower populations, 19 geometry pairs and three full 114-axis covariance matrices, plus the previously closed muon statistics. Muon and pedestal objects compare exactly with the independent closed subset; no fit rerun or settings change.

PhysVal independently identifies a protocol omission: stage moments lack descriptive quantiles required by protocol line340. Preserve the closed frozen producer/output; add nodd_response_quantiles.py as an explicit separate attachment to the same event totals. The post-run descriptive grid is [0,.01,.05,.16,.5,.84,.95,.99,1], linear interpolation, with no new gate, event selection, seed or calibration tuning. Bind exact full-response/runs/output/input identities, preserve zeros and ordered event headers, and reproduce all closed means/SD/zeros before export. Four focused controls pass (0.059s): independent order-statistic interpolation, output tamper, wrong population/moments and reordered identities. Source is committed before real attachment execution. The initial omission and original output remain inspectable.

Observed primary full-response ranges, still under separate assessment: nODD/ODD raw means .488009–.629338 and PN means .485926–.628229; substantial baseline geometry differences are not assigned solely to tiling or digitization. PN/raw mean changes are −1.2143% to −0.6644% in nODD and −.7932% to −.4859% in ODD. No raw zero-energy shower events occur in either geometry. Full original-framework agreement is still running; no pass is inferred from this characterization.

The new transport/native compact record is 268,914 bytes, SHA a66bd142cea60a0f95ec05bb77594594ac97280fc16f6f6fd3cd95072a8819fc: exact source/SDK/geometry/registration/48-population seed/input/output/receipt hashes, four initialized Geant4 audits and native query aggregate proofs. It contains no event/cell/trial payload or serialized RNG state.

### I118-NODD-CaloTech-FinalFigures

```json
{
  "id": "I118-NODD-CaloTech-FinalFigures",
  "role": "CaloTech",
  "input_revision": "45e17d0e797d4ab6c2a1dee835f50d73f966b638",
  "inputs": [
    "README.md",
    "docs/validation/issue117/nodd-digitization-protocol.md",
    "software/analysis/calorimeter_digitization/plot_nodd_digitization.py",
    "docs/validation/issue117/previews/nodd-digitized-response.json",
    "docs/validation/issue117/previews/nodd-transport-validation.json"
  ],
  "mode": "write",
  "writable_paths": [
    "build/issue117/nodd/figures-first"
  ],
  "task": "Render and visually inspect the actual complete nODD/ODD response figures using current committed plotter, no source edits. Public compact response docs/validation/issue117/previews/nodd-digitized-response.json SHA ae770b1113ee96df5f9667d8bd590e27ffde0c6f89582cc5a81ddca66ae53fd8, object-identical closed runtime summary adbdbe66. Renderer SHA e535056258d61073c8084ef6614db900fd3e6f6831f782ad8cd0bb4798a3b8e9 remains unchanged from e43. Use actual Matplotlib3.11.2 existing interpreter /Users/salzburg/Documents/work/installed/acts-nodd/pyvenv/bin/python with MPLCONFIGDIR=/private/tmp/nodd-issue117-matplotlib. Run CLI now WITHOUT --reference, fresh --output build/issue117/nodd/figures-first, rendering four real response figures. View all four and assess readability/axes/legend/full ranges/error/flows/prototype scope against compact data; do not alter numerical data/scales/selections. MIP PNG must byte-match private refined.png SHA fc5aa712969f1cbcf3d18c2540ab1d5b0fdf08871502ff3b11af8375b51561bf because same actual muon data/source/rcParams. Report any mismatch or consequential display issue before a source fix. Full original-reference comparison is still running; wait for explicit actual compact reference path/SHA handoff before rendering the fifth with reference_plot or CLI, preserve first four bytes and report equality if rerun. No invented reference input. Main will copy final actual five public artifacts and do independent image QA/replot checks; you only own ignored figure directory, no tracked source/docs/metadata, commits, installs, messages or delegation. Native/transport/analysis are frozen and must remain untouched.",
  "deliverable": "Actual source-pinned four figures now, actual fifth after reference handoff, image-by-image visual QA and output/runtime hashes; no premature reference pass.",
  "completion": "Return actual image paths/hashes and clarity assessment; original-reference fifth waits for closed data."
}
```

## Separate full-data assessment and first response figures

PhysVal exact-source assessment independently reconstructs all 42 non-muon ROOT populations / 8,000 events / 4,889,774 ECAL hits: all raw/native totals, accepted counts/energies and generator PDG/origin/direction/p/total-E denominators match; maximum Etruth discrepancy 7.11e-15 GeV. All38 longitudinal axes/means/SEM and energy sums match. Together with the earlier independently checked 1,500 muons this covers all9,500 transports. Its independent 38×5,000 joint event/reference resamples reproduce 133,362 scalar/count/bin/covariance checks, including all114 axes and three114×114 covariance matrices. Full-source/input/native/hash checks pass. No shower numerical blocker remains. All3,800 nODD PN showers fall below common-scale response0.8 versus3/3,800 ODD; this is reported as adverse baseline geometry evidence without tiling-only or electronic attribution.

The separately executed quantile attachment at45e17d0e exits0, 139,724bytes SHA5e06a66c69d0638c6a09796db17715fbeccf36668b023368080e7cd2f90f74fe. PhysVal independently matches all3,078 quantiles plus38row identities/denominators, source/public-response/native-runs bindings and no-event-payload boundary. Public response object equality with original runtime output is independently confirmed. Protocol quantile omission is closed without editing the frozen main/helper/protocol or any original output.

CaloTech renders four actual figures using committed45e17d0e and rendererSHAe535056258d61073c8084ef6614db900fd3e6f6831f782ad8cd0bb4798a3b8e9, Matplotlib3.11.2/NumPy2.5.4, normal0. Main copies them byte-identically from ignored figures-first to public previews. SHA256: electron ca3cca65084371833479b21011386b03f049a21d5d3501fc73c0cd3cf0c3c218; photon5c47912333c57553c14ef44e4db3332a8eac15148ca7711ae5fc6026804d8ae6; MIPfc5aa712969f1cbcf3d18c2540ab1d5b0fdf08871502ff3b11af8375b51561bf; comparison12d357ea4e367ecc64562886fa0e9675949ff8d0ca34ea3bf41be627d35c32c6. MIP exactly matches refined preview. CaloTech, main and separate PhysVal each view allfour actual original-resolution PNGs; axes/legends/captions/error bars/tables and scope are visible without cropping or overlap. PhysVal confirms plotted means/errors/denominators/MPV conventions/unknown crossings match its independent reconstruction. Independent rerender remains in progress. The fifth original-reference figure awaits actual data, without any fabricated reference input.

One prepare invocation used unsupported --output and returned2 before dispatch; corrected by redirecting validated prepare stdout. Initial combined patch failed context matching and changed no files; corrected focused patches applied. No scientific/source/transport failure concealed.
