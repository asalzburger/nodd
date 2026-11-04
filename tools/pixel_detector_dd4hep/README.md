# Pixel detector DD4hep source

The maintained default is the **DES040 balanced working baseline**, selected by
expert review and the human implementation direction on 2026-10-29. Its pixel
barrel nominal radii are **31.5/57/96/182 mm**, with **12/22/18/30 staves**.
Existing endcap logical layers 1..9 sit at |z|=615/865/1115/1333/1565/1780/2090/
2440/3070 mm; new logical layer 10 is at 950 mm on each end. It repeats the
complete original layer 2 local module/support/cooling assembly. IDs follow
logical layer identity, not longitudinal ordering. The working pixel inventory
is **5,666 modules and 12,410 sensitive chip areas**, including the unchanged
3,050 barrel modules and 6,794 barrel chip areas.

The selection, tradeoffs and scope are in
[DES040](../../docs/design/DES-040-tracker-resolution-optimization.md) and the
[human selection record](../../docs/design/inputs/DES-040-balanced-selection.json).
This working simulation baseline does not certify engineering service capacity,
thermal performance or a new Geant4 material map. The retained optimisation uses
its separately qualified effective profile transport and homogeneous added-disk
ACTS material; detailed DD4hep donor geometry and that approximation are distinct.

## Generate from maintained sources

Pure generation and source controls require Python only:

```sh
python3 -B tools/pixel_barrel_dd4hep/export.py --output build/pixel-barrel
python3 -B tools/pixel_detector_dd4hep/export.py --output build/pixel-detector
python3 -B tools/tracker_dd4hep/export.py --output build/tracker
python3 -B -m unittest discover -s tools/pixel_barrel_dd4hep -p 'test_*.py' -v
python3 -B -m unittest discover -s tools/pixel_detector_dd4hep -p 'test_*.py' -v
python3 -B -m unittest discover -s tools/tracker_dd4hep -p 'test_*.py' -v
```

CMake builds these same defaults. The pixel output contains `pixel-detector.xml`,
`materials.xml`, `expected.json`, `service-accounting.json`, `config.json` and
`manifest.json`, with the standalone barrel under `barrel/`. The integrated
tracker retains its beam pipe, 28.8 mm passive pixel aperture, strips, readouts
and existing factories. No canonical source imports the optimisation prototype.

[The balanced pixel configuration](../../detector/config/pixel-detector-balanced.json)
centralises placements; [the barrel configuration](../../detector/config/pixel-barrel-balanced.json)
retains the frozen barrel inputs and refers to that placement contract. Generators
emit complete repeated units at those coordinates. They never patch a previously
generated XML. The original donor datum still determines radial luminous-region
compensation, patch placement and support inventory; changing a disk station is
a rigid translation. Barrel local module and stave structures stay fixed. Ring
radii and foot faces follow the corresponding layer without recomputing the
local mounting design. Cable radial bands move while wedge angle preserves
exact reference inventory.

The source audits report ring/foot CFRP volume changes, local cable placement,
donor identity, new support/cooling and collector inventory. Existing collectors
move with their logical disks; layer 10 adds donor 2 collectors. Rails retain the
fixed carrier/flange span and cross-sections with one slot at each physical
station. **Global trunk, bypass and rear-turn geometry, material recipes and
inventory stay the reference control.** Their cumulative branch connectivity,
capacity and hydraulic performance are not requalified by the added disk.
Inherited service-space failures remain visible.

## Historical explicit controls

No old input snapshot or reference configuration is repinned. Use these explicit
controls to reproduce their geometry:

```sh
python3 -B tools/pixel_detector_dd4hep/export.py \
  --config detector/config/pixel-detector-trimmed.json --output build/pixel-des019
python3 -B tools/pixel_detector_dd4hep/export.py \
  --config detector/config/pixel-detector.json --output build/pixel-des015
python3 -B tools/pixel_barrel_dd4hep/export.py \
  --config detector/config/pixel-barrel.json --output build/barrel-des013
python3 -B tools/tracker_dd4hep/export.py \
  --pixel-config detector/config/pixel-detector-trimmed.json --output build/tracker-reference
```

DES019 has 5,362 modules/11,806 chip areas and nine disks per end at the original
PR40 stations. DES015 is the explicit quad-only control. PR29 barrel configuration
also remains available. Artifact metadata and generator hashes identify the
executing source revision, so physical reference reproducibility does not imply
byte-identical regenerated metadata. Original frozen TDR and validation reports
remain historical evidence.

## Native construction and display

Read the [ACTS Spack workflow](../../skills/acts-spack/SKILL.md) and run the node
preflight before native work. Do not modify a shared dependency installation to
satisfy that preflight. Use the task's verified runtime and repository-local build.
Construction, overlaps, ACTS conversion and Geant4 checks are separate from the
Python source tests. Existing historical native reports establish only their
recorded source/configuration, not an automatic pass for a new default.

`tools/pixel_detector_dd4hep/refresh.py` can build repository factories, run its
configured CTests and export ROOT/nodehammer views in an activated environment.
Its `--geant4-init` option initializes DDG4/FTFP_BERT without transporting events;
it is not a material scan or tracking validation. The standalone pixel compact
has no beam pipe, strips or magnetic field. Use the integrated tracker entrypoint
for those components, with a separate explicit field/transport configuration.

The reusable C++ factories remain `PixelComponents`, `PixelEndcapParts` and
`PixelEndcap`. Existing XML parameters already express the balanced placement;
no factory schema or sensitive-detector change is required. Endcap systems remain
2 (negative) and 3 (positive); barrel system 1 and all segmentation/bit fields stay
fixed. New logical layer 10 fits the existing unsigned four-bit endcap field.
