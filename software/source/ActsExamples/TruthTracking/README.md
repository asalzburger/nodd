# Native truth-tracking observer (PROTOTYPE)

This isolated sidecar observes ACTS event collections. ACTS performs generation,
Geant4/Fatras transport, geometric digitization, truth association and Kalman
fitting. The observer neither changes measurements nor fits tracks.

Build against the exact existing source/runtime and pybind11 ABI; do not rebuild
or install shared dependencies:

```sh
source software/env/truth_tracking.sh
cmake -S software/source/ActsExamples/TruthTracking \
  -B build/truth-tracking-baseline/native -G Ninja \
  -DNODD_ACTS_SOURCE="$PWD/../nodd-software-layout/software/submodules/acts" \
  -DNODD_ACTS_BUILD="$PWD/../nodd-software-layout/build/acts" \
  -DPython_EXECUTABLE="$PWD/../nodd-software-layout/build/pyvenv/bin/python" \
  -Dpybind11_DIR=/path/to/matching/pybind11-3.0.4/share/cmake/pybind11
cmake --build build/truth-tracking-baseline/native --parallel 2
```

The current ACTS build uses pybind11 3.0.4, internals ABI11. The newer Spack-view
pybind11 3.1.0 has ABI12 and is rejected by a compile-time guard. Explicitly
select the existing matching package; no dependency install is required.

Example100-event pilot (production uses20000):

```sh
python software/running/nodd_truth_tracking.py \
  --simulation fatras --pt 1 --events 100 --threads 1 \
  --manifest docs/validation/gen3-material-map-run/selection.json \
  --nodd-dir ../nodd-software-layout \
  --build-dir ../nodd-software-layout/build/dd4hep \
  --output build/truth-tracking-baseline/pilot-fatras-pt1
```

Replace backend with `geant4` and momentum with1,10,100 as needed. Both transport
and fitting consume the effective constant field in `campaign.json`; the human
selected3T. Geant4 uses detailed DD4hep solids and FTFP_BERT, one thread,25ns
maximum global time and the native outer tracking volume as the kill volume.
Its sensitive mapper explicitly includes `Silicon` and `pixel_Silicon`.
Fatras enables native electromagnetic interactions. Neither backend kills
secondaries as a campaign customization. Primary truth tracking excludes neutral
and secondary candidates and requires7measurements, without a pT threshold.

The map is decompressed under the task-owned native build directory and loaded
through the PR100 keyed-map audit. All65portals/8550bins must match. Physical
DD4hep materials remain intact; existing silicon/pipe tracking slabs are cleared
before installing the complete map. No upstream ODD map is substituted.

Digitization entries use each actual native sensor geometry ID, physical
thickness and local Box u/v axes. Long strips have two physical segmentation
axes but only `indices:[0]`: precision80um bins in u and one full-length bin in
v. The native stereo face transforms already carry the relative angle. A
single-axis segmentation silently drops these hits in the pinned native
channelizer; the control is retained separately and excluded from the baseline.
Pixels and short strips have two measured coordinates. Non-divisible widths
are encompassed by a centred grid while preserving the exact requested pitch.

Digital activation, exact path-length charge, zero threshold, native clustering
and merging are explicit ideal-response choices. No added drift, diffusion,
charge noise or empirical variance table is introduced. The native merged
cluster variance uses the squared cell weights times width²/12, normalized by
total weight²; multiple-cell clusters can have smaller uncertainty than a
single pitch/√12. This is not calibrated electronics performance.

`audit.root/audit` retains every event, including zero-candidate events. Scalar
counts are `event_nr`, `generated`, `simhits`, `measurements`, `selected`,
`fit_attempts` (truth proto tracks passed to the native fitter), `fit_tracks`,
`invalid_covariance` and `primary_measurements`. Vectors retain measurement
geometry IDs and dimensions. Count differences distinguish the7measurement
selection from failed native fits. Invalid covariance counts missing reference
surfaces, nonfinite matrices or nonpositive diagonals; the downstream analysis
applies its own covariance checks. Fit output is retained without a post-fit
minimum-measurement cut.

`particles.root/particles` retains all generated truth. The standard native
`tracksummary_kf.root/tracksummary` contains truth association, fitted perigee
parameters and all36covariance components (`writeCovMat=True`). Native track
states and parameter-performance ROOT outputs are also written. Run reports
retain actual configuration, source/runtime/input/output hashes and ROOT schema.
Outputs are ignored; compact scientific reductions belong in the main report.

An old Geant4 default-material control was stopped before its first event during
expensive native production-cut initialization; its incomplete ROOT files are
not simulation evidence. Controls are named explicitly and excluded from the
campaign. Never reinterpret their raw output as the corrected pilot.

The human subsequently requested a Fatras error parametrization. `--training`
uses the independent `error_training` seed and log-uniform pT distribution from
campaign.json, retaining the standard native `measurements.root/measurements`
writer needed by ACTS `Examples/Scripts/Digitization/error_parameterisation.py`.
Training positions are not altered by the truth-proto correction or fitted
covariance calibration. Final performance runs pass `--error-table` with the
separately frozen RMS JSON. Native volume IDs and measured-coordinate sets must
match exactly; empty, nonfinite or nonpositive RMS data fail before simulation.

The pinned native clustering implementation recomputes merged-cluster covariance
and discards its pre-cluster variance table. The isolated `ClusterErrors`
algorithm therefore copies the native measurement collection after clustering,
preserving order, geometry IDs, values and associations. It sets measured
marginal variances to the frozen cluster-size RMS squared, zeroes off-diagonal
entries (the table defines independent marginals), and clamps overflow to the
last RMS entry. No calibration is performed on the independent training sample.

The pinned native truth finder also indexes measurement→simhit associations twice.
`CorrectTruthProtoTracks` retains the native association and time ordering while
using the direct simulated-hit index and deduplicating measurement indices.
The original helper output is retained in historical diagnostic controls. At
larger G4 statistics its invalid hit pointers caused segmentation violations in
two first-pass cases. Production therefore schedules the identical native
`ParticleTrackParamExtractor` and `TrackParameterSmearing` seed stages directly,
followed by the corrected proto finder; the unsafe original finder is never
executed. Its legacy count field is a zero sentinel with an explicit disabled
flag, not an observed comparison. Native ACTS still supplies the truth initial
parameters and the full Kalman filter/smoother. All six first-pass cases,
including completed and crashed outputs, are retained under
`pre-reference-removal-controls` and excluded from the final common-source run.

Geant4 `--geant4-run-mode persistent` uses the documented granular native event
loop: one run initialization, one `ProcessOneEvent`/`TerminateOneEvent` pair for
each independent ACTS event, then normal event-loop/run termination. ACTS still
clears its event store and sets the recorded per-event random seed. This avoids
repeated traversal of unchanged production-cut geometry for each `BeamOn(1)`.
The standard mode remains available. Before production, same-seed small controls
must compare all generated-particle and simulated-hit payloads between modes;
any mismatch is reported. `--write-simhits` retains the native `hits.root` for
this check. No several-particle Geant4 event replaces the single-muon events.

`UniqueAssociations` removes repeated (measurement, particle) pairs caused by
several simulated steps contributing to one merged cluster, retaining every
distinct particle label. The native inverse map then makes the7measurement
selection count unique physical measurements. The full measurement–simhit map
is preserved for truth averaging and charge contributions. Raw and unique
primary association counts are both retained. The scientific source revision
and all local implementation/binary hashes are captured at process launch;
later journal commits do not alter the recorded executed identity.
