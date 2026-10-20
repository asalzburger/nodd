# IC-A1 — fixed-interface feasibility assessment

Input revision: `15015d378b5b77b3bb11698809d1680d12b8a91c`.
Role: explicit SysArch fallback mandate, read in full; no native-profile claim.
Mode: read-only repository; scratch calculations only. No engineering approval.

## Finding

Literal azimuthally continuous inner-wheel chamber coverage to R=5.45 m is physically impossible with the retained BT, 500 mm chamber depth, HCAL and ECT positions. Twelve finite BT inner legs intersect the whole axial slot. Much of the current fan-shaped empty area is nevertheless avoidable if the chamber segmentation contract changes. Those two statements must be kept separate.

## Exact physical obstruction

The pinned magnetic configuration has BT inner-leg centre radius 6.7−2.1=4.6 m and warm cross-section 0.50 m normal by 0.60 m tangential. In each seam's meridional/tangent frame its occupied rectangle is x=[4.35,4.85] m, y=[−0.30,+0.30] m throughout the wheel depth z=[6.4956,6.9956] m. The BT centreline straight section extends to |z|=11.8−1.0=10.8 m; the wheel is well within it. The outer leg starts at R=8.55 m, outside the wheel; no filled annular cryostat is assumed.

Explicit adverse witness: (4.6,0.1,z) m at z=6.4956,6.7456,6.9956 is inside both the actual warm BT mask and a conventional 12-sector trapezoid with 20 mm seams and 5.45 m outer-vertex radius. The three points are across the full chamber depth, not merely a centre-plane drawing. Their containing prism and source masks are retained in `interface-check.json`.

At the circle R=4.6 m, the actual twelve occupied slots cover 24.9289% of phi; the conservative 50 mm clearance boxes reserve 29.0912%. These are single-radius geometric fractions, not solid-angle efficiency. For the actual slot the angle bound is |phi−30°k|≤asin(0.3/4.6). They are discrete rectangles, never a whole annulus.

The existing full-volume policy conservatively expands the rectangle to x=[4.30,4.90] m and y=[−0.35,+0.35] m. This is stronger than a rounded Euclidean Minkowski boundary near a corner and is already the governing policy. The selected affine corridor reaches y=0.36 m at x=4.30 m: the extra 10 mm is a certification design margin, not coil material. Actual minimum separation between the current straight side and the physical box is 64.5828 mm; the full gap at the outer seam is approximately 941.0 mm. Straight edges extending this obstruction all the way to bore and rim cause avoidable extra white area.

With one whole trapezoid per 30° sector, straight side edges cannot form a local bulge around a BT box and then return to a narrow outer seam. A conventional near-radial edge giving a 20 mm outer seam passes through the witness. Eliminating the fan gaps while preserving the finite BT slots therefore requires more chamber pieces, a non-trapezoidal footprint, a change to coil geometry, or a differently qualified stagger/depth arrangement. Merely shifting the same 500 mm wheel axially cannot resolve the BT conflict.

## Axial and frame interfaces

HCAL rear: |z|=6.4412 m. ECT warm front: 7.05 m. Gross slot: 0.6088 m. With 0.5 m depth and 50 mm margins at both ends, allowed wheel centre is 6.7412..6.7500 m. The selected 6.7456 m gives 54.4 mm at each end and only ±4.4 mm centre movement. The HCAL margin remains provisional; this calculation does not appoint the calorimeter owner or approve the margin.

All 484 retained support prisms were inspected. Eighty-four have z AABBs within 50 mm of the positive wheel depth. Their full-prism XY projections have minimum radius at least 5.60 m. Thus any wheel prism entirely inside R≤5.45 m is at least 150 mm radially separated from these members; even 50 mm support padding is safe. The nearest members are the front inner carrier ring, spanning z=6.15..6.45 m and minimum R=5.60 m. Front lugs span z=6.45..7.05 m but have minimum radius 5.70 m. This bound uses actual finite prisms and all support members, not only a centre-plane section or assumed C12 support symmetry.

B1's outer axial bound is |z|=6.4456 m, so the current end face has the intended 50 mm gap to the inner wheel. B2 and B3 have minimum full-prism projected radii 6.45 and 7.95 m, safely outside the retained 5.45 m wheel bound. Keeping these bounds makes radial-band repacking locally compatible with the saved barrel geometry. Enlarging the wheel past its bound needs a new barrel/frame audit, because it encounters front lugs/ring/spokes.

Endpoint ownership: MuonTech owns chamber segmentation/envelopes; SysArch owns BT/ECT/support reservations and shared clearances; the HCAL owner must confirm the provisional 50 mm downstream clearance. SoftEng owns representation fidelity. Global right-handed metres, z along beam, x horizontal/y up apply. This assignment changes no endpoint input.

## Sufficient radial recovery bounds; no adoption

For a conservative radial recipe, every lower-band vertex with R<4.30 m is below all inflated BT inner-leg boxes. Every upper-band point with R>sqrt(4.90²+0.35²)=4.912484097 m is above them. These are sufficient separation bounds, not maximally permissive boundaries and not a claim that the intervening annulus is fully occupied. At each 15°+30°k sector, a less conservative upper-band supporting-plane bound is u>4.90 cos15°+0.35 sin15°=4.823623215 m, where u is the chamber sector axis. All twelve inner-leg rectangles lie behind that plane. The BT outer legs and return pieces remain excluded independently by radial and axial bounds.

An illustrative scratch recipe used a lower outer-vertex R=4.29 m, the current corridor sides across a middle band, and an upper whole trapezoid with u=4.93..5.266875082 m. The lower/middle and middle/upper base planes have 20 mm gaps. All 72 scratch prisms (three bands × twelve sectors × both ends) pass exact support/barrel/panel SAT: 34,848 support tests, 76,032 barrel tests and 2,556 candidate-pair tests, with zero conflicts. Three representative BT full-volume adaptive certificates pass at 5 mm resolution; the explicit C12 magnetic source supplies the equivalent rotated BT geometry. Separate full-volume BT certificates for an upper band starting at u=4.83 m pass for every sector and both ends, with zero all-member support/barrel conflicts. ECT separation is the retained 54.4 mm whole-volume supporting-plane bound.

These illustrate geometric feasibility only. They are distinct from MuonTech’s independently optimized proposal and must not be substituted for its actual dimensions or geometric fractions. The upper band is 336.9 mm wide for the conservative recipe, or 436.9 mm using u=4.83 m. Both are below the original 500 mm ordinary minimum span. The current exception removes the maximum radial cap for whole wheels; it does not automatically authorize narrow fragments or change the one-whole-sector choice. A future selected segmentation needs its own dimensions, minimum-envelope qualification, inventories, all-volume checks and uncertainty treatment before adoption.

## Full-depth counter limitation

Radial splits add front/back ray losses. A straight IP ray whose midplane radius is 4.6 m shifts by 4.6×0.5/6.7456=0.340963 m between the two normal faces. A radial seam therefore matters over far more than its 20 mm physical width for the same-chamber double-face observable.

For the conservative upper band, u0/zfront=4.93/6.4956 exceeds u1/zback=5.266875082/6.9956. No straight IP ray can cross both normal faces of that upper chamber, even though its midplane XY footprint closes the fan gap. The less conservative u0=4.83 m bound admits a limited full-depth range, but does not establish ACTS availability or a useful MDT segment. Do not quote recovered 2D area as a full-depth, same-module, material, momentum-resolution or reconstructed-efficiency gain. This assignment runs no ACTS propagation or field calculation.

## Actual checks and provenance

Portable command (executed successfully, exit 0): `python3 -B interface-check.py --repo . --revision 15015d378b5b77b3bb11698809d1680d12b8a91c --output interface-check.json`. Source and output are supplied alongside this report; this command combines the separately executed base and all-fold checks. It reads immutable `git show REV:path` inputs, verifies all imported working-tree scientific modules byte-equal those pinned inputs, uses exact source masks/finite SAT, retains occupied witnesses and positive separation controls. No simulation dependencies were invoked. The checker requires NumPy and a checkout whose checked scientific input bytes match the pinned revision; it deliberately refuses substitutions from a different working tree. Output records repository-relative source paths and hashes, with no machine-specific input paths. All seven assigned primary inputs were read; magnetic configuration and toroid exact-mask source were additionally read at the same revision. SHA256 identities are retained in the report JSON.

Source anchors at the pinned revision: `tools/muon_layout/wheels.py` lines 55–85 (affine dimensions), 112–159 (full-volume supporting planes and finite BT boxes); `tools/toroid_prototype/geometry.py` lines 36–80 (actual rounded-racetrack and tangential-slab mask); selected DES040 contract; candidate geometry actual members/panels and magnetic configuration; `xy-sections/sections.json` inner-wheel boxes. The current candidate, maps, inventory, OBJ, ACTS evidence and source files are unchanged.

Files changed in repository: none. No external messages, nested delegation, approval, sign-off or adoption. Main unresolved alternatives: accept the unavoidable finite BT slots and revise radial segmentation; move/change BT; alter depth/stagger within a new axial/interface contract; qualify alternative chamber technology/shape. The present whole-trapezoid prototype remains DRAFT.
