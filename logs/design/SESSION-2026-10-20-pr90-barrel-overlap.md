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
