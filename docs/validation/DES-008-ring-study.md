# DES-008 long-strip ring and sandwich study

- Date: 2026-09-25
- Status: **PROTOTYPE**, analytical screening only; no detector acceptance
- Design: [DES-008](../design/DES-008-long-strip-modules.md), under DES-005
- Inputs/code: [reproduction instructions](../../tools/long_strip/README.md)
- Retained output: [JSON results](DES-008-ring-study.json)
- Comparison method: DES-007 / [PR21](https://github.com/asalzburger/nodd/pull/21)
  at `17d84a4c92916a49929db3c5e75684e51bf613b7`

## Geometric result

A **six-ring, 96×96 mm² continuous-strip sandwich** is a useful working geometry:
402 module pairs, one sensor-outline type, no missed pairs on either sampled grid
or any of the three straight-ray vertex fixtures, and no intersecting trial body
prisms. It is conditional on readout feasibility for 96 mm strips, about twice
ITk's cited long-strip row length. The six-ring wedge is a competing geometry,
with 358 pairs and about 2.6% less silicon-outline area, but six sensor types and
approximately 100 mm maximum strip spans. Neither is approved hardware.

Two sensors per module are explicit. The relative stereo angle is 40 mrad,
mid-plane separation 5 mm and per-sensor thickness 0.300 mm. The target annulus
is 700–1100 mm, the reference disk z=1320 mm and vertices z=−150,0,+150 mm.
These are provisional design scenarios, not fixed tracker interfaces.

![Compared sensor outlines](../design/figures/DES-008-rings.svg)

| Candidate | Rings | Sensor types | Module pairs | Sensor count | Two-sensor outline area / annulus | Worst missing-pair area, either grid | Trial body intersections |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Wedge, continuous strips | 6 | 6 | 358 | 716 | 3.191 | 0 sampled | 0 |
| Square 96×96, continuous strips | 6 | 1 | 402 | 804 | 3.276 | 0 sampled | 0 |
| Narrow 48×96, continuous strips | 6 | 1 | 858 | 1716 | 3.496 | 0 sampled | 0 |
| Square 96×96, two nominal 48 mm rows | 6 | 1 | 402 | 804 | 3.276 | 0.3124% | 0 |
| Wide 96×48, 48 mm strips | 12 | 1 | 786 | 1572 | 3.203 | 4.4223% | 0 |
| Wide 96×48, added-ring control | 14 | 1 | 910 | 1820 | 3.708 | 1.3428% | 924 |
| Square 96×96, five-ring control | 5 | 1 | 338 | 676 | 2.754 | 2.4588% | 0 |

Dimensions are tangential ×radial. Area counts **both** sensor outlines, including
inactive internal seams but excluding outside guard/die extensions. An ideal
nonoverlapping double layer would have ratio 2, not 1; divide these ratios by two
for comparison to PR21's single-sensor-area ratios. The active annuli also differ,
so absolute module totals should not be compared as efficiency improvements.
The wedges here use straight clipped strips, not a validated radial strip mask.
“Types” counts outlines only; stereo assembly handedness, readout hybrids, gap
variants and mounting fixtures can add manufacturing variants.

## Why the rejected cases matter

The five-ring square and twelve-ring wide configurations have **zero missing
normal-projection samples**, yet lose 2.46% and 4.42% of pair coverage once the
actual sensor planes and vertex rays are used. Testing only the projected union
would incorrectly shortlist both. In the wide twelve-ring case, 1.63% of the
annulus on the refined +150 mm vertex scan sees both sensor-side labels from
unrelated modules but no same-module pair; those are not counted as valid stereo
measurements. A reconstruction that matches hits across modules would be a
separate measurement/ambiguity contract.

The split square has a 0.100 mm inactive band in each sensor's own rotated frame.
Its worst area loss is 0.3124% on the 250×720 grid and 0.2814% on the 500×1440
grid. The 100×360 scan even gives 0.5289% at the nominal settings: narrow seams
are not numerically converged by these grids. These are measured grid outcomes,
not a precision estimate of total inefficiency. Removing the seam in the explicit
control restores zero missing samples; it does not establish a manufacturable
seam-free two-row sensor. Continuous strips and revised staggering are physically
different alternatives.

Adding rings alone does not solve the short-module case: fourteen wide rings
still miss pairs and have 924 intersecting occupied prisms. These are
**conservative reserved-volume conflicts**, not DD4hep solid-overlap counts.
The current four-level arrangement is inadequate for that candidate; supports,
attachments, overlap and disk placement must be studied together.

## Gap, angle and mounting scans

The following controls use the continuous-strip square candidate on a coarser
100×360 grid, retaining the same margins, ring/module counts and tilt convention.
Full per-vertex and split-row results are retained in JSON. These one-parameter
scans do not establish robustness for arbitrary combined changes.

| Mid-plane gap [mm] | Free silicon-face gap [mm] | Internal cooling-stack residual [mm] | Adjacent-level body clearance [mm] | Trial body intersections | Worst missing-pair samples |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1.8 | 1.5 | −2.5 | 3.9 | 0 | 0 |
| 4.0 | 3.7 | −0.3 | 1.7 | 0 | 0 |
| 5.0 | 4.7 | +0.7 | 0.7 | 0 | 0 |
| 6.6 | 6.3 | +2.3 | −0.9 | 615 | 0 |
| 10.0 | 9.7 | +5.7 | −4.3 | 615 | 0 |

The internal fixture subtracts two 0.2 mm interfaces, two 0.2 mm support skins
and a 3.2 mm tube outer diameter from the free silicon-face gap. It says only
whether this stack fits in one dimension. CMS's smaller-gap bridge architecture
must not be rejected by applying this different embedded-tube fixture to it.
At larger gaps, body collisions appear despite apparently complete pair coverage.

Reusing PR21's 3 mm centre-level spacing gives **1038** intersecting trial bodies.
Increasing the radial mounting/service allowance from 5 to 30 mm at nominal
spacing gives **335**. The nominal body stack is 7.3 mm, and the four-level
assembly spans **31.3 mm**, excluding common support, manifold and access space.

All continuous-strip square angle scans (0/20/40/52/80 mrad) have zero sampled
pair gaps and body conflicts on the coarse grid. The zero-angle case nonetheless
has **rank-one information**: pair coverage alone is not stereo performance.
The ideal 80 µm binary-pitch errors are:

| Relative angle [mrad] | Across-strip error [µm] | Along-strip error [mm] |
| ---: | ---: | ---: |
| 0 | 16.33 | unmeasured |
| 20 | 16.33 | 1.633 |
| 40 | 16.33 | 0.817 |
| 52 | 16.34 | 0.628 |
| 80 | 16.34 | 0.408 |

These estimates assume the true track direction and independent strip errors;
DES-008 derives the covariance and explains separation-dependent parallax and
false combinations. At nominal gap, the maximum within-pair radial displacement
in the vertex fixture is **4.70 mm**. It must be propagated between planes.

## Occupied envelope and support handoff

The nominal square's occupied radial range is **677.55–1123.68 mm**. Wedges span
675.91–1124.04 mm; narrow rectangles 678.03–1122.33 mm. These fit the 1140 mm
tracker host boundary in this simplified comparison, but leave only about 16 mm
at the outer edge for everything beyond the modeled body. They also intrude
below the proposed 700 mm short/long-strip transition. This is an explicit
DES-007/DES-008 interface question, not a demonstration of mutual clearance.

Only local occupied prisms are represented. The next mechanical review must
locate the rotated bonding edges and contact lands, decide between an embedded
cooling spine and external cold rails/bridges, route services to the shared
corridor, and preserve fastener/assembly access at each level. There is no tube
routing, shared carrier, stiffness/deflection, thermal, hydraulic or full material
model in this result. A barrel stave layout is also still required.

## Reproduction and verification

The retained JSON records the starting Git revision plus working-tree state,
SHA-256 of inputs and both source files, full configuration, tolerance, Python
3.14.6, NumPy 2.5.3 and Matplotlib 3.11.2. Source hashes identify the executable
study before its first commit. There is no random seed because no randomness
is used. Points are polar-bin midpoints with radial area weights; base grid
250×720, refined grid 500×1440. Boundary epsilon is 1e-9 (coordinates in mm;
polygon cross-products in mm²). Zero sampled gaps is not a continuous proof.

Commands actually executed:

```sh
python3 -B -m unittest discover -s tools/long_strip -p 'test_*.py' -v
MPLCONFIGDIR=/tmp/nodd-long-strip-mpl XDG_CACHE_HOME=/tmp/nodd-long-strip-cache \
  reference/cache/envelope-venv/bin/python -B tools/long_strip/study.py \
  --refined --sweeps --figure docs/design/figures/DES-008-rings.svg
```

Nine geometry/measurement tests passed. They include independent full enumeration
of all sensor polygons with row masks and finite-z projection, comparison to the
accelerated pairing algorithm, covariance inversion, singular-angle behavior,
rotation-centre checks, 3D overlap and cooling-failure controls. The overview was
rendered and visually inspected. Repository dashboard and session checks are
recorded in the [session record](../../logs/codex/SESSION-2026-09-25-long-strip-research.md).

No DD4hep build, Geant4 transport, ACTS conversion/navigation, curved tracks,
material scans, electronics qualification or human scientific approval was run
or inferred. Next actions remain sensor/readout review, assembly/interface design,
converged seam/edge studies and then a separately authorized detailed prototype.
