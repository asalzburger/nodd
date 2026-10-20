# IC-P1 — independent physics/claim/figure assessment

Reviewed revision: `0d7a815fc299c971be1c6af3911c50e9f0a9b585`.
Role: explicit PhysVal fallback mandate; no native-profile claim. This review context authored neither the closure study nor its implementation. Repository mode: read-only. The dirty session Markdown was excluded from the evidence.

**No material claim or figure defect found.** The retained evidence answers PR90 comment6285814869 as a bounded feasibility question. Literal continuous closure conflicts with the fixed BT legs; recovering much of the extra fan-shaped gap is geometrically possible after changing the segmentation contract. This assessment grants no adoption, design sign-off or human acceptance.

## Independent observables and physical interpretation

Primary inputs were the actual candidate dimensions/bases, study construction source and magnetic mask/box definitions at the reviewed revision, followed by the retained reports and figures. The current wheel contains twelve convex whole trapezoids per end. Its affine straight sides clear each finite BT rectangle but extend that clearance into radial regions without BT material. The obstruction is twelve localized slots, not a filled annulus.

The actual BT warm rectangle is x=4.35–4.85 m, |y|≤0.30 m in each seam frame; its straight section spans the entire wheel slab z=6.4956–6.9956 m. The 50 mm componentwise clearance box is x=4.30–4.90 m, |y|≤0.35 m. The additional 10 mm tangent margin is a certification choice. Independently, the point (4.6,0.1,z) lies in an ordinary 20 mm-seam full-sector chamber and in the warm leg throughout that depth. The incorrectly unrotated radial-bound control also intersects a BT box. Axial translation within the allowed centre interval 6.7412–6.7500 m cannot remove the obstruction.

The independent checker reconstructs the optional bands from the projected clearance rectangle and outer-corner bound, rather than substituting their reported metrics. It clips the front/back slope halfspaces and evaluates solid angle through a Green-theorem boundary integral, separately from the source's spherical-triangle calculation. It reproduces:

| Observable | Current | Two bands | Three bands, slot localized |
| --- | ---: | ---: | ---: |
| Chamber area per end [m²] |63.166752|77.553256|78.688450|
| Planar missing area [%] |31.171240|15.495188|14.258241|
| Full-depth same-chamber ray loss [%] |30.153774|19.170277|27.972034|
| Same ray loss, 30 mm border proxy [%] |34.891588|25.379053|34.808183|

The planar denominator is π(5.45²−0.70²). The whole-depth ray denominator per end is 2π[1/√(1+(0.70/zfront)²)−1/√(1+(5.45/zback)²)]. Denominators are common across layouts within each metric. In-plane 30 mm erosion is only a border proxy; it supplies no detector-response model. A retained explicit counterexample has its front point in one radial band and rear point in another, explaining why added radial seams hurt this same-chamber observable despite better planar closure.

The plotted M1 outer band has base-distance 0.410663677 m and a small nonzero full-depth cone, 0.001062109 sr per sector. A1's distinct conservative outer band has zero cone. The reports correctly distinguish those recipes. Both violate the old 0.50 m minimum span. Two bands give 24 outlines/two shapes per end, but their 3.350306 m inner cassette and radial tiling require an explicit contract amendment. Neither option is adopted or covered by the prior ACTS results.

## Actual checks and figure evidence

The portable [physics-check.py](physics-check.py) and executed [physics-check.json](physics-check.json) record the focused checks (exit 0):

- Independent areas and solid angles agree with retained values within 3×10⁻¹² in the loss fractions. An additional 65,536 common iid direction bank, seed20261020, agrees within 0.61 sampling standard errors. The retained M1 1,048,576-direction result was inspected, not rerun.
- All displayed footprints are convex; actual bases are orthonormal. Reconstructed display vertices agree within 5.7×10⁻¹⁵ m. Independent SAT checks against all twelve inflated BT boxes give zero conflicts in 864 positive-end tests; the axial supporting bounds extend these checks through the entire depth. All 84 support members near the positive slab have projected minimum radius at least 5.60 m. The retained M1/A1 full-volume/interface matrices were inspected, not broadly rerun.
- Both actual pinned PNGs were visually inspected. Layout counts, localized BT slots, metric labels, narrow-band warning and unadopted/no-efficiency captions are legible and consistent. All 72 blue comparison SVG paths and both detail paths match the source display polygons within 3.5×10⁻⁸ m after decoding the actual axis transforms, consistent with SVG coordinate serialization.
- All recorded source and figure SHA-256 values match the reviewed blobs, including the M1 checker identity and A1 input identities. Precommit drawing-source flags are explicit; the final reviewed bytes resolve to their recorded hashes. All 350 old scientific Git blobs match both the baseline and reviewed revision. The old evidence index and DES040 are preserved byte-for-byte as prefixes; their additions are the separate-study link and explicitly unadopted feasibility contract.

## Limits and recommendation

No ACTS, field, material, response, reconstruction or engineering calculation was performed. A scratch rerender using system Python stopped before rendering because Matplotlib was unavailable; no dependencies were changed. PNG inspection plus exact source/artifact hashes and independent SVG-coordinate checks support this figure assessment. Chamber internals, useful segment response, sag/alignment, services and mechanical qualification remain open before any adoption.

The target's final contract sentence “same ideal annulus denominator” admits a minor editorial ambiguity despite the clear earlier distinction; “common denominator across layouts for each metric” would be clearer. It does not affect the numerical or scientific conclusion. Recommend retaining the study as the conditional feasibility answer with its existing unadopted and geometry-only limits. Repository files changed by this reviewer: none.
