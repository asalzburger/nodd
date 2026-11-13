# Two ECAL working baselines and issue 114 integration

- Status: **DRAFT / PROTOTYPE**
- Date: 2026-11-04
- Authority: the human campaign request restores both ECAL options on main,
  with EDM/I/O from [issue 114](https://github.com/asalzburger/nodd/issues/114).
  This authorizes the bounded integration; engineering sign-off remains open.
- Governing designs: DES025, DES030–034, DES039 and DES043; ADR008–011.

## Baseline contract

**NODD DESIGN CHOICE:** retain LAYOUT-001 (Si–W) and LAYOUT-002 (LAr) as
selectable working baseline packages. Both use the maintained DES043 tracker,
the existing inner-solenoid allocation, and the merged DES039 FCAL design.
No physical dimension or material is retuned during restoration.

`tools/calorimeter_baselines/export.py` exports the current tracker and the
selected complete ECAL barrel/endcaps, then composes their compact descriptions.
Its manifest distinguishes the constructed tracker/ECAL stage from the shared
solenoid allocation, analytical HCAL regional designs, and ROOT-only FCAL design.
Those remaining systems are not silently represented by sensitive air envelopes.
The two packages therefore have runnable tracker/ECAL geometry and a common
design baseline; complete detector construction and response remain follow-ups.

### Si–W Geant4 hierarchy

**NODD DESIGN CHOICE (human-directed 2026-11-10):** default the maintained
LAYOUT-001 export to reusable solid wedge mothers for DES-030 and DES-031.
Use the enclosing volume's own material for each wedge. A 0.25 mm padding
around the existing frame bounds separates the new boundaries from physical
hardware while keeping the nominal inter-wedge gap. The added volumes serve
navigation. Keep the physical solids, material definitions, placements,
readouts and cell-ID encoding of the working baseline.

The compact keeps its replica poses and gains an envelope description. The
factory places one logical wedge per component and inherits side and sector
from its placements, layer from the interior placements and module from the
existing sensors or boards. The endcap reuse includes the existing proper
negative-side rotation. Legacy standalone exports and compacts without an
envelope retain their assembly hierarchy for historical reproduction.

### LAr Geant4 hierarchy

**NODD DESIGN CHOICE (human-directed 2026-11-13):** use reusable solid
inclined-period mothers in the maintained LAYOUT-002 export. One barrel
template is placed 1536 times; three turbine templates are placed
384/720/1360 times on each end. Their boundaries follow adjacent absorber
steel faces and the original annular/axial clipping. Each mother uses the
actual enclosing material. Existing daughter shapes, materials, transforms,
replica IDs and virtual readouts retain their definitions. Standalone
component exporters keep the legacy assembly control; `--real-periods`
selects the maintained hierarchy there.

The [placement investigation](../../validation/lar-placement/README.md)
records native equivalence, material scans and one matched serial timing
pair. The [default-export validation](../../validation/lar-placement-default/README.md)
checks the maintained route. This changes the simulation hierarchy of the
DRAFT / PROTOTYPE candidate; it grants no engineering or response acceptance.

**FACT (source):** standalone Si–W barrel and endcap exports both use system8;
standalone LAr barrel/endcaps use10/11, while the FCAL design proposes10.
See DES030/031 exporters, DES032/033 geometry builders and
`tools/forward_calorimeter/inputs.json` at the source revisions retained in the
campaign journal. These standalone component namespaces cannot be composed
unchanged.

**NODD DESIGN CHOICE:** the integrated namespace preserves beam-pipe0 and tracker IDs1–7,
Si–W barrel8 and LAr barrel/endcaps10/11; only integrated Si–W endcaps map8→9.
Reserve12 for a future integrated FCAL and13/14 for future HCAL regions.
These reservations do not modify the standalone FCAL/HCAL proposals or establish
a cell-ID service. The exporter records each actual source→integrated root ID;
readout bit layouts, local IDs, placements and materials retain their meaning.

Added ECAL material names are prefixed per component, with fraction references and
detector material attributes transformed together. The tracker retains every existing material/element name, including the factory’s hardcoded Beryllium; ECAL Air/Vacuum are also namespaced, preserving even source serialization or recipe differences. Conflicting definitions within one namespace fail. This prevents two
components from silently selecting different recipes under one shared name.

## Initial digitization boundary

**FACT (issue114):** restore hit/cluster structs, EDM4hep conversion, metadata,
fixtures and persistent round trips against ACTS355ea684 and installed
EDM4hep/podio. Algorithm wrappers retain collection configuration and handles,
and explicitly reject execution until a physical implementation is supplied.
Threshold response, connected-component clustering, jets, upstream hooks and
tracker relocation are excluded. This is the first data/algorithm interface
stage, not calibrated digitization or shower reconstruction.

## Review handover and next gates

The unanswered [PR75 review](https://github.com/asalzburger/nodd/pull/75#issuecomment-6278091329)
survives consolidation. Its eleven questions are grouped below without claiming
engineering calculations that were not performed.

| Review questions | Retained evidence / remaining work |
| --- | --- |
| 1–3: radial space, turbine separation, Si–W compactness | DES032/033/034 and the retained DES032 transition review distinguish routing choices from intrinsic technology requirements. The800mm front gap remains a routing hypothesis; define real header/feedthrough endpoints and compare rear egress before changing it. |
| 4: figure readability | Current DES043 layout views use the fixed component palette and labelled FCAL hatching from merged PR112. Historical PR75 figures remain dated source evidence. |
| 5–6: materials, dimensions, physics criteria | DES030–034 distinguish public hardware facts, calculated inventories and project choices. These prototypes were not optimized or accepted using shower/jet/PF performance. |
| 7 and9: forces, mass, flows and engineering feasibility | Recorded mass/power/ideal-flow ledgers are accounting calculations. Structural, thermal, hydraulic, load-path and irradiation qualification still require engineering analysis and human review. |
| 8: geometry checking | Retained native ROOT/DD4hep shape, placement, material, ID and overlap audits, with recipes/seeds/tolerances, establish their exact isolated scopes. New integrated compacts require their own native audit; old component passes are not a union pass. |
| 10–11: complete object hierarchy, tolerances and both layouts | The exporter preserves component hierarchy and checks namespace/material composition. Full connected services, installation tolerances, machine pipe/shielding and complete detector interfaces remain unqualified. |

HCAL81/84/85 retain the common-module and separate regional design proposals.
The regional configurations currently fit the Si–W dimensions; a LAr regional
parameterization and independent replay are required. FCAL88 is already merged;
its readout/DD4hep/Geant4 integration is the next implementation gate.

Further response work must define units/calibration, timing/noise/thresholds,
quenching/optical and SiPM effects, then benchmark physical digitization before
introducing calibrated clustering. Jets and particle flow follow calibrated
clusters. None of these later steps is marked complete by this campaign.
