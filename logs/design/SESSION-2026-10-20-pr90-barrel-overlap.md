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
