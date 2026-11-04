# Gen3 material-mapping surface survey

This first-step prototype reads an existing recording. It exports the actual
native Gen3 portals, overlays recorded material and proposes passive-material
carriers. It does not run new geantinos or install a material map.

The retained [report](../../../docs/validation/gen3-material-mapping/README.md)
contains the figures, full-scan statistics, per-layer carrier IDs, additional
service-surface suggestions and explicit unresolved cases.

## Native inputs

Activate the node's existing ACTS Spack environment as described in the
`acts-spack` skill. In the **same** zsh process, source `thisdd4hep.sh`,
`geant4.sh` and the selected ACTS build's `this_acts.sh`. On macOS, an
intermediate system shell can discard `DYLD_LIBRARY_PATH`. Do not install or
change shared dependencies. The caller supplies a compatible nODD adapter,
compact and five factories; main currently contains adapter placeholders.
The retained run uses the separately identified migration build at
`../nodd-software-layout`, source `530080cfe16c7513228bf60238b99d4b9938538a`.
Its exact ACTS/module/library/factory hashes are retained. No unmerged adapter
source is copied into this PR.

```sh
# With the native runtime already activated in this shell:
$NATIVE_PYTHON software/analysis/gen3_material_mapping/export_geometry.py \
  --nodd-dir "$NODD_RUNTIME_CHECKOUT" --build-dir "$DD4HEP_BUILD" \
  --output build/gen3-material-mapping/geometry.json

# Repeat --factory for all five built nODD factories. This reuses the
# density-checked classifier and also writes aligned per-step labels.
python3 software/analysis/material_profiles/categorize.py \
  --input "$MATERIAL_RECORDING" --compact "$TRACKER_COMPACT" \
  --factory "$BEAM_PIPE_FACTORY" --factory "$PIXEL_FACTORY" \
  --factory "$SHORT_BARREL_FACTORY" --factory "$SHORT_ENDCAP_FACTORY" \
  --factory "$LONG_STRIP_FACTORY" \
  --output build/gen3-material-mapping/labels --write-steps
```

`categorized_steps` vectors are aligned with `material_tracks`. The accompanying
`profiles.root.regions.csv` records native component/child placement paths, with
explicit placement-copy suffix removal for source DetElement matching. Density
agreement cannot establish identical recipes or the absent recording revision.
Two inherited float32 active/guard ambiguities remain conservatively passive;
see the classifier diagnostics and previous report.

## Survey and plots

Use the pinned documentation plotting environment from
[../README.md](../README.md); no C++ ROOT or ACTS import is needed in this stage.
This survey uses uproot/awkward/NumPy for the recorded point arrays and
Matplotlib for the scientific figures. The existing unrooted profile workflow
remains available separately.

```sh
$PLOT_PYTHON software/analysis/gen3_material_mapping/survey.py \
  --input "$MATERIAL_RECORDING" \
  --labels build/gen3-material-mapping/labels/profiles.root \
  --geometry build/gen3-material-mapping/geometry.json \
  --near-mm 10 --scatter-stride 40 \
  --output build/gen3-material-mapping/survey

$PLOT_PYTHON software/analysis/gen3_material_mapping/export_tables.py \
  --data build/gen3-material-mapping/survey \
  --output build/gen3-material-mapping/survey

$PLOT_PYTHON -m unittest discover \
  -s software/analysis/gen3_material_mapping -p 'test_*.py' -v

MPLCONFIGDIR="$PWD/build/mpl-cache" \
$PLOT_PYTHON software/analysis/gen3_material_mapping/plot.py \
  --data docs/validation/gen3-material-mapping \
  --output build/gen3-material-mapping/replot
```

The survey targets the supplied 100,000-track DES-025 prototype. It rejects
nonzero starting vertices, non-straight rays and unsupported non-axisymmetric
portals. It checks full aligned step coverage and per-track budget closure.
The native exporter independently checks sensor frames, finite bounds,
identifiers and complete ACTS serialization round trip. Neither check is
material-mapping closure or tracking-performance validation.

`survey.json` contains all assignments and flags. `geometry-summary.json`
retains the actual portal/volume catalogue, owners and native source hashes.
The 40 MB full sensor/link export and 698 MB recording remain under ignored
build/storage paths. Compressed `scatter.npz` and `occupancy.npz` are retained
for portable figure replay. The scatter is every 40th material step; all
classification, budgeting, thresholds and flags use the full recording.


## Configurable mapping/validation trial

The user-selected follow-up is documented in the
[trial report](../../../docs/validation/gen3-material-map-run/README.md).
`mapping_config.json` centralizes all bin counts;`select_surfaces.py` resolves
native portal roles and writes the exact65-surface manifest. Build the isolated
[native support](../../source/ActsExamples/MaterialMapping/README.md),then run
`software/running/nodd_material_mapping.py` and
`software/running/nodd_material_validation.py` in the verified ACTS runtime.
`export_validation.py` reduces only total validation material;`plot_validation.py`
overlays it on the existing Geant4 stack and draws the selected portals.
The original first-step survey remains a separate reproducible control.

The [cumulative expert-review diagnostic](../../../docs/validation/gen3-material-map-run/cumulative/README.md)
uses `cumulative_profiles.py` and `plot_cumulative.py` to compare accumulated
Geant4 material with thin ACTS portal interactions versus r, |z| and origin
distance in configurable |η| intervals. It reuses the existing full recordings.
