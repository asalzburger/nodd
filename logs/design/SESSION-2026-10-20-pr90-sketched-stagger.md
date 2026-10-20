# PR90 updated sketch and half-sector middle station offset

The user asked to address the next PR90 comment and then said the comment was updated. The authoritative edit is comment6290378667 at2026-10-20T12:12:08Z. Its earlier outward-selection wording was superseded before implementation. The coordinator visually inspected the public sketch c3b4672b-c7e1-468b-94ee-01314dc2a8ee: inter-coil B1 moves inward; coil-plane B1 stays outside BT. No signed redirect URL or downloaded remote image is retained in Git.

A preimplementation DES040 amendment declares the R4.63 trial, full-depth overlap, clearances, fixed hardware, phase7.5 B2 and limits. An optional question asked whether “middle stations” includes endcap wheels. No answer arrived before construction; the documented minimal scope is B2 only, with endcaps fixed. A15degree rotation would leave the24-facet edge set unchanged. This is a prototype assumption, not a human endcap decision.

Start was clean at a12efbb5f169e5e02cd1f36aee48c1e748b6ce6f on codex/muon-chamber-layout. Repository nodd-coordinate, nodd-design-evidence and nodd-review-validation workflows apply. The acts-spack skill governs native runtime reliance. No exact root/subagent token counters are exposed; missing usage is not zero.

## SS-A1 before dispatch

```json
{
  "id": "SS-A1",
  "role": "SysArch",
  "input_revision": "a12efbb5f169e5e02cd1f36aee48c1e748b6ce6f",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "docs/validation/DES-040/barrel-overlap-2026-10-20/candidate/geometry.json",
    "tools/muon_layout/barrel_overlap.py",
    "tools/muon_layout/layout.py",
    "tools/muon_layout/geometry.py",
    "tools/muon_layout/support.py",
    "tools/toroid_prototype/geometry.py",
    "docs/validation/DES-040/inner-barrel-2026-10-20/interface-check.json",
    "docs/validation/DES-040/inner-barrel-2026-10-20/conditional-report.md"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Updated PR90comment6290378667 at12:12:08UTC supersedesolderoutwardselection. Actualsketch: retainB1coilplaneevenfacetsR5.2, moveintercoiloddB1 inwardbetweenBTinnerlegs (approxR4.6), wideningforoverlap. RootpreimplementationDEScontractprovisionallyR4.63, full-depth30mmborder0.1degoverlap, depth0.5, neighborphysical20mm, coil/support/HCAL50mm. MiddleB2offset7.5deg (halfof15degchamberpitch);15degwouldnotdealign24facetedges. Endcapsfixedunlessuserclarifiesalsoincluded; do notassumeendcaprotation. IndependentlyderivewholevolumeB1feasibleinterval inclactualHCALsteel/cover+externalservicejacket/routes (HCALsource0e8530d pinnedinMUON001/DES039;egressradius4.3,jacket.025 mayexceedcornerbound4.23946). Actualsourcevsreservations distinguish. CheckchangedB2frame/ECTinterfaces andall484supports, actualC12symmetry; derivegeometryofsourceproposedwidth/margins, anyphysicalblockers/necessarycuts. CriticallycheckoldnativeentranceR4.35 andforwardoffsetagainstnewB1frontface: proposeboundednumericalentranceoutsideHCAL/beforeeverypanel andnegativeinside-startwitness. Comparefullznotcentralonly. Fixedmagnets/maps/B3/endcaps/HCAL/frame; no material/reconstruction/leverarmguarantee. Scratchportablechecker/report --repo --revision --output /private/tmp/pr90-SS-A1-* only; no repositorywrites, nativeACTS/dependencies, Gitcommits,nestedagents or externalmessages. ReadnewdirtyDESappendasworkflowcontractbutnumericinputspinned; sourceadditionalHCALcommitexactrecord. Coordinateearlyconstraintswithrootand /root/sketched_chambers; finalboundedreport/checker/results, no approval.",
  "deliverable": "Pinned independent physical-interface and native-start-bound contribution, actualsourcechecks andconcreteconstraints/cuts.",
  "completion": "RootcanreconcileupdatedsketchwithactualHCAL/services/coils/frame andvalidnativeentrance, nooldblockedcoil-planeinterpretation orfalseleverarmclaim."
}
```

## SS-M1 before dispatch

```json
{
  "id": "SS-M1",
  "role": "MuonTech",
  "input_revision": "a12efbb5f169e5e02cd1f36aee48c1e748b6ce6f",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "docs/validation/DES-040/barrel-overlap-2026-10-20/candidate/geometry.json",
    "tools/muon_layout/barrel_overlap.py",
    "tools/muon_layout/layout.py",
    "tools/muon_layout/geometry.py",
    "tools/muon_layout/support.py",
    "tools/toroid_prototype/geometry.py",
    "docs/validation/DES-040/inner-barrel-2026-10-20/interface-check.json",
    "docs/validation/DES-040/inner-barrel-2026-10-20/conditional-report.md"
  ],
  "mode": "write",
  "writable_paths": [
    "tools/muon_layout/sketched_stagger.py",
    "tools/muon_layout/sketched-stagger-config.json",
    "tools/muon_layout/test_sketched_stagger.py"
  ],
  "task": "ImplementupdatedPR90comment6290378667 latest12:12:08 sketch asnewisolatedunsignedprototype: keepB1evencoilplaneR5.2, moveB1oddintercoilinwardprovisionallyR4.63 (notoldoutward5.75, notblockedcoil-plane4.05), deriveoddwidthfor0.1degfull-depthangularoverlapwith30mmborder. Fixed500mmdepth,50mmcoil/support/HCALmargins,20mmphysicalstaggerneighbor,20mmnominalseams,4mmaxzseedandexistingusefularea/zpolicy. SysArchSS-A1 assessesactualHCALservicesegressR4.3jacket.025; coordinateearly, radius4.63 leaves55mmradialmarginabove4.325 but mustverifywholegeometry. R4.60maybeonlyclearancediagnostic; recordanyfinalradiuschoicebeforefrozenfinalconstruction. B2phase+7.5deg (half15degfacetpitch) withsameR6.7, widths/zlimits; freshallchangedB1/B2packing aroundfixedcoils/all484supports. Endcapsfixedunlessrootupdatesassignmentfollowinguserclarification. B3current432objectsandendcaps192retainvalueequal, magneticmaps/inputs/HCAL/framefixed. ReusephysicalhelperkernelbutnooldcertificatesforchangedB1/B2; cachekeyactualradius+phase+shape+configs,uncachedactualorientationcoilproofs andfullallpanelpairchecks,negativecontrols/determinism. Do notrequirecountreductionorretuneforgeometricperformance; reportcount/families/cuts/gainloss honestly. APIbuild(baseline,config)->geometry,controls;CLI--geometry/--config/--output,defaultnewdated docs/validation/DES-040/sketched-stagger-2026-10-20/candidate;scratchdevoutput/private/tmp/pr90-SS-M1-*. Ownonly3newfiles. Rootownswrappers/native/OBJ/maps/figures/docs/records. BeforeimplementreadrootdirtyDESpreconstructioncontract(whichalreadyexists); scientificbaselinepinnedtoa12. Buildfromcurrent8884aebhash input; focusmeaningfulpositive/adversechecks,no broadACTS/fieldsimulation,shareddeps,otherrepoedits,Gitcommits,nestedagentsorexternalmessages. Sendearlygeometryrecipe/constraintsthenfreeze-ready3files/tests/checksummary. No engineeringapproval.",
  "deliverable": "Threeownednewsource/config/testfiles deterministicfreshB1/B2prototypegeneration plusactualfocusedchecks/results/limitations.",
  "completion": "Physicalfull-volumeconstraints/IDs/fixed-objectidentitypass; freshchangedpanelproofsandnegativecontrolsverified, updatedsketchandB2phaseimplementedorspecificphysicalblockerreported."
}
```

## Execution through source/artifact freeze

SS-A1 and SS-M1 were dispatched as fresh generic contexts with the full saved role mandate/contract after these assignments were recorded. No native role-profile loading is claimed. SS-A1 delivered a pinned read-only SysArch assessment and20-source portable checker. SS-M1 owned only its three new source/config/test files and returned936 panels,312 fresh changed-panel proofs and9 passing tests; no child commit, native run or dependency change occurred.

The coordinator reconciled source services: the knownR4.325 bound is DES034 ECAL water-egress reservation, not installedHCAL material or complete externalHCAL routing. R4.63 lies in the sufficient(4.625,4.645246881422)m interval with55mm service-bound and35.33094mm neighbor margin. B2 hardware requires48 more chambers. Endcaps/B3/maps/frame stay fixed. Retained native entranceR4.35 is safe for the finalR4.63 choice; the R4.60 diagnostic has an inside-start witness.

Source freeze65cf2741bd697ddb8c4022a751f275b41f63241e includes construction, wrappers, config/tests, design contract and journal. Root reran9unittests (6.505s) and compiled the3wrappers. Final generator and native/export wrappers executed from this freeze; wrapper guards match source bytes to Git. Geometry SHA2567b2b0de109a5ec4a908e4f91a05e9caf9bdedfa6141b09d7c82a98b56e7cfc02. Root generated new candidate,4nativeOBJ bundles/2ZIPs, inventories, finite XY/longitudinal plots and bounded native/geometric results in sketched-stagger-2026-10-20. Figures were visually inspected. All709 prior declared scientific source/evidence files remain byte-exact.

ACTS Spack preflight returned warningexit2 for changed setup/lock fingerprints; user warned before dependent work. Fresh activation verified ci-dependencies. An initial acts import before setting installed python/setup.sh failed; corrected setup imports successfully. Python3.14.5,NumPy2.5.4,Matplotlib3.11.2 and all3retained native/core SHA256s were verified. Restricted sysctl warnings were nonfatal. No shared rebuild/install or mutation was used.

Generator passes437580panelpairs,312freshuncachedcoil audits and484supports per changed panel;9focused tests include adversarial/deterministic controls. SysArch root replay with finalcandidate passes. Native1024zero tracks allcomplete/nooutlineorborder mismatch;256curved smoke has197complete/59fieldmasked, withallrows retained. Newfull4pi iid65536/seed40088 three-stationborder57.7698→59.0866%,5608gain/4745lose; no material/response/reconstruction claim. Middle-wheel uniformeta3 remains UNMET. Actual per-track chord/spacing distributions and component controls prevent a blanket improvement or constant-lever-arm claim.

## SS-P1 before dispatch

Artifact freeze11ec9bb670bca2b882929d1d2b4ef7d9da534da6 precedes this separate fresh-context PhysVal assessment. Root retains publication ownership.

```json
{
  "id": "SS-P1",
  "role": "PhysVal",
  "input_revision": "11ec9bb670bca2b882929d1d2b4ef7d9da534da6",
  "inputs": [
    "docs/validation/DES-040/sketched-stagger-2026-10-20/README.md",
    "docs/validation/DES-040/sketched-stagger-2026-10-20/candidate/geometry.json",
    "docs/validation/DES-040/sketched-stagger-2026-10-20/candidate/geometry-controls.json",
    "docs/validation/DES-040/sketched-stagger-2026-10-20/artifacts.json",
    "docs/validation/DES-040/sketched-stagger-2026-10-20/native-validation/validation.json",
    "docs/validation/DES-040/sketched-stagger-2026-10-20/native-validation/full-sphere-inputs-and-distances.npz",
    "docs/validation/DES-040/sketched-stagger-2026-10-20/views/views.json",
    "docs/validation/DES-040/sketched-stagger-2026-10-20/interface-check.json",
    "docs/validation/DES-040/sketched-stagger-2026-10-20/unchanged-evidence.json",
    "docs/validation/DES-040/sketched-stagger-2026-10-20/inputs/source-manifest.json",
    "tools/muon_layout/sketched_stagger.py",
    "tools/muon_layout/sketched-stagger-config.json",
    "tools/muon_layout/sketched_validation.py",
    "tools/muon_layout/sketched_artifacts.py",
    "tools/muon_layout/sketched_views.py",
    "tools/muon_layout/geometry.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Independently assess the exact final frozen updated-sketch candidate/artifacts and scientific README at 11ec9bb. Read pinned files, never dirty source as evidence. B1evenR5.2/oddR4.63 inward, B2phase7.5 barrel only; fixedB3/endcaps/maps/frame. Check source/config/field identities;936counts/15barrelfamilies;312changed freshproofs/all484supports and437580actualpairs with independent source geometry checks/adversecontrols as feasible; actual finite chambers/support/HCAL-service distinction, knownECAL waterjacket55mm but completeexternalHCALrouting unqualified; map/world and entire entrance margins, diagnosticR4.60. Independently reproduce primary full4pi geometry counts, pairedgains/losses/componentcontrols/spacing/lossclasses from actual936/888prisms and retained65536iid bank(seed40088), using independently implemented finite full-depth ray mathematics rather than merely reading reported counters. Check NPZ directions/commoncohort, mask/class exhaustiveness and samplingSE; no false constantleverarm or momentum/reconstruction claim. Check zero-field native event masks/finiteface membership vs analytic1024rows includingborder, curvedstatuses197complete/59masks andall256retained. Validate native corners/OBJ/MTL/ZIP/inventory identity and actualSVG/figure source geometry plus inputarchive20blobs and709prior identities. Reuse pinned helper mathematics only while stating independence limits; do not claim newnative engine execution. No shareddependency/native fullsimulation/field solve needed; no physical/source/artifact edits, commits, nestedagents or externalmessages. Ownscratchonly /private/tmp/pr90-SS-P1-*. Return earlymaterialfindings then portablechecker/report/results with exacttarget hashes/commands/checks. Aim bounded relevant checks, avoid broad historical reruns. No human acceptance. Root owns reconciliation/publication.",
  "deliverable": "Separate exact-artifact PhysVal report, portable pinned checker and actual structured result in scratch, identifying material findings and limits.",
  "completion": "Primary claims independently reproduced or concrete correction identified; actualartifact boundaries and adverse tradeoffs assessed without signoff."
}
```

SS-P1 reproduced primary rays/SAT/spacing and found a minor stale global-limit sentence in validation JSON, inherited from the old central-only wrapper. Root corrects only its scope string and the future source string; JSON metadata_amendment preserves original11ec9bb reportSHA, actual65cf274 execution source and a canonical hash of all unchanged scientific fields. Raw native/ray/geometry/OBJ/figure bytes are unchanged. No numerical rerun is warranted for this label correction. Exact amendment review follows the committed change.

## SS-P2 before dispatch

String-only scope amendment committed before follow-up assessment.

```json
{
  "id": "SS-P2",
  "role": "PhysVal",
  "input_revision": "1d9a49fee5651e41855bd5ad6fdb6adc475b0407",
  "inputs": [
    "docs/validation/DES-040/sketched-stagger-2026-10-20/README.md",
    "docs/validation/DES-040/sketched-stagger-2026-10-20/native-validation/validation.json",
    "tools/muon_layout/sketched_validation.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Bounded follow-up to independent SS-P1 assessment of original11ec9bb670bca2b882929d1d2b4ef7d9da534da6. Assess exact1d9a49fee5651e41855bd5ad6fdb6adc475b0407 scope-label amendment: compare source validation module and validationJSON against original11ec9bb, confirm only global limits sentence and explicit metadata_amendment changed, all scientific fields equal with canonicalhash and originalreportSHA correct. Retained execution source65cf274 remains factual; future source change string-only, no new execution implied. Verify raw geometry/NPZ/nativeevents/OBJ/figures and all other scientific files value/byte-identical to11ec9bb. README scope clarification correct, no newphysics needed. Use exactGitobjects only, repo read-only; scratch /private/tmp/pr90-SS-P1-* only. No rerun whole numerical/native scan or dependencies, commits, nestedagents/externalmessages. Return portable metadata-amendment checker/report/JSON or same finalreport preciseaddendum; note originalstale sentence nowresolved. Originalrolemandate remainsfullyapplicable; noengineeringacceptance.",
  "deliverable": "Exact-commit metadata correction addendum with actual checks/hashes and unchanged-science evidence.",
  "completion": "Scope-label finding resolved without altered scientific results or false source/acquisition claim."
}
```

## Independent assessment reconciliation

SS-P1 exact11ec9bb independently reproduces all primary rays/paireduncertainties/componentcontrols/lossclasses/spacing,437580panels pairs,151008changed-panel/support comparisons, nativefiniteevents/corners,4OBJexports/ZIPs/inventories/SVG,20sourcearchiveblobs and709prioridentities. Coil-distance helper reproduction is explicitly not independent coil mathematics. Final normalized-edge checkerSHA25627bbd537db22348598ad796c63a911d8cbd7f2ead6545761878867731ccc4fd6 passes in60.252s in independent systemPython3.14.6/NumPy2.5.1; prior3d6checker is superseded. Parser-only initial curved-depth/input-header fixes and unit normalization are documented in reviewerreport; no sourcephysics/rawartifact/tolerance requirement changed.

SS-P2 exact1d9a49fee5651e41855bd5ad6fdb6adc475b0407 verifies the scope-label correction and resolvesF1: all80other dated artifactfiles unchanged, scientificJSON canonicalhash23af330273597f01e3643f8470e5e1a5903178c7b2fcc46e6a0b138d2783776b equal; actual65cf274 executed-source identity remains correct. Root standard-library amendment replay also passes. No newfield/native scan for this metadata-only correction. No engineeringapproval is inferred.

Coordinator final27bbd537 portablechecker replay passes at exact11ec9bb in59.731s; finalresult/log retained underreview/coordinator-*. Earlier intermediate3d6replay also exited0 but is not the publishedfinalchecker. Root validators pass199sessionrecords,69tasks/38documents/21reviewrounds and8roles/3skills. Usage/site checks retain210disjoint historicalobservedturns/624299405tokens; this task has no exactcounter observation.

## Publication and closeout

Normalpush publishes reviewedscience/reviewheadec575d2e41e95e6b3ba059932a222fc1ac379b62. PR90title is “Muon System: refine wheels and stagger barrel stations”; bodyrewrittenaroundnewcurrent936candidate and immutable11ec9bbdownloads/ec575d2e41e95e6b3ba059932a222fc1ac379b62reviewlinks, keeping historical888/outward936controlsdistinct. Reviewerreply6291082626 postsupdatedsketch/OBJ/results andexplicitB2-onlyinterpretation. Purpose-builtGitHubreadback confirmsremotehead/title/body/reply; bodyandreply matchsubmittedfiles exactly (apartfromEOFwhitespace). No newreviewers/commentedits orhumanendcapscopeanswerarrivedbeforepublication.

Readback at2026-10-20T12:42:14Z: CIbuildIN_PROGRESS,token-siteSUCCESS,deploySKIPPED. No merge/forcepush/signoff/productionintegration orshareddependencychange. Projecttask/DES040reports/PR90snapshot updated in samePR. Record-onlycloseout follows; recordedpublishedheadis the observedscientific/reviewhead beforethatcloseout, not a self-referencingclaim about itsfuturecommit. Exacttokenusage remainsunavailable; summaryhas199sessions/210disjointobservedturns and624299405historicalobservedtokens. Newtask/root/childusage ismissing,notzero.

Final closeout validation:199pairedsession records (194closed),69tasks/38documents/21reviewrounds,8roleprofiles/3workflow skills, tokenvalidate/build andlocalignoredsitepreview allpass. Observedusagecountersremainunchanged andmissingcurrenttaskcoverageisexplicit. gitdiffwhitespacegate passes beforeeachcommit.
