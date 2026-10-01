# Optional nodehammer display

For the preliminary barrel plus PR36 endcaps, use the
[combined pixel workflow](../pixel_detector_dd4hep/README.md). It generates full,
barrel, endcap, disc, stave, module and sensitive-only projects with the same
import/round-trip audits. The instructions below retain the barrel-only defaults.


Nodehammer is useful for interactive geometry selection, cutaways and sharing a
portable pixel-barrel scene. Use it alongside DD4hep `geoDisplay` and the
[geometry validation](../../detector/README.md), whose physics checks remain
authoritative. This workflow changes no detector dimensions or materials.

The [assessment](../../docs/validation/nodehammer/results.md) records the tested
revision, screenshots and limitations. The input remains the **PROTOTYPE** of
[DES-012](../../docs/design/DES-012-dd4hep-pixel-barrels.md).

## Build once

Use the [ACTS Spack skill](../../skills/acts-spack/SKILL.md) and run its preflight
before relying on local libraries. Activate ROOT/DD4hep in the same shell used
for these commands. On the current Mac:

```sh
python3 skills/acts-spack/scripts/preflight.py
source /Users/salzburg/cernbox/configs/acts/acts_setup.sh
unset ACTS_SPACK_SETUP
setup_spack
source /Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view/bin/thisdd4hep.sh
python3 tools/nodehammer/build.py --jobs 6
```

Preflight currently reports changed setup/lock fingerprints; the task-specific
DD4hep build/import tests establish the capabilities used here. Do not install
or modify shared Spack dependencies to silence that warning.

Prerequisites: Git, `uv`, Ninja, CMake, a C++23 compiler, and an activated compatible
ROOT/DD4hep installation. The standard nodehammer Python wheel has neither heavy
importer. The helper clones the requested fork under ignored `reference/cache/`,
checks the exact [source pin](upstream.json), creates a local Conan environment
using the **active Spack Python**, and builds both importers plus the native
viewer. Using a different Python under this Spack runtime failed in testing.
Existing source checkouts with a different revision or tracked changes are
rejected, not reset. `--source` and `--build` allow other local directories.

[conan.lock](conan.lock) pins the resolved recipe revisions. The build records
its profile, binary hash, source revision and ROOT version in
`build/nodehammer/build-manifest.json`; the resolved local lock is reused on
subsequent builds. This is a tested macOS arm64 workflow, not a claim that every
compiler/platform is qualified or that binaries are bitwise reproducible.
No nodehammer dependency is added to the detector factory or normal CMake build.

## Refresh after detector updates

First rebuild/export the current compact using the [detector instructions](../../detector/README.md).
Then, in the activated shell:

```sh
export DD4HEP_LIBRARY_PATH="$PWD/build/dd4hep/detector:${DD4HEP_LIBRARY_PATH:-}"
export DYLD_LIBRARY_PATH="$PWD/build/dd4hep/detector:${DYLD_LIBRARY_PATH:-}"
python3 tools/nodehammer/prepare.py
```

`--compact`, `--nodehammer` and `--output` override the default paths. Use the
maintained `build/dd4hep/detector/compact/pixel-barrel.xml`, accompanied by its
`expected.json` and materials. Do not use a stale compact-probe export.
On Linux use the corresponding `LD_LIBRARY_PATH` plugin directory.

The helper checks binary provenance, structured import diagnostics, every expected
entity/material/centre, all sensor normals and sensitive tags, imported RGB,
the NHB round trip, and every selected tessellated placement. It checks GLB
transforms and box dimensions in metres and explicit RGBA/BLEND settings.
Assembly and world bounding boxes are omitted from rendering; physical parents
such as foam cores and titanium tubes are retained. No leaf-only filtering or
descendant merging is applied to the full view.

Outputs in `build/nodehammer/pixel/`:

| File | Use |
| --- | --- |
| `full.nhproj` | All physical solids, including mounting and services |
| `sensitive.nhproj` | Active sensor patches |
| `stave.nhproj` | Layer 1, stave 0, including its nested cooling and modules |
| `*.glb` | The same selections in metre-based glTF 2.0 |
| `*.toml` | Generated styles from `detector/config/display.json` |
| `pixel.nhb`, `pixel.json`, `roundtrip.json` | Portable semantic geometry and audit inputs |
| `*.render.json`, `report.json` | Mesh inventories, checks, hashes and commands |

Each `.nhproj` embeds the NHB and config through nodehammer's `project pack`;
recipients need no nODD plugin, XML includes or Spack runtime to interpret its
geometry. Nodehammer's internal IDs are reindexed on NHB import and are **not**
DD4hep packed cell IDs. Sensor shape changes can be re-exported without changing
this workflow. A new material family or incompatible hierarchy/schema fails the
audit for explicit review rather than silently using an unknown style.

## View locally

```sh
build/nodehammer/native/nodehammer viewer open build/nodehammer/pixel/full.nhproj
```

Use the hierarchy to select or hide volumes and the angle-cut controls to expose
the interior. Native transparency is not yet implemented at the pinned revision;
RGBA and `BLEND` are retained in GLB for viewers that support them. The complete
scene contains the nested DD4hep solid envelopes, not boolean-subtracted material
regions. Coplanar silicon parent/daughter faces may show z-fighting; use the
sensitive-only project to inspect active coverage.

A repeatable one-shot cutaway (camera distances are ROOT centimetres):

```sh
build/nodehammer/native/nodehammer viewer shot build/nodehammer/pixel/full.nhproj \
  -i pixel.nhb -c full.toml -o build/nodehammer/pixel/cutaway.png \
  --shot-width 1600 --shot-height 1000 \
  --camera-target-x 0 --camera-target-y 0 --camera-target-z 0 \
  --camera-distance 170 --camera-yaw 55 --camera-pitch 20 \
  --angle-cut --cut-start 0 --cut-end 90 --no-pause-when-unfocused
```

At this revision `shot` requires explicit archive input/config keys, even though
the upstream skill's shorter example omits them. Specify all six camera values
together. This display cut is a shader effect; it leaves the source and exported
geometry intact. A working desktop/GPU is required.
The viewer persists preferences between runs. For a reproducible full axial
view use the same command with `--camera-yaw 0 --camera-pitch 0
--angle-cut=false`; explicitly setting these avoids inheriting an earlier cut.

For an existing ROOT export, explicitly select the importer:

```sh
build/nodehammer/native/nodehammer inspect --output-format json summary \
  --input-format tgeo -i build/dd4hep/detector/pixel-barrel.root
```

ROOT imports lack DD4hep sensitive tags, so the automated pixel workflow uses
the compact instead. The pinned `.root` extension autodetection is defective;
the explicit flag was verified. `--strict` also rejects informational diagnostics
at this revision. The helper instead rejects structured import warnings/errors,
uses `fallback="fail"` for tessellation and checks placement completeness.

Nodehammer also offers `project publish` and browser serving, but these need a
matching `nodehammer-web` runtime. This PR verifies native viewing and portable
packing, not browser compatibility or website publication. Do not publish raw
compact files as a browser project: pack the converted NHB instead.

Run the lightweight safeguards without Spack:

```sh
python3 -B -m unittest discover -s tools/nodehammer -p 'test_*.py' -v
```
