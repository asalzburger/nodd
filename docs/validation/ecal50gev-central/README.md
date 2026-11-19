# Central 50 GeV electron validation

**PROTOTYPE, ECAL-only B=0.** New single-electron showers at one fixed direction:
total energy **50 GeV**, **η=0.1**, **φ=+0.7°**, origin vertex. This compares the
selected restored 1.8 mm Pb LAr baseline with the physically staggered Si–W
comparator. It uses 2,000 independent calibration events and 10,000 held-out
evaluation events per detector. The earlier broad-spectrum sample is not reused.

## Requested observables

| Graph | Definition | Reported spread |
| --- | --- | --- |
| Raw Geant4 deposited energy | S=sum of active barrel+endcap ECAL hit deposits, GeV | Sample SD(S), SD(S)/mean(S) |
| Raw deposited-energy fraction | R=S/50 GeV | SD(R)=SD(S)/50, mean(R), SD(R)/mean(R) |
| Sampling-response corrected fraction | T=S/(f×50 GeV), f=mean_calibration(S/50 GeV) | Held-out mean(T), SD(T), SD(T)/mean(T) |

The summed sensitive collections are `BARRELHits`+`EDGEHits` for Si–W and
`LArBarrelHits`+`LArEndcapHits` for LAr. These are raw active-medium energy
deposits before digitization. Absorber/support energy deposits are not included
in these sensitive-hit sums.

The independently fitted f is an **effective visible response fraction**. It
includes sampling, containment and dead-material losses at this energy/direction;
it is not a separately scored active/(active+passive) material sampling fraction.
Evaluation events are not recentered. A constant 1/f correction changes the
energy scale and SD normalized to the beam energy; **SD/mean stays exactly
unchanged**. No Gaussian fit, tail rejection, leakage correction, electronics
noise or reconstructed-resolution claim is introduced.

## Direction and geometry

φ=0 crosses internal tangential board gaps in this exact Si–W compact. A
geometry-only clearance scan before the new showers selected φ=+0.7°, close to
the maximum-minimum tangential clearance near +0.7020°. The direction is 10.55°
from the nearest sector boundary, with at least 16.797942 mm tangential active
clearance across the sensor thicknesses. It intersects active silicon in 44/48
layers. At fixed η=0.1, layers 18, 19, 22 and 23 remain in small staggered axial
row gaps. This is a favourable interior direction, not globally optimized shower
response or a completely gap-free trajectory. The same direction is used for LAr.

Geometry identities, point, numerical transport policy, seeds, population sizes
and statistical definitions were frozen in [protocol.json](protocol.json) before
production. [Pilot controls](pilot-controls.json) retain the complete 100-event
readbacks and measured disk forecast. Geometry and validated binary artifacts are
the same as the [restored LAr](../lar-restored/README.md) and
[matched Si–W](../lar10k/README.md) controls.

[Direction evidence](direction-controls.json) · [Per-layer ray intersections](direction-reproduced.json) ·
[Reverified environment](environment.json) · [Specialist assessments](reviews.json).
The reference ray check can be repeated without the native runtime:

```sh
python3 -B software/analysis/lar_response/central_direction.py \
  --compact ../nodd-ecal10k/build/ecal-staggering/production-input/detector.xml \
  --eta 0.1 --phi-deg 0.7 --output build/ecal50gev-repeat-direction.json
```

Adding `--scan` repeats the predeclared 0…8° geometry-only scan with 0.0001°
spacing. This analytical rectangle/prism check is separate from native
navigation and shower-response validation.

## Independence and uncertainty

| Detector | Calibration events / seed | Evaluation events / seed |
| --- | --- | --- |
| LAr | 2,000 / 705020 | 10,000 / 705021 |
| Si–W | 2,000 / 705030 | 10,000 / 705031 |

Event identity is the composite `(detector, population, transport_seed, event)`.
The repeated primary four-vectors are intentionally identical; independent
transport seeds distinguish the samples. Pilot seeds 705019/705029 are excluded
from inference. Every evaluation event, including zeros and tails, is retained.

Pointwise 95% percentile intervals use 1,000 independent whole-event bootstrap
replicates, seed 5019001. Each detector's calibration and evaluation populations
are independently resampled; one common f is refitted per replicate. Calibration
uncertainty is not added as independent per-event noise. The summary retains
labelled scalar covariance and contrasts. Intervals condition on these saved
transports and exclude detector/material/physics-list systematics. Repeated
showers at one energy and direction do not validate transfer to another energy,
direction or a full detector with upstream material/field.

## Reproduce

Use the existing node-specific ACTS Spack runtime after its preflight and actual
doctor check. No dependency installation is required. The recorded runtime is
DD4hep 1.38, Geant4 11.4.3 and ROOT 6.40.04. Native transport uses FTFP_BERT,
0.7 mm production cuts, 5 mm maximum active charged step, event seeding and
twelve workers per process. LAr and Si–W lanes may run concurrently; timings are
descriptive, not a throughput comparison.

Prepare exact fixed primaries on the retained, hash-verified ECAL-only compacts:

```sh
python3 -B software/analysis/lar_response/central_sample.py \
  --protocol docs/validation/ecal50gev-central/protocol.json \
  --lar-source ../nodd-lar-compact-hadron/build/lar-restored/sample \
  --siw-source ../nodd-ecal10k/build/ecal-staggering/production-input \
  --output build/ecal50gev-repeat/inputs
```

Each output sample manifest binds the protocol, exact geometry/material and new
primary bytes, point, population and intended transport seed. Use fresh run
directories. For each detector first run/audit the 100-event pilot, then the
2,000 calibration and 10,000 evaluation populations, with the seeds above.
Retain a 30 GiB free-space reserve and require the full requested counts; do not
silently reduce them. The pilot forecast uses twice all projected production
bytes plus that reserve.

LAr example, substituting the matching population/count/seed:

```sh
lar_build=../nodd-lar-compact-hadron/build/lar-restored
software/env/run.sh python3 -B software/analysis/lar_response/transport.py run \
  --sample build/ecal50gev-repeat/inputs/calibration/lar \
  --output build/ecal50gev-repeat/calibration/lar \
  --geometry-library "$lar_build/factories/libnODDLArBarrelPrototype.dylib" \
  --geometry-library "$lar_build/factories/libnODDLArEndcapPrototype.dylib" \
  --audit-library "$lar_build/audit/libnODDLArResponseAudit.dylib" \
  --events 2000 --threads 12 --seed 705020 --max-step-mm 5 --reserve-gib 30
software/env/run.sh python3 -B software/analysis/lar_response/transport.py audit \
  --sample build/ecal50gev-repeat/inputs/calibration/lar \
  --run build/ecal50gev-repeat/calibration/lar
```

Si–W example:

```sh
siw_build=../nodd-ecal10k/build/ecal10k
software/env/run.sh python3 -B software/analysis/calorimeter_digitization/angular_sample.py run \
  --sample build/ecal50gev-repeat/inputs/calibration/siw \
  --output build/ecal50gev-repeat/calibration/siw \
  --geometry-library "$siw_build/calo/libnODDCalorimeterPrototype.dylib" \
  --audit-library "$siw_build/audit/libnODDAngularAudit.dylib" \
  --events 2000 --threads 12 --seed 705030 --reserve-gib 30
software/env/run.sh python3 -B software/analysis/calorimeter_digitization/angular_analyze.py audit \
  --sample build/ecal50gev-repeat/inputs/calibration/siw \
  --run build/ecal50gev-repeat/calibration/siw
```

The exact reused library hashes and original producer/source revisions are
recorded with the readback/analysis evidence. To rebuild the historical libraries
or regenerate the geometry, follow the original
[restored LAr recipe](../lar-restored/reproduce.md) and
[matched Si–W references](../lar10k/reproduce.md), retaining their pinned source
identities. A source-only export is not a native transport check.

Analyze with the existing NumPy 2.5.4/Matplotlib 3.11.2 Python:

```sh
plot_python=/Users/salzburg/Documents/work/installed/acts-nodd/pyvenv/bin/python
"$plot_python" -B software/analysis/lar_response/central_analyze.py analyze \
  --runs build/ecal50gev-repeat --output build/ecal50gev-repeat/analysis
MPLCONFIGDIR="$PWD/build/ecal50gev-repeat/mpl" \
  "$plot_python" -B software/analysis/lar_response/central_analyze.py plot \
  --summary build/ecal50gev-repeat/analysis/summary.json \
  --output build/ecal50gev-repeat/figures
```

Full ROOT/events, compacts, verbose logs and caches remain ignored locally.
Only compact bin counts/moments/flows, scalar inference, provenance, figures and
the recipe are retained in Git. Replotting needs only the compact summary; native
readback and independent event-level checks need the retained full runs.
