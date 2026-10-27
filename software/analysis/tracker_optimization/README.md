# Constrained tracker optimisation prototype

Governed by [DES040](../../../docs/design/DES-040-tracker-resolution-optimization.md)
and [issue103](https://github.com/asalzburger/nodd/issues/103). Production
assembly, PR101 sources, original maps and calibration remain unchanged.

`variants/` centralises the layer radii, original disk datums and optional new
pixel disk pair. Unspecified placements retain the reference. Preserve module
types, alternating stave offsets and all local structures. Collector wedges and
rail cutouts follow the disk stations. Fixed carrier/flange/trunk envelopes stay
unchanged; service routing and capacity remain unqualified.

The study uses native Gen3 conversion, Fatras, geometric digitisation and the
unchanged corrected truth finder/Kalman chain from PR101. The Gaussian response
uses its unchanged smearing schedule. Native material and calibration IDs are
rebuilt for each candidate and joined to the reference by physical roles/layers.
Material profiles are relocated with per-bin area/count inventory factors;
the added disk is a native homogeneous area-weighted donor mixture **behind**
its sensitive faces. This is an effective-profile approximation, not a fresh
Geant4 material map. Transition-aggregate material and frozen error incidence
remain potential systematic effects.

## Execution

First follow the node-specific ACTS Spack preflight and existing native setup.
The available runtime was directly verified despite changed setup fingerprints:
adapter530080c, compiledACTS355ea684, ROOT6.40.04, Python3.14.5, pybind3.0.4.
The material helper links the existing ACTS Core without modifying it:

```sh
source software/env/truth_tracking.sh
cmake -S software/source/ActsExamples/TrackerOptimization \
  -B build/tracker-resolution-optimization/native \
  -DNODD_ACTS_SOURCE="$(pwd)/../nodd-software-layout/software/submodules/acts" \
  -DNODD_ACTS_BUILD="$(pwd)/../nodd-software-layout/build/acts"
cmake --build build/tracker-resolution-optimization/native

python -B software/running/nodd_tracker_optimization.py \
  --variant software/analysis/tracker_optimization/variants/balanced.json \
  --compact ../nodd-software-layout/build/dd4hep/detector/tracker/tracker.xml \
  --nodd-dir ../nodd-software-layout \
  --build-dir ../nodd-software-layout/build/dd4hep \
  --manifest docs/validation/gen3-material-map-run/selection.json \
  --output build/tracker-resolution-optimization/NEW-CASE \
  --events 10000 --pt 10 --seed 52042 --digitization geometric
```

Use a fresh output directory. `--prepare-only` exports the candidate geometry,
material map, calibration, digitisation and audits without generating events.
`--digitization gaussian` switches only the response. Its recorded native
algorithm minimum is10 retries, allowing11 draw attempts at sensor boundaries.
The same constant3T field, origin muons, |eta|<=4 and seven-hit fit selection
remain fixed. The ten-hit goal is measured over **all generated events**.

Run the separate full native overlap check on the prepared compact:

```sh
python -B software/analysis/tracker_optimization/check_geometry.py \
  --compact build/tracker-resolution-optimization/NEW-CASE/tracker.xml \
  --library-dir ../nodd-software-layout/build/dd4hep/detector \
  --output build/tracker-resolution-optimization/NEW-overlaps.json
```

## Analysis and replay

Use the existing isolated analysis environment, or install
`software/analysis/truth_tracking/requirements.txt` in a separate venv.
`analyze.py --case LABEL=DIRECTORY` is repeatable. Labels such as
`baseline-pt10` and `balanced-pt10` enable paired differences after exact
generated-event and reconstruction-contract equality checks.

```sh
python -B software/analysis/tracker_optimization/analyze.py \
  --case baseline-pt10=build/tracker-resolution-optimization/BASELINE \
  --case balanced-pt10=build/tracker-resolution-optimization/BALANCED \
  --bootstrap 400 --output build/tracker-resolution-optimization/comparison.json.gz
python -B software/analysis/tracker_optimization/plot.py \
  --input build/tracker-resolution-optimization/comparison.json.gz \
  --output build/tracker-resolution-optimization/figures
python -B -m unittest discover -s software/analysis/tracker_optimization -p 'test_*.py' -v
```

Residuals use fit-minus-truth; all pulls use truth-minus-fit, wrapping phi.
Time is unmeasured and prior dominated. Retain finite tails, full SD/RMS,
central68.27% half-width, bias, wrong charge and missing/invalid fits. Signed
q/pT supplements nonlinear pT, whose apparent core can improve while curvature
and charge identification worsen. Pointwise event-bootstrap and95% Wilson
intervals do not certify every eta/phi trajectory or include model systematics.

`screen.py` is a finite-patch straight-ray schedule screen, borrowing unchanged
strip counts from a named reference sample. Its complete mutation ledger,
grid/seeds/hashes and limitations are retained. It supplies candidates for
native tests and cannot establish tracking performance or mechanical clearance.
