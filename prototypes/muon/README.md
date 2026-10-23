# DES-039/040 muon DD4hep prototype

Isolated **PROTOTYPE**, following issues [92](https://github.com/asalzburger/nodd/issues/92) and [93](https://github.com/asalzburger/nodd/issues/93). DES-039 and DES-040 remain DRAFT. The exact PR90 candidate supplies 936 chambers and 36 warm coil reservations. Chambers preserve each source ID, origin, basis, quadrilateral footprint and 500 mm depth. Warm racetracks use exact boxes and quarter-annuli, combined into three shared union volumes so overlapping ECT sleeve reservations are represented once.

This first stage uses **nonsensitive Air envelopes**. It establishes a native geometry and transport smoke test, without asserting chamber/coil materials, realistic gamma conversion or detector response. Supports, HCAL, magnetic fields and drift tubes are absent. The [contract](../../docs/design/DES-040-muon-chambers-frame.md#dd4hep-realization-and-simulation-contract-2026-10-23), [interface assessment](../../docs/validation/DES-040/dd4hep-2026-10-23/interface-review.md) and [execution report](../../docs/validation/DES-040/dd4hep-2026-10-23/README.md) retain scope and evidence.

Use the existing installation after the [ACTS Spack preflight](../../skills/acts-spack/SKILL.md). Do not install or modify shared dependencies. From the repository root, in the same shell:

```sh
python3 skills/acts-spack/scripts/preflight.py
source /Users/salzburg/cernbox/configs/acts/acts_setup.sh
unset ACTS_SPACK_SETUP
setup_spack
source /Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view/bin/thisdd4hep.sh
source /Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view/bin/geant4.sh

python3 -B tools/muon_dd4hep/export.py --output reference/cache/muon-dd4hep/compact
cmake -S prototypes/muon -B reference/cache/muon-dd4hep/build -G Ninja
cmake --build reference/cache/muon-dd4hep/build --parallel 2
python3 -B tools/muon_dd4hep/run_validation.py \
  --compact reference/cache/muon-dd4hep/compact/muon-system.xml \
  --expected reference/cache/muon-dd4hep/compact/expected.json \
  --library reference/cache/muon-dd4hep/build/libnODDMuonPrototype.dylib \
  --output-dir reference/cache/muon-dd4hep/run-new
```

On other verified nodes, use their recorded activation paths and platform library suffix. Each run requires a fresh output directory. The exporter reads the frozen source and natural-element table from Git, verifies their hashes, and creates `muon-system.xml`, `materials.xml` and `expected.json`. The prototype builds independently of the production detector targets.

The runner executes the installed `checkOverlaps`, inspects native geometry independently, then starts `ddsim` only after that gate passes. The stock script exits zero even for overlaps and passes its tolerance directly to ROOT; this runner converts the chosen physical 0.00001 mm numerical tolerance with `dd4hep.mm` and checks the overlap collection explicitly. It compares all chamber vertices, identifiers and transforms, all 288 CSG primitive instances, and deterministic coil occupancy probes against the source. Numerical tolerance is separate from the inherited 50 mm design clearance.

The simulation uses 1,000 DDSim `uniform` (flat polar theta and azimuth) 20 GeV gammas, seed 92393 and FTFP_BERT. For this compact without tracking hits, the tracker-region user particle handler is disabled. A small `nODDMuonEmptyEvent` begin-event action supplies an empty owned hit container because DDG4 skips persistence when that pointer is null. It creates no hit collections. DD4hep's native ROOT writer is selected explicitly to persist MC truth. Success requires exactly 1,000 persisted events. The run records commands, configuration, versions, file hashes and failures; ROOT output stays local and is identified by its digest.

```sh
python3 -B -m unittest discover -s tools/muon_dd4hep -p 'test_*.py' -v
```

Controls include corrupted manifests, geometry/identifier mutations, incomplete inventories, a missing factory, a native failure following stock-script success, and a wrong output event count. The native audit also accepts `--root-output PATH` to export a display geometry. Its success is geometry evidence, not engineering acceptance.

The next stage of issue 93 needs an explicit internal model before filling chambers: the issue says approximately **30 mm radius**, whereas the ATLAS MDT precedent uses approximately **30 mm diameter**. Two multilayers of three layers require exact finite-cylinder containment in the narrow endcap fillers, plus documented gas, wall, pitch, separation, identifiers and sensitive response. See the interface assessment; no radius is silently changed by this implementation.

The requested `--gun.distribution uniform` is flat in polar theta and azimuth. DDSim uses the separate `cos(theta)` option for equal-solid-angle directions; this run does not use that option and supplies no solid-angle coverage estimate. See registered source `SRC-DD4HEP-GUN-1.38`, [Gun.distribution](https://github.com/AIDASoft/DD4hep/blob/v01-38/DDG4/python/DDSim/Helper/Gun.py#L74-L79).
