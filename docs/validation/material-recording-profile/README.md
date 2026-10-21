# ODD/nODD tracker material-recording profile

Report ID: VAL-MATERIAL-PROFILE-2026-10-21. Date: 2026-10-21.
This characterizes the existing DRAFT / PROTOTYPE detector and software;
DES-024/025 remain DRAFT. It grants no detector design or material acceptance.

The dominant recurring cost is **Geant4 run initialization**, specifically
`G4ProductionCutsTable::CreateCoupleTables` / `ScanAndSetCouple`, rather than
probe transport or ROOT output. ACTS invokes `BeamOn(1)` for every sequencer
event. Geant4 rebuilds the material/cut associations for each run by traversing
the region volume tree separately for each material.

The completed comparison and integrity measurements are retained in
`results.json`; native phase measurements, hierarchy inventories, library/input
identities, exact branch-equivalence checks and reduced profiler evidence are
retained alongside this report. Large ROOT files and full profiles stay ignored
under `build/jobs/material-profile`.

## Matched scenario and scope

Both cases use **100 events × 100 neutral geantinos per event**, seed 228,
uniform eta in [-4,4], phi in [0,360 degrees], a vertex at the origin, zero
vertex spread, one serial Geant4 manager and one ACTS sequencer thread. The
momentum generator is uniform over 1–10 GeV, charge/mass are zero, and the
material recorder forces PDG0 geantinos. Both retain `recordElementFractions=False`,
ROOT pre/post-step coordinates and recalculated totals. No reconstruction
material map, transport cuts, step limits or material simplifications are added.

The ODD Tracker XML explicitly includes the **solenoid**, even marking it as a
tracker detector. The generated comparison wrapper retains the original
definitions, beam pipe, pixel detector/PST, short/long strips, every associated
passive constituent and identifier/plugin definition. It removes only that
solenoid include and omits calorimeter, muon and field sections. Native
inventory verifies the resulting scope. nODD uses the unchanged combined
beam-pipe/tracker compact from the existing software build.

Native physical models remain distinct. ODD has a 23.6–24.4 mm beryllium pipe;
nODD has a 27–27.8 mm pipe plus an explicit numerical-vacuum bore. Both extend
to |z|=4000 mm. ODD world half sizes are (12,12,12) m; nODD uses
(4,4,4.1) m. Air and Vacuum retain the recorder's existing exclusion from
recorded slabs, while transport still traverses them. The world boundaries,
module technologies, passive supports, cooling and service/material recipes
are preserved. Material totals are therefore different observables, not a
performance-equivalence criterion between the two detectors.

The primary 100-event runs use the same ACTS build at source
`355ea68493b326956756c9386d2fd9eaf9328568`, the same build-local Python environment,
DD4hep1.38 and Geant4 11.4.3. ACTS and both detector factory builds are
RelWithDebInfo (`-O2 -g -DNDEBUG`). Runtime nODD source is
`530080cfe16c7513228bf60238b99d4b9938538a`; ODD source is
`d70556f33b1c36abdf101a07ad8cf57eb56fbdf1`. The separate sister ACTS checkout is
dirty and is not the ACTS framework comparator. The unchanged ODD factory is
rebuilt task-locally against the same dependency view. An initial sister-factory
run and the first local rebuild both exposed mixed Xerces initialization. Both
final comparators therefore explicitly load DDG4 before PyROOT. Exact binary
hashes and matched loaded-image UUIDs distinguish source pins from executed
artifacts. The earlier nODD run is retained as a diagnostic repeat.

This task starts from fetched main
`e980c41f47605091e94d85a463e31cf0bdf2edd8`. PRs77–80 are marked merged through
stacked target branches, while this main snapshot contains the initial software
layout. The benchmark explicitly points to the existing software-layout runtime;
it does not assume the later source migration exists on main or merge it here.

## Measured causes

The steady-state native sample contains 6259 main-thread samples:

| Native function/path | Samples | Fraction |
| --- | ---: | ---: |
| `UpdateCoupleTable`, cumulative | 6192 | 98.93% |
| `ScanAndSetCouple`, exclusive | 5471 | 87.41% |
| `GetMaterial` + TLS accessor/stub, exclusive | 719 | 11.49% |
| Native event processing, cumulative | 18 | 0.29% |

These are sampled stack fractions, not exact time counters. The separate
first-event window contains 5059/6201 samples in voxel optimization and
extent/refinement work. Representative paths are:

```text
Sequencer::run
  Geant4MaterialRecording::execute
    Geant4SimulationBase::execute
      G4RunManager::BeamOn
        G4RunManager::RunInitialization
          G4RunManagerKernel::RunInitialization
            G4ProductionCutsTable::UpdateCoupleTable
              CreateCoupleTables
                ScanAndSetCouple -> G4LogicalVolume::GetMaterial
```

The first event also follows
`ResetNavigator -> CloseGeometry -> BuildOptimisationsSequential ->
G4SmartVoxelHeader::BuildVoxels/RefineNodes -> CalculateExtent`.
Its duration must not be divided by the number of probes and presented as
per-track transport cost. Native event timers separately measure actual event
transport/material recording after initialization. Per-step diagnostic timing
includes callback measurement overhead and is reported separately from the
uninstrumented primary comparison. Framework `timing.csv` isolates ROOT writing.

The scaling mechanism is explicit in Geant4 v11.4.3
[run initialization and region update](https://github.com/Geant4/geant4/blob/v11.4.3/source/run/src/G4RunManagerKernel.cc#L609)
and [material/cut table construction](https://github.com/Geant4/geant4/blob/v11.4.3/source/processes/cuts/src/G4ProductionCutsTable.cc#L126).
The current nODD default region has 1159 materials and 661997 expanded physical
nodes: approximately **767 million volume visits per association rebuild**.
This occurs at every ACTS event, even though the material model is unchanged.

| Native geometry inventory | ODD | nODD |
| --- | ---: | ---: |
| Geant4 logical volumes | 440 | 661997 |
| Geant4 physical placement objects | 66085 | 661997 |
| Geant4 instantiated materials | 9 | 1159 |
| World daughters | 5 | 649614 |
| Largest daughter set | 7356 | 649614 |
| Geant4 solids | 488 | 805991 |

nODD creates fresh constituent volumes and solids throughout its repeated
structures. Its 18703 TGeo assemblies largely disappear into Geant4 imprints:
the TGeo world has 9 children, but the Geant4 world has 649614. ODD reuses
module/stave templates and retains physical Air layer envelopes. These are
software representation differences in addition to genuine passive-detail
differences. The nODD shape inventory includes 589307 boxes, 29560 subtraction
solids, 492 intersection solids, 10728 tori and 5890 extruded solids. Retained
source XML also has 47344 cuts, including repeated cuts within compound solids.
The nODD compact is 200451288 bytes. Parsing/construction, first-run voxelization
and recurring association scans are distinct costs; the native phase evidence
separates them.

## Guarded association reuse experiment

The optional native helper skips the association rebuild only for this
**immutable, single-world neutral-geantino harness**. It preserves `BeamOn(1)`,
per-event seeds and all event/run lifecycle callbacks. It changes neither
production cuts nor materials, geometry, identifiers, stepping or ROOT options.
The primary comparison remains available with no helper loaded.

Before reuse it requires closed geometry, unmodified cuts, one tracking world,
one active root region and matching table/material counts. It checks **every
logical volume** against its current material, region, exact cuts object,
registered region mapping, used couple, couple index and table membership.
Any failed check delegates to Geant4's original update. Configuring a user
energy-cut vector permanently disables reuse: Geant4's `IsModified()` alone does
not cover that API. The helper is opt-in and task-local; it is not installed into
the shared environment or enabled in the normal recorder.

Post-transport adverse controls exercise material/region/cuts-pointer changes,
in-place cut changes, null/stale couples, an extra region and open geometry.
Pointers, values and geometry are restored before checking valid state again.
The final energy-vector control disables reuse for the remainder of the
diagnostic process; no altered fixture is transported. Exact comparison of all
32 ROOT branches, including every jagged material step and pre/post coordinate,
is required across all 10000 probes. Checks and scope limits remain technical
evidence rather than permission to apply this shortcut to arbitrary mutable
Geant4 jobs.

## Measurement limits and reproducibility

Wall and process CPU time are separate counters. Peak RSS is the Darwin
`getrusage` byte count, not physical footprint or incremental detector memory.
The timed interval starts before Python framework imports and ends after
sequencer finalization; dependency activation, process teardown, hashing,
inventory and post-transport adverse checks are outside it. Component timers
are inclusive/nested and must not be summed. Parsing is the actual Xerces DOM
parse; the remaining DD4hep construction interval includes factory construction
and volume-manager setup. Other pipeline initialization is reported as a
residual rather than falsely attributed entirely to physics initialization.

The host is shared and CPU affinity is not pinned. The primary nODD run had two
15-second native `sample` windows (2 ms interval); event statistics retain those
events. Short diagnostic processes ran concurrently on other cores. There is
one primary run per detector, so these are observed timings, not a universal
speed ratio or statistical performance confidence interval.

Early timing-shim trials altered weak inline symbol selection and are excluded.
The final helper uses hidden inline visibility; loaded binary identities and
an uncached control establish the original slow path. The stale acts-spack
registry warned about changed setup/lockfile fingerprints and missing full
sources. Installed runtime imports, library identities and all 12 dataset
directories were verified without modifying shared dependencies.

Commands and implementation are in
[the profiling-tool guide](../../../tools/material_recording_profile/README.md).
The paired [session journal](../../../logs/codex/SESSION-2026-10-21-material-profile.md)
retains assignment/review targets, actual checks, excluded attempts and unknown
token coverage. No overlap, engineering, material-realism or reconstruction
acceptance is inferred from these timings.
