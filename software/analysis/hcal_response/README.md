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


## DES046 variable edge units

The appended `unit:8` field occupies bits42–49. Existing bits0–41 and normal
unit0 cell identities remain unchanged. Each original or edge family supplies
an explicit channel subset, real core sizes, complete original parts, carrier
size and active anchor in `expected.json/units`. Each carrier template declares
its unit; the factory adds that ID exactly once on the compound sensitive child.
The segmentation table has nine fields per cell:
`unit,module,sensor,cx,cy,cz,sx,sy,sz`, in the active-volume local frame and mm.
There is no inferred fixed-width lattice. Missing subset addresses are invalid.

The converted-Geant4 gate reads the hash-bound physical-unit manifest and checks
every named sensitive solid against its source box-minus-recess regions, using
that solid's actual placement. The full readback includes unit bits in parent
IDs, validates the exact per-unit channel subset and checks every saved global
position against the corresponding physical centre. All original closure,
field/material/cut/process, map and worker checks remain required.

Use [the prospective protocol](../../../docs/validation/hcal50-edge/protocol.md)
and DES046. Preserve the first DES045 sample. To regenerate the matched angular
primaries, use `prepare --primary-sample ../nodd-hcal-pion50/build/hcal50/sample`;
the original HEPEvt/truth bytes and hashes are verified and copied unchanged.
The angular analysis accepts `--baseline-run` pointing to the original
`../nodd-hcal-pion50/build/hcal50/production12`. It resamples matched primary IDs
jointly across both geometries and angular projections, retains the joint
covariance and paired width differences, and writes a separate comparison plot.
The old published summary can still be replotted with `analyze.py plot`.

## Frozen fixed-direction calibration and validation

Root's geometry-only selector supplies an immutable JSON receipt containing
`winner.eta` and `winner.phi_rad`. Pass its values and file to preparation:

```sh
python3 -B software/analysis/hcal_response/transport.py prepare \
  --geometry build/hcal50-edge/geometry --output build/hcal50-edge/calibration-input \
  --fixed-eta "$eta" --fixed-phi "$phi" --direction-receipt "$direction_receipt" \
  --sample-role calibration --sample-id fixed-calibration --events 2000
```

Run and audit those2000 primaries with transport seed202650102. Freeze their
single effective response factor before analysing validation:

```sh
python3 -B software/analysis/hcal_response/analyze.py calibrate \
  --run build/hcal50-edge/calibration12 --output build/hcal50-edge/calibration.json
```

Prepare a separate10000-primary `--sample-role validation` input using the same
fixed receipt/direction, and run/audit it with seed202650103. The runner rejects
a seed inconsistent with its cohort role. Input vectors may be identical;
separate sample IDs and event-seed sequences distinguish independent showers.
Then use:

```sh
python3 -B software/analysis/hcal_response/analyze.py fixed-analyze \
  --run build/hcal50-edge/fixed-validation12 \
  --calibration-run build/hcal50-edge/calibration12 \
  --calibration build/hcal50-edge/calibration.json --output build/hcal50-edge/fixed-analysis
```

The three inclusive panels show raw energy S[GeV], raw fractional response
S/Etrue, and sampling-corrected relative residual S/(fs*Etrue)−1. Their summary
states sample SD, denominators, bias, quantiles, zeros and histogram counts.
A positive constant scale cannot improve SD/mean; the point estimate and every
defined bootstrap replicate check that identity. SD(S)/50 and SD(S)/(fs*50)
are true-energy-relative widths and differ from SD(S)/mean(S).

The1000 two-sample bootstrap replicates use independent validation/calibration
generators with seeds13001001/13001002. Each validation resample is shared across
all panels; each independent calibration resample refits fs for that replica.
The central result uses the original frozen fs, retaining validation bias.
Calibration fs, all scalar intervals, covariance and undefined counts are
retained. This effective50GeV pion response factor includes geometric and
hadronic losses; it is not an intrinsic material sampling fraction or evidence
that compensation, digitization or reconstruction has been supplied.
