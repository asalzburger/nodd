# SESSION-2026-10-20-pr90-endcap-xy — Three wheel XY cross-sections

User requests addressing new PR90 comment. New substantive comment6285630535 requests x-y crosssectionofthreeendcapwheels; prior6285484312 notes8families improvement. Comment URLs are public; no remote image/private signedlink retained. Start99bb67a6d3a65d4ef6de30ff2def8698b3ed053d, cleanbranchcodex/muon-chamber-layout. CurrentPRhead matches. Existingprototypegeometry, field, OBJ andcoverage remainimmutable; scope addsreproduciblefigureoutputs fromactualfiniteplanes only.

Apply nodd-coordinate and nodd-review-validation with explicitfallbackprofiles; nodepreflight readbeforeusinginstalledplottingPython.

## XY-P1 assignment (before dispatch)

```json
{
  "id": "XY-P1",
  "role": "PhysVal",
  "input_revision": "99bb67a6d3a65d4ef6de30ff2def8698b3ed053d",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "docs/validation/DES-040/wheels-2026-10-20/candidate/geometry.json",
    "tools/muon_layout/draw.py",
    "tools/muon_layout/support.py",
    "tools/toroid_prototype/geometry.py",
    "docs/validation/DES-040/wheels-2026-10-20/README.md"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Bounded independent input/display assessment for new PR90 comment6285630535: add x-y cross-sections of the three endcap wheels. At exact99bb input useactualwheelcentres positivez6.7456,9.5,12.8 and actualsourcefiniteprisms. Root implements new isolated wheels_xy.py and outputs in wheels-2026-10-20/xy-sections. Read-only check source expectations perwheelcounts, positive/negative mirrorview conventions, section_polygon accuracy, actualframe material_parts hollowstock semantics and coil exact zslice method. Need focused independent expected data/checks for root: no projectionsofnonintersectingobjects, commonmetricaxes no cropping, unchanged geometry/field/coverage andprecisionclaim. Root proposes blueendcap polygons, greywarmcoil sections and greyframe actualmaterialcuts, 3panelPNG+SVG and perwheelPNGs, fullsourceIDs/coordinatesprovenance; optional barrelcontext notnecessary. Can suggest accurateefficient analyticwarmcoilcrosssection vs existingrasterhelper (explicit resolution ifraster), no designchanges. Return brief report/JSON and boundedindependentcheck script if useful in /private/tmp/pr90-XY-P1-* only. No repo/dependency/source edits, no ACTS runtime needed, no nestedagents/externalmessages orhumanapproval. Later root willfreezeactualplots andgive exactrevisionfor finalfigurecheck ifneeded; thisassignment reviews pinnedinputs/displaycontract only.",
  "deliverable": "Expectedplane/count/extent/convention checks and meaningful source/visualvalidation plan, with actual independent checks and limitations.",
  "completion": "Root has an independently assessed displaycontract andprimarysource expectations; no physicaldesignchange orapprovalclaim."
}
```

## Drawing and independent input checks

Rootadds isolated tools/muon_layout/wheels_xy.py andnewxy-sections/outputs. Eachwheelplane isderivedfromactualpositive-endmodulecentres;144blueendcapprisms only, common±10m/globalxright,yup/equalaspect. Greywarmcoilsections analyticfromexactroundedrectangledistance+tangent slab, notraster; frame usesactualhollowstockparts ratherthanfilledouterreservations. No geometry/field/OBJ/inventory/nativecoverage byteschanged. ParentREADME addslinkonly; dated202filemanifest staysimmutable anditspriorindexhashreproducible at99bb.

Preflight exit2 flags changedsetup/lock; warned beforedependentwork. Freshsetup activeci-dependencies; installedPythonverified NumPy2.5.4/Matplotlib3.11.2. Onlyplottingused, no ACTSrun/build/source/dependencyedits. Existingrestrictedsysctl andinitialdefaultfontcachewarningsnonfatal; actualdrawrun usesprivate/tmp caches. Rootgenerationcontrols pass150000exactcoilmembershipqueries,144offplanechamberadversecases, negativeendglobalXYidentity. Actualcounts12/108/24chambers,24/48/0coilrectangles,120/96/0stockparts. RootinspectedcompositePNG: commonaxesandlegend/captions legible, allobjects insidebounds.

XY-P1 source99bb independent16,332body/planechecks and2,359,296analyticcoilqueries pass, adverseface/outside/tangentfixtures pass; no blockingfinding. Itassessesinput/displaycontract, notfinalfiguresorengineeringacceptance. Portableinputchecker requestedforretention; finalfigureassessment follows exactcommitfreeze.

Firststagedwhitespacecheck exited2 onMatplotlibSVGtrailingblanks; the batchedcommandsequencecontinuedtocommitd26599c. Thiswasnotyetpushed. CorrectednewgeneratorSVGformattingto stripline-endblankswhilepreservinglinebreaks/pathnumbers andexplicitpathfontmode; ordinaryfollowupcommitbeforereview/publication, nohistoryrewrite. Allnumericaloutputs/PNGpixels mustmatch; finalSVGpathsemanticcomparisonandstagedcheck requiredbeforepush.

## XY-P2 assignment (before dispatch)

```json
{
  "id": "XY-P2",
  "role": "PhysVal",
  "input_revision": "a914323fdc6a7fed15468e396c0a583041862530",
  "inputs": [
    "tools/muon_layout/wheels_xy.py",
    "docs/validation/DES-040/wheels-2026-10-20/xy-sections/README.md",
    "docs/validation/DES-040/wheels-2026-10-20/xy-sections/sections.json",
    "docs/validation/DES-040/wheels-2026-10-20/xy-sections/provenance.json",
    "docs/validation/DES-040/wheels-2026-10-20/xy-sections/endcap-wheels-xy.png",
    "docs/validation/DES-040/wheels-2026-10-20/xy-sections/endcap-wheels-xy.svg",
    "docs/validation/DES-040/wheels-2026-10-20/xy-sections/unchanged-inputs.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Final bounded actualfigure assessment at exacta914323fdc6a7fed15468e396c0a583041862530. You authoredXY-P1independentinputchecks, none ofrootplotimplementation; disclosecontext. InspectactualcommittedsectionsJSON versuspinnedgeometry99bb andindependentXY-P1expectedcuts/IDs/supportstockcounts/coils. Verifyactualartifacts/provenancehashes, common\u00b110mequalaxes, bluechambers/greycoil andhollowframestocksections; no projections/cropping/mirrors/physicschanges. VisuallyinspectcompositePNG andoneindividualPNG, verifyallSVGXMLparse andno rasterimage tags. Rootalreadyprovedall4PNGs/sectionsbyteidenticalandSVGpathsemanticidenticalbefore/afterformatfix. Reuseyourindependentexpectedcuts, no newbroadtests/ACTS. NeedconciseMD/JSON withactualcheckresults, no unresolvedmaterialfindingsifnone andlimitations, scratchonly /private/tmp/pr90-XY-P2-*. No repo/source/dependencyedits,nestedagents,externalmessages/humanapproval. Finalcurrentdocsaddlinksrecordonlyafterthisreview; allactualfigurebytes/sourcefrozenhere.",
  "deliverable": "Briefexactrevisionactualfigure report/JSON andmeaningfulcheckevidence in scratch.",
  "completion": "CorrectactualthreewheelXYsectionsandlegibilityverified; materialfindingsreportedbeforepublication; no engineeringapproval."
}
```

## Actual final-figure review and publication

XY-P2 at a914323fdc6a7fed15468e396c0a583041862530 finds no unresolvedmaterialfinding. Independentcuts matchactual144chamber/216stock/72coilpolygons,0vertexresidualafterpinnedrounding; all9artifacthashes/sizes,5sourcehashes, all4SVGXML/no-rasterchecks pass. CompositeandmiddlePNG visuallyinspectedlegible/uncropped. All201baselineevidenceGitblobs unchanged; parentREADMEindexoldbytesprefix retained. SourceexecuteduncommittedatgenerationHEADbutactualSHA matchesreviewedfrozenbytes; no cleancommittedgenerationclaim. Reports copiedunchanged; rootrequestsportableadaptationoffinalchecker toremove scratch-only dependencies beforefinalretention.

PR90head a914323 verifiedafterpush; bodyaddsPNG/SVG/individualviewlinks withoutremovingexistingcontent. Reply posted: https://github.com/asalzburger/nodd/pull/90#issuecomment-6285801467 . DirectpublicPNGembedusesimmutablea914source. No merge, geometry/field/OBJ/inventory/propagationrerun ordesignsignoff.

## Closeout

FinalportableXY-P2adaptation gitshowsallinputs andindependentmath, CLIrepo/revision/outputonly; rerunresultJSONbyte-identicaltooriginalassessment. Retainedsource/results inxy-sections/review withoriginalreportunmodified; scratchfilenames mappedbyREADME. All9drawingartifact/5sourcehashes unchanged afterreview; maintainedlinksresolve. Current69task/38document/21round and194session validators pass; sessionusage summary/tokenpreviewbuilt. Exactcurrentroot/childtokens unavailable:usageempty, notzero. Historicalpreview210disjointturns/624299405observedtokens mustnotbeallocatedtocurrenttask.

Publicationreply https://github.com/asalzburger/nodd/pull/90#issuecomment-6285801467; PRbodyaddsimmutablePNG/SVG/indexlinks, a914323publishedheadverified. At2026-10-20T07:32:54Z remotechecksbuildIN_PROGRESS/token-siteSUCCESS/deploySKIPPED; no scientificbuildpassclaim. Finalrecord/review-onlycommit follows inGit history. Thisboundeddisplaytaskclosed denotesdeliveredreviewfigures, no physicaldesignchange/signoff/engineeringacceptance. Datedgeometry/magnetics/OBJ/inventories/propagation andbaselineartifactmanifest remainunchanged; onlyparentindexappendlinkisdocumentedexception.

## Token-accounting correction — 2026-10-20

The authorized usage-only recovery [PR90 inventory](../usage/USAGE-2026-10-20-pr90.json) supplies 6 disjoint closed client turns: 9,956,373 input + 46,180 output = **10,002,553 observed tokens**. Cached input 9,759,232 and reasoning output 13,404 are subsets. All imports passed dry-run first. Direct visible-request/session-ID metadata and pinned task narratives identify the owner; specialist edges/root-turn IDs corroborate child ownership. No time-only allocation or duplicate parent/child aggregate was used. Earlier empty-usage notes remain historical; active closeout, model/client identity and other-device completeness remain unknown. Scientific artifacts and design status are unchanged.
