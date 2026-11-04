# Isolated native portal material prototype

This sidecar decorates the selected **existing** Gen3 portal objects with
`ProtoSurfaceMaterial`. It clears existing sensor, pipe and volume material
before assigning exactly the manifest inventory; the complete Geant4 inventory
is then mapped without double-counting native slabs. Physical DD4hep solids,
materials, sensor transforms and the shared ACTS installation are unchanged.
The Python manifest validates bin axes/counts and uniqueness. The native module
also checks native portal identity, full-phi coaxial finite bounds and validates
the whole request before clearing any material. Material keys survive the
native serialization/reload. The source is a DRAFT/PROTOTYPE under DES-025.

The selected ACTS runtime must already have Gen3, keyed material-map support,
`MaterialMapper`, `MaterialValidator` and their Python bindings. Main currently
contains an adapter placeholder, so the caller identifies a compatible native
adapter build explicitly. No shared build or source is changed by these steps.

## Build

Run the acts-spack preflight and activate the verified Spack/DD4hep/Geant4/ACTS
runtime in the **same shell** as these commands. Use the actual source and
libraries matching the imported ACTS bindings; a similarly named installed
ACTS is insufficient. On macOS avoid an intermediate system shell that strips
the activated dynamic-library search path.

```sh
cmake --fresh -S software/source/ActsExamples/MaterialMapping \
  -B build/gen3-material-map-run/native -G Ninja \
  -DNODD_ACTS_SOURCE="$ACTS_SOURCE" -DNODD_ACTS_BUILD="$ACTS_BUILD" \
  -DPython_EXECUTABLE="$NATIVE_PYTHON" -Dpybind11_DIR="$PYBIND11_CMAKE" \
  -DNODD_PYBIND11_INTERNALS_VERSION=11
cmake --build build/gen3-material-map-run/native --parallel 2
```

The sidecar's pybind11 internals ABI must match the existing ACTS bindings.
The retained ACTS build reports `__pybind11_internals_v11_system_libcpp_abi1__`.
The current shared Spack view points to pybind11 3.1.0 (internals v12), which
cannot exchange ACTS objects with it. An **already installed** pybind11 3.0.4
prefix supplies compatible v11 headers/config; select it explicitly using
`pybind11_DIR`. A compile-time assertion rejects the wrong headers. No package
is installed or changed. Runtime reports retain sidecar and ACTS binding hashes.
The sidecar keeps ACTS template RTTI visible across libraries: hiding it makes
the core's dynamic casts miss proto material, silently producing homogeneous
maps. The runtime checks the key through the actual core registry before mapping,
and checks native mapped bin counts and exact keyed identities after reload.
If both configured axes have one bin, ACTS finalizes a homogeneous slab; the
reload audit requires that native type and one bin. Any request with more bins
must reload as binned material. Homogeneous fallback cannot silently satisfy a
multi-bin request.

## Mapping and validation

`--build-dir` is the DD4hep compact/factory build, while `NODD_ACTS_BUILD` above
contains the ACTS libraries. `--output` is a directory. All bin counts come from
the selection manifest; `--native-module-dir` can select a different task-local
sidecar directory.

```sh
"$NATIVE_PYTHON" software/running/nodd_material_mapping.py \
  --input "$MATERIAL_RECORDING" \
  --manifest build/gen3-material-map-run/selection.json \
  --nodd-dir "$NODD_RUNTIME_CHECKOUT" --build-dir "$DD4HEP_BUILD" \
  --events 1000 --output build/gen3-material-map-run/mapping

"$NATIVE_PYTHON" software/running/nodd_material_validation.py \
  --map build/gen3-material-map-run/mapping/material_map.json \
  --manifest build/gen3-material-map-run/selection.json \
  --nodd-dir "$NODD_RUNTIME_CHECKOUT" --build-dir "$DD4HEP_BUILD" \
  --events 1000 --tracks 100 --threads 1 --seed 43 \
  --eta-range -4.5 4.5 --phi-range -3.141592653589793 3.141592653589793 \
  --output build/gen3-material-map-run/validation
```

Mapping follows the pinned ACTS `Examples/Scripts/Python/material_mapping.py`:
`RootMaterialTrackReader`, `IntersectionMaterialAssigner`,
`BinnedSurfaceMaterialAccumulator` with empty-bin correction, `MaterialMapper`,
`MaterialMapping`, `JsonMaterialWriter`, and mapped/unmapped ROOT writers.
The recording has Geant4 **pre-step** positions, and the upstream ROOT reader
does not shift them. The sidecar therefore supplies a native framework algorithm
between reader and mapper that moves every position by
`0.5 * slab.thickness() * recorded_unit_direction`. It preserves material
properties and total budgets, writes no derivative recording, and leaves the
original ROOT file unchanged. The synthetic `mat_s*`/`mat_e*` branches are not
used as physical endpoints.

Validation follows the upstream `material_validation.py`, using an independent
configurable particle gun, `ParticleTrackParamExtractor`,
`IntersectionMaterialAssigner`, `MaterialValidator`, `MaterialValidation` and
`RootMaterialTrackWriter`. It loads the saved map with native
`JsonMaterialDecorator.materialMaps.apply(geometry)`. Exact keyed surface count
and absence of leftover proto slabs are checked. Validation uses straight rays,
an origin vertex, uniform eta and uniform phi (radians). It is a material-map
survey, not a Geant4 rerun or tracking-performance acceptance.

The upstream mapper assigns material to the closest intersected selected
surface. Before/after in the manifest describes each carrier's placement
relative to a sensitive layer; no strict per-step pre/post assignment is
imposed by that mapper. Reports record this limitation, the full mapped and
unmapped budgets, exact native material inventory, configuration and hashes.
The ROOT files retain each track, including empty mapped/unmapped tracks.

```sh
python3 -m unittest discover -s software/analysis/gen3_material_mapping \
  -p test_material_runtime.py -v
```
