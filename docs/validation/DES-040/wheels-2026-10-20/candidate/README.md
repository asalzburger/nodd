# DES040 selected whole-wheel prototype

The selected DES039/DES040 contract shortens each ECT at its front by 0.50 m,
leaving the rear fixed. Input revision is
`a32558a419404dfe741182b6713ce1f31062fd37`, with the separately recorded
2026-10-20 selected design amendment. This is an isolated outline prototype;
it has no chamber internals or human engineering acceptance.

The frozen [geometry](geometry.json) contains 1,344 chamber envelopes: barrel
stations 168/360/528, and endcap stations 24/216/48 over both ends. There are
12 whole inner and 24 whole outer trapezoids per end. The 216 middle panels are
geometrically unchanged, with fresh certificates. B1/B2/B3 half-lengths are
6.4456/9.2/12.5 m. The new wheel centres are at |z|=6.7456/12.8 m; all outlines
are 0.5 m deep. The first-to-last disk-centre span is now 6.0544 m; the barrel
measurement radii retain their 3 m span.

The inner-wheel straight sides form affine corridors around the BT legs,
with 50 mm coil clearance and an additional 10 mm tangent margin at the
inflated-box constraint. Full derivation and chosen parameters were recorded
before generation in `tools/muon_layout/wheels-config.json`. Inner bases are
0.354423346/1.901652879 m, with radial base-distance 4.666416782 m. Outer bases
are 0.164140917/2.186062207 m, with radial base-distance 7.679008474 m and
20 mm normal seams. Outer corners are bounded by 5.45/8.45 m. These whole-sector
cassette reservations are exempt from the ordinary 1.5 m radial module cap;
they make no long-tube manufacturing or precision claim.

The [controls](geometry-controls.json) pass all 1,344 full-volume coil and
support-clearance certificates, all panel-pair overlap checks, and conservative
HCAL bounds. No unresolved cells are accepted. Analytic axial separation and
inflated BT-box SAT certify the new inner wheels; independent adaptive probes
cross-check all 72 whole-wheel prisms. The frame has 484 members, 1,378 actual
material parts, 156 ports and 10 grounds. All 36 coil case IDs have material
contact paths to ground. Only 48 front lugs change, from |z|=6.45–6.55 m to
6.45–7.05 m; the other 436 members are copied exactly. Added gross aluminium
proxy stock is 1.44 m³ (3,888 kg). Unique-union mass, forces and stiffness are
separate qualifications. No case walls or their mass have been invented.

Inner-wheel axial gaps to HCAL and ECT warm reservations are 54.4 mm each.
The HCAL margin is a provisional 50 mm choice, distinct from the inherited
50 mm coil clearance. The B1-to-inner-wheel seam is 50 mm. The outer wheel
starts at |z|=12.55 m, 100 mm after the rear carrier bound. Actual barrel modules
retain coil/support-driven exclusions; these clearances do not imply full
three-station coverage. The maximum chamber radius/|z| are 8.513349341/13.05 m.

## Straight-ray wheel gaps

The primary, **analytic full-depth** loss relative to an ideal annulus is
**30.1538% inner / 2.7372% outer**. It includes corridor/seam and polygon-boundary
losses. Adding the separate 30 mm border proxy gives **34.8916% / 8.9171%** loss.
The denominator requires both depth faces to lie in the same ideal circular
annulus. Both ends are included. These quantities describe isolated outlines;
they are neither reconstruction efficiency nor a coil/material veto.

The 240×720 midpoint grid aliases thin seams: it reports only 0.7018% outer
loss. It is retained as an adverse sampling cross-check, not the primary result.
The portable [independent check](independent-check.py) samples 524,288 directions
uniformly in each annulus's solid angle and uses direct convex-face crossings.
Its [executed output](independent-check.json) agrees with the analytic envelope
losses within 0.23 and 1.51 sampling standard errors, respectively. These errors
are Monte Carlo sampling errors only. Wheel losses are correlated and must not
be multiplied as independent detector efficiencies. Native before/after ACTS
transport is produced separately.

## Reproduce

Run from the repository root, using Python with NumPy and Matplotlib for views:

```sh
python -m tools.muon_layout.wheels --magnetic-config docs/validation/DES-040/wheels-2026-10-20/magnetic/configuration.json --output docs/validation/DES-040/wheels-2026-10-20/candidate
python docs/validation/DES-040/wheels-2026-10-20/candidate/independent-check.py --root . --output docs/validation/DES-040/wheels-2026-10-20/candidate/independent-check.json
python -m unittest tools.muon_layout.test_geometry tools.muon_layout.test_layout tools.muon_layout.test_support
```

The generation command records its source and magnetic fingerprints in the
controls. The 21 existing geometry/layout/support tests passed. The independent
check records its script/input hashes, seed, sample count, runtime and observed
residuals. [Shape mapping](shape-change-mapping.json) distinguishes retained,
changed, removed and new semantic IDs. The [view](geometry-views.png) shows
blue outlines and actual grey BT warm boxes in the inner-wheel plane; its R–Z
panel is an envelope projection. It does not replace the finite-volume proofs.
