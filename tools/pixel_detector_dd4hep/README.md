# Preliminary pixel detector

[DES019](../../docs/design/DES-019-trimmed-mixed-pixel-dd4hep.md) is the default
working pixel baseline on main: the selected PR34/35 barrel plus concentric
four single-module rings and two quad-module rings, with DES018 inner-ring
removals on outer discs and the reviewed PR40 disc datums. This human-selected
**preliminary baseline** remains separate from production ODD. Formal design
status stays DRAFT. Coverage, thermal and service-space failures remain open.

## Build, validate and prepare nodehammer

Read the [acts-spack workflow](../../skills/acts-spack/SKILL.md) and run preflight.
On the current Mac, from this checkout, use one shell:

```sh
python3 skills/acts-spack/scripts/preflight.py
source /Users/salzburg/cernbox/configs/acts/acts_setup.sh
unset ACTS_SPACK_SETUP
setup_spack
source /Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view/bin/thisdd4hep.sh
source /Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view/bin/geant4.sh
python3 -B tools/pixel_detector_dd4hep/refresh.py --geant4-init
```

The recorded Spack fingerprints differ from this installation; DD4hep 1.38,
ROOT 6.40.04 and Geant4 11.4.2 were verified for this task. The helper uses the
active Python, builds only repository code, runs all six CTests, exports ROOT,
audits nodehammer and optionally initializes Geant4 **without events**. It writes
commands, log hashes and outcomes to `build/dd4hep/pixel-workflow.json`. It does
not install dependencies. Native nodehammer must already be built using
[its instructions](../nodehammer/README.md). `--nodehammer /absolute/path/nodehammer`
can reuse the existing binary and adjacent build manifest from another checkout.
`--without-display` runs the geometry checks without that optional tool.

Inspect the resulting projects:

```sh
build/nodehammer/native/nodehammer viewer open build/nodehammer/pixel-detector/full.nhproj
build/nodehammer/native/nodehammer viewer open build/nodehammer/pixel-detector/disc.nhproj
```

Other views are `sensitive`, `barrel`, `stave`, `endcap` (positive side), and
`module` (one positive-endcap module, components only). Each project is portable;
copy the `.nhproj` alone to a nodehammer installation. Native transparency remains
an upstream limitation. Use selections/cutaways to expose nested material.
The GLB companions retain opacity and metre units. The workflow repairs only the
verified upstream float32 translation-rescaling error, preserving binary meshes
and the existing audit tolerance; raw-export hashes and corrections are recorded.

For DD4hep's viewer:

```sh
export DD4HEP_LIBRARY_PATH="$PWD/build/dd4hep/detector:${DD4HEP_LIBRARY_PATH:-}"
export DYLD_LIBRARY_PATH="$PWD/build/dd4hep/detector:${DYLD_LIBRARY_PATH:-}"
geoDisplay -input "$PWD/build/dd4hep/detector/pixel-detector/pixel-detector.xml"
```

On Linux set `LD_LIBRARY_PATH` instead of `DYLD_LIBRARY_PATH`. The coloured ROOT
export is `build/dd4hep/detector/pixel-detector.root`. The original barrel entry
point `build/dd4hep/detector/compact/pixel-barrel.xml` remains available.

## Inputs and reusable blocks

- [pixel-detector-trimmed.json](../../detector/config/pixel-detector-trimmed.json):
  default mixed baseline, pinned layouts/apertures and service reservations.
- [pixel-detector.json](../../detector/config/pixel-detector.json): explicit DES015
  quad-only control, reconciled to the reviewed PR40 disc datums.
- `export.py`: composes the unchanged barrel with repeated endcap assemblies.
- `endcap_modules.py`: source-derived quad modules with support-facing ASIC stacks.
- `endcap_parts.py`: explicit unit-bearing shapes and exclusive volume inventory.
- `endcap_services.py`: carrier, slotted rails and reference service cells.
- `PixelComponents`: shared C++ sensor/module factory.
- `PixelEndcapParts`: passive primitives and disjoint tongue construction.
- `PixelEndcap`: short factory assigning disc/module/sensor placement IDs.

No endcap applies the barrel's slim-z module rotation. Single modules have one active rectangle; quad modules retain four distinct
active rectangles and passive silicon seams. Endcap system IDs are 2 (negative) and 3
(positive), with disc 1..9 and unchanged module/patch IDs. The existing barrel
system ID and bit layout are preserved. Endcap bit layout is documented in DES015.

Update source designs first, then deliberately update reviewed SHA pins. Export
fails on stale inputs. Never edit generated XML or silently repin after a failed
check. Rebuild and refresh all viewer projects after changing a source model.
Pure export/source-conservation checks need only Python:

```sh
python3 -B -m unittest discover -s tools/pixel_detector_dd4hep -p 'test_*.py' -v
```

## Geant4 follow-up boundary

`--geant4-init` tests DDG4 conversion, 11,806 sensitive paths in the default
baseline (14,858 in the explicit quad-only control), the standard truth
handler and FTFP_BERT initialization. No events are transported. The compact has
no magnetic-field definition, beam pipe, strips or surrounding detector. A next
PR should add explicit field/gun settings, small event runs, hit/energy-deposit
inspection, step limits/cuts suited to thin silicon, reproducible seeds and
Geant4 overlap checks. The initialization defaults are not physics qualification.

Detailed results, effective-material limitations and the rear flange packing
failure are in [the validation report](../../docs/validation/DES-015/results.md).
The default combined compact now implements the **DES019 trimmed mixed-module
preliminary baseline** selected on 2026-10-06. Configuration:
[`pixel-detector-trimmed.json`](../../detector/config/pixel-detector-trimmed.json).
The existing `pixel-detector.json` remains an explicit DES015 quad-only control with PR40 datums;
pass it explicitly with `--config` to reproduce that export. Old validation
reports are historical controls, not evidence for the new default.

The endcaps retain DES017 radial/tangential single and quad frames, frozen
support faces/colours, compensated centres and DES018 per-disc ring removals.
The combined inventory is 5,362 modules and 11,806 sensitive chip areas; barrel
3,050/6,794 is unchanged. Service inventories use 248 retained endcap cooling
circuits, not nine identical discs. The native readout maps template IDs
losslessly to bounded fields; source identifiers are recorded in `expected.json`.
See [DES019](../../docs/design/DES-019-trimmed-mixed-pixel-dd4hep.md) and its
[results](../../docs/validation/DES-019/results.md). Preliminary selection is
not sign-off; inherited coverage, thermal, routing and packing limits remain.

Main integration checks and rigid disc-position reconciliation are retained in
[the integration report](../../docs/validation/DES-019/main-integration/results.md).
