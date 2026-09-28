# DES-009 — Module coverage and support tradeoffs

Date: 2026-09-28. **PROTOTYPE; draft module models, no detector sign-off.**
Governing contract: [DES-009](../design/DES-009-module-populated-layouts.md).

Staggering improves reachable-station coverage substantially, particularly in
the short-strip barrels. It does not make these layouts hermetic. The best
mechanically cleared trials still miss approximately 4.5–4.9% of their eligible
stations on the independent random sample; pixel barrel gaps dominate. Pint is
the more economical of the two fully staggered study candidates, with about
2.3 m² less sensor surface and slightly better station coverage. Neither is
ready for selection as a detector design.

## What was built and measured

The study uses the named DES-006 layers and exact input snapshots from pixel
PR #8, short-strip PR #21 and long-strip PR #22. It places real finite active
rectangles: separate RD53 chip islands on a shared pixel sensor, 48 × 96 mm
short-strip sensors, and two physically separated, stereo-rotated 96 × 96 mm
long-strip sensors per module. Pixel finished outlines and service allowances
remain explicit trial assumptions. No module is cropped to an ideal layer.

Six placement patterns are compared for each candidate:

| Pattern | Placement hypothesis | Mechanical disposition |
| --- | --- | --- |
| `flat` | Trial bodies on unstaggered staves/rings; no added tilt | Endcap occupied boxes clash; retained adverse control |
| `staggered` | Barrel phi/z and endcap r/phi staggering, four normal levels | Many body clashes; active coverage alone is insufficient |
| `tilted` | Staggering plus 12 degree local tilt, except prescribed pint inclines | More clashes, including cross-layer clashes; not a selectable support model |
| `hybrid` | Flat cylindrical barrels; staggered discs and inclined rings | 216 pixel endcap body clashes |
| `hybrid_clearance` | Hybrid with eight pixel-endcap levels and compatible azimuthal repetition | Zero detected trial-body overlaps and host overruns |
| `staggered_clearance` | Cleared endcaps plus barrel normal spacing derived from body thickness and curvature | Zero detected trial-body overlaps and host overruns |

The last two are numerical clearance hypotheses, not engineered staves. All
original failing controls remain in the results. The 12 primary cases each
use 8,992 directions/vertices for each of three trajectories: straight and
charges ±1 at pT = 1 GeV in constant Bz = 3 T. Twelve smaller pixel-family and
outline controls use a common 1,536-direction subset, including a matching
mixed-family baseline. The independent check uses 4,096 uniformly sampled
eta/phi/x/y/z points for each of the four cleared cases. A second check uses
the same points with **total p = 1 GeV**. Across these runs there are **477,312
trajectory evaluations**; repeated straight controls are included in that count.

The domain is eta ∈ [-4,4], full phi, x,y ∈ [0,1] mm and z ∈ [-150,150] mm.
The primary grids explicitly include all four transverse corners at three
longitudinal positions; independent points sample the interior. Seeds and
sampling measures are retained. These are numerical integration/probe weights,
not a collider event distribution. Fractions change with grid phase and vertex
weighting; apparent charge asymmetries on the grid are not physics conclusions.

**Metrics:** a sensor hit is one physical sensor, even if several pixel islands
are crossed. A complete long-strip pair needs both faces of the same module.
A station counts once by station ID; pint's related barrel/inclined pieces
share their nominal station group. Missing coverage compares sets of ideal
eligible station IDs against actual reached stations, so an extra overlap
cannot hide a missing station elsewhere. Long-strip stations require a complete
pair. Regional station counts need not add to total when a station spans regions.
Gross silicon counts each physical sensor face once, including both long-strip
faces; active area excludes guard regions and chip seams. Readout-chip silicon
and passive supports are excluded from the quoted sensor surface.

## Cleared candidates: independent random sample

Triplets below are straight / positive charge / negative charge. Loss is the
fraction of all eligible station opportunities missed, **not** a fraction of
tracks with zero hits. All four candidates have at least one sensor hit for
every sampled trajectory; none reaches every eligible station on every track.

| Candidate | Modules | Gross / active sensor m² | Mean sensor hits | Missing eligible stations % | Tracks reaching all eligible stations % |
| --- | ---: | ---: | ---: | ---: | ---: |
| cobe, hybrid clearance | 21,971 | 197.673 / 192.914 | 13.434 / 13.554 / 13.477 | 10.950 / 10.957 / 11.268 | 37.18 / 37.23 / 36.35 |
| cobe, staggered clearance | 27,600 | 253.539 / 247.493 | 16.074 / 16.168 / 16.114 | 4.863 / 4.868 / 4.924 | 63.16 / 63.55 / 62.43 |
| pint, hybrid clearance | 22,223 | 198.871 / 194.075 | 14.337 / 14.465 / 14.390 | 10.254 / 10.285 / 10.531 | 38.92 / 39.14 / 38.75 |
| pint, staggered clearance | 27,116 | 251.238 / 245.262 | 16.842 / 16.938 / 16.882 | 4.480 / 4.492 / 4.567 | 64.92 / 65.38 / 64.04 |

The fully staggered trials have minimum **5 distinct stations** in this random
sample, with mean approximately 9.7–9.9. Sensor minima depend on charge and
sample; complete distributions and the grid's adverse cases are retained.
The flat controls even have trajectories with zero sensor hits on the primary
grid. This rules out a claim of sampled hermeticity for those controls.

For total p = 1 GeV, the bent-track station losses in the cleared staggered
trials are 4.869/4.889% (cobe, ± charge) and 4.504/4.586% (pint). The ranking
persists, but the directions follow different helices because pT = p/cosh(eta).
The fixed-pT and fixed-p studies are separate results, not interchangeable
definitions of the input momentum.

## Where support complexity buys coverage

The following barrel losses use the independent random sample, avoiding the
largest aligned-grid effects. Silicon penalties compare the same barrel before
and after its staggering; endcaps are unchanged between the cleared choices.

| Region | Missing stations %, hybrid → staggered, straight / + / − | Added barrel silicon | Trial occupied normal depth |
| --- | --- | ---: | --- |
| Pixel barrel, both candidates | 28.40/28.14/28.82 → 15.56/15.47/15.60 | 55.55%, 1.169 m² | 1 → approximately 11–18 mm |
| cobe short-strip barrel | 10.25/10.29/10.83 → 2.47/2.32/2.31 | 33.31%, 8.047 m² | 2 → approximately 11–16 mm |
| pint short-strip barrel | 13.44/13.91/14.10 → 0.88/0.80/0.86 | 39.37%, 4.549 m² | 2 → approximately 11–16 mm |
| Long-strip barrel, both candidates | 23.92/26.68/26.50 → 1.46/2.99/2.60 | 87.75%, 46.650 m² | 7.3 → approximately 38–40 mm |

**Prioritise short-strip barrel staggering.** It has a clear geometric benefit
for a comparatively modest increase in silicon and occupied depth, especially
for pint's shorter cylindrical section. Preserve a flat-stave control while
support, cooling and service concepts are developed.

**Treat long-strip barrel staggering as a conditional investment.** Recovering
same-module stereo pairs is valuable, but this implementation adds 2,479 barrel
modules and almost doubles barrel sensor area. Quantify the resulting momentum
and pattern-recognition benefit before accepting its support depth and channel
cost. A shallower shingle or different overlap scheme merits a separate proposal;
this study has not optimised it.

**Do not buy the present pixel-barrel depth without redesigning its gaps.** The
remaining approximately 15.5% station loss shows that these pitches, radial
offsets and inactive-edge hypotheses are inadequate together. The first barrel's
trial body reaches r = 26.023 mm, only 1.023 mm above the nominal host minimum.
That is not a verified beam-pipe or service clearance. Revise longitudinal overlap
and module phase with the full displaced luminous region before increasing depth
further. Test a qualified pixel outline and seam response as soon as available.

**Keep endcap staggering, and avoid the tested extra tilt.** For both cleared
choices, independent-sample endcap losses are 0.86–1.04% for pixels, ≤0.052%
for short strips and zero observed for long strips. Pixel/short/long endcap
normal envelopes are 9.4/11/31.3 mm. The original four-level pixel placement
clashes; the eight-level arrangement clears the trial boxes. The 12 degree
tilted trial brings collisions and no demonstrated buildable advantage. This
does not establish that every possible tilt is unnecessary.

**Avoid adding complexity to pint's inclined rows on this evidence.** Their
existing alternating placement uses a 5 mm normal envelope, and all 48 inclined
pieces have zero sampled ideal-reference misses. Their full 96 mm sensors
overhang the original finite meridional segments. Those overhangs are retained,
counted in silicon and checked against the trial bodies; material/services and
independent-measurement value still need assessment.

No currency, assembly-labour, material-budget or cooling estimate is available.
Module count, silicon, normal levels and occupied depth are the available
complexity proxies. A zero trial-box overlap count certifies only those boxes,
not full local-support engineering.

## Pixel families and shape uncertainty

Single, double and quad families are all exercised. The primary mixed policy
uses singles on the first two pixel barrels and quads elsewhere, requiring two
families. Uniform-family controls retain the same strip population and sample,
so their module counts and pixel coverage can be compared directly. These controls
use the original stagger pattern and therefore retain mechanical failures;
they do not establish a viable uniform-quad inner barrel.

The guard/interchip hypotheses are varied from 0.25/0.1 mm to 1.0/0.5 mm around
the nominal 0.5/0.2 mm. Those variations change coverage and physical area;
they are not measurement uncertainties or qualified manufacturing ranges.
Fewer assemblies favour quads where curvature and packaging permit, but the
study does not justify eliminating the small inner-barrel family. Detailed
control tables accompany the primary results.

## ACTS and execution evidence

Native ACTS validation is pending final execution. The initial single-large-leaf
Navigator experiment passed straight-track sensitive-ID checks but missed some
bent-track surfaces. That failed navigation control must remain visible.
Per-target ACTS propagation audits are being executed separately; they cannot
establish that a production navigation hierarchy is validated.

The node preflight reported changed Spack setup/lock fingerprints. Actual local
imports and required capabilities were checked using the authorized sister
checkout/install. The Geant4 data-directory warning was observed; no Geant4
transport, full material simulation, reconstruction efficiency or resolution
measurement is claimed. Code/input hashes identify the uncommitted prototype
used by the bulk runs; source HEAD alone is not the implementation revision.

## Retained results and reproduction

Result bundles and exact execution/check records are added after the native
audits. The [workflow instructions](../../tools/module_layout/README.md) describe
fresh output directories, external models/layers, momentum and sampling configs,
input/code hashes, ACTS requirements and explicit unsupported-shape failures.
Future sensor updates require editing the input snapshot/classification and
rerunning the same commands, not replacing older accepted evidence.
