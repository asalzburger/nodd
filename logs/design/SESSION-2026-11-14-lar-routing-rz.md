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
