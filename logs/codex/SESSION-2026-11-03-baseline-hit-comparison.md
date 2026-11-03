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

Exact client-reported root/specialist token counters unavailable. Usage remains empty/unknown, not zero. No historicalusage duplicated. Final exact-revision PhysVal assessment of code/figures/nativecontrols is pending; no engineering/reconstruction acceptance inferred.

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
