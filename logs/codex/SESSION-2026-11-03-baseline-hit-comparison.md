# SESSION-2026-11-03-baseline-hit-comparison

## Scope and selected request

User requested old/new baseline #hits versus eta in two options: stacked+totalmarkers, individualmarkers+totalmarkers. Work started clean at fb6af4afbcde7603566e6c5941607f64764e7240 in existing codex/baseline-material-comparison. This is a new bounded task with its own paired journal. No PR/publication was requested. Source specifications DES025/DES043 and ADR003 retain existing approval states.

## Method and outcomes

Initially considered reducing the saved material steps through TGeo. Separate PhysVal early assessment identified that category/sensitivity matching cannot certify physical hit identity: same-density guard edges and multiple placements can remain ambiguous. Replaced that inference with direct live G4prestep touchables in fresh matched geometry runs; no use of rounded positions, tinyX0bounds or logicalvolume-onlydedup. These are distinct positive-length sensitivephysicalvolume crossings, including chip/strip overlaps and edgegrazes, not response/plane/reconstructed hits.

Read and applied acts-spack preflight, nodd-coordinate and nodd-review-validation procedures. Preflight still exits2 for stale setup/lock and unverified fullsources; directly verified imports/headers and successful native runs. No shared installs or geometry changes. Generic PhysVal role was supplied explicitly; no native-profile loading claim. Coordinator kept tightlycoupled implementation/execution.

Both100k cases use1000events×100rays,seed228,eta[-4,4],fullphi,origin,one thread and the unchanged persistent MaterialPhysicsList sidecar. One normalrun/eventloopinit/termination,1000events,noabort. All100000 event/track IDs and initialdirection/vertex fields exactly paired. Sourceold530080c/current62f6056 actualcompact/material/allfivefactory hashes match original material comparison identities. Old131.4s/current206.3s co-scheduled diagnostic timing, not a speed benchmark.

Observer uses upstream ACTS SteppingActionList, forwarding unchanged MaterialSteppingAction first.300current probes preserve all32 scalar/jagged material branches exactly against the existing current sample. Full uniqueDD/G4sensitive placement inventories45646/46682,all names/material densities match. Full path+copy number indexes and perray sets guard identity. Nativehits1,407,273old/1,493,379current, no secondary/unmatched/duplicatepath/incompleteevent failures. No observedsplitpositive orzero-sensitive steps; no independent splitstep/touchablemockfixture executed.

Independent geometric finitebox controls using nativeGen3 transforms/bounds/thickness agree for256old and256current rays. A zero-thickness plane control differs12/13rays dueedgegrazes; retained as observable distinction, not relabeled a passing plane-hit comparison. Earlier128raycurrent check also passed finiteboxes after6 plane mismatches. Missing/stale exploratory source paths were read-only search failures; located matching old native export and freshly exported it with the maintained historical guard.

Mean total14.07273→14.93379: pixel5.80622→6.64029,shortstrip4.54608→4.57307,longstrip3.72043exact perrayunchanged. TotalpairedSEM0.00424. Allgeneratedrays enter everycomponent includingzeros; totalSEM uses perray totals with retained componentcovariancematrices. No readoutpitch/service-only attribution or efficiency claim.

Two unrooted0.1.0rc1 PNG/PDF/SVG comparisons rendered and visually inspected: oldleft/newright, fixedpixelblue/SSorange/LSteal, blacktotalmarkers, commonaxes, readablelegends.5focused tests pass;17 existing materialcomparison tests stillpass. Source/render/nativeinput hashes retained; largeCSV/ROOT/nativegeometry/logs remain ignored underbuild/hit-comparison. Originalmaterial evidence/inputs unchanged.

## Reproduction and files

Recipes and compactmodel/binwisecontrol evidence under software/analysis/hit_baseline_comparison and docs/validation/baseline-hit-comparison. Optional observer/ROOTwriter flags added to existing geantino driver; defaults retain native material stepping. No detector/configuration changes. Scientifictracking item added; no design approval advanced.

## Token accounting and follow-up

Exact client-reported root/specialist token counters unavailable. Usage remains empty/unknown, not zero. No historicalusage duplicated. Final PhysVal assessment completed at0aec2ef08553a2fbc24867a7cff4fd4ada0b67ae with no material delivery blocker; no engineering/reconstruction acceptance inferred.

## Scope and initial approach

User requests old/new #hits versus eta, stacked+totalmarkers and individualmarkers+totalmarkers. Use same immutable original/current Geant4samples and explicit matching geometry. Hits mean distinct positive-length sensitivephysicalplacements perray, not materialsteps or reconstructed/digitized response. Coordinator owns tightlycoupled nativeanalysis+plotting; separatePhysVal methodology/result assessment. Unrooted and mandatory componentpalette retained. Preflight exits2 (stale setup/lock,fullsources unverified); directlyverifyloadedruntime beforedependentprocessing.

## Assignment HITCOMPARE-PhysVal-01

```json
{
  "id": "HITCOMPARE-PhysVal-01",
  "role": "PhysVal",
  "input_revision": "fb6af4afbcde7603566e6c5941607f64764e7240",
  "inputs": [
    "software/analysis/material_profiles/categorize.C",
    "software/analysis/material_profiles/categorize.py",
    "docs/validation/tracker-propagation/README.md",
    "docs/validation/baseline-material-comparison/README.md",
    "docs/validation/geantino-material-profiles/provenance.json",
    "README.md"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Early bounded methodology assessment in /Users/salzburg/Documents/ChatGPT/agentic-detector/nodd-baseline-material-comparison for new user request hits-vs-eta old/current baselines, two render options:stacked components+blacktotalmarkers and individualcomponentmarkers+blacktotalmarkers. Coordinator plans extend existing densitycheckedcategorizer optional--count-hits, perray count distinct fullTGeo sensitivephysicalplacement paths with positive recorded path length, deduplicate same sensor splitsteps, use DD4hep sensitive flags, group pixels/short/longstrip (beam/passive nohits), keep zeros and actual perbin denominators. Neutral origin straightGeant4geantino samples are same as material comparison, common[-4,4]/0.1eta bins; old100k eta4.5 cropped88698, current100k eta4. Current149 passiveGraphiteG4audit doesnotprovidehits butstrictmaterialgatekept. Need assess if recordedmaterialpositions/floatboundaryrescue can faithfully count distinctsensitiveplacements, ambiguity/error handling and scope wording geometriccrossings vsresponsehits; propose minimum meaningful dedup/identity controls. No simulations/build/importnative/edits/delegation. Read exact source snapshot before author conclusions. Finalexactrevisionfigure/resultassessment will follow after implementation.",
  "deliverable": "Concise methodology risks/requirements for defensible sensitive-crossing hit profiles, nohumanacceptance.",
  "completion": "Identify material blockers and minimum controls; return actualread-only checks and limits."
}
```

## Assignment HITCOMPARE-PhysVal-02

```json
{
  "id": "HITCOMPARE-PhysVal-02",
  "role": "PhysVal",
  "input_revision": "0aec2ef08553a2fbc24867a7cff4fd4ada0b67ae",
  "inputs": [
    "docs/validation/baseline-hit-comparison/README.md",
    "docs/validation/baseline-hit-comparison/current-box-control.json",
    "docs/validation/baseline-hit-comparison/figures/.gitignore",
    "docs/validation/baseline-hit-comparison/figures/hits-markers.pdf",
    "docs/validation/baseline-hit-comparison/figures/hits-markers.png",
    "docs/validation/baseline-hit-comparison/figures/hits-markers.svg",
    "docs/validation/baseline-hit-comparison/figures/hits-stacked.pdf",
    "docs/validation/baseline-hit-comparison/figures/hits-stacked.png",
    "docs/validation/baseline-hit-comparison/figures/hits-stacked.svg",
    "docs/validation/baseline-hit-comparison/figures/plot-report.json",
    "docs/validation/baseline-hit-comparison/observer-noninterference.json",
    "docs/validation/baseline-hit-comparison/old-box-control.json",
    "docs/validation/baseline-hit-comparison/old-native-export-summary.json",
    "docs/validation/baseline-hit-comparison/profiles.json",
    "docs/validation/baseline-hit-comparison/provenance.json",
    "docs/validation/baseline-hit-comparison/runs.json",
    "software/analysis/hit_baseline_comparison/HitCounter.C",
    "software/analysis/hit_baseline_comparison/README.md",
    "software/analysis/hit_baseline_comparison/check_boxes.py",
    "software/analysis/hit_baseline_comparison/check_observer.py",
    "software/analysis/hit_baseline_comparison/plot.py",
    "software/analysis/hit_baseline_comparison/reduce.py",
    "software/analysis/hit_baseline_comparison/test_profiles.py",
    "software/analysis/hit_baseline_comparison/test_retained.py",
    "software/running/nodd_geantino_recording.py",
    "README.md",
    "docs/validation/baseline-material-comparison/classification-provenance.json",
    "docs/validation/geantino-material-profiles/provenance.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Final bounded independent assessment at exact0aec2ef08553a2fbc24867a7cff4fd4ada0b67ae in /Users/salzburg/Documents/ChatGPT/agentic-detector/nodd-baseline-material-comparison. Inspect primary binwise profiles/nativecontrols and bothPNGs beforeauthorconclusions. Userwanted old/new #hitsvs eta, stacked+blacktotalmarkers and individualcomponentmarkers+blacktotalmarkers. Methodchangedafteryourfinding:directliveG4prestepfulltouchablephysicalpath+copyID positivepaths, DDsensitiveuniqueLogicalname/materialmatching+fullDD/G4inventory45646/46682. OriginalACTSMaterialSteppingAction forwardedfirst viaupstreamSteppingActionList.300observerraysall32materialbranches exactlyequal priorcurrentcampaign. Fullmatched100krays eachseed228 eta\u00b14, origin,fullphi,one thread,persistentlifecycle1run/noabort; checkrawCSV/metrics underignored build/hit-comparison/{old,current} and 300samplecurrent-observer-smoke asneeded withexisting analysisPython. IndependentnativeGen3 finitebox256rays old/current matches;plane-onlycontrol12/13differencesexplicitfiniteedgegrazes. Thisisvolume crossings,notACTSplanesorresponsehits. Bothbaselinesfreshgenerated; originaloldmaterialseedunknownnotused. Allnativecasescompletedexit0. Dedupbyperraysetfullphysicalindex; nosplitpositiveorzero-sensitive observedinactualsamples, noindependenttouchablemockfixtureclaimed. Checkaccounting,zeros,componentcovariance/totalSEM,exactraypairing,scopeclaims/palette/markers,originalmaterialsourceidentity andliveobservernoninterference. Youmayrun5focusedoffline tests and readnativeCSV/ROOT/JSON withsiblingnodd-unrootedPython3.11. DoNOT rerunsimulations/build/install/edit/delegate/publish. Actualsource/runtimeassessedlimitedtopinnedsource/retainedresults;reportmaterialdeliveryblockersorprecisequalifications,notengineeringacceptance. Keepbounded;rootonlyeditslogs/trackingduringreview.",
  "deliverable": "Concise exact-source scientific/source/figure review withactualchecks,findings,limits and materialblockers toqualifieddelivery.",
  "completion": "Assess finaltwofiguresandcount/evidence/identitymethod and returnboundedfindings;nohumanapproval."
}
```

## Final identity/storage checks

ACTS source rechecked clean at355ea68493b326956756c9386d2fd9eaf9328568. Both original top-level storage materialROOT hashes remain unchanged. Complete new native processes and fresh oldGen3 export exited0. New task staged/history payload inspection excludes fullCSV/ROOT/nativegeometry/cachefiles. session_log.py summary executed; current task stillhas no exactclient counters.

## Final assessment and closeout

HITCOMPARE-PhysVal-02 at0aec2ef08553a2fbc24867a7cff4fd4ada0b67ae found
no material blocker to qualifieddelivery. Independently checked allraw100k
CSV/metrics percase,80bin means/zeros/covariances/variances within1e-13,
exactpairing,fullgeometry/input/source hashes,300×32materialbranchequality,
256finiteboxrays perbaseline,5tests and bothPNG visuals. No nativejobs rerun,
no filesedited, nohumanacceptance. Limitsofboundedcontrols and unexercised
native splitpositive/zero-sensitive fixture remain explicit. Curated assessment
retained in docs/validation/baseline-hit-comparison/review.md.

Project/session validations and usage summary executed. This task has no exact
client-reported tokenobservations, so coordinator/specialist input/output remain
unknown. New taskhistory28stagedfiles/27blobs totals1295067bytes,largest273275byteSVG;
noCSV/ROOT/nativegeometry/cachepayload committed. Figures/data/recipe complete,
originalstorageinputs unchanged. No PR,push,publication or externalmessage requested/performed.
