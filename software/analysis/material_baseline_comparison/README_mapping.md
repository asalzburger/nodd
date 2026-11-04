# Current-baseline native material map

`map_workflow.py` binds the maintained Gen3 exporter, portal selector, native
ACTS material mapper and independent validator to the current DES043 geometry.
It requires **46,682 native sensor planes, 120 volumes and 54 sensor groups**.
The historical exporter retains its 45,646-plane/117-volume guards unchanged.
Current portal IDs come from the fresh native export; no old-map IDs are reused.

The policy remains [mapping_config.json](../gen3_material_mapping/mapping_config.json):
one phi bin, the existing detector-specific z/r bins, pixel barrel carrier after
the sensitive layer and other layer carriers before it, plus beam-pipe, gap,
separator and world-shell carriers. Shared native portals use the maximum
requested bin count. Existing sensor, pipe, surface and volume material slabs
are cleared by the native sidecar before the complete recorded inventory is
mapped. Physical DD4hep solids and material recipes are preserved.

## Environment and native support

Follow the repository `acts-spack` preflight and directly verify the current
runtime. The stale node registry alone does not establish readiness. In a fresh
zsh, source `software/env/truth_tracking.sh`; it uses the existing sibling ACTS
build and virtual environment without installation. Native scripts initialize
DDG4 before ROOT/ACTS.

The existing `nodd_portal_material` sidecar can be reused with its matching
pybind11 3.0.4/internals11 ABI. `--sidecar-evidence` identifies an actual retained
native run whose binary and C++ source hashes must match the loaded sidecar and
current source. The current Spack-view pybind11 headers may be newer; do not
rebuild against them by accident. If a rebuild is needed, use the maintained
[native build recipe](../../source/ActsExamples/MaterialMapping/README.md) with
the verified matching package and a task-local output directory.

## Reproduce

From this repository root, after the fresh current compact and five factories
including their DD4hep component registry files have been built:

```sh
source software/env/truth_tracking.sh
mapping_tool=software/analysis/material_baseline_comparison/map_workflow.py
mapping_output=build/material-comparison/agent-mapping
mapping_build=build/material-comparison/dd4hep
mapping_runtime=../nodd-software-layout
mapping_native=../nodd-gen3-material-mapping/build/gen3-material-map-run/native
mapping_evidence=../nodd-gen3-material-mapping/build/gen3-material-map-run/homogeneous-smoke-final/mapping/mapping-report.json

python -B "$mapping_tool" prepare --runtime "$mapping_runtime" \
  --build-dir "$mapping_build" --output "$mapping_output"

# Wait for the coordinator's fresh Geant4 recording to complete. The report
# must contain completed=true, exact event accounting, and matching input hashes.
python -B "$mapping_tool" map --runtime "$mapping_runtime" \
  --build-dir "$mapping_build" --output "$mapping_output" \
  --native-module-dir "$mapping_native" --sidecar-evidence "$mapping_evidence" \
  --recording build/material-comparison/geant4-current/tracks.root \
  --recording-report build/material-comparison/geant4-current/metrics.json \
  --events 1000 --tracks 100

python -B "$mapping_tool" validate --runtime "$mapping_runtime" \
  --build-dir "$mapping_build" --output "$mapping_output" \
  --native-module-dir "$mapping_native" --sidecar-evidence "$mapping_evidence" \
  --events 1000 --tracks 100
```

Training is 1,000 events × 100 neutral geantinos, seed228, uniform eta[-4,4],
full phi and origin vertex. The recorder's software revision is kept distinct
from the current geometry source revision; compact, material and factory hashes
bind the actual geometry. Historical eta[-4.5,4.5] training cannot pass this gate.

Independent validation uses 1,000 events × 100 ACTS straight rays, seed43,
uniform eta[-4,4], full phi, origin and one thread. This samples the mapped
surfaces independently; it does not rerun Geant4 transport or establish detector
acceptance. The mapping config's historical validation defaults remain intact;
the current validation command explicitly overrides their eta support.

`preparation-report.json`, `current-mapping-report.json` and
`current-validation-report.json` retain geometry/runtime identities, native
inventory, counts, map keys, binning/reload audits, total and individual-ray
material conservation, and exact commands. Raw geometry export, map, mapped and
unmapped material tracks, independent rays and logs remain under ignored build
paths. Completed stage reports reject accidental replacement; failed command
attempts retain separate local logs.

The native reader's pre-step positions move to slab midpoints only for mapping;
original recorded slabs and per-track totals remain unchanged. The native
nearest finite intersection assigns material to selected carriers. Empty-bin
correction is enabled. This preserves the existing mapping approximation and
does not imply that every material step is strictly before/after its carrier.

The pinned ACTS ROOT reader explicitly omits slabs whose recorded length is
exactly zero (`RootMaterialTrackIo.cpp:317–320`). Current per-ray auditing
therefore counts these exact omissions separately, requires every nonzero slab
to appear in mapped or unmapped output, and requires each ray's X0/L0 budgets
to close within the unchanged 1e-10 numerical check. No small positive slab is
discarded by this audit. The raw recording and historical raw-step guard remain
unchanged. An initial run through that guard is retained as an adverse control
when this distinction is encountered; its outputs are not silently presented
as a successful legacy audit.

Pure identity/count controls require no native installation:

```sh
python3 -B -m unittest discover \
  -s software/analysis/material_baseline_comparison -p 'test_mapping.py' -v
```

Full conservation, exact native map-key/binning reload and origin/count checks
require the local or regenerated native payloads. Commit concise reports,
needed binwise evidence, resulting plots and reproduction recipes only; full
ROOT/geometry outputs and bulky logs stay local under the artifact policy.
