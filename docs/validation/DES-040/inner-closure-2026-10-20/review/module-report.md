# IC-M1 — Why the inner wheel does not close

Input revision: `15015d378b5b77b3bb11698809d1680d12b8a91c`.
Role: MuonTech, explicit fallback mandate; read-only study. No repository files,
magnet/frame/HCAL dimensions, chamber geometry or ACTS evidence changed. All
alternatives below are **unadopted geometric diagnostics**, not engineering
feasibility or detector acceptance.

The open wedges have two causes. Twelve real BT inner legs cross the entire
500 mm-deep inner-wheel slab, so uninterrupted closure is impossible while those
legs and their clearance stay fixed. Their warm footprints are 4.35–4.85 m along
each coil plane and ±0.30 m across it. The adopted conservative 50 mm clearance
boxes span 4.30–4.90 m and ±0.35 m. Their twelve footprints sum to 5.04 m²;
the warm legs alone sum to 3.60 m². These box areas are not a claimed optimized
minimum dead area for Euclidean corner clearance.

The additional long triangular gaps are avoidable in principle. The current
contract requires one whole trapezoid per 30° sector. Its straight side connects
a 10 mm half-seam near the bore to a 360 mm half-corridor at the BT guard box,
including the existing 10 mm tangent certification margin. That straight line
spreads the local coil exclusion towards the bore and beyond the coil. The
reviewed XY section matches the actual finite prism footprint to rounding; this
is not a plotting gap.

A concrete optional **two-band** recipe retains twelve sectors per band, 500 mm
depth, |z|=6.7456 m, bore 0.70 m, outer vertex radius 5.45 m, 20 mm radial seams,
fixed coils/frame and the same 50 mm clearances. In each sector-centred coordinate
u, use half-width `w(u)=u*tan(15°)-delta/cos(15°)`:

| Band | u near / far [m] | delta [m] | Near / far base width [m] |
| --- | --- | --- | --- |
| Lower | 0.700000 / 4.050306 | 0.010 | 0.354423 / 2.149847 |
| Coil corridor | 4.070306 / 5.345973 | 0.360 | 1.435872 / 2.119500 |

These are base apothems, not cylindrical radii. The transition derives from the
**actual rotated box**, not an R≈u approximation: projecting the certification
box [4.30,4.90]×[-0.36,+0.36] m onto the 15° sector axis gives
[4.060306,4.826211] m. The lower band ends 10 mm before its minimum; the upper
band starts another 20 mm later and uses the wide corridor. A naive lower band
ending at u=4.29 m was tested and correctly rejected for BT overlap.

This doubles inner-wheel outlines from 12 to 24 per end and adds one geometric
shape family. It needs a new explicit radial-tiling/cassette contract: the present
whole-wheel contract forbids radial tiling, and its exemption from the old 1.50 m
ordinary-module cap does not automatically qualify the 3.350 m lower-band span.
Services, tube dimensions, alignment/sag, background response and construction
are unassessed.

| Geometric diagnostic | Current whole trapezoids | Two bands | Three bands, localized slot |
| --- | ---: | ---: | ---: |
| Outlines per end | 12 | 24 | 36 |
| Face area per end [m²] | 63.1668 | 77.5533 | 78.6884 |
| Midplane area missing vs circular annulus | 31.1712% | 15.4952% | 14.2582% |
| IP rays missing a full-depth same-chamber crossing | 30.1538% | 19.1703% | 27.9720% |
| Same full-depth diagnostic, 30 mm border | 34.8916% | 25.3791% | 34.8082% |

The solid-angle denominator is the ideal annulus requiring both depth faces
inside radii 0.70–5.45 m. Fractions include seam and polygon-boundary losses;
they are straight-ray geometry, not ACTS propagation, measured efficiency or
reconstruction performance. In particular, radial splitting can put entry and
exit in different chambers. Thus a better blue midplane area need not improve
the defined same-chamber two-face observable.

For the slot-localized three-band diagnostic, the middle band ends at
u=4.836211 m and the outer band begins at 4.856211 m. The latter reaches
u=5.266875 m with a 20 mm angular seam, so its span is only **0.410664 m**,
violating the old **0.50 m useful-module minimum**. It is not an admissible module
proposal under that rule. A fourth raw diagnostic divides the lower band in two;
it is retained in JSON rather than used as a headline alternative. None of these
recipes is optimized or adopted. A stepped/notched cassette could localize the
exclusion while retaining a connected envelope, but would require a different
shape/native-volume representation and separate validation.

Actual scratch checks: each optional chamber passed the existing whole-volume
analytic ECT/BT-return/outer-leg planes and exact SAT against all twelve inflated
rotated BT boxes. SAT found no optional-panel pair intersections, no conflicts
with any of the 484 unchanged support envelopes at 50 mm clearance, and no
intersection with the 1,320 other chambers. The occupied-BT and naive-radius
negative fixtures were rejected. A common bank of 1,048,576 iid uniform-cos(theta)
and phi directions at seed409090 checked the analytic full-depth solid angles;
all four cases agreed within 1.34 sampling standard errors. This checks geometric
calculation, not engineering suitability. No ACTS scan or magnetic calculation
was run or needed for this read-only question.

Source locators, all at the full input revision above:

- `tools/muon_layout/wheels.py`, lines49–85: affine side derivation; lines112–159:
  full-volume analytic separation and rotated-box SAT.
- `tools/muon_layout/wheels-config.json`, `inner_wheel`, `depth_m`, clearance keys:
  current choice, extra margin and no-radial-tiling rule.
- `docs/design/DES-040-muon-chambers-frame.md`, selected revision contract and
  original bounded choices: whole-sector cassette scope and old module bounds.
- `candidate/geometry.json` under the dated DES040 evidence directory: actual
  chamber transforms, magnetic parameters and 484 finite support bodies.
- `xy-sections/sections.json` in that directory: reviewed exact z section.

Portable reproduction uses `--repo`, `--revision` and `--output`; it obtains every
scientific input and geometry kernel with `git show` from the exact commit into
a temporary import tree. It writes only the requested output. The JSON retains
source hashes, dimensions, counts, proof outcomes, raw diagnostics and sampling.
