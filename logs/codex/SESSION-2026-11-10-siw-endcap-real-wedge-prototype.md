# SESSION-2026-11-10-siw-endcap-real-wedge-prototype — Si–W endcaps with real wedge mothers

The user asked, “Ok, repeat that for the Endcap.” The preceding barrel
prototype defined the isolated scope. The maintained nODD checkout remains
at `a8630d48baee5b17c8b0dee387b3f47d34c8ae49` with a clean tracked tree.
The endcap test reuses one real polygonal wedge for both sides, with the
same Air material as the parent world. Its axial offset keeps the stock
global placement of every layer. The existing negative-side rotation,
custom tile shapes, material recipes and readout XML remain the reference.
Side and sector are encoded on the wedge placement, layer on the sampling
region and module on the original active sensor. The prototype factory and
run outputs live in ignored build storage.

The acts-spack preflight reported changed setup and lock fingerprints.
Fresh imports and dataset checks verified DD4hep 1.38 /3yd4hz3,
Geant4 11.4.3 /wfg55xi, ROOT 6.40.04, podio and EDM4hep on the same Mac Studio.

| Endcap geometry | Wedges per side | Sensitive paths | Geant4 placement objects | DDG4 map | Zero-event wall |
| --- | ---: | ---: | ---: | ---: | ---: |
| Stock | 4 | 43,008 | 921,617 | 32.91 s | 37.05 s |
| Real wedge | 4 | 43,008 | 115,211 | 4.58 s | 7.91 s |
| Real wedge | 16 | 172,032 | 115,235 | 17.82 s | 21.68 s |

The matched single-thread runs use stock material, transforms and
Geant4 setup. All 43,008 matched Geant4 touchables agree in volume ID,
material and world transform. Both full prototype endcaps recover all
172,032 expected IDs, with the sector-0 controls rotated through each
side. The maximum position difference is 9.10e-13 mm. All 144 native ROOT
material rays agree to within 3e-10 mm in per-material path length and
agree exactly in sensitive-layer crossings. The conservative envelope
bound checks 115,202 physical piece bounds per logical wedge and finds
0.245 mm minimum clearance. The air wedge envelopes are mutually
disjoint. Their nearest axial gap to the earlier barrel envelope is
29.5 mm. The scope is a prototype geometry and transport check.

The isolated full endcap prototype transported one nominal pT 50 GeV
electron at each of eta +2 and -2, with mirrored phi and zero field.
The initial smoke readback rejected hits outside the aimed side. The
negative shot produced three small hits in the positive endcap. Their
positions agree with the positive sensor planes, and their linked
shower ancestors were produced on the negative side. The corrected
audit validates every hit against its sensor plane and side. It finds
2,456 hits in the positive shot and 2,359 targeted plus three opposite
hits in the negative shot. Both event files are retained. Maximum
hit-plane residual is 0.000196 mm. These samples establish transport
and hit-ID functionality.

Combining both real-wedge prototypes in the same ECAL-only compact
produced **531,936 sensitive paths in
23.53 seconds**, with
31.55 seconds total zero-event startup. All
mapped IDs, silicon materials and transforms agree exactly with the
isolated prototypes. The stock ECAL pilot's saved map build took
3953.835 seconds on the same node, giving
a map-only ratio of 168.0. The stock reference
is the prior retained measurement. The new combined startup is a
zero-event run. A full-detector native overlap and shower-response
campaign is outside this test.

## Reproduce locally

Use a fresh ignored prototype directory containing the retained
`source/`, runner and audit scripts. The previously retained ECAL-only
stock compact and factory directory is `pilot_dir`. The retained barrel
prototype directory is `barrel_dir`. Run from the maintained repository
root with the existing Spack runtime.

```sh
software/env/run.sh cmake -S "$prototype_dir/source" -B "$prototype_dir/factories" -G Ninja -DCMAKE_BUILD_TYPE=Release
software/env/run.sh cmake --build "$prototype_dir/factories" --parallel 2
software/env/run.sh python3 -B "$prototype_dir/run.py" "$pilot_dir" "$prototype_dir" stock:4 wedge:4 wedge:16
python3 -B "$prototype_dir/containment.py" "$prototype_dir/wedge-16"
stock_lib="$pilot_dir/factories/libnODDCalorimeterPrototype.dylib"
endcap_lib="$prototype_dir/factories/libnODDEndcapRealWedgePrototype.dylib"
software/env/run.sh python3 -B "$prototype_dir/material_rays.py" "$prototype_dir/stock-4" "$stock_lib"
software/env/run.sh python3 -B "$prototype_dir/material_rays.py" "$prototype_dir/wedge-4" "$stock_lib" "$endcap_lib"
python3 -B "$prototype_dir/compare.py" "$prototype_dir" "$pilot_dir"
software/env/run.sh python3 -B "$prototype_dir/run_combined.py" "$pilot_dir" "$prototype_dir" combined:16 "$barrel_dir"
```

The `smoke/` directory retains the steering file, macro, saved events
and readback script. Run that macro with the stock and prototype
libraries in `DD4HEP_LIBRARY_PATH` and `DYLD_LIBRARY_PATH`, with
`I118_TRANSPORT_AUDIT` set to a fresh output path. Use DDSim with
`--runType run --enableG4Gun --numberOfThreads 1 --random.seed 23019999
--physics.list FTFP_BERT --physics.rangecut 0.7 --part.userParticleHandler ""
--outputConfig.forceEDM4HEP` on the full endcap prototype compact.
After readback, `compare_combined.py` collects the combined validation
and smoke evidence into `results.json`. Exact client usage counters
were unavailable during this active turn.

## 2026-11-11 accounting correction and publication

Exact closed-turn usage is now recorded from the [PR129 recovery inventory](../usage/USAGE-2026-11-11-pr129-siw-wedges.json), using matched app request/turn IDs and verified parent/child metadata. Earlier statements that counters were unavailable describe the active-turn observation at the time. No counters are estimated or shared between canonical owners. The active merge-readiness turn and other-device/reviewer-task history remain excluded.

This original paired record is published with PR129 from the preserved pilot worktree; its original Git provenance, checks and scientific limits remain intact. Only attribution, exact usage and this dated correction are added. The pilot worktree remains unchanged.
