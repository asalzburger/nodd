# PR90 inner-barrel reviewer follow-up

User: “Check if there are new comments on the PR and address them if present”. Clean start56f12ef5b2a9bd410cb77e95ac3140557d92f1b2 on codex/muon-chamber-layout. New reviewer comment https://github.com/asalzburger/nodd/pull/90#issuecomment-6288294033 asks coil-plane inner barrel chambers below coils and longer/wider intercoil chambers for coverage, analogous to outerbarrel. Interpret secondbullet as tangential width consistent with the requested transverse stagger; no new zlength request is inferred. Need actual HCAL/BT space before authoring geometry. No human sign-off; active888candidate fixed pending feasibility. Exact root/specialist token counters unavailable, not zero.

## IB-A1 before dispatch

```json
{
  "id": "IB-A1",
  "role": "SysArch",
  "input_revision": "56f12ef5b2a9bd410cb77e95ac3140557d92f1b2",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "docs/validation/DES-040/barrel-overlap-2026-10-20/candidate/geometry.json",
    "tools/muon_layout/barrel_overlap.py",
    "tools/muon_layout/layout.py",
    "tools/muon_layout/geometry.py",
    "tools/muon_layout/support.py",
    "tools/toroid_prototype/geometry.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "PR90 new human reviewer comment6288294033 asks innerB1 analogous stagger: move coil-plane chambers now above BT inner legs below those coils, and widen intercoil chambers to improve angular coverage. Independently assess feasibility against actual fixed BT warm geometry, HCAL prototype and all support interfaces. Current888outline baseline696barrel+192endcap, B1R5.2depth0.5, BTcenter6.7halfr2.1warmhalfnormal0.25tangent0.30, HCALboundcorner4.23946. Do not adopt these as a guessed answer: derive actual radial/azimuthal room from source. Distinguish conservativeHCALcornerbound from actual finiteHCALpolygons; find relevant pinned HCALsource/baseline artifact if available before claiming material intersection. Need exact possibleB1R interval below coils at50mmclearance/500mmdepth, actualcoil+HCAL point witness or stated bound-only scope, alternatives and consequences if impossible. Need separate angular overlap/physical SAT proof and no source changes. Preservecurrentactive geometry/maps/OBJ/frame/endcaps. Any narrowerchamber/HCAL/magnetredesign is unselected unsignedalternative requiring explicit physical choice, not automatic retune. Scratchportablechecker/report --repo --revision --output /private/tmp/pr90-IB-A1-*. No repo edits, dependencies,nativeACTS, Git commits, nested agents or external messages. Read AGENTS/PROJECT and design-evidence/review workflow, give early hardbounds then finishfocusedactualmath. Do not implementcandidate or grantapproval.",
  "deliverable": "Exact-revision independent interface feasibility report plus portable numerical checker/actual results identifying requestedinnerstagger room or concrete obstruction and minimal physical changes.",
  "completion": "Root can answer reviewer honestly using actual HCAL/BT geometry and finite-clearance bounds, with no inferred approval or silentlychangedphysics."
}
```

## IB-M1 before dispatch

```json
{
  "id": "IB-M1",
  "role": "MuonTech",
  "input_revision": "56f12ef5b2a9bd410cb77e95ac3140557d92f1b2",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "docs/validation/DES-040/barrel-overlap-2026-10-20/candidate/geometry.json",
    "tools/muon_layout/barrel_overlap.py",
    "tools/muon_layout/layout.py",
    "tools/muon_layout/geometry.py",
    "tools/muon_layout/support.py",
    "tools/toroid_prototype/geometry.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "PR90 comment6288294033 asks innerB1 analogous stagger: move coil-plane B1panels below BTinnerlegs, widen intercoil panels to improve angularcoverage. Read actualcurrentsource and assess bounded outline design options without repo changes. Derive requestedinner-evencoil-plane radiallocation vsfixedHCAL/BT (do nottrustconservativeHCALbound asliteralshape). If requestedinward movement cannotfit500mmdepth+50mmclearances, quantify geometricproblem, and derive conditional feasible alternative retainingallfixedmagnets/HCAL/frame: keepcoilplaneB1aboveinnerBTlegatR5.2, movetwelveintercoilB1facetsoutwardtrialR5.75 andwiden to0.1degree30mmborderfull-depthprojection. Do notadoptalternative; testfinitevolume/coreinterfaces andB2gap, actualcounts/family/coverage tradeoffs using scratchbuild/customfacetpacking on immutablebaseline. No sourcechanges, historicalcertificate reuseorhallucinatedACTS. First priority requestedinnerundercoilfeasibility; ifblockedphysically, returnconcreteoptionsnotanactivecandidate. Existing B2/B3/endcaps/frame/magneticmapsfixed; no tube/material/responseengineeringclaim. Scratch portable focused calculation/proposal report /private/tmp/pr90-IB-M1-*. No repository writes, Gitcommits, dependencies,nativeACTS,broadscans,nestedagentsorexternalmessages. Coordinateearlyphysicalboundswithrootand /root/inner_barrel_interfaces. No designapproval.",
  "deliverable": "Pinned MuonTech feasibility contribution with requestedinwardconstraints and a conditionalfixedhardwareoutward alternative if useful, derivation and actualboundedchecks/results.",
  "completion": "Root has concrete reviewable innerbarrel response or physicalblocker, no unexplainedcollision or silently adopted alternative."
}
```


## Exact-source contributions and outcomes

IB-A1 SysArch completed pinned56f12ef withHCAL0e8530d56d171f38c9d53d3c60c8b48803680bbd hash-matched to MUON001/DES039 provenance. Stdlib checker10controls pass. FixedBTinnerwarmface4.35m and500mmdepth/50mmmargin imply R<=4.05m (limiting expanded-boundarycontact, notacceptedcertificate). ActualHCALcover fullwidthfootprints requireR>=4.458m onalignedplanes or4.530252500m onotherplanes. All48movedcoilplaneB1panels intersectactualHCALplates/cover in28416SATpairs; actualinteriorsteel(4.12,0,1)m andcover(4.153,0,1)m witnesses avoidz0seam. OtherB1/support/chamberSATchecks clear; HCAL isactualblocker, notfilledcircumcircle. Currentgeometryunchanged.

IB-M1 MuonTech completed conditionalunselectedintercoilR5.75trial usingexistingpackkernel andfresh144uncachedorientationcoilproofs,484supportmembers,437580finalchamberpairs. Current792nonB1objects fixedvalueequal. B1count96→144 andfamilies1→4,total936ifselected. Full65536iid4pi samecassettefinitebankseed40087 (allbarrel/endcapalternativesORwithin3stationIDs) findsoutline65.615845→64.266968%,border57.440186→56.398010%; notthepriorcentral-onlybank. Border1245gain/1928lose,delta−1.042175pp (pairedSE0.085856pp). Losses565framepacking,1034zseam/samecassette,329finitebarrelreach; allphysicallylocalized. StandaloneB1borderarea grows60.0174→63.9252% butthree-stationproxyworsens, soalternative isnotadopted/recommendedasoverallcoverageimprovement. PortableCLIextractionreplay matchesallscientificresults/lossIDs andoutlinesbytes. No nativeACTS/DD4hep/Geant4 orfieldsolve needed becauseactivecandidateunchanged; no shareddependenciesmodified.

Plottingruntime preflight warned changedsetup/Spacklockfingerprints; freshsameshell setup_spack, actualactiveci-dependencies andinstalledNumPy2.5.4/Matplotlib3.11.2 importsverified before plotting. DefaultPythonNumPy2.5.1/stdlib sufficesforcontributioncheckers. InitialparentworkspaceGitqueryhadnoHEAD; changedimmediatelytoexplicitknownPRcheckout, nobranch/filemodifiedthere. Existing888currentcandidate,bluegreyOBJ,jointmap,frame,endcaps andpreviousscientificevidence remainimmutable.


## IB-P1 before dispatch

```json
{
  "id": "IB-P1",
  "role": "PhysVal",
  "input_revision": "94d474906660619587b66e850019f0f0fb8e03bd",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "tools/muon_layout/inner_barrel_views.py",
    "docs/validation/DES-040/barrel-overlap-2026-10-20/candidate/geometry.json",
    "docs/validation/DES-040/inner-barrel-2026-10-20/README.md",
    "docs/validation/DES-040/inner-barrel-2026-10-20/interface-check.py",
    "docs/validation/DES-040/inner-barrel-2026-10-20/interface-check.json",
    "docs/validation/DES-040/inner-barrel-2026-10-20/conditional-check.py",
    "docs/validation/DES-040/inner-barrel-2026-10-20/conditional-check.json",
    "docs/validation/DES-040/inner-barrel-2026-10-20/conditional-B1-outlines.json",
    "docs/validation/DES-040/inner-barrel-2026-10-20/views/views.json",
    "docs/validation/DES-040/inner-barrel-2026-10-20/unchanged-evidence.json",
    "docs/validation/DES-040/inner-barrel-2026-10-20/inputs/source-manifest.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Independent actual-artifact assessment of PR90 latestinnerbarrelproposal feasibility, at exactrevision. Inspect primarygeometry/magnetic/HCALsource before authorconclusions. Evaluate requestedbelow-BTinnerleg B1 placement against real finite16sectorHCALsteel/cover and retained500mmdepth/50mmmargins, notjustcornercircle; identify any incorrectcollision/no-fit claim with source/polygon/witness. Extra HCALsource0e8530d56d171f38c9d53d3c60c8b48803680bbd is pinned in baselineMUON001 andnewarchive/manifest; gitobjectavailable, mustreadexactblobs notdirtysibling. Evaluate unselectedoutwardintercoiltrial: finitegeometry/cert/source identity, changedB1outlines only with fixedotherobjects, wholevolume/corner separation and actual reportedcounts/families. Recompute boundedfull4pi geometricbank independently (notrepository kernel): stationarysamecassettebothdepthfaces; unionbarrel/endcapwithin3stationIDs, exposegained/lost/SE denominators andlocalcut/seam/end classifications. Do not confusewithpriorcentral-onlybank, efficiencyortransport. CheckactualPNG/SVG/displaypolygons/sourcehashes/geometrymetadata, invalidcounterfactual vsunselectedalternative vsactivecandidate. Verify old687source/evidenceblobidentities andactive888geometry/OBJ/mapsunchanged. Scope is boundedstandard-library/NumPy geometry/artifactaudit, no nativeACTS/DD4hep/Geant4 reruns, fieldsolve, packages, broadoptimization orauthorimplementationreviewofowncode. No repositorywrites; scratch portable checker/report/results /private/tmp/pr90-IB-P1-*, --repo --revision --output frompinnedgitblobs. No nestedagents/Gitcommits/externalmessages. Return earlymaterialfindings andfinalcheckedsource/result/limits, nohumanapproval. Rootwillhandleclaimedphysicaldecision andpublicresponse;do notsilentlyselectanyalternative.",
  "deliverable": "ExactrevisionPhysVal report and portable focused artifactchecker/results in scratch, concretefindings orboundedassessment ofphysicalobstruction/conditionaladversetradeoff andunchangedactivecandidate.",
  "completion": "Root can answernewreviewercomment using independently assessedfinitegeometry anddeclaredcoverage scope; anyunsupportedclaim corrected, allopenphysicalchoicesandengineeringlimits preserved."
}
```


## Independent final actual-artifact assessment

IB-P1 reviewed exact94d474906660619587b66e850019f0f0fb8e03bd without importing authoredrepositorykernels. Successful final27.8191s checker independently reproduces all65536full4pi bankcounts/pairedSE/lossclasses;437580conditionalchamberpairs,69696B1/supportpairs,3456straightlegpairs;actual48inwardHCALconflicts;700uniqueplotpolygons and1932actualSVGpolygons;all12archiveblobs and687prioridentities. No materialconclusioncorrection identified. Four adverse/observablecontrols pass. No physics/geometry/figure correction required; active888unchanged. Reviewer's unverified adjective'dirty' for unusedsiblingtree removed asrecord-onlycorrection (rootobservedsiblingclean0e). Lowimpactprovenancenote: viewsruntimeversionsmissingat94target. Rootadds supplementalplotting-runtime.json fromactualobservations: generatingNumPy2.5.4/Matplotlib3.11.2 verifiedbeforeplotting, samePythonexecutableversion3.14.5readbackafterplotting. Exactreviewtargetunchanged; supplementalmetadataisoutsideassessment, no byte-identicalplotregenerationclaimed. No simulation/dependencychange or humanapproval.
