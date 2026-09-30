# Pixel barrel DD4hep prototype

This standalone assembly implements the human-selected PR #29 baseline at
`c79c2194e23e99c4d2696ca2d6628a388b96f5e4`. Its implementation contract is
[DES-012](../docs/design/DES-012-dd4hep-pixel-barrels.md). It is a **PROTOTYPE**:
engineering qualification, material review and full-detector integration remain
open. It does not replace the production ODD description.

## Build and validate

Run the [Spack preflight](../skills/acts-spack/SKILL.md) first. On the verified
local node, activate the existing dependencies in the same shell as the build:

```sh
python3 skills/acts-spack/scripts/preflight.py
source /Users/salzburg/cernbox/configs/acts/acts_setup.sh
unset ACTS_SPACK_SETUP
setup_spack
source /Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view/bin/thisdd4hep.sh
cmake -S . -B build/dd4hep -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo
cmake --build build/dd4hep --parallel 4
ctest --test-dir build/dd4hep --output-on-failure
```

On other nodes, supply a verified DD4hep/ROOT installation and its Python
bindings, CMake and a C++20 compiler. No dependency installation is performed by
this repository. ROOT and DD4hep must share a compatible Python interpreter.

The library and plugin registration file are built in `build/dd4hep/detector/`;
the generated compact entry point is `compact/pixel-barrel.xml` in that directory.
CTest loads the library explicitly. For another DD4hep frontend, add the library
directory to `DD4HEP_LIBRARY_PATH` and the platform dynamic-library search path.

The pure exporter tests need only Python 3.10+:

```sh
python3 -B -m unittest discover -s tools/pixel_barrel_dd4hep -p 'test_*.py' -v
```

## View with geoDisplay

After the build and DD4hep activation above, from the repository root:

```sh
export DD4HEP_LIBRARY_PATH="$PWD/build/dd4hep/detector:${DD4HEP_LIBRARY_PATH:-}"
export DYLD_LIBRARY_PATH="$PWD/build/dd4hep/detector:${DYLD_LIBRARY_PATH:-}"
geoDisplay -input "$PWD/build/dd4hep/detector/compact/pixel-barrel.xml"
```

On Linux set `LD_LIBRARY_PATH` instead of `DYLD_LIBRARY_PATH`. The directory
contains both the library and its `.components` plugin registration. The validator
normally loads the library explicitly, whereas `geoDisplay` discovers it through
these paths. Add `-load_only` for a geometry-loading check without opening the
interactive display.

Use the CMake-generated compact above. The local `build/pixel-compact-probe/`
directory was an early development export and is not maintained by CMake. Its
old eight-element material table can abort ROOT with
`Cannot add element having Z=18 to mixture Air`. The current exporter supplies
the complete 98-element table; changing Air or removing argon is not the fix.
Rebuilding refreshes the canonical compact when its inputs change.

## Configurable provisional cable material

[config/pixel-barrel.json](config/pixel-barrel.json) is the canonical configuration.
`cable_volume_fractions` describes the **outer cable footprint**, before the
routing's separate packing void. The default is 0.10 copper, 0.40 polyimide and
0.50 air by volume. It is a provisional design choice, not a measured cable.
Fractions must be finite, nonnegative and sum to one. The exporter computes
mass fractions and density; never put volume fractions directly into DD4hep
material XML. Routing dimensions and IDs remain fixed during material variations.

For a sensitivity run, copy the configuration to a new file and change only these
fractions (for example 0.05/0.40/0.55 or 0.20/0.40/0.40). Then, in the activated
DD4hep shell:

```sh
python3 -B tools/pixel_barrel_dd4hep/export.py \
  --config build/cable-variant.json --output build/cable-variant
python3 -B tools/pixel_barrel_dd4hep/validate.py \
  --compact build/cable-variant/pixel-barrel.xml \
  --expected build/cable-variant/expected.json \
  --library build/dd4hep/detector/libnODDPixelBarrel.dylib \
  --output build/cable-variant/validation.json
```

Compare completed low/nominal/high validation reports with:

```sh
python3 -B tools/pixel_barrel_dd4hep/compare_materials.py \
  --low build/cable-cu05/validation.json \
  --nominal build/dd4hep/detector/validation.json \
  --high build/cable-cu20/validation.json --output build/cable-comparison.json
```

This requires identical compact geometry, IDs, ray paths and sensitive crossings,
unchanged non-cable material properties, and increasing mass/X0 with copper.
Use `.so` on Linux. Full-liquid CO₂ density and effective carbon mass fraction
are separately configurable. These knobs do not imply thermal/hydraulic approval.

## Components and identifiers

- `PixelComponents` builds modules, support/cooling staves, rings and mounting feet.
- `PixelServices` builds effective annular service sectors.
- `PixelBarrel` assembles layers and assigns stable placement IDs.
- `export.py` translates the pinned baseline into XML and an expected inventory.
- `materials.py` owns material recipes and volume-to-mass normalization.
- `validate.py` audits the constructed physical geometry, IDs, mass and navigation.

The local module frame is tangent x, beam y, outward radial z. Sensors face
radially inward; chips and local support are outward. The DD4hep hierarchy is
barrel → layer → stave → module → silicon substrate → active patch. Guards and
seams remain passive silicon. The 64-bit readout descriptor is
`system:5,layer:3,stave:6,module:16,sensor:16,x:-9,y:-9`; module and patch IDs
retain their source values. Signed x/y fields index 50 µm pixels in a patch, with half-pitch offsets
so the even 400 × 384 grid ends at the active patch boundaries.
Sensitive volume identifiers leave x/y zero. No digitization is implemented.

Local tubes contain separate CO₂ daughters. Parent material is counted only in
its exclusive volume. End-bay effective cells preserve cable, Ti and CO₂ inventory
from the routing model while avoiding overlapping illustrative elbows. Their
constituent maps and source-route ownership are exported in `service-cells.json`.
The cells smear turns/manifolds; they are not manufacturing drawings. A 0.255 mm
provisional graphite shim connects each ASIC back to the inherited support plane.

## Updating shapes or engineering input

Update the upstream model through its reviewed workflow first. Then update the
configuration's source SHA-256 pins (and the support input's layout pin when
applicable), document the new baseline revision and rerun export/build/CTest.
Stale pins fail explicitly. Do not change pins merely to make a test pass.
CMake tracks generator, model, configuration and retained baseline dependencies.
Never edit generated compact files as the canonical input.

Each export retains source/input/configuration hashes and Git revision in
`manifest.json`. Each validation report records loaded compact/library hashes,
versions, tolerances and deterministic ray definitions. Compare counts, every
sensitive transform, identifier uniqueness, constituent inventory, overlaps and
material rays against the prior evidence. Expected inventory tests independently
compare sensitive placements to the pinned source layout; construction validation
compares XML output with actual ROOT placements and capacities.

Geant4 transport, ACTS conversion, field propagation, omitted bonds/bump metals/
passives, endcap integration, electronics detail and support engineering are
future work. See the [retained validation report](../docs/validation/DES-012/results.md)
for actual results and limitations, and [NOTICE](NOTICE.md) for element provenance.
