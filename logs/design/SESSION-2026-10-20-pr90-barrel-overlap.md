# PR90 outer-barrel overlap and longer chambers

User asks addressing newcomment6287612852. Startclean e0fd6ad0e4cd8df96356c00ab35095446c3e9ce3. Sketchvisuallyinspected viahiddenGitHubattachmentbrowser: proposedneighborouterbarrelfacetsangularlyoverlapwithradialstagger. Webopenattachmentfailedcache; browser renderedactualsketch. No imagewasdownloadedorcommitted. Currentendcaps/magnets/framefixed. Exactperturnusage unavailable, notzero.

## BO-M1 before dispatch

```json
{
  "id": "BO-M1",
  "role": "MuonTech",
  "input_revision": "e0fd6ad0e4cd8df96356c00ab35095446c3e9ce3",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "docs/validation/DES-040/refined-wheels-2026-10-20/candidate/geometry.json",
    "tools/muon_layout/wheels.py",
    "tools/muon_layout/layout.py",
    "tools/muon_layout/geometry.py",
    "tools/muon_layout/support.py",
    "tools/muon_layout/refined_wheels.py"
  ],
  "mode": "write",
  "writable_paths": [
    "tools/muon_layout/barrel_overlap.py",
    "tools/muon_layout/barrel-overlap-config.json",
    "tools/muon_layout/test_barrel_overlap.py"
  ],
  "task": "PR90comment6287612852 asks staggered outer-barrel neighboring facets with angular overlap (sketch: even coil-plane chamber stays inner, odd inter-coil facet movesradiallyoutandextendsazimuthally without physicalsolidintersection), andlongerzchambersto reducecount. Fixedmagnets/all484supports/current192endcaps/3stationcenters andbarrelhalfz6.4456/9.2/12.5. AllunsignedisolatedPROTOTYPE; nochamberinternals/engineeringapproval. Currentbarrels1056=168/360/528 withmax2mseedlengthandadaptivecuts. Implement deterministic newcandidate inowned3files only. Preferouterstation3 evenfacetsphi0+30kR8.2unchanged, oddfacetsphi15+30kR8.75(firstdesignchoice0.55moffset); widenoddfacet to overlapneighbor full-depthangularcoveragewith30mmborder butcertifywholevolumesclear usingSATandactualcoil/supportprisms. Widthformula derivefrom actualevenactiveangularlimit, oddouterdepthface andsmall0.1degdesign overlap; record anychange/limit fromactualchecks. Approxoddhalfwidth1.34m/outercorner9.10m mapdomainR9.5, so capcandidateallcorners<9.4m andreportenvelopegrowth. Increasemaxbarrelseedinglengthfrom2to4m(theprovisionalcandidate); compare3/6m maybediagnostics ifuseful; do not blindlypicklargest orweaken50mmcoil/supportclearances. Existingpacking recursivelysplitwholequadrectangles aroundcoils/frame, addmaxzseammergingonlyifactualwholevolumecertifies. Keepnominalzextents, keependcapsbyteequal; freshbarrelcoil/support/pairchecks and independentnegativecontrols. C12cachekeymustincludeactualradius/geometryconfig; no reusedcertfrombaseline. SourcewrapperROOTotherscannotmodify. Newoutput docs/validation/DES-040/barrel-overlap-2026-10-20/candidate. API build(baseline,config)->geometry,controls andCLI --geometry/--config/--output. Recordbefore/aftercounts/actualsizes andalllimitations. InitialDES040contract appendedbyrootbeforeyoustartsource. Own3filesonly;generatedoutputscratch/private/tmp/pr90-BO-M1-* duringdevelopment. No editsotherrepo paths, dependencies,sharedACTS, nestedagents, Gitcommits, externalmessages. Provideearlyrecipe thenfinishfocusedpositive/adversetests. Rootowns nativeexport/coverage/plots/runtimes/docs.",
  "deliverable": "3ownedsource/config/testfiles forouterangularoverlap andlongerzpacking, actualphysicalchecks/sourcehashes andboundedauthorreport.",
  "completion": "Actual3Dnonoverlap/50mmconstraints pass; reducedcountanddeclaredangularoverlapquantified oractualobstructionreported, allotherinterfacesretained."
}
```

## BO-A1 before dispatch

```json
{
  "id": "BO-A1",
  "role": "SysArch",
  "input_revision": "e0fd6ad0e4cd8df96356c00ab35095446c3e9ce3",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "docs/validation/DES-040/refined-wheels-2026-10-20/candidate/geometry.json",
    "tools/muon_layout/wheels.py",
    "tools/muon_layout/layout.py",
    "tools/muon_layout/geometry.py",
    "tools/muon_layout/support.py",
    "tools/muon_layout/refined_wheels.py",
    "tools/toroid_prototype/geometry.py",
    "docs/validation/DES-040/refined-wheels-2026-10-20/README.md"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "PR90comment6287612852 asks staggered outer-barrel neighboring facets with angular overlap (sketch: even coil-plane chamber stays inner, odd inter-coil facet movesradiallyoutandextendsazimuthally without physicalsolidintersection), andlongerzchambersto reducecount. Fixedmagnets/all484supports/current192endcaps/3stationcenters andbarrelhalfz6.4456/9.2/12.5. AllunsignedisolatedPROTOTYPE; nochamberinternals/engineeringapproval. Currentbarrels1056=168/360/528 withmax2mseedlengthandadaptivecuts. Independently assessouterfacetstagger+longerchambers: deriveexactSATseparation/20mmphysicalneighborclearance and angular-full-depthgain vsactualwidth/30mmborder. Source24facets phase0,depth.5,R3=8.2; oddfreebetweenBTplanes movesouttrialR8.75, evenunchanged. Exactvolumecoil/frame interfacesoverwholezrequired; checkradialenvelope<9.4fixedmapR9.5, currentworld9.1canresizeworldonlyifneeded withoutfieldrecalc. Preserve all192currentendcaps inclopeneta3constraint. Examineactualbarrel fragmentation alongz; suggestlongercassette4mmaxseedcandidate vs2mcurrent, identifyhardcoil/frameinterruptionbreaks andcount/familytradeoff, not engineeringqualification. Needprimarysourcednumericinputsandindependentsufficientgapbound/negativewitness for angularoverlapatsameRcolliding. Scratchportablechecker/report --repo/--revision/--output asneeded /private/tmp/pr90-BO-A1-*, norepo/source/dependencyedits, nestedagents, Gitcommits or externalmessages. Coordinateearlyconstraintswithrootand/root/barrel_chambers whenready; do notauthorfinalimplementationor grantapproval.",
  "deliverable": "PinnedSysArchcontribution withexactradial/neighbor/coil/frameconstraints,world/maplimitsandlongztradeoffs, portablefocusedchecks/report.",
  "completion": "Rootcanreconcileproposalwithactualfixedhardwareandmap; nocorneronlyorazimuthalonefalseclearanceclaim."
}
```


## Source and acquired results

Source freeze `7d8c51f304dc79bd187279580b4e1cb5464f7974` follows the preimplementation contract. Eight focused tests pass; selected4m candidate has696 barrels (96/168/432),192unchanged endcaps,888total.264 freshly certified z-seam merges; all484supports fixed and checked per barrel;393828panel pairs clear;696actual-orientation uncached coil audits pass. Barrel dimension families7→13, including96B3 and48B2 widths below0.5m under the inherited area/z policy. Odd B3 radial stagger0.55m, bordered template angular overlap0.1degrees, true finite neighbor gap69.625277mm. Actual max chamber radius9.099797510m leaves0.20249mm within the native9.1m world; this is only a numerical chamber world, not passive material or installation qualification.

Fresh-shell activation used acts_setup.sh, unset ACTS_SPACK_SETUP, setup_spack, then installed acts-nodd Python with task-local MPLCONFIGDIR/XDG_CACHE_HOME. Preflight warns changed setup/lockfile fingerprints; NumPy/Matplotlib and actual baseline/current native construction pass. No shared dependencies changed. Propagator397ca6d59d2798cd5ab53e1faa78bccf8250de6d324d2eafe9be14c39c7a005d; writerf4c9842fd7534b7adb64b086495c25092bc6d1e6022665dfbc621aeeb024ee62; coref4c040fa6c331fca6180dc75589fbc95ec30fc485c2edbefb891fda46cdf7088. All new geometry/artifact/native modules exit0 at source freeze.1024zero-field tracks complete and agree with independent finite prism tests;256curved-smoke rows retain197complete/59field-masked.65536mirrored rows from32768iid central-band directions yield three-station56.6040→69.3878%, border48.2971→61.8225%. No reconstruction/material-response claim.449prior source/evidence files remain byte-exact; magnets/frame/endcaps fixed, uniform middle eta3 remains UNMET.

Actually viewed barrel XY comparison, longitudinal comparison and combined OBJ PNG; common axes/source polygons agree visually. Initial staged whitespace check stopped on one blank EOF in this journal; normalized and passed before commit. Initial session validator rejected draft activity fields; corrected to the required tool/skill schema. Earlier web attachment cache failure was bypassed by rendering the public attachment directly in the browser; no image download or private URL entered in Git.


## BO-P1 before dispatch

```json
{
  "id": "BO-P1",
  "role": "PhysVal",
  "input_revision": "0933e439a69e199fb17e250d792ba35d0feaf9ab",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "tools/muon_layout/barrel_overlap.py",
    "tools/muon_layout/barrel-overlap-config.json",
    "tools/muon_layout/test_barrel_overlap.py",
    "tools/muon_layout/barrel_artifacts.py",
    "tools/muon_layout/barrel_validation.py",
    "tools/muon_layout/barrel_views.py",
    "docs/validation/DES-040/refined-wheels-2026-10-20/candidate/geometry.json",
    "docs/validation/DES-040/barrel-overlap-2026-10-20/README.md",
    "docs/validation/DES-040/barrel-overlap-2026-10-20/candidate/geometry.json",
    "docs/validation/DES-040/barrel-overlap-2026-10-20/candidate/geometry-controls.json",
    "docs/validation/DES-040/barrel-overlap-2026-10-20/artifacts.json",
    "docs/validation/DES-040/barrel-overlap-2026-10-20/native-validation/validation.json",
    "docs/validation/DES-040/barrel-overlap-2026-10-20/views/views.json",
    "docs/validation/DES-040/barrel-overlap-2026-10-20/prior-evidence-identity.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Independently assess exact frozen source and ACTUAL artifacts for PR90 reviewer comment6287612852. Read primary source/geometry/native events before author conclusions. New barrel-only unsigned prototype: Rodd8.75m vs even8.2, widened odd B3 angular overlap,4m max z seed with certified seam merging. Check actual888chambers (696barrel96/168/432 +192unchangedendcaps), 13barrel dimension families vs7, narrow hardware fragments/size policy, correct source/config/provenance identity, full-depth projected overlap vs physical nonintersection including actual z cuts/supports. Check actual native zero1024 and curved256 event rows against finite source and report, retain59fieldmasks; bank65536mirrored from32768iid central eta0..1/fullphi with fixed906320seed, expected geometric56.604\u219269.388%/border48.297\u219261.8225%. Do not mistake for efficiency/material/reconstruction. Inspect final PNGs/SVG/source membership/nativeOBJ/MTL/ZIP counts/corners/hash and 449prior source/evidence blob identities. Native worldR9.1 narrow0.202mm margin is numerical-only; frame/feet extendoutside; allfieldsunchanged no solve. Keepuniformmiddleeta3UNMET. Review only bounded focus; do not rerun broad native/field/performance studies or install dependencies. Portable checker with --repo --revision --output reads pinned git blobs (not dirty sources), NumPy/stdlib okay; scratch output /private/tmp/pr90-BO-P1-check.py/.json/-report.md. No repository edits, source edits, Git commits, external messages, nested agents or shared dependencies. Current dirty journal only has schema capitalization fix outside science and will be closed by root; review exact0933e43 artifact/source bytes. Do not review your own prior implementation (you authored none). Return actual commands/results, material findings with locators and limitations; independent context does not grant human sign-off.",
  "deliverable": "Exact-revision PhysVal report and portable focused actual-artifact checker/results in scratch, substantive scientific findings or bounded no-new-blocker assessment.",
  "completion": "Root can reconcile final geometry/native/OBJ/figures/coverage claims against actual frozen data and preserve unresolved physics/engineering limits."
}
```


## Independent assessment and claim reconciliation

BO-P1 runs a separate NumPy/stdlib checker against exact frozen artifact revision0933e439a69e199fb17e250d792ba35d0feaf9ab. Actual39checks pass across495pinned blobs, including888source volumes/393828pairs,696×484support envelopes, native event pairing, independent finite-rectangle bank, mesh/ZIP/view hashes and449prior blob identities. It does not rerun native transport or the coil distance kernel, and grants no human approval.

The separate paired bank comparison finds6198gained/2009lost outline directions out of32768iid, net+12.783813pp (conditional paired MCSE0.267298pp); border6655gained/2223lost, net+13.525391pp (MCSE0.277673pp). Among outline losses508missB1only,605B1+B3,896B3only, noneB2. Representative zero-based geometric-bank rows13/163 cross relocated zseams and no longer fit both depth faces in the same cassette. This explains local proxy losses; it does not establish reconstruction loss. Root adds this combined stagger/z-packing tradeoff prominently to README and PR text instead of claiming pointwise improvement. No source, geometry, native data, maps, OBJ or plots change after review target. Added separate author seed-diagnostics method documents signed-mu seed40090/16384bank, distinct from final seed906320/32768iid mirroredbank.

Initial BO-P1 preparer rejected a directory input; listed regular pinned files and prepared successfully before dispatch. Reviewer checker-only2D-cross/NumPy compatibility, nonconvexcoil centroid orientation and1e-10drawing rounding checks were corrected within scratch; no repository scientific gate was weakened. Root draft sessioncheck-status capitalization was corrected, and session/project/token/workflow validators then pass. Token preview uses210disjoint historical turns/624299405observedtokens; this root/specialist turn has no exact client counters and adds no usage observation.


## Publication and closeout

Frozen source7d8c51f304dc79bd187279580b4e1cb5464f7974; actual artifact target0933e439a69e199fb17e250d792ba35d0feaf9ab; prepared-contract/schema journalc094335; final independent assessment/claim clarificationb34bb375524bb1e8591e9a5adf9c2c0b3d1d8ab0. Normal pushes only. PR90 title now `Muon System: refine wheels and stagger longer barrel chambers`; body rewritten around888currentoutlines with currentOBJ/XY/longitudinal/inventory/report links, explicit13vs7barrelfamilies andpairedlocal-loss caveat, retained historical endcap/field/spacing links anduniformmiddleeta3UNMET. Reply https://github.com/asalzburger/nodd/pull/90#issuecomment-6288205162 posted using exact bodyfile. Metadata/reply readback verifiespublishedhead/title/body andcommentID. No reviewer reply was overwritten; prewrite PRbody matched the task-start body. No merge or human approval.

GitHub at2026-10-20T09:49:31Z: buildPENDING, token-siteSUCCESS, deploySKIPPED. Local geometry/unit/native/artifact/independent/project/session/token/workflow checks pass. Record-onlycloseout follows. Current root/specialist per-turn counters unavailable, usageempty/notzero; validated historical dashboard subtotal remains210disjointturns/624299405observedtokens. The JSON lists changedfiles and all precloseout resultcommits; the final record-only commit cannot include its own SHA. Remaining human design choices: mechanical feasibility of staggered/long/narrow chambers and13families, local same-cassette coverage tradeoffs, chamber internals/material/response/reconstruction, and the fixed ECTmiddleeta3obstruction. No additional permission or approval was required for this requested prototype follow-up.
