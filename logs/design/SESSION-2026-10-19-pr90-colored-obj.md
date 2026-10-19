# SESSION-2026-10-19-pr90-colored-obj — Current geometry OBJ

## Scope and evidence

Starting at634a5b91f56eeab123cf4f72d62b0850a3bd827d on codex/muon-chamber-layout, clean worktree. User explicitly limits this task to comment1 of PR90: chambers blue and coils grey. Comments6274941662/6276580954 request current geometry first. No chamber rearrangement, new propagation study or detector approval is implied. Existing ACTS dirty files and scientific evidence remain preserved.

Using the repository coordinate/review workflows and acts-spack skill. Node preflight again warns stale registry fingerprints and unavailable staged DD4hep/Geant4 full sources; installed ACTS header/library capability will be checked directly for this export. No dependency change or ACTS source edit is needed.

## Selected conversation

User: “Take the comment of PR #90 and tackle comment one: produce an obj file for chambers (blue) and coils (grey).”

## Assignment OBJ-A1 recorded before dispatch

```json
{
  "id": "OBJ-A1",
  "role": "SoftEng",
  "input_revision": "634a5b91f56eeab123cf4f72d62b0850a3bd827d",
  "inputs": [
    "tools/muon_layout/acts/propagate.cpp",
    "tools/muon_layout/acts/prepare.py",
    "docs/validation/DES-040/geometry.json",
    "tools/toroid_prototype/geometry.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Read-only bounded API/export fidelity audit: recommend native ACTS ObjVisualization3D from unchanged current TrackingGeometry inspect-only face corners, blue chambers, grey36toroid warm coil envelopes, no frame/world/entrance/trajectory. Check OBJ/MTL writer colors, units, object names, relative mtllib, native finite face winding orientation and coil mesh corner/seam issues. Root handles implementation and environment verification. Installed ACTS preflight warnings already reported; no dependent runtime/build until root confirms. No shared edits/dependencies/nested agents/external messages; scratch /private/tmp/pr90-obj-A1-*. External read-only API reference is /Users/salzburg/Documents/work/installed/acts-nodd/include/Acts/Visualization/ObjVisualization3D.hpp.",
  "deliverable": "Short evidence-based export/API pitfalls and validation recipe with exact source locators; no unperformed runtime claim.",
  "completion": "Actionable verified API/color/winding/unit findings for current input; preserve source and frozen scientific evidence."
}
```

## Token accounting

Exact root/child per-turn counters unavailable. Usage remains unknown, not zero; no estimated or overlapping observations are added.

## Implementation contract

Use unchanged native ACTS inspection face vertices and the installed ObjVisualization3D writer, with metre coordinates and outward face winding. Export all 1560 chamber envelopes blue, plus36 fixed toroid warm allocations grey. No geometry rearrangement, frame/world/entrance/track objects or new coverage calculation. The central solenoid is outside this muon-layout export. Curves use64segments/quadrant (<0.1mm chord deviation). Emit relative sibling MTL and deduplicate only identical ACTS material blocks; pack OBJ+MTL together for portable import. Check all source corners, closed oriented object topology, volumes, colors and roundtrip positions. Sources are committed before final acquisition/provenance.

OBJ-A1 confirmed the native API color output, /256 color convention, absolute-path pitfall in write(path), repeated identical material definitions and need to orient chamber polygons using their geometric interior. Its read-only recommendations were reconciled into the exporter. CMake build against the refreshed installed Core succeeded. Setup/Spack-lock/library fingerprints still match the earlier successful rebuild; all pre-existing ACTS source changes remain untouched.

## Executed export and checks

Source b553824a2ecd6d11527ac4f1e5a12753a1a14cc1 supplied all seven exact source hashes. Actual unchanged native ACTS inspection completed in0.075s (zero tracks by design), followed by ObjVisualization3D output of1596objects:1560blue chambers and36grey warm toroids. Final OBJ has46800quads/187200vertices. Every object is closed with consistent outward winding; maximum native-source corner residual3.6621e-15m, OBJ roundtriperror0, chamber volume residual6.3228e-14m3. Curve chord sagitta9.4123e-5m. Deduplicated identical ACTS material blocks to exactlytwo colors, preserving /256 conversion and sibling MTL. ZIP members are byte-identical to OBJ/MTL. Root visually inspected the full preview; transparent chambers are preview-only.

All33journal/documentation tests and the retained ACTS artifact/hash check passed. Executable and Core library match the earlier run, and all15pre-existing ACTS source-file hashes are preserved. No physical geometry, field, MDT resolution, old propagation source or scientific output changed. Frozen output assessment/publication pending.
