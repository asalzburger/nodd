# Reuse the frozen staggered ECAL calibration

The recorded default is **`nodd-ecal-staggered-spline-v1`**. The linear comparator
is **`nodd-ecal-staggered-linear-v1`** (`kind='original'`). Both are isolated
**PROTOTYPE** calibrations for the exact staggered ECAL geometry. The complete
coefficients, knots, normalizations, regional response scales, fallback and
closure factors are in [frozen/models.json](frozen/models.json). No training data
are needed to apply them. [The versioned manifest](frozen/manifest.json) records
model IDs, units, geometry/feature compatibility, domain and limitations.

The coefficients were frozen at `e65962c259cec1f8744252fccfa17211004f4d61`
before independent validation. The coefficient-file SHA-256 remains
`8595d8fd74d17edf2561d889e52910b3badbd358b446b951ca5083938c7ccdf1`.
The numerical source and published predictions are unchanged by this interface.
Pin the Git revision as well as the model ID when consuming it. Future
recalibration gets a new version, retaining this record.

## Command-line application

Use Python with NumPy; inference needs no ROOT, Geant4, training campaign,
truth columns or new dependency. From the repository root:

```sh
python3 -B software/analysis/calorimeter_digitization/highstat_inference.py \
  --features build/ecal-highstat/campaign/batches/validation-000/analysis/features \
  --output build/ecal-highstat/reuse-example
```

Choose a fresh output directory. `--kind original` applies the linear comparator.
The input directory contains `features.npz` and `receipt.json` produced by the
unchanged [feature extractor](../../../software/analysis/calorimeter_digitization/highstat_readback.py).
The application verifies the model/source and feature-file hashes, exact feature
semantics and compact-geometry hash before opening arrays. It reads only
`features`, `signal`, `region`, `valid_axis`, and `event`. Additional truth columns
in study files are unused; files containing only these measured columns work.
The receipt retains `status`, `events`, `feature_sha256`, `compact_sha256` and
the four feature-semantic fields from the manifest.

`calibrated.npz` retains input event IDs and contains:

| Field | Meaning |
| --- | --- |
| `energy` | Final estimated energy, GeV, including global closure |
| `pre_energy` | Estimated energy before global closure, GeV |
| `gain` | Correction before closure, bounded to 0.5–3; one for fallback rows |
| `clipped` | Regional prediction lies beyond a gain bound |
| `feature_extrapolated` | At least one feature is outside its training range |
| `zero_signal` | Measured silicon signal is exactly zero |
| `fallback` | Invalid reconstructed axis; training-only global response is used |

The output receipt binds model ID, manifest, inference/core source, input
features/receipt and output hashes, units and flag counts. Event outputs remain
local and ignored. Existing output directories are never overwritten.

## Python application

```python
import json
import sys
sys.path.insert(0, 'software/analysis/calorimeter_digitization')
from highstat_inference import calibrate

receipt = json.load(open(feature_directory / 'receipt.json'))
semantics = {key: receipt[key] for key in
             ('feature_names', 'producer_sha256', 'feature_recipe_sha256',
              'geometry_helper_sha256')}
result = calibrate(features, signal_GeV, region, valid_axis,
                   geometry_sha256=receipt['compact_sha256'],
                   feature_semantics=semantics)
estimated_energy_GeV = result['energy']
```

`features` is a finite N×10 array in exact manifest order. `signal_GeV` is the
finite nonnegative sum of silicon deposits. `region` is integer 0 when at least
half the measured signal is in the barrel, otherwise 1. `valid_axis` is boolean.
Invalid-axis feature rows remain finite placeholders, as in the frozen
extractor. The API requires explicit compatibility evidence; the CLI additionally
checks feature bytes and event identities.

For valid axes, the saved regional model predicts normalized response `p`, and
`pre_energy = signal / response_scale / clip(p, 1/3, 2)`.
For invalid axes, `pre_energy = signal / fallback_response`.
Then `energy = pre_energy * closure`, including fallback rows. Zeros stay
exactly zero. Closure factors are 1.0854609054699023 (spline) and
1.0857735225335063 (linear). Reuse never refits coefficients or scales.

## Domain, validation and merging

Validation used origin electrons, total energy 10–80 GeV, uniform eta −3…3 and
full phi, zero field, FTFP_BERT, 0.7 mm range cuts and a 5 mm sensitive charged-step
limit. Geometry/material hashes are in the manifest; the loader checks compact
geometry, and the caller must preserve the remaining simulation context. Other
particles, geometry/material revisions, fields, noise/digitization settings or
energy ranges require new validation.

The spline's fresh-20k width is 30.209%, mean response 1.00300. Local energy bias,
sector-seam losses, zeros and clipping remain in the [report](README.md). This
is not intrinsic fixed-energy resolution or detector acceptance. That cohort
has been inspected and must not select later tuning.

Reuse controls run in the existing NumPy CI job. Local complete-sample regression
also compares both models with all 20k retained frozen predictions, without a
new fit or transport. Applying the same models in 10k chunks introduces only
measured floating-point matrix-product roundoff (maximum ratio difference
4.89e-15); the full 20k evaluation is bit-exact. No tolerance was relaxed in
the full-population check. [Compact reuse verification](frozen/reuse-validation.json)
records this distinction. Raw inputs and outputs stay local.

[PR137](https://github.com/asalzburger/nodd/pull/137) is stacked on
[PR136](https://github.com/asalzburger/nodd/pull/136). The open dependency order
is **PR133 → PR134 → PR135 → PR136 → PR137**, starting from main. A maintainer
must merge dependencies and retarget each successor to main, preserving the
commits needed by coefficient/validation provenance: use merge commits for
this stack. Squashing or deleting
unmerged dependency branches can require explicit restacking; do not assume
GitHub moved a successor's target. Recheck CI and mergeability after retargeting.
Preparing PR137 does not approve or merge predecessors or grant detector sign-off.
