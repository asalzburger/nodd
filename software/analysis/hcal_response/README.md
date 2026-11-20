# Standalone HCAL 50 GeV pion transport

Isolated DES-045 DRAFT/PROTOTYPE. Uses the unchanged DES-036 scintillator/passive
solid material domains with a compound sensitive carrier representation and
explicit module/tile cell addressing. No optical response, Birks quenching,
SiPM saturation, digitization, calibration or reconstructed energy is applied.

Follow `docs/validation/hcal50/protocol.md` and the acts-spack preflight. Build:

```sh
software/env/run.sh cmake -S software/analysis/hcal_response -B build/hcal50/audit -G Ninja -DCMAKE_BUILD_TYPE=Release
software/env/run.sh cmake --build build/hcal50/audit --parallel 3
python3 -B software/analysis/hcal_response/transport.py prepare --geometry build/hcal50/geometry --output build/hcal50/sample
```

Run/audit first the 24-event serial and MT controls in fresh directories using
`run --events 24 --threads 1` / `--threads 12`, the same sample and transport seed
202650001. Then run/audit `--events 10000 --threads 12`. Each `run` requires
`--sample`, `--output`, `--geometry-library`, and `--audit-library`; the latter
is `build/hcal50/audit/libnODDHCALResponseAudit.dylib` on the tested macOS node
(use the platform library suffix elsewhere). Serial maps are populated before
worker creation. The actual converted Geant4 sensitive solids are checked at
11,467 points each against the original tile box-minus-recess material domains,
including edges, reflector gaps, board seams and service areas. Producers,
inputs, libraries and actual geometry artifacts are hashed before and after transport. Full native geometry/sample/ROOT/log/event
ledgers stay local under ignored `build/`.

```sh
software/env/run.sh python3 -B software/analysis/hcal_response/transport.py audit --sample build/hcal50/sample --run build/hcal50/serial24
software/env/run.sh python3 -B software/analysis/hcal_response/transport.py audit --sample build/hcal50/sample --run build/hcal50/mt24
python3 -B software/analysis/hcal_response/transport.py compare --first build/hcal50/serial24 --second build/hcal50/mt24 --output build/hcal50/serial-mt.json
python3 -B -m unittest discover -s software/analysis/hcal_response -p test_transport.py -v
```

An independent stepping observer sums every positive Geant4 energy deposit in
sensitive PSHost volumes and requires closure against native calorimeter hit
sums before writing an event receipt. Saved readback checks both collections,
complete unique primaries, momentum/energy/direction, exact canonical IDs and
parent placement membership, cell counts and energy closure against native hit
sums. Every saved global position is compared with its original physical tile
center transformed by the exported carrier pose; the 0.001 mm tolerance covers
persisted float32 position rounding. The readback records its auditor source
hash separately from the frozen transport launcher hash. Closure tolerances allow double summation and persisted float rounding;
they do not hide missing/invalid deposits. The 60-bin longitudinal profile and
last-six-layer fraction are recorded for every primary, including zero events.

World-boundary escaped kinetic energy is a separate diagnostic. It is not a
complete calorimetric energy balance, includes no escaped rest mass and does
not identify local rear/side leakage or repeated local HCAL boundary crossings.
The earliest primary inelastic-process position is recorded when observed.
Serial/MT comparison uses exact saved cell IDs, deposits and positions by event
ID. Neither successful execution nor these numerical checks grant engineering
approval or full-energy collider containment.
