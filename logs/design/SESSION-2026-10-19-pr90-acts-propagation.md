# SESSION-2026-10-19-pr90-acts-propagation — PR90 ACTS chamber boundary propagation and momentum coverage

## Scope and evidence

State collection method, available context, limitations, related IDs and starting
revision. Identify uncommitted user changes present before work.

## Selected conversation

Attribute requests to the user and outcomes to the assistant. Mark exact quotes
and paraphrases explicitly. Include corrections and changes in direction.
Exclude private model state, confidential content, and irrelevant system context.

## Decisions and outcomes

State rationale, alternatives, consequences and what remains unresolved. Never
convert implementation authorization into human design sign-off.

## Commands and validation

Record relevant commands, actual exits/results, failed attempts and remedies.
Distinguish structural checks from detector acceptance.

## Changes and revision links

List changed files or refer to the paired JSON inventory. Result commits are
recorded only once they exist; Git history locates this record's enclosing commit.

## Token accounting

Record the client-provided per-turn usage source and import command, or state why
exact counters are unavailable. Report observed input/output sums and missing
coverage from `session_log.py summary`; empty usage means unknown, not zero.
Never copy raw client archives or private model state. Do not duplicate turns
across tasks or add cached/reasoning subsets to the input/output totals.

## Follow-up

List remaining work, missing measurements and any human review needed.

## Assignment A1 recorded before dispatch

```json
{
  "input_revision": "b3ff6a3b2ae111251fbc126d5ad489114877c3c7",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "docs/validation/DES-040/geometry.json",
    "docs/validation/DES-040/results.json",
    "tools/module_layout/acts_validate.py",
    "tools/acts_binding_probe/probe.py",
    "docs/validation/MUON-001/results.md",
    "tools/toroid_prototype/map.py",
    "docs/validation/DES-039/map-metadata.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "id": "A1",
  "role": "SoftEng",
  "task": "Read-only ACTS API feasibility for PR90 reviewer6268359299/6268670798: real ACTS TrackingGeometry of all1560finite chamber prisms and native EigenStepper/Navigator propagation in joint field map; record actual boundary global hits, count only2large faces not4sides. Investigate verified local ACTS checkout /Users/salzburg/Documents/work/dev/acts-nodd at555c66e71d0639665c2fa3d5574a0fe7f3f62cde with unrelated dirty files (preserve all), installed include/library paths. Root is re-verifying acts-spack environment after warningchangedsetup/lock and no DD4hep/Geant4 fullsources; do not run dependent builds/runtime until rootconfirms. Inspect modern C++/Python geometry APIs, dense-volume/BVH or Gen3 per-chamber leaf/portal navigation, GenericCuboid/Trapezoid boundary orientation and custom MagneticFieldProvider. Prior module_layout records gen3singleleaf curved candidate loss; avoidassumingthatapproachworks. Recommend smallest robust native C++ prototype built outside shared ACTS tree, read sources only. No nestedagents/externalmessages/repo writes. Scratch /private/tmp/pr90-acts-A1-*.",
  "deliverable": "Cited exact installed/source API recipe for physical envelope TrackingGeometry+finite boundary hit recorder+3Dfield provider and navigation correctness controls; identify limitations early.",
  "completion": "Actionable verified source/API findings, preserve ACTS dirty tree, no claimed runtime pass without execution."
}
```

## Assignment P1 recorded before dispatch

```json
{
  "input_revision": "b3ff6a3b2ae111251fbc126d5ad489114877c3c7",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "docs/validation/DES-040/geometry.json",
    "docs/validation/DES-040/results.json",
    "tools/module_layout/acts_validate.py",
    "tools/acts_binding_probe/probe.py",
    "docs/validation/MUON-001/results.md",
    "tools/toroid_prototype/map.py",
    "docs/validation/DES-039/map-metadata.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "id": "P1",
  "role": "PhysVal",
  "task": "Read-only design/validation criteria for reviewer PR90 actual ACTS field+chamber propagation, boundary hitXY/RZ and phi-eta coverage at muonsystem entrance, minimum momentum through1TeV, >5segments. Determine correct min5GeVIP vs localafterHCAL interpretation fromMUON001; propose honest primary vacuumgeometry benchmark versus material qualifications withoutinventing eta-dependent eloss. Define2largefaces/chamber as segmentproxies, sidesrecordedbutexcluded, duplicate/reentry/pairedstation counters, denominators including failures/nonentrants, charge andlow/mid/1TeV samples, entranceclosedcylinder withcaps versusbarrel-only cylinder meaning andsampling. Preservefixedgeometry/map. Reviewfield interpolation masks/out-of-map policy andcontrols (zero/constant field analytic, exactfiniteboundary, charge reversal, maxstep/tolerance convergence, navigator misses) needactualACTS intersectionsnotpolylinepostprocess. Laterimmutableimplementationreview separately. No repo edits/nestedagents/externalmessages. Scratch /private/tmp/pr90-acts-P1-*.",
  "deliverable": "Bounded observable/method proposal and adversarial tests, source locators and threshold semantics; not a sign-off.",
  "completion": "Concrete faithful interpretation of >5largeface segments and representative entrance maps, numerical/failure scope explicit, no unmeasured response claims."
}
```

## Assignment S1 recorded before dispatch

```json
{
  "id": "S1",
  "role": "SoftEng",
  "input_revision": "a4d3788f89a79af8b31ff694e811b543af792d3c",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "docs/validation/DES-040/geometry.json",
    "docs/validation/DES-039/map-metadata.json",
    "tools/toroid_prototype/map.py",
    "docs/validation/MUON-001/results.md"
  ],
  "mode": "write",
  "writable_paths": [
    "tools/muon_layout/acts/CMakeLists.txt",
    "tools/muon_layout/acts/propagate.cpp",
    "tools/muon_layout/acts/README-engine.md"
  ],
  "task": "Implement native C++ ACTS chamber-boundary propagation engine against EXISTING installed ActsCore, no sharedACTS edits/build/install. Read A1 source findings. Preserve exact1560JSONprisms asnativeTrackingVolumes(GenericCuboid8vertices), actual6finiteportals each, worldcylinderR9.1m halfZ11.5m, fulluniqueIDs despite8bitvolumefield viavolume2/layer(panel+1) andboundaryIDs. Native EigenStepper+Navigator and surface-reached actor hits; no postprocessedpolylineasprimary. Local stateful position-refresh navpolicy and conservative spatialportal index allowed: compareindexed/exhaustive controls, tightmaxsteps; disclose pitfalls. Include allsidefaces raw but2largefaceflags onlysegments. Geometry/magnet fixed; vacuum no matter. InstalledcriticalheadersmatchACTS555c66e71d0639665c2fa3d5574a0fe7f3f62cde andlibActsCorehashc540a14dabe6af18d2264823d816a326b6d96d925884cccb6ecc74c52a7e1066; dirtyACTSfilespreserve. Root verified Spackactivationenv andsetup/lockfreshhash, no source install, willbuildengine/task-localruntimeverify. No dependenciesinstall/sourceedits; rootownsprepare/analyze/plot. INPUT/OUTPUT CONTRACT BELOW. No nestedagents/externalmessages. Implementfastenoughfullscan~100krays; sendAPI/compileissuesearly.\nI/O agreed with root (metres/Tesla/GeV externally; ACTS mm/Tconverted internally):\n--geometry path (text whitespace): first unsigned N; each row id(no whitespace,slashesallowed) station depth_m origin3 basis9(ROWMAJOR) vertices8(localx,y4CCW). Engine computes exact8cornerworld points.\n--map path binary: 8 ASCIIbytes \"NODDMAP1\"; uint64LE nr,nz,nphi; float64LE r_m[nr], z_m[nz],phi_deg[nphi]; float32LE B[nr*nz*nphi*3] Corder(r,z,phi,Br/Bphi/Bz); uint8valid[nr*nz*nphi]. Exact trilinearcyl12fold%30 thenCartrotation; ANYmaskedcorner=>ACTSResultfailure; nozero/extrap. --field map(default)/zero/constant with --bz T supportanalyticcontrols.\n--tracks path: firstN; rows track_id p_GeV charge x_m y_m z_m dx dy dz (directionsunit). Seed/generatedgridhandledroot.\n--output-dir path write hits.csv,tracks.csv,geometry.csv,metadata.json (simplemanualjson okaynojsondep).\nhits.csv: track_id,sequence,panel_index,face_index,is_large,geometry_id,x_m,y_m,z_m,path_m,dx,dy,dz (panel_index0based; facesourceorder0..5; enginecomputeis_largebyabsnormaldotprism.normal\u22481). Record actualACTScurrentSurface actorpositions only. No world/virtualentrancefacesasmuonhits.\ntracks.csv: track_id,status,error,path_m,steps,x_m,y_m,z_m,field_queries; externalCapturemustretainpartialhits/stepsonpropagationfailure. statuses: completed,field_masked,outside_map,navigation_error,step_limit,path_limit,returned_to_entrance ifimplemented. Neverthrowouttrack;outputexactinputN rows, nonfinitefailureexplicit.\ngeometry.csv: panel_index,face_index,is_large,geometry_id,cx_m,cy_m,cz_m,nx,ny,nz (actualnativefacecentre+normal foraudit); additionalnativecornerexport/metadata counts useful.\nmetadata.json: ACTSgeometry counts(unique1560chambers+world/9360faces), IDuniqueness,worldbounds,step/tolerance settings/CLI,queryfail counters etc.\n--max-step-m default0.05, --tolerance-m default1e-6 ifACTStolerance unitsmeaning doc; --path-limit-m100; --max-steps20000; --policy indexed(default)/exhaustive (same refreshedfiniteportalswithoutspatialindex).\n--inspect-only no tracks buildsandexportsgeometry, verifiescounts/includescorners; --query-field inputpointsfile (N; xyz_m rows) outputfield.csv point_index,status,Bx_T,By_T,Bz_T for numericreadercontrols (skipgeom/tracks whenquerymode).\nOptional entrance abort at inward recrossing closedcylR4.35/H6.5 usingnativevirtualsurfaces or accuratelyboundedactor check; otherwisefieldfail catches return andreportlimit. Primarylaunchpointsare10umoutside entrance so no initialboundary ambiguity.\nNativepolicy candidateball/AABBindex mustconservativelycovermaxstep plusstepback budget; everyactualpositionchangeinvalidatespolicy, exhaustivecontrolsmandatory. If curvedfiniteboundsstale/unexpectedmiss discussrootbeforebroadscan. No hand-fabricated hits.\n",
  "deliverable": "CMake/onecpp/readme engine with portableCLI and nativefieldprovider plus geometry/hit/track inspectors; ROOT willcompile/runcontrols. Scratch onlytemporarysmokes asneeded, ownedrepo3files only.",
  "completion": "EnginecompilesagainstinstalledActsCore or preciseAPIissuesreported; actual ACTSnativesurface-intersections, stablefaceIDs, strictmaplookupandrecordedfailures, step/path budgets and spatial/exhaustive modecontrols. No engineering/responseclaim."
}
```

## Assignment S2 recorded before dispatch

```json
{
  "id": "S2",
  "role": "SoftEng",
  "input_revision": "a4d3788f89a79af8b31ff694e811b543af792d3c",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "docs/validation/DES-040/geometry.json",
    "docs/validation/DES-040/results.md"
  ],
  "mode": "write",
  "writable_paths": [
    "tools/muon_layout/acts/draw.py",
    "docs/validation/DES-040/acts-propagation/hit-positions.png",
    "docs/validation/DES-040/acts-propagation/entrance-segments.png",
    "docs/validation/DES-040/acts-propagation/entrance-paired-stations.png",
    "docs/validation/DES-040/acts-propagation/momentum-coverage.png"
  ],
  "task": "Create/read-onlyrenderACTS reviewerplots, onlyowneddraw.pyand4PNGs. Root/S1buildnativeACTSengineandanalysis; you MUSTplotactualreturnedACTShits, nevergenerate/inventhits orretunegeometry. Input API: draw(workdir, outputdir) loads tracks.npz,hits.npz,summary.json. tracks.npz: arrays track_id (rowindex),momentum_GeV,charge,sample(0phi-etamap,1iidfullsphere),eta_bin,phi_bin,eta_pos,phi_pos_deg,outer_unique_faces,active_unique_faces,outer_paired_stations,active_paired_stations,incomplete(bool),eta_edges,phi_edges_deg. Extraarrayspossibleignore. hits.npz: track_id,panel_index,station,face_index,is_large,active,x_m,y_m,z_m,path_m. summary.json['configuration'] containsplot_momentum_GeV[2.65,100,1000], fullcaseparams; configrootuncommittedtools/muon_layout/acts/config.json method alreadygovernedcommittedDES040. Alllocalp; initialentranceclosedR4.35/H6.5 radialdir,noIPtransport/matter. Reports\u22656uniqueouterlargefaces,andpaired3stationsseparate; failuresunknownkeptdenom. hit-positions.png 3rows(low/mid/1TeV)\u00d72colsXY/signedZ-r projections actualhits coloredstation, sidesgrey/separatemarker; bothchargeslabelled, noefficiencyfromdensity. entrance-segments.png 2charges\u00d73momenta phi0..360/eta\u22123..3 segmentmultiplicity 0..6(6+ bin) fromgrid sample0 rows; hatch/markincompleteevents, evenifthresholdalreadyproven keepvisible. Maponejitteredray/cell notconvergedefficiency; unknownbefore6notzeroinefficiency. entrance-paired-stations.png sameforactive_paired_stations0..3, physical30mmborderproxy explicit. momentum-coverage.png forsample1 fullsphere all5p/bothq lower/upperavailabilitybands: provenpasslower=sum(pass)/N, upper=(sum(pass)+sum(incomplete&~pass))/N; >5largeface and3pairedstationouter/activecurves informative; bandsnotstatCI. Goodtitlesunitslegendsreadablemargin; noAPIimplementationdetailinplotexceptneededscientificscope. UsepureMatplotlibinstalledPythonwithoutACTS, noSpackdependency. Frozendatawillarrivelater; preparecode/fixturesinscratch, NOTrepresentfixturesasfinal. Norepootheredits/nestedagents/externalmessages.",
  "deliverable": "Parameterizeddraw.py API+CLI andfourvisuallyinspectedfinaldataPNGs; reportsource/runtime/hashesandlimits.",
  "completion": "FourclearreviewplotsderivedfromrootactualACTSarrays; nofakeprojection/counter/denominators, visiblecharge/momentum/failure/localvacuumdefinitions."
}
```

## User-directed prerequisite: rebuild ACTS (2026-10-19)

User requested rebuilding acts-nodd against the updated Spack dependencies before resuming muon work. The external source/build/install operations are now explicitly authorized. Existing dirty ACTS source file hashes were captured in task-local scratch before the rebuild; preserve all edits. Preflight again reports changed setup/lock and absent staged DD4hep/Geant4 full sources; installed packages and the user's ACTS source checkout are the required capabilities here.

Assignment A2 (SoftEng, read-only, same source555c66e71d0639665c2fa3d5574a0fe7f3f62cde plus preserved dirty source): inspect ACTS current CMake/preset versus updated Spack environment/cache for stale explicit dependency version/path pins. Inputs are the user setup script, ACTS presets and external CMake cache. No source/build/install modifications or dependency installs; scratch /private/tmp/pr90-acts-A2-*. Deliver precise likely compatibility hazards and verification recommendations. Completion is a read-only audit, never a claimed runtime pass. Root separately executes the authorized build.

### Rebuild observations (in progress)

- `acts build acts-nodd 8` recreated its prescribed Python venv, then configuration failed on stale EXPAT2.8.5 cached paths; current Geant4 requires EXPAT2.9.0. Full log kept in task scratch.
- Saved the existing cache and ran `cmake --fresh` with the same github-ci preset, RelWithDebInfo, ODD, C++20, install prefix and Python executable. Fresh configure completed; full 8-worker install build is in progress. No dependency requirements or source tests were relaxed.
- Updated installed environment observed: DD4hep1.38/3yd4hz3, Geant4 11.4.3/wfg55xi, Eigen5.0.1/4hly7in, Boost1.90.0/yi2vs77, vecmem1.28.0/rs6hy7v and Python3.14.5/t4h4oe7.
- A2 separately audited caches and the Spack view: both missing vecmem1.27 paths and existing stale EXPAT/ROOT/Python absolute paths required fresh resolution. Fresh cache resolves current prefixes. The CLHEP warning compares an alias to the same resolved installation. A2 performed no runtime/tests or ACTS modifications. Scratch report SHA2568caf6b2b0e0e79a0918c91188153f88ebfadd5e6c6d2652546b1b9c8cd55c6e9.
- Existing15dirty source files were hash-captured before the build and remain unchanged at the intermediate check. Final preservation and runtime/test results are pending.

Rebuild prerequisite completed successfully: full install,385C++ tests,3integration suites,28Python passes/2optional-input skips, installed runtime imports and12Geant4 dataset presence checks. All15pre-existing source edits preserved. Evidence: docs/validation/DES-040/acts-propagation/rebuild.md and rebuild.json. Muon work resumes against rebuilt libActsCore SHA256f4c040fa6c331fca6180dc75589fbc95ec30fc485c2edbefb891fda46cdf7088.

Finite-portal adverse control after rebuild: normal aggregate package configuration/build nowpasses. Inspect reports1561nativevolumes/9360uniquechamberfaces/3120largefaces. Initial1umtargeting aborts finiteportalassert; tightened10nmtargeting completes butrecords onlyexitwhereanalytichelixtwoboundariesrequired. Preserved negativecontrol; DES040 face-audit amendment drafted BEFORE new policy implementation. S1 extension: same three owned engine files and same SoftEng mandate; implement explicit surface-audit primary mode retaining finite-portal negative control, native infinite-support plane roots with finite face ownership/coplanar fanout, no manufactured polyline roots. Record actualmode and do not claim validatedportalvolume transitions.

## Assignment S3 recorded before dispatch

```json
{
  "id": "S3",
  "role": "SoftEng",
  "input_revision": "faa544a1fa424906c68b27bcf37db181d783b84e",
  "inputs": [
    "tools/muon_layout/acts/prepare.py",
    "tools/muon_layout/acts/analyze.py",
    "tools/muon_layout/acts/config.json",
    "docs/design/DES-040-muon-chambers-frame.md"
  ],
  "mode": "write",
  "writable_paths": [
    "tools/muon_layout/acts/controls.py",
    "docs/validation/DES-040/acts-propagation/controls.json"
  ],
  "task": "Extend same fully passed SoftEng mandate: implement and execute reproducible native ACTS field/geometry/boundary controls against root/S1 actual engine. No edits to otherfiles. Preserve physicalgeometry/map. S1 changes engine independently; roothandlesproduction/provenance. Nativecontrols detailed in dispatch. No nestedagents/externalmessages/dependencychanges; scratch ignoredreference/cache/pr90-acts controls subdirs.",
  "deliverable": "controls.py runnableCLI --work/--executable/--output and actualcontrols.json with exactcommands/settings/passmetrics; no fakeclaims ifblocked.",
  "completion": "Actual executable controls strictfield parity,finitegeometryIDs/corners,zerofieldexactrayclips,constantfieldhelix qB flips,adversecurvededge2faces,finiteportalnegative retained,indexed/exhaustive,maxstep/tolerance refinements with sequence/counter/status comparisons."
}
```

Initial audit controls retained in controls-initial.json: field4111queries,max1.64e-14Tresidual; native1560prisms/9360faces/corners≤3.7e-15m; zeroB40rayspassed. Tightroot/parallel-side/indexed-exhaustive/refinement controls FAILED; production remainsgated. Source trace identifies lostnativebackstepwhenrefreshdiscardsovershottarget. S1proposed preservingACTSnativecorrection plusconservativecurvatureActorsteplimiter fornoforwardtangentroots; methodamendmentrecordedbeforeimplementation. No tolerance enlargement/assertiondisable orphysicalretuning.

S1native-stepdiagnostic: missed1nmxentryremained3.9936nmahead; configuredsurfaceTolerancewas1nm butindependentNavigatornearLimitdefault100nmdroppedforwardcandidate. DocumentednearLimit0beforenativeoptionfix. No hitorcontroltolerancerelaxation.

Secondgate92ff retained:counts/statuses800refinementagree, coordinatesup90umfail10umgate; grazingamplifiesfewumtrajectorydrift. Unboundedexhaustivesupportsteststallsonghostplaneswhosefinitefaces9.9–18.5maway. DocumentedboundedfullAABBscanversusgridandindependent10pmRK/1pmrefinementBEFOREimplementation. No controlthreshold, physicalgeometryormapchanges.

## Assignment R1 recorded before dispatch

```json
{
  "id": "R1",
  "role": "PhysVal",
  "input_revision": "8ad71821a27c22a88b90ba1b56d732dd449b351c",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "tools/muon_layout/acts",
    "docs/validation/DES-040/acts-propagation/controls.json",
    "docs/validation/DES-040/acts-propagation/rebuild.json",
    "docs/validation/DES-040/geometry.json",
    "docs/validation/DES-039/joint-field.npz"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Separate exact-revision assessment of committed ACTS implementation/method/controls at8ad7182; mainproductionrunongoing, do notclaimresultreviewyet. Apply previouslypassedfullPhysValmandate, no predeterminedfinding. Inspect nativegeometry/field/APIunits/finitefaceaudit correctness, candidatebound+guard+targettolerances, pathologicallimits, counters/reentry/samestationdedup anddenominators/thresholdsemantics; inspectnegativecontrolclaimconsistency. Runboundedread-onlychecks/scratch only. No edits/shareddependencychanges/nestedagents/externalmessages. Laterrootprovidessecondfrozenartifactrevisionforfinalscientificassessment.",
  "deliverable": "Scratch /private/tmp/pr90-acts-R1-review.md/json with exacttargetcommit, actualchecks, concretefindingsorpassandlimitations; finalartifactreviewremainsseparatepending.",
  "completion": "Evidence-basedcode/methodassessment of8ad7182 withoutauthorshipclaimorhumansignoff; sendblockingissuesearly."
}
```

R1target corrected BEFORE dispatch to 85b044d2a5591828efe492a651b8aee11593a42b (onlyrunmergerfingerprintvariablerenameafter8ad7182). Firstnative149kscancompletedall10shards,butmergerguardincorrectlycomparedoverwrittengeometrysettosourcehashdict; correctedat85b044dandrerequestedfreshsamebinaryscanbeforeanalysis. No nativecontrolthresholdorfieldgeometrychange.

R1separatesourceassessmentcaughtpurecontactsbeingincludedinliteralcrossingcounter; fixedandexcludedbeforelarge-facesets, added6contactregression. All11unittests pass. Productiontangent_eventssum0, soresultsunchanged. Originalacquisitioncontrolrecordpreservedascontrols-acquisition.json; postprocessinggateandanalysisrerunwithcounterfix. R1alsoindependentlyvalidated1037newfieldpoints,all1560nativeprismsand3analyticcylinderreturncases. FormalR2artifactassessmentpending.
