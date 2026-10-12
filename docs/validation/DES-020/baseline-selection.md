# DES-020 — Phi-tilted short-strip barrel baseline selection

2026-10-06. The user selected+15° same-radius staves as the working baseline and requested a PR and review notification. DES-020 remains DRAFT. This selects the detailed barrel executable defaults; subsystem/endcap integration and engineering qualification remain open.

## Executable behavior

`model.load()`, model/export/coverage CLIs without `--input`, and the standalone CMake `compact/` select the unchanged `inputs-phi-tilted.json`. Populations44/56/80/108 give288 staves/8,064 modules/990,904,320 channels. Nominal radii260/340/480/660mm, active±1200mm, sensor U/V/N, local assembly, cells, services and input bytes are unchanged from the retained tilted alternative.

`inputs.json` is an explicit historical control. CMake `compact-control/` builds its284 staves/7,952 modules. Historical figure generators explicitly choose that control so a default change cannot silently redraw the old study as tilted. Existing figures, native/ROOT/Geant4 results and angle/mounting failures are preserved.

## Actual checks

Fresh standalone configure/build and all3 CTests passed:11 Python model controls, tilted default native audit and explicit tangential native audit. The default model CLI printed8,064 modules/288 staves. Its full generated layout matches the retained tilted placement, requiring exact structure/discrete values and the established8ULP serialized float envelope. No tolerance was changed.

The [new default native audit](baseline-selection/native.json) and [explicit control audit](baseline-selection/native-control.json) both pass unchanged1e−5mm overlaps, sensor/constituent transforms, identifiers, anisotropic cells, mass/material inventories and sparse navigation rays. Default has8,064 sensors/251,610 physical placements; control has7,952/248,118. Actual execution was dirty starting0f1ac4c622546535396d95c145d11fccf8b01755 plus exact recorded compact/input/producer/library hashes. Publication commits do not replace those execution revisions. DD4hep imported, ROOT6.40.04 and Geant411.4.2 verified after registry fingerprint warnings; shared dependencies were unchanged. Geant4/ROOT persistence/coverage are the retained previous executions, not new reruns.

All38 pre-existing DES-020 retained artifacts, input JSON files and drawings were checked byte-identical. The new baseline selection files are additive. Logger/dashboard validation and full start/main-relative whitespace checks are recorded in the [task journal](../../../logs/design/SESSION-2026-10-06-short-strip-tilted-baseline.md).

## Coverage and remaining gates

The identical103,040-track refined sample retains the same eligible nominal-cylinder denominator for each layout:

| Model | Eligible crossings | Tangential misses | Tilted misses |
|---|---:|---:|---:|
| Straight |183870|1311 (0.713%)|225 (0.122%)|
| Positive,1GeV/4T |182446|1132 (0.620%)|210 (0.115%)|
| Negative,1GeV/4T |182448|1135 (0.622%)|174 (0.095%)|

These count missed eligible layer crossings, not track efficiency. Both have zero sampled misses beyond100mm from nominal ends, but nonzero end losses mean full sampled coverage still fails. Tilt and inventory differ together; no tilt-only performance or continuum claim. See [retained tilted report](phi-tilted/results.md).

Collector51.54% mean fill still exceeds50%, the65mm collector end1310mm conflicts with the old strip disc1295.5mm datum, and adverse service, warm/channel-scaled thermal and data cases remain failed. Seat/web/bond/clamp/torsion, electronics/CTE, hydraulics/dry-out, bending/manifold access and full-detector integration require review. Baseline selection does not close these gates or grant design sign-off.

## Resource accounting

Usage-only recovery verifies three completed turns with persisted disjoint boundaries and every request increment reconciled. Canonical owners are the original barrel session, phi alternative session and read-only coverage-comparison session. Dry-run then import recorded the five actual counters once each; the [curated inventory](../../../logs/usage/USAGE-2026-10-06-short-strip-barrel-turns.json) retains original recovery source, request counts, event hashes and attribution. Combined observed total28,362,996tokens (input28,120,009/output242,987); cached27,107,072 and reasoning123,635 are subsets. Execution model/client version remain unknown. Active baseline-promotion and later bookkeeping counters and older project gaps are excluded; this is not an all-project total.
