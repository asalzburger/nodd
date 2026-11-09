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
