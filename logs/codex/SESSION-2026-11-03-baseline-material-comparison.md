# SESSION-2026-11-03-baseline-material-comparison

## Scope and selected request

Contemporaneous bounded material characterization from clean source62f6056395e0dfee0c7985cf24e88dc9919c4e2d in branch codex/baseline-material-comparison. User requested a material map for the new baseline and two Geant4 component stacks, with PR112 colors, sensitive/passive alpha1/0.5, ACTS black markers and ratios, and old total/short-strip dotted references on the new figure. Both supplied top-level storage inputs are immutable. No PR creation, publication or design approval was requested.

The existing `acts-spack`, `nodd-coordinate` and `nodd-review-validation` procedures were applied. Explicit generic-role assignments below supplied the SoftEng and PhysVal profiles; native role loading is not claimed. Their files/outputs were disjoint. No further delegation.

## Outcomes and checks

- Supplied2mm producer metrics prove PR109 before PR110 services. Preserved it as an intermediate paired-ray control; freshly built/exported current main and recorded100000 geantinos separately, seed228, eta±4, fullphi, origin, one thread.
- Persistent real MaterialPhysicsList completed1000 events with one run/event-loop initialization/termination, no abort,200.22s wall. Adapter/driver bytes retained from e954832; current geometry identity separately bound by compact/material/all-five-factory hashes. No shared dependency changes.
- SoftEng fresh native export46682 planes/120volumes/54groups;67 portals/8650 bins. Full native map/reload passes,0 unmapped nonzero slabs, exact every-ray/global budget closure.100000 independent ACTS validation rays seed43 completed; origin/count checked.
- Historical raw-step audit initially failed. Pinned ACTS reader explicitly skips185 exact-zero slabs on161 rays; every count difference equals those zeros, every positive slab remains and all budgets close exactly. Failure retained locally; historical guard unchanged, current reader-boundary audit explicit.
- Strict TGeo classification initially FAILED149 material mismatches/0unassigned on18,319,623steps. Full diagnostic rerun retained all149. Native G4 audit1043 strictinterior queries verifies Graphite2.21g/cm3 and storedrho/X0/L0, unique named matching passiveDD4hepvolume. No tolerance/geometry change. Optional hashbound audit resolves those149 in a final full classification with0unresolved/0unassigned. The G4/TGeoCSG conversion discrepancy remains open, not certified away.
- Native profiles independently checked against all100000 categorized rays, including zeros, covariance-aware totalSEM and per-ray closure. Cropped legacy alignedeta bins to[-4,4], preserving88698G4/88923ACTSrays; current100000each. No phi range relabeling. Ratio errors conditionalACTSraySEM only; no maptraining/covariance or significance claim.
- unrooted0.1.0rc1 rendered two PNG/PDF/SVG figures; coordinator visually inspected both PNGs: legends, palette, alpha, blackmarkers/ratios and dotted old references legible. TotalX0−7.20%,shortstripX0−27.65%;totalL0+2.89%. MatchedPR109/currentraycontrol totalX0−10.41% isolates whole redesign, not cables/pitch alone.
- Current locality diagnostic:48.16%X0 assigned>50mm, max413.23mm. Phi1/locality and missing old recording seed/revision remain limits.
-17 offline tests passed. Initial added map-grid test assumed rows=phi; actual pinned ACTS matrix rows=z/r,columns=phi. Corrected the test to verify that actual serialized axis order and all67 grids; counts8650/2003empty agree with native report.
- Preparatory source lookups with stale paths and firstGen3attempt missing `.components` failed before use; built5component-index targets, retry passed. First audit attempted before diagnostic file existed and failed; retried after full classification. Final audit rerun used stable source bytes; hashes independently checked. Intermediate failures remain local.
- Staged whitespace check initially found generated SVG path-line trailing spaces; plot exporter now strips them before artifact hashing, regenerated figures and all17tests pass. No visual/numerical change. Project validator initially rejected a task/stream role mismatch; restored the WS-TRACK role label and validation passes.
- Node preflight exits2 for changed setup/lock/full-source registry; actual imports,12datasets,factorybuilds and full native execution verified separately. This is not a clean registry certification.

## Changes and reproduction

Retained recipes and compact binwise/model artifacts under software/analysis/material_baseline_comparison and docs/validation/baseline-material-comparison. FullROOT, XML/nativegeometry, per-step audit tables and bulky logs remain ignored under build/material-comparison. Source and artifact manifests state exact hashes, versions, seeds/settings and commands. Existing old evidence remains unchanged. Scientific task record added without advancing design/sign-off states.

## Token accounting

Exact client-reported per-turn counters were unavailable for coordinator and both specialists. Usage remains empty/unknown, not zero; no token estimate or overlapping historical accounting. Client is Codex desktop; version/threadID unavailable. No external messages or PR accounting was performed for this task.

## Follow-up

Exact-revision PhysVal review is pending for source, retained map/binwise evidence and both figures. Geometry-conversion CSG discrepancy, phi averaging, locality and broader engineering/tracking qualification remain follow-ups independent of the delivered characterization.

## Initial source and inputs

Current source62f6056395e0dfee0c7985cf24e88dc9919c4e2d includes reduced-service PR110 and palette PR112. User supplied old0.5mm Geant4 is exact prior reference034fe2f6...100000tracks with eta[-4.5,4.5]; new2mm supplied filecfbab8b...100000tracks has producer metrics proving PR109 compact8e59eedd before PR110 services, eta[-4,4]. Inputs are preserved unchanged. Coordinator explained mismatch and will record current geometry separately, use provided2mm as intermediate control, and compare old/current on common eta[-4,4]. Total changes also include balanced pixels; no pitch-only saving is inferred. Registry preflight warns changed setup/lock and unverified full sources; actual imports/datasets/builds will be checked.

## Assignment MATCOMPARE-SoftEng-01

```json
{
  "id": "MATCOMPARE-SoftEng-01",
  "role": "SoftEng",
  "input_revision": "62f6056395e0dfee0c7985cf24e88dc9919c4e2d",
  "inputs": [
    "software/running/nodd_material_mapping.py",
    "software/running/nodd_material_validation.py",
    "software/analysis/gen3_material_mapping/material_runtime.py",
    "software/analysis/gen3_material_mapping/select_surfaces.py",
    "software/analysis/gen3_material_mapping/mapping_config.json",
    "tools/tracker_dd4hep/export_gen3.py",
    "software/source/ActsExamples/MaterialMapping/PortalMaterial.cpp"
  ],
  "mode": "write",
  "writable_paths": [
    "software/analysis/material_baseline_comparison/map_workflow.py",
    "software/analysis/material_baseline_comparison/README_mapping.md",
    "software/analysis/material_baseline_comparison/test_mapping.py"
  ],
  "task": "Implement and EXECUTE the current-baseline ACTS material-mapping and independent straight-ray validation workflow, preserving existing legacy guards. Coordinator supplies current main PR110+112 fresh DD4hep factories/compact under build/material-comparison/dd4hep and records100000 geantinos into build/material-comparison/geant4-current/tracks.root (these may be preparing; coordinate readiness). Own all native Gen3 export/selection/map/validation outputs under build/material-comparison/agent-mapping, but source ownership only the three named files. Existing runtime nodd-software-layout ACTS355ea684/build/pyvenv; preflight warned stale setup/lock/full-source registry, direct runtime will be checked. Existing MaterialMapping native sidecar under sibling nodd-gen3-material-mapping/build/gen3-material-map-run/native may be reused only with explicit source/ABI/binary verification; otherwise build task-local without installs. Follow software/env/truth_tracking.sh in fresh zsh and DDG4-first. Use current maintained export_gen3 selected46682 planes rather than weaken historical45646 guard. Full map all recorded material on selected current native portals; clear existing sensor/pipe/slabs to avoid double count; same binning policy as old mapping, dynamic current surface IDs. Independent validation1000events\u00d7100rays, seed43, eta[-4,4], full phi, origin; training Geant4 seed228 same eta. Closure, exact map keys/native binning/reload, track counts and truthful provenance required. No shared installation/geometry change, no oldmap ID transplant. Coordinator owns fresh recording, classification and plots. Do not modify coordinator-owned sources/logs/tracking; return commands/outcomes/hashes and limitations. No further delegation/publication.",
  "deliverable": "Reusable narrow workflow + recipe/tests where meaningful, and completed current native Gen3 export/map/100000-ray validation with compact reports and local payloads. Return evidence paths; coordinator curates reports and review.",
  "completion": "Mapping conservation/reload and independent validation succeed, or precise reproducible blocker with unaffected work completed; no physics approval."
}
```

## Assignment MATCOMPARE-PhysVal-01

```json
{
  "id": "MATCOMPARE-PhysVal-01",
  "role": "PhysVal",
  "input_revision": "62f6056395e0dfee0c7985cf24e88dc9919c4e2d",
  "inputs": [
    "software/analysis/material_profiles/categorize.C",
    "software/analysis/material_profiles/export_profiles.py",
    "software/analysis/gen3_material_mapping/export_validation.py",
    "software/analysis/gen3_material_mapping/plot_validation.py",
    "docs/validation/gen3-material-map-run/README.md",
    "README.md"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Early independent methodology assessment for user-requested two Geant4 component stacks (old and new), ACTS mapped material as black markers and ACTS/Geant4-total ratio, old total and old shortstrip dotted references on new plot. Mandatory PR112 palette: beam#ffcc66,pixel#0066cc,short#ff9933,long#009999; sensitive opaque/passive alpha0.5. Need no simulation/imports/edits/builds/delegation. Old storage 0_5 ROOT hash034fe2... is exactly prior100000 legacy Geant4 sample (original geometry530080c association, no embedded original seed/revision), eta[-4.5,4.5], prior retained material profiles + ACTS map/validation at sibling nodd-gen3-material-mapping. User supplied2_0 file hashcfbab8... is100000 PR109 geantinos, verified producer metrics at sibling nodd-pr109-geantinos/storage/nodd-tracker-strixel-2_0.root/metrics.json identifies8e59eedd compact WITHOUT PR110 reduced services, eta[-4,4]. Coordinator explained mismatch and will preserve inputs, freshly record current PR110+112 geometry and make new native map/independent validation, using provided2mm sample as intermediate service-change control. New/old also differ in balanced pixel layout, so total changes cannot be attributed solely to readout/services. Evaluate normalization (every track contributes zeros), sensible common eta range[-4,4]/0.1 bins, conditioning of old cropped profiles, ratio errors/denominators/correlations from map-training sample, sensitivity-density-boundary classification, limits on saving attribution and minimum controls. Final artifact/source review will be a later exact-revision assignment. No acceptance claims.",
  "deliverable": "Return concise methodology risks, required controls and defensible plot/statistical definitions before final implementation.",
  "completion": "Identify conditions needed for faithful comparison and any immediate scientific blocker, with source locators and scope limits."
}
```
