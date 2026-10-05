# DES-002 — Candidate A mounting rings and barrel assembly

Status: **PROTOTYPE**, 2026-09-30. Response to
[PR #29's mounting-ring request](https://github.com/asalzburger/nodd/pull/29#issuecomment-5910690174).
Governing proposal: [DES-002 PS-C13/C14](../../../design/DES-002-pixel-barrel-support-cooling.md#mounting-rings-for-candidate-a).
The selected module layout, sensitive surfaces and outward stave stack are unchanged.

## How many rings, where, and why?

Propose **six rings per barrel**, with **24 rings across B1–B4**:

| Ring centre z | Role | Constraint proposal |
| --- | --- | --- |
| −546 mm | End mounting ring | Connect barrel to global end support; one axial locating station |
| −330 mm | Intermediate stiffening ring | Hold cross-section shape, share loads; permit longitudinal contraction |
| −110 mm | Intermediate stiffening ring | Same |
| +110 mm | Intermediate stiffening ring | Same; plane used for the new x–y drawings |
| +330 mm | Intermediate stiffening ring | Same |
| +546 mm | End mounting ring | Connect to opposite global end support; permit longitudinal contraction |

The **two end rings provide the mounting interfaces**, and four intermediate rings
tie the staves together through bearing feet. A circular ring is a natural common
datum for these uninclined barrel columns; segmentation for assembly and its
joints still need design. The existing thin-stave calculation strongly motivates
intermediate restraint: the isolated 1120 mm end-supported beam screen gives
millimetre-scale sag. Six stations retain the earlier proposed station count,
with at most **220 mm** spacing. They are a starting engineering hypothesis,
**not a proven minimum** or an optimization result.

The interior rings are not anchored to an infinitely stiff external reference.
Their deformation, the collective barrel bending, end-mount compliance, thermal
distortion and vibration require a complete cage model and measurement. Merely
adding rings does **not** validate the earlier 250 mm simply-supported sag values.
A qualified global support connection or sufficient cage stiffness remains
necessary. The global end brackets are an unresolved interface, not a hidden
zero-mass component.

**PS-F07 — FACT:** IBL used support rings and a segmented central ring clipped
to stave feet. Its central ring increased radial stiffness while allowing other
motions; residual temperature-dependent distortion remained. This is a useful
precedent for both the concept and its qualification limits, not a source for
nODD's six stations. See [IBL §7.3](https://arxiv.org/html/1803.00844), printed/PDF
p. 75, catalogue source `SRC-ATLAS-IBL-PRODUCTION-2018`.

## Drawings

The new **x–y section at z = +110 mm** cuts one complete ring on each barrel,
with all staves, outward cooling and stagger-dependent feet. The previous
[z = +25 mm section](../outward-A/results.md) remains the view between rings.

![All four barrels through a mounting ring plane](barrel-all.png)

![Barrel absolute-radius versus z view](barrels-rz.png)

| View | PNG | PDF | SVG |
| --- | --- | --- | --- |
| B1, full ring and all 12 staves | [PNG](barrel-B1.png) | [PDF](barrel-B1.pdf) | [SVG](barrel-B1.svg) |
| B2, full ring and all 22 staves | [PNG](barrel-B2.png) | [PDF](barrel-B2.pdf) | [SVG](barrel-B2.svg) |
| B3, full ring and all 18 staves | [PNG](barrel-B3.png) | [PDF](barrel-B3.pdf) | [SVG](barrel-B3.svg) |
| B4, full ring and all 30 staves | [PNG](barrel-B4.png) | [PDF](barrel-B4.pdf) | [SVG](barrel-B4.svg) |
| Combined x–y | [PNG](barrel-all.png) | [PDF](barrel-all.pdf) | [SVG](barrel-all.svg) |
| Combined \|r\|–z, with B4 end detail | [PNG](barrels-rz.png) | [PDF](barrels-rz.pdf) | [SVG](barrels-rz.svg) |

The longitudinal figure is a projection over azimuth, including both radial
stagger levels and actual module/active-patch extents. Vertical dotted guides
locate ring stations; they do not represent solid walls connecting the layers.
The ring itself exists only over its 8 mm z width. The end detail shows the
service bay rather than implying that the projected 190 mm trunk radius is an
exclusion cylinder at every z. Module sensor/ASIC internals remain unresolved;
green sensitive planes stay at their exact baseline coordinates.

## Envelope, material and service checks

**PS-C13 — NODD DESIGN CHOICE, proposed:** ring section 1 mm radial × 8 mm axial,
with inner radius 0.5 mm beyond the outermost corner of that layer's stave stack.
Each stave has one 4 mm tangential × 8 mm axial foot at each station; its varying
height follows the baseline radial staggering. Feet extend from the outward
back face to the curved inner ring surface. They are solid CFRP screening
envelopes, not detailed bearings or pins through the cooling core.

**PS-I07 — INFERENCE:** derive ring radii from actual module/stave corners.
Calculate ring mass from π(Router² − Rinner²) times axial width and the inherited
1.73 g/cm³ CFRP screening density. Integrate each foot's curved cross-section,
then multiply by axial width and density. This counts all six stations on every
layer and all **492 feet**; shared rings are not charged once per stave.

| Layer | Ring inner–outer radius | Foot height range | Six rings | All feet |
| --- | --- | --- | --- | --- |
| B1 | 42.516–43.516 mm | 0.799–5.783 mm | 22.44 g | 13.05 g |
| B2 | 67.604–68.604 mm | 0.687–4.071 mm | 35.53 g | 17.31 g |
| B3 | 115.133–116.133 mm | 1.130–6.687 mm | 60.33 g | 23.33 g |
| B4 | 189.983–190.983 mm | 0.880–4.635 mm | 99.39 g | 27.44 g |
| Total | — | — | **217.69 g** | **81.14 g** |

Total represented addition: **298.84 g**, excluding ring joints, inserts, pins,
adhesives, sliding/flexural details, flex/services and global end mounts. A radial
crossing of a 1 mm ring alone contributes about **0.474% X0** with the inherited
effective CFRP radiation length; this is a local crossing, not an average or a
sum over all 24 rings. Full directional material scans remain necessary. This
new outward inventory replaces neither the earlier evidence nor its explicit
inward-only rib calculation; it is separate proposed material.

**PS-I08 — INFERENCE:** moving the end stations inward from ±560 to ±546 mm
places the end rings at **|z| = 542–550 mm**, leaving **5 mm** before the
reserved barrel service bay at |z| = 555 mm. The intermediate centres move from
±336/±112 to ±330/±110 mm to keep a simple near-uniform pitch. All feet remain
within the continuous stave length; module rows are retained. B4's outer ring
radius exceeds the projected 190 mm trunk radius by 0.983 mm, but there is **no
radial–axial intersection** because the actual trunk starts beyond the rings.
This does not qualify global end brackets or pipe/connector installation space.

The executed nominal screen reports **zero intersections** for new rings/feet
against module bodies, stave boxes, other rings/feet, existing support reservations
and reserved service volumes. Ring tests use radial–axial extents; foot tests use
conservative enclosing boxes and the existing oriented-box separating-axis test.
Own-ring contact at each curved foot is intentional. Numerical tolerance is
10⁻⁷ mm for the OBB test (the existing service projection helper uses 10⁻⁹ mm);
neither is a manufacturing or cooldown allowance. No full DD4hep, ACTS, FEA,
thermal/hydraulic qualification or tracking-performance run is claimed.

## Reproduction and retained evidence

```sh
MPLCONFIGDIR=/tmp/nodd-des002-mpl python3 -B tools/pixel_support/mounting.py
python3 -B -m unittest discover -s tools/pixel_support -p 'test_*.py' -v
```

The generator and [configuration](../../../../tools/pixel_support/mounting.json)
are isolated prototypes. [screening.json](screening.json) records unrounded
results, command, source revision, exact baseline/source hashes and Python,
NumPy and Matplotlib versions. [artifacts.json](artifacts.json) records all 18
exports and the numerical screen. Earlier inward and between-ring evidence
remains unchanged. The controls include intentionally putting a ring in the
service bay, retaining module coordinates and inventory, rejecting feet wider
than the spine, and comparing analytic foot volume to numerical integration.

Human review is still needed for the proposed ring count and constraint scheme,
complete cage/end-mount stiffness, joints, assembly tolerances and material.
