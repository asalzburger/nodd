# Persistent material-recording adapter (PROTOTYPE)

This task-local sidecar follows the existing TruthTracking persistent event loop,
using the real ACTS `MaterialPhysicsList` required by `Geant4MaterialRecording`.
It does not relabel FTFP_BERT, modify a shared ACTS installation or bypass the
production-cut update. One ordinary Geant4 run spans the fixed recording case;
ACTS still sets each event's seed, clears its event store and records its own
independent Geant4 event. The native recorder's actions/stepping stay unchanged.

Use one fresh process, one manager and one ACTS thread. Geometry, materials,
regions, cuts, physics and actions must remain immutable until termination.
Dynamic reconfiguration or resuming a completed case is unsupported. The
adapter checks argument/event counts and run aborts, rejects another manager,
exposes lifecycle counts, rejects incomplete completion and supports idempotent
normal finish. These conditions do not establish general mutable-Geant4 safety.

The matching ACTS Python bindings must be imported before this sidecar. The
existing ACTS runtime needs pybind11 3.0.4/internals ABI11, not the newer view's
3.1.0/ABI12. No shared dependency install is required.

See [the baseline comparison recipe](../../../analysis/material_baseline_comparison/README.md)
for exact build/run commands and the current-geometry recording. The unchanged
adapter/driver were retained from e9548326e424f968cf9cd27d73588b6a17655eed;
its earlier standard/persistent 300-probe equality control covered all32 ROOT
branches at zero numeric tolerance. The current100000-probe lifecycle is recorded
separately. Those controls do not test active-run mutation/abort recovery.
