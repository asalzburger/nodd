# DES036 — Common HCAL readout module checks

2026-10-15. **DRAFT / PROTOTYPE.** Isolated local geometry and budgeting evidence;
no production integration, detector acceptance or human engineering sign-off.

The isolated [common module](../../design/DES-036-hcal-common-readout-module.md)
was executed at `97d0bb64c22f63c0680c543a97c5b05ce2acc4b8`. Source/config,
XML, native library and checker identities are retained in [budgets.json](budgets.json),
[native.json](native.json) and [transport.json](transport.json). The recorded
dirty state includes the then-untracked evidence, drawing and session records;
module/native/transport implementation files matched that commit. The final
evidence commit only adds SVG whitespace normalization to the drawing producer;
it does not change the executed module or checks. The initial assignment was pinned at
`7f354fe20307b6fee996c7043e68e5d80dc23a8a`, with the explicit 1.1 mm recess
amendment recorded before final construction.

## Executed checks

| Check | Observed result |
| --- | --- |
| Standard-library module controls | **44 passed**, exit 0: 35 geometry/material/channel/service/budget controls and nine saved-run provenance/finiteness controls |
| Existing calorimeter hardware/assembly controls | **14 passed**, exit 0; earlier prototypes retained |
| Standalone CMake configure/build | Exit 0; separate `nODDHCALReadoutPrototype` factory, no production target |
| Native DD4hep/ROOT inspection | **PASS**, exit 0: 395 physical parts, 72 unique sensitive IDs, 360 local cell probes |
| Native overlaps | Zero reported at **1e−5 mm**, ROOT seed 36; single-thread check |
| Shape/material/placement ledger | Actual primitive dimensions, Boolean cutter transforms, constituent mass fractions, capacities, sensitivity and placements agree with the exported ledger |
| Material and sensitive rays | First/last tile: one sensitive crossing each; board seam and service bay: zero |
| Actual coolant-bore navigation | Both y-axis bores contain 240 mm water and no solid interruption along the sampled centreline |
| Saved Geant4 transport | **PASS**, exit 0: one event aimed at sensor 0 on each board; two finite positive-energy saved hits with valid IDs |
| Figure QA | Generated PNG inspected; board seam, service bay, tile recess and buried cooling cross-section visible |

Native checks use ROOT/DD4hep objects, not the analytic model's capacity or
intersection routines. Bore rays independently test native material navigation;
they do not establish fittings, flow or thermal transfer. Overlap, placement and
ray checks cover this fixture and tolerance, not manufacturing precision.

The transport runner used the executed gun argument `10*GeV`, direction +z,
seed 42, FTFP_BERT and a compact with no field definition. Each saved MC primary
was separately checked: PDG 13 and momentum `(0,0,10)` GeV/c. The gun argument
is therefore not described as a verified 10 GeV kinetic energy. Run settings
are verified against runner metadata and argv; their recovery from saved hit
data is not claimed. Actual event completion, primary properties, hit energies,
positions and identifiers are read from saved outputs. Input/output hashes bind
each run to the passing native compact, materials, inventory and library. The
local raw command metadata is hashed; the retained transport report replaces
absolute command paths with named aliases and retains component hashes.

## Conditional budgets

| Quantity | Value |
| --- | ---: |
| One 36-tile board, exclusive material | 207.354570 g |
| Shared carrier, exclusive material | 2,603.205642 g |
| Two boards + carrier | 3,017.914782 g |
| Fixture including once-only 30 mm steel patch | 24,495.514782 g |
| Powered channels / connected tiles | 156 / 72 |
| Nominal heat / ideal water flow at 5 K rise | 5.939381 W / 0.284181 g/s |
| 100 µA / 1 mA per-device current stress heat | 6.235733 W / 8.957333 W |
| DAQ utilization at 750 kHz / 1 MHz | 93.75% / **125%, OVERLOAD** |
| 512-sample memory at 25 ns minus 12.5 µs | 300 ns ideal margin |

These are inventory-derived quantities under DES036's stated project choices.
The heat excludes bias-regulation losses and does not predict irradiated SiPM
current. The shared 3 mm copper plate dominates carrier mass. A 6.25% nominal
DAQ arithmetic margin is small; framing, occupancy, finite FIFO queues, bursts
and the unselected carrier concentrator/egress still require a readout model.
Separate trigger lanes do not increase the DAQ allocation.

## Reproduction and runtime

Actual node runtime: DD4hep **1.38** (`7deaacd`), Geant4 **11.4.2** (`cpge6jj`),
ROOT **6.40.04** (`7nazwew`), Spack Python **3.14.5**. Standard-library controls
used system Python **3.14.6**. Drawing used already-installed Matplotlib
**3.11.2** in the existing ACTS virtual environment. No dependencies installed.

The node preflight warned that the setup and lockfile fingerprints had changed.
Runtime imports, versions, factory construction and Geant4 datasets were then
reverified in the activated environment. Sandboxed `sysctl`/`ps` diagnostics
and CMake dependency/policy warnings were retained. An early native attempt
hit ROOT parallel teardown after printing results; explicit single-thread
overlap operation and orderly teardown fixed it. Final commands exited zero.

From the repository root, run:

```sh
python3 -B -m unittest discover -s tools/hcal_readout -p 'test_*.py' -v
python3 -B -m unittest discover -s tools/calorimeter_hardware -p 'test_*.py' -v
python3 -B tools/hcal_readout/export.py --output build/hcal-readout/fixture
```

Activate the verified node-specific ACTS Spack environment, then its DD4hep
`thisdd4hep.sh` and Geant4 `geant4.sh` scripts. In that same shell:

```sh
cmake -S prototypes/hcal_readout -B build/hcal-readout/factory
cmake --build build/hcal-readout/factory --parallel 2
python3 -B tools/hcal_readout/native.py --compact build/hcal-readout/fixture/readout.xml --expected build/hcal-readout/fixture/expected.json --library build/hcal-readout/factory/libnODDHCALReadoutPrototype.dylib --output build/hcal-readout/fixture/native.json
python3 -B tools/hcal_readout/smoke.py --directory build/hcal-readout/fixture --library build/hcal-readout/factory/libnODDHCALReadoutPrototype.dylib
```

Use `.so` on Linux. The [tool guide](../../../tools/hcal_readout/README.md)
describes the deterministic exports and limits. ROOT files, complete inventory,
simulation logs and per-job metadata remain in ignored local build output;
their actual hashes are recorded, without promising byte-identical ROOT files
on rerun. Regenerating at a later Git revision changes the execution metadata.
The [drawing](../../design/figures/DES-036/common-module.svg) is generated by
`tools/hcal_readout/plot.py`; its [inputs](../../design/figures/DES-036/inputs.json)
bind the inventory and producer source.

## Review and remaining gates

[Independent PhysVal review](review.md) found two saved-hit checker defects at
`fe477db`: missing execution provenance and failure to reject NaN energy. Both
were corrected and independently reviewed at `97d0bb6`; nine new fault-injection
controls passed. The coordinator subsequently ran the final native and transport
commands above. The earlier 0.9 mm recess was also explicitly amended to 1.1 mm
to fit the sourced maximum package-height case; regression controls retain that
failure and the corrected geometry.

Next work is component/package selection and optical/tolerance characterization,
then a continuous-acquisition queue/occupancy model and thermal/hydraulic checks.
Luminosity, pileup, regional dose/fluence and lifetime temperature targets are
still needed before radiation feasibility can be assessed. Repeated structures
and full shower/digitization validation follow those gates. ACTS conversion is
not applicable to this local calorimeter module. No optical response, ASIC
emulation, sustained-rate, radiation, fabrication, structural or thermal
qualification was run. DES036 remains DRAFT with human engineering sign-off
pending.
