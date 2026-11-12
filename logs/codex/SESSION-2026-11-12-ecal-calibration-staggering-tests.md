# SESSION-2026-11-12-ecal-calibration-staggering-tests — Held-out ECAL calibration and physical board staggering tests

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

User authorizes implementation and execution of the proposed calibration/layout tests. Scope: isolated PROTOTYPE real board staggering and reconstructed-position calibration; identicalretained10k primaries,12DDSimworkers, diskguard, held-outcomparison. No production integration/sign-off or full-depthsector-interface redesign. Main owns feature extraction/calibration/protocol/run/audits/plots andrecords. Originaldata remainlocalunchanged.

Explicit generic-agent roleinstructions are prepared below, not nativeprofileloading.

```json
{
  "id": "ECAL-TESTS-SOFTENG",
  "role": "SoftEng",
  "input_revision": "3af5538faf884d0abce98b0956c0e6d4f45d4527",
  "inputs": [
    "docs/validation/ecal10k-untiled/calibration-layout-options.md",
    "tools/calorimeter_hardware/barrel_layout.py",
    "tools/calorimeter_hardware/edge_layout.py",
    "tools/calorimeter_hardware/barrel_export.py",
    "tools/calorimeter_hardware/edge_export.py",
    "docs/validation/ecal10k-untiled/results/comparison.json"
  ],
  "mode": "write",
  "writable_paths": [
    "software/analysis/calorimeter_digitization/staggered_geometry.py",
    "software/analysis/calorimeter_digitization/test_staggered_geometry.py",
    "tools/calorimeter_hardware/edge_layout.py"
  ],
  "task": "Implement isolated physical staggered-board compact preparation for original ECAL-only10k tiled geometry, native library unchanged if feasible. Main owns calibration/features/transport/audits/publication. User authorizes actual tests of priorrecommendations. Retain slab\u00b196joint phases, absorber/skins/support/cooling stack/envelopes/plane locations. Implement independent4layer tangent/axial phases00,48/0,0/48,48/48. Fullslab axial rows move48awayfrombay on halfphasedlayers; repack shortslabs safely. Tangential boardphasing needs real narrowed edgeboard/sensor templates/guards/ASIC stacks, not unbuildable continuousSi or masks-only moves. Suggested feasible family: existing94x94PCB/90x90Si/88x88active; on tangenthalfphasedlayers use(N-1)fullboards+two46x94PCB/42x90Si/40x88active edgeboards, twoASICs each, preserving oldouterPCBspan and ASICcapacity, smallSi-area delta explicit. Check derivation yourself. ExistingmoduleIDs <~560; reservedhalfboardIDs700+2*row+side fit10bits. Newhalf masks simple rectangles canretainEdgeGrid with newreservedmodulemasks. Endcaps need4physicalpacking/maskfamilies; use existingpack/hardware generation with optionaldefault-preserving tangentphase/innerpartialrow parameters in ownededge_layout.py. OffsetmoduleIDsphase*256 (verify each<256). Preserveactualsense/guard/PCB/ASIC geometries and originalmaterials; avoidoverlaps. Newregionsperphase existingreplicaschoosefamily; retainsectorenvelopes. XML-only transformation/generation must hashverify source/material/primarybytes and recordmass/coverage/parts/IDs changes and limitations. Preserve baseline public factories, library and prior artifacts. Can importexistinghardwarehelpers. Use onlyownedfiles; sourcechecksumupdatedwhereexistingexport expectsownedpackerchanges. No full transport or publishing/commits; create meaningful tests and a fresh preparedinput for main nativeaudit.",
  "deliverable": "Return scoped implementation/input, exact source evidence, actualchecks and limitations to coordinator.",
  "completion": "Deliver requested contribution or concrete missinginputs; do not delegate, publish or grant acceptance."
}
```

```json
{
  "id": "ECAL-TESTS-CALOTECH",
  "role": "CaloTech",
  "input_revision": "3af5538faf884d0abce98b0956c0e6d4f45d4527",
  "inputs": [
    "docs/validation/ecal10k-untiled/calibration-layout-options.md",
    "tools/calorimeter_hardware/barrel_layout.py",
    "tools/calorimeter_hardware/edge_layout.py",
    "tools/calorimeter_hardware/barrel_export.py",
    "tools/calorimeter_hardware/edge_export.py",
    "docs/validation/ecal10k-untiled/results/comparison.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Assess physical candidate implementation constraints promptly. Work from priorfourphaseproposal, current source and source geometry. Coordinate with SoftEng. Check feasible tangential narrowedgeboard family46x94PCB/42x90Si/40x88active twoASICs: (N-1)full+2edge preserves originalPCBspan with2mmgaps, smallSi decrease; ASIC/geometricreadout/guard/manufacturing rationale andID budgets. Check axialhalfphaseawaybay and shortslab handling; endcapphasedpack minimumshape/ASIC/sourcefamily constraints. Advise dense coverage screening/no geometry-onlyresolution claim. No edits, no full-depthsector seam redesign in this firstmodule-staggering test. Give concrete constraints, counters andproposedacceptancetests.",
  "deliverable": "Return scoped implementation/input, exact source evidence, actualchecks and limitations to coordinator.",
  "completion": "Deliver requested contribution or concrete missinginputs; do not delegate, publish or grant acceptance."
}
```

```json
{
  "id": "ECAL-TESTS-PHYSVAL",
  "role": "PhysVal",
  "input_revision": "3af5538faf884d0abce98b0956c0e6d4f45d4527",
  "inputs": [
    "docs/validation/ecal10k-untiled/calibration-layout-options.md",
    "tools/calorimeter_hardware/barrel_layout.py",
    "tools/calorimeter_hardware/edge_layout.py",
    "tools/calorimeter_hardware/barrel_export.py",
    "tools/calorimeter_hardware/edge_export.py",
    "docs/validation/ecal10k-untiled/results/comparison.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Freeze a practical prospective calibration/analysis protocol. Need baseline/raw vsbaseline/calibrated andnewphysicalstagger/raw/calibrated onexact10k inputs with12threads. Main implements reconstructedhit-barycentre/axis features (no truth inference), lowdimensional smoothresponsemap, eventIDoutercrossfitting and training-onlyhyperparameterchoice. TrueEtraininglabels/evalonly. Propose robust boundedpredictor, feature choices (localgap/maskexposure, reconstructedeta/phi, longitudinalfractions) and validation including narrowtrueE slices, signedeta/sectors, tails/zeros andtrainingprior bias. Prefer NumPy-onlysmallridge/smoothmap withphysicalgeometryexposure; no newdependenciesneeded. Need practical pairedbootstrap withcalibrationtraininguncertainty (outerbootstrap/refit), immutablefolds, no posthocselection/cuts. Provide early protocol decisions before fitting, then independent exactsource/results reviewlater. Continuous sample remainsdiagnostic. No writes/fits/runs/delegation/publication.",
  "deliverable": "Return scoped implementation/input, exact source evidence, actualchecks and limitations to coordinator.",
  "completion": "Deliver requested contribution or concrete missinginputs; do not delegate, publish or grant acceptance."
}
```
