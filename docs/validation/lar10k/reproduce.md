# Reproduce the matched raw-response comparison

Follow the [prospective protocol](protocol.md). Use the node-verified existing
Spack installation through `software/env/run.sh`; no shared package changes are
needed. Full XML, ROOT files, event ledgers and logs stay under ignored `build/`.

The retained exact Si–W inputs are in
`../nodd-ecal10k/build/ecal10k/production-input`; original and staggered audited
responses are in `../nodd-ecal10k/build/{ecal10k,ecal-staggering}/production12`.
Their regeneration recipes are in the retained Si–W validation reports. The
analysis checks their distinct compact hashes and the common primary hashes.

```sh
work=build/lar10k-resume
python3 -B tools/calorimeter_baselines/export.py --layout LAYOUT-002 --output "$work/layout002"
python3 -B software/analysis/lar_response/transport.py prepare \
  --baseline "$work/layout002" \
  --primary-sample ../nodd-ecal10k/build/ecal10k/production-input --output "$work/sample"
software/env/run.sh cmake -S software/analysis/lar_response -B "$work/audit" -G Ninja -DCMAKE_BUILD_TYPE=Release
software/env/run.sh cmake --build "$work/audit" --parallel 3
```

Build the LAr barrel/endcap factories using the existing
[component recipe](../../../tools/lar_calorimeter/README.md), or use the unchanged
PR138 artifacts after verifying their recorded hashes. Set `barrel_library`,
`endcap_library` and `audit_library` to the actual platform-specific paths.
The executed macOS artifacts use `.dylib`; Linux uses `.so`.

```sh
software/env/run.sh python3 -B software/analysis/lar_response/transport.py run \
  --sample "$work/sample" --output "$work/production12" \
  --geometry-library "$barrel_library" --geometry-library "$endcap_library" \
  --audit-library "$audit_library" --events 10000 --threads 12 \
  --seed 133812341 --max-step-mm 5 --reserve-gib 30
software/env/run.sh python3 -B software/analysis/lar_response/transport.py audit \
  --sample "$work/sample" --run "$work/production12"
```

Before production, use fresh directories for serial/MT24-event controls (threads
1/12, cap5) and the two 100-event pilots (threads12, cap0/5). Compare controls
by saved event ID, including individual cells, energies and positions. Cap0
preserves native limits. Both pilot readbacks must pass; their response
differences are a gross sensitivity diagnostic, not a convergence test or a
policy-selection procedure. The five-millimetre production cap is predeclared.
[Controls](controls.json) retain compact results and exact receipt bindings.

Serial preinitialization populates both volume managers and all 43,648 raw native
contexts before worker creation. Each worker audits native materials, cuts,
field, step limits and processes; full readback validates every primary and hit.
The observed sequential Geant4 thread ID is −1; production requires all twelve
worker IDs0–11. A successful transport exit and successful saved-data readback
are separate checks.

The existing pure plotting Python is
`/Users/salzburg/Documents/work/installed/acts-nodd/pyvenv/bin/python`
(NumPy2.5.4, Matplotlib3.11.2 in the executed environment). It needs no native
ACTS geometry build for this analysis. Use any equivalent recorded analysis
environment on another node.

```sh
plot_python=/Users/salzburg/Documents/work/installed/acts-nodd/pyvenv/bin/python
"$plot_python" -B software/analysis/lar_response/compare.py analyze \
  --siw-original ../nodd-ecal10k/build/ecal10k/production12 \
  --siw-staggered ../nodd-ecal10k/build/ecal-staggering/production12 \
  --lar "$work/production12" --protocol docs/validation/lar10k/protocol.md \
  --bootstrap 1000 --seed 13001000 --output "$work/comparison"
MPLCONFIGDIR="$work/mpl-cache" "$plot_python" -B software/analysis/lar_response/compare.py plot \
  --summary "$work/comparison/summary.json" --output "$work/figures"
```

Use fresh output directories; commands reject accidental sample/run/analysis
overwrites. The committed compact summary permits replotting without event data;
rerunning full source-binding checks needs the retained local ROOT/input files.
