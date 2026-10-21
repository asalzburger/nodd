# Matched material-recording profiling

This node-bound tool compares existing ODD and nODD tracker compacts without
editing their physical material. See the [findings report](../../docs/validation/material-recording-profile/README.md).
Run each detector in a fresh process. Generated data belongs under ignored
`build/jobs`, never in Git.

The runtime argument explicitly selects the existing software-layout source,
ACTS build, Python environment and nODD factories. It does not run an installer,
copy ODD data into a shared installation, or modify a dependency. Read the
repository's acts-spack instructions and run their preflight first. The ODD
factory defaults to this task's `build/odd/factory/libOpenDataDetector.dylib`;
`ODD_FACTORY` overrides that exact library path. Source/binary identity must be
verified separately. Both detectors load DDG4 before PyROOT to give their XML
runtime the same initialization order. A factory rebuild alone does not fix
mixed Xerces initialization in the existing dependency environment.

```sh
runtime=/Users/salzburg/Documents/ChatGPT/agentic-detector/nodd-software-layout
view=/Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view
out="$PWD/build/jobs/material-profile"
mkdir -p "$out"
zsh tools/material_recording_profile/build_odd.sh "$runtime" "$PWD/build/odd"

# Matched primary comparison, sequentially, with explicit 100 × 100 defaults.
zsh tools/material_recording_profile/one.sh "$runtime" nodd "$out/nodd-100" --inventory > "$out/nodd-100.log" 2>&1
zsh tools/material_recording_profile/one.sh "$runtime" odd "$out/odd-100" --inventory > "$out/odd-100.log" 2>&1

"$runtime/build/pyvenv/bin/python" tools/material_recording_profile/summarize.py \
  "$out/odd-100" "$out/nodd-100" "$out/results.json"
```

Defaults are100 events,100 probes/event, seed228, uniform eta[-4,4],
phi[0,360degrees], origin vertex and one thread. Additional options passed to
`one.sh` override the explicit defaults using the standard argument parser.
The ODD wrapper preserves native definitions and all tracker/PST/passive
components, removes the explicit Solenoid include, and excludes calorimeter,
muon and fields. Its provenance file hashes the entire source XML tree.

`metrics.json` records wall/phase CPU intervals, cumulative total process CPU,
event markers and Darwin peak RSS in bytes. Total CPU includes interpreter and
preload startup before the wall interval. Framework `timing.csv` separately records writer cost. `--inventory`
collects native TGeo and Geant4 counts after the timed interval;
`--inventory-only` constructs the pipeline without transporting events.
`loaded-libraries.json` audits and hashes resolved images after timing. Initial
steering/runtime and factory hashes remain inside the timed phases.

For macOS native phase timing:

```sh
zsh tools/material_recording_profile/build_native.sh "$view" "$out/libNativeTiming.dylib"
NATIVE_TIMING_LIBRARY="$out/libNativeTiming.dylib" \
  zsh tools/material_recording_profile/one.sh "$runtime" nodd "$out/nodd-phases" \
  --events 2 --tracks 100 --inventory --step-timing > "$out/nodd-phases.log" 2>&1
```

The native helper forwards calls through dyld's interposition ABI. It times
actual Xerces parsing, DD4hep conversion, cut-table updates, geometry closure
and event processing. Not every virtual/internal call can be intercepted;
Python/framework intervals supply the containing phases. Timers are inclusive;
do not sum nested entries. `--step-timing` wraps the existing material stepping
callback and includes measurement overhead; use it for diagnostic attribution,
not the primary uninstrumented timing. The helper uses hidden inline visibility.
Keep DDG4 first even with the helper: startup order measurably affects timings
and parsing in this environment, with its precise native mechanism unresolved.

The opt-in reuse prototype is restricted to this immutable, single-world
neutral-geantino harness. It validates the existing material/cut association of
every logical volume, rejects changed or unsupported states, and otherwise
delegates to the original Geant4 update. A user energy-cut vector disables reuse
for the process lifetime. It does not change cuts or the `BeamOn(1)` lifecycle.

```sh
MATERIAL_REUSE_STATIC_COUPLES=1 NATIVE_TIMING_LIBRARY="$out/libNativeTiming.dylib" \
  zsh tools/material_recording_profile/one.sh "$runtime" nodd "$out/nodd-reuse-100" \
  --inventory --guard-check > "$out/nodd-reuse-100.log" 2>&1
"$runtime/build/pyvenv/bin/python" tools/material_recording_profile/compare_output.py \
  "$out/nodd-100/tracks.root" "$out/nodd-reuse-100/tracks.root" "$out/nodd-equality.json"
```

Run the same candidate command with `odd` for its control. `--guard-check`
performs adverse tests **after transport**, restores the changed pointers/cut
values and rebuilds geometry after the open-geometry test. The final energy-cut
vector test leaves reuse disabled; no subsequent event is processed. These
checks can add substantial elapsed time after the reported benchmark interval.
Output comparison aligns tracks by event and generated direction and requires
exact values in every scalar and jagged ROOT branch, not identical ROOT bytes.

Attach the system native profiler to a task-owned process during first-event
and steady-state windows. Process attachment may require desktop/sandbox
permission. The process ID is recorded in its metrics file.

```sh
sample PROCESS_ID 15 2 -mayDie -file "$out/nodd-steady.sample.txt"
python3 tools/material_recording_profile/sample_summary.py \
  "$out/nodd-steady.sample.txt" "$out/nodd-steady.summary.json"
python3 -B -m unittest discover -s tools/material_recording_profile -p 'test_*.py' -v
```

The summary excludes idle worker threads, accounts for recursive frames once
in cumulative counts and retains exclusive leaf counts. Sampling percentages
are approximate. Preserve full raw profiles locally; curate only relevant
stacks and portable summaries into the scientific report.
