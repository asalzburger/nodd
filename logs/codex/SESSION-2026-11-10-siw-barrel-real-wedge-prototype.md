# SESSION-2026-11-10-siw-barrel-real-wedge-prototype — Si–W barrel with real wedge mothers

The user asked, “Can you try a Prototype? Don’t change the baseline yet.”
This prototype is isolated in ignored build storage. The maintained geometry
checkout at `a8630d48baee5b17c8b0dee387b3f47d34c8ae49` has a clean tracked tree.
The separate C++ factory builds one real polygonal wedge mother and reuses
it at each stock sector transform. The wedge uses the exact ambient Air
material. Stock board and layer shapes, transforms and segmentation are
reused. Side and sector move to the wedge placement and layer stays on the
sampling-region placement.

The acts-spack preflight warned about changed setup and lock fingerprints.
The fresh environment verified DD4hep 1.38 /3yd4hz3, Geant4 11.4.3 /wfg55xi,
ROOT 6.40.04 and all listed datasets. The first local compile rejected the
XML child tag type. The first DDSim launch also rejected Python imports
outside the callback scope. Both failed attempts are retained. The
corrected local factory and all three timing cases exited normally.

| Case | Sensitive paths | Geant4 placement objects | DDG4 map time | Zero-event wall |
| --- | ---: | ---: | ---: | ---: |
| Stock, four sectors | 89,976 | 2,205,213 | 175.40 s | 182.61 s |
| Real wedge, four sectors | 89,976 | 551,308 | 1.09 s | 6.57 s |
| Real wedge, sixteen sectors | 359,904 | 551,320 | 4.21 s | 10.86 s |

The single-thread DDSim probes shared the same Mac Studio. Both matched
four-sector compacts are barrel-only and run a zero-event macro with
the same Geant4 configuration and touchable audit. The actual DDG4 volume
IDs, silicon material and world transforms match for all 89,976 A/B
sensors. The full prototype resolves all 359,904 expected volume IDs
and agrees with the sector-0 control rotated through all sixteen sectors.
Maximum position difference is 4.55e-13 mm. The native ROOT comparison
checks 81 rays for matched material lengths and active-layer crossings.
The analytic containment check covers all 33,941 piece and board bounds in
the shared wedge. The narrowest clearance is 0.245 mm and the wedge angular
inset keeps neighboring envelopes disjoint. Full union overlap validation
and a calorimeter response campaign remain follow-up work.

One full-barrel prototype electron with nominal pT 50 GeV, eta 0.50,
phi 0.123 rad, zero field, 0.7 mm range cut and 5 mm sensitive step limit
transported and persisted 874 valid barrel hit cells. This is a transport
smoke test. The measured comparison covers the isolated barrel and uses
neither endcap nor tracker components.

## Reproduce locally

Use a fresh ignored build directory containing the retained `source/`,
`run.py`, `steering.py`, `audit.hpp` and audit scripts. The input directory
contains the verified prior pilot's `detector.xml`, `materials.xml` and
stock Si–W factory. From the nODD repository root, with those two directories
assigned to the shell variables `prototype_dir` and `pilot_dir`:

```sh
software/env/run.sh cmake -S "$prototype_dir/source" -B "$prototype_dir/factories" -G Ninja -DCMAKE_BUILD_TYPE=Release
software/env/run.sh cmake --build "$prototype_dir/factories" --parallel 2
software/env/run.sh python3 -B "$prototype_dir/run.py" "$pilot_dir" "$prototype_dir" stock:4 wedge:4 wedge:16
python3 -B "$prototype_dir/containment.py" "$prototype_dir/wedge-16"
stock_lib="$pilot_dir/factories/libnODDCalorimeterPrototype.dylib"
wedge_lib="$prototype_dir/factories/libnODDBarrelRealWedgePrototype.dylib"
software/env/run.sh python3 -B "$prototype_dir/material_rays.py" "$prototype_dir/stock-4" "$stock_lib"
software/env/run.sh python3 -B "$prototype_dir/material_rays.py" "$prototype_dir/wedge-4" "$stock_lib" "$wedge_lib"
python3 -B "$prototype_dir/compare.py" "$prototype_dir" "$pilot_dir"
```

The original prototype directory contains the resulting `results.json`,
the smoke steering, macro and audit, and the local logs and ROOT output.
The active client turn had no exposed exact token counters.

## 2026-11-11 accounting correction and publication

Exact closed-turn usage is now recorded from the [PR129 recovery inventory](../usage/USAGE-2026-11-11-pr129-siw-wedges.json), using matched app request/turn IDs and verified parent/child metadata. Earlier statements that counters were unavailable describe the active-turn observation at the time. No counters are estimated or shared between canonical owners. The active merge-readiness turn and other-device/reviewer-task history remain excluded.

This original paired record is published with PR129 from the preserved pilot worktree; its original Git provenance, checks and scientific limits remain intact. Only attribution, exact usage and this dated correction are added. The pilot worktree remains unchanged.
