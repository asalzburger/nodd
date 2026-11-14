# SESSION-2026-11-14-lar-routing-rz — LAr routing RZ drawings

## Scope and selected request

Exact user request: “Can you make an rz view of the old and new routing proposal ?”
Continuation of existing draftPR142, using its dedicated branch at clean initial
revision21d2f01f99156034f7a80257fa642f1c2a4d9548. New bounded drawing session;
prior task journals and token ownership remain distinct. PROJECT stageB applies.

## Drawing choices and current status

The main equal-scale RZ figure compares old/new routing with unchanged ECAL/HCAL
positions and800mm front gap. The separate conditional400mm-gap view shifts ECAL
only; HCAL radial exit stays500mm. The crop shows the outer positive-z region;
forward collar is off-screen and unresolved. Drawings show one representative
100mm jacket with analytical normal offsets, dashed20mm clearance, projected
rings/board rows and conceptual neck. No actual port/bundle fit is implied.

Inputs are read as pinned committed Git blobs; source, script and output hashes
are retained. Centreline placement seeds are explicit drawing choices. No detector
configuration, native geometry or response model changed. Existing Matplotlib/
NumPy Python only; no native runtime or dependency installation.

First visual inspection found the comparison legend overlapping its footer;
separated margins/legend/footer and corrected the rear leader to avoid the500mm
dimension label. Initial inventory refresh ran before README existed and failed;
added README and reran successfully. Final images are being checked before review.

Matplotlib SVG path lines also emitted trailing whitespace. The first diff check
reported this; normalized whitespace during SVG export, parsed XML, rehashed and
reproduced all outputs before publication. PNG pixels unchanged. The unissued
review contract was refreshed to the corrected source revision before dispatch.

## Revision-specific visual review assignment

Recorded before dispatch; explicit generic SysArch role fallback.

```json
{
  "id": "LAR-RZ-SysArch",
  "role": "SysArch",
  "input_revision": "170d3d8f8f89bde0ef5076bd42281409a86116e0",
  "inputs": [
    "tools/lar_calorimeter/draw_routing_rz.py",
    "tools/lar_calorimeter/barrel.json",
    "tools/lar_calorimeter/endcaps.json",
    "tools/lar_calorimeter/services.json",
    "docs/design/inputs/DES-032-side-rear-routing.md",
    "docs/design/inputs/lar-gap-options/routing-rz/README.md",
    "docs/design/inputs/lar-gap-options/routing-rz/routing-rz.json",
    "docs/design/inputs/lar-gap-options/routing-rz/routing-rz-comparison.png",
    "docs/design/inputs/lar-gap-options/routing-rz/routing-rz-gap-target.png"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Review exact committed RZ drawings against pinned21d2f01f source proposal/configuration. Inspect images visually after verifying working-tree bytes equal pinned blobs, or extract pinned image bytes to ignored build before view_image. Check finite100mm jacket and20mm offset depiction, source/seed provenance, old/new same800mm gap versus separately conditional400mm target, fixed500mm radial exit despite900mm rear EC space, conceptual neck/ports/HCAL labels, and misleading omitted context. Confirm clear image layout and flag factual or safety-of-interpretation errors. This is visual/source review only, no new route/engineering acceptance; no nested delegation.",
  "deliverable": "Concise findings or no findings with exact target revision, image inspection and actual checks; return only, no writes except ignored image extraction if needed. Coordinator curates into PR142 drawing session.",
  "completion": "Report reviewed revision and source hashes/locators, visual findings, actual checks, limits and no authored artifact changes."
}
```

Initial SysArch review170d3d8f found no factual geometry/interpretation issue but
required the fixed component palette. Corrected ECAL/HCAL fills, substructure
shades/legend and text contrast; reproduced and rehashed all outputs.

## Final visual review assignment

Recorded before dispatch; exact corrected target.

```json
{
  "id": "LAR-RZ-SysArch-final",
  "role": "SysArch",
  "input_revision": "d1864261f52e0acd8554620bb82c78a51ed756e4",
  "inputs": [
    "tools/lar_calorimeter/draw_routing_rz.py",
    "tools/lar_calorimeter/barrel.json",
    "tools/lar_calorimeter/endcaps.json",
    "tools/lar_calorimeter/services.json",
    "docs/design/inputs/DES-032-side-rear-routing.md",
    "docs/design/inputs/lar-gap-options/routing-rz/README.md",
    "docs/design/inputs/lar-gap-options/routing-rz/routing-rz.json",
    "docs/design/inputs/lar-gap-options/routing-rz/routing-rz-comparison.png",
    "docs/design/inputs/lar-gap-options/routing-rz/routing-rz-gap-target.png"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Verify palette remediation and final visual readability at this exact revision. Compare with prior170d3d8f assessment; confirm fixed ECAL#cccc00 and HCAL#cc6600 fills and matching legend, labelled light ECAL substructure, legible dark text, and no changed geometry/qualifications. Verify new hashes and inspect both PNGs visually. Retain previous factual assessment by reference; no native validation or engineering acceptance, no nested delegation.",
  "deliverable": "Concise findings or no findings with exact target revision, image inspection and actual checks; return only, no writes except ignored image extraction if needed. Coordinator curates into PR142 drawing session.",
  "completion": "Report reviewed revision and source hashes/locators, visual findings, actual checks, limits and no authored artifact changes."
}
```

## Final visual assessment and checks

LAR-RZ-SysArch-final reviewed d1864261f52e0acd8554620bb82c78a51ed756e4 after
the palette correction. No remaining findings in this bounded review. Verified
all nine assignment hashes/working-tree equality, source/script/PNG receipt
hashes and both final images. Fixed yellow ECAL/orange HCAL fills/legend, labelled
light ECAL substructure and dark text are legible. Prior factual geometry/limits
remain unchanged. The reviewer contributed earlier topology inputs; this is
separate source/visual verification, not independent engineering qualification.
No authored changes, native validation or human acceptance.

Coordinator rerendered all4PNG/SVG exports plus receipt to a clean directory:
byte-identical; SVG XML parses, all7source hashes verify, and wrong-source input
fails closed. Analytical normals have unit length and retain100mm jacket width
and20mm offsets; centreline offset619.403mm, rear maximum z6330mm, bus wall
clearances30/51mm and fixed500mm radial exit agree with the proposal. No full
bundle/port fit claim or detector change.

## Token coverage

Two completed visual-review turns belong to this drawing session. The newly
available prior routing parent stays in its original session. Current drawing
parent counters are not finalized and excluded; missing model/provider/version
remain unknown. Exact observations are imported from the selected usage-only
recovery, with no raw private state or duplicated cumulative counters.
