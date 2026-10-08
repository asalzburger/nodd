# DES-024 — Straight beryllium beampipe

- Status: DRAFT
- Date: 2026-10-08
- Scope: user-authorized implementation for review; no engineering sign-off.

The requested pipe is a concentric, passive beryllium wall. All dimensions below
are centralized in `detector/config/beampipe.json`. The bore is a distinct vacuum
volume. Its wall DetElement is a Tube directly placed in the world, permitting
DD4hep-backed ACTS cylindrical conversion without a surrogate filled cylinder.

| Parameter | Classification | Value and rationale |
| --- | --- | --- |
| Wall thickness | NODD DESIGN CHOICE | 0.8 mm, explicit user request on 2026-10-08. |
| Inner radius | NODD DESIGN CHOICE | 27 mm; interpretation of requested radius pending confirmation. Outer radius is 27.8 mm. |
| Half length | NODD DESIGN CHOICE | 4000 mm; inherited straight-pipe extent covering the tracker, provisional pending interaction-region engineering. |
| Be density | FACT | 1.848 g/cm³, ODD v6.0.2 `xml/OpenDataDetectorMaterials.xml`, material Beryllium (SRC-ODD-BE-602). |
| Composition | NODD DESIGN CHOICE | Pure natural Be; no alloy, coating, flange or bellows included. |
| Vacuum | NODD DESIGN CHOICE | Existing nODD numerical placeholder: hydrogen at 1e-12 g/cm³, not a pressure specification. |
| System ID | NODD DESIGN CHOICE | 0, passive reserved ID; tracker readout systems 1–6 unchanged. |
| World margin | NODD DESIGN CHOICE | Standalone fixture 100 × 100 × 4100 mm half sizes; assembly takes maxima of component envelopes. |

The inferred wall volume is π[(27.8 mm)²−(27 mm)²] × 8000 mm;
its mass follows from that volume and the stated density. Directional wall paths
from the origin are 0.8 cosh(η) mm until the finite axial end truncates a ray.
These are independent analytical validation controls, not tuned reference outputs.

Validate dimensions, elemental composition, mass, bore contents, DD4hep flags,
zero overlaps at 1e-5 mm and radial/oblique radiation-length paths. The integrated
model must additionally verify clearance against the actual tracker placements.

Vacuum pressure, mechanical stability, buckling, heating, alignment, beam impedance,
forward transitions, installation, flanges and supports remain unqualified. This
straight cylinder is an explicit simulation baseline, not a buildable vacuum system.
