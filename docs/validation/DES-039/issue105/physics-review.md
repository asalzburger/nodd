# Independent PhysVal assessment of issue105

Date: 2026-10-29. Explicit generic-agent PhysVal mandate; no native-profile
loading claim, no files changed by the reviewer, no human sign-off.

The initial assignment I105-PhysVal examined
`1ab7b951f6f3af99ada47c0881b8180e86a1da35`, reading primary source/code inputs
before the author's conclusions. The current scientific code was subsequently
assessed under the two amendment contracts below. Exact contracts and curated
handoffs are in the [session journal](../../../../logs/design/SESSION-2026-10-29-issue105-toroid-redesign.md).

## Initial findings retained

1. P2: a geometrically available but coil-clipped barrel suppressed a usable
   wheel of the same station. The original code undercounted the specified
   barrel/wheel station union. At eta0.984375,phi0.0625°, barrel-first gave
   `[false,true,true]`; forced wheels exposed the missing S1 crossing.
2. P2: a retained sampled100% at-least-two-station value below eta3 must not
   imply continuous coverage. The denser134400-cell bank found48 narrow
   one-station directions; conditional solid-angle availability was99.9594375%.
3. The exterior field screen is order-sensitive. With unchanged retained
   currents and fixed solenoid,97 probes (the retained maximum and96 nearest
   points from `exterior_probes(config,32)`) gave:

   | Pack order / corner segments | Maximum joint field [T] |
   | --- | ---: |
   | 6 /32 | 3.50000000 |
   | 8 /64 | 3.59096498 |
   | 10 /96 | 3.64464108 |

   All occur at `[4.905880352497365,0,-5.629113377474582] m`. These sampled
   points remain below4T but establish no global/exterior/interior bound.
   The3.5T screen must remain a discretization-specific diagnostic.
4. P3: initial dirty-source prose did not match a retained clean replay flag.
   The report now refers to the actual recorded commit/flag and code hashes.

The initial review verified all eight retained source hashes plus the input
hash, ran six focused tests and an independent134400-direction nested/control
scan. It found a robust same-bank gain before the station fix, with nonmonotonic
angular sampling. The author reproduced the subsequent denser scan in
[refinement.json](refinement.json), rather than transferring old numbers.

## Station-union correction

I105-PhysVal-amendment assessed
`3540fc6e181f078b1a89727b69d8fc95c2046345`.
The reviewer ran seven tests and independently combined old-code barrel-only
and wheel-only availability on134400 directions. Comparison with the corrected
code gave **zero station-count mismatches** and **zero selected-distance-order
failures**. The regression now gives D,B,B and S1 atz6.7456m. A retained barrel
is preferred when both surfaces are usable; otherwise the usable wheel supplies
the point for path and signed-bending calculations. Finding1 is resolved.

The new map domain±15m and explicit no-map status were metadata-only: removing
`map` objects left old/new physical input configurations identical.

## Deterministic chord checks

I105-PhysVal-amendment-2 assessed
`578521769b323674b49c1aaba836b3b0d632fb99`.
Eight focused tests passed. The reviewer independently checked seed105,
261 directions as one batch and chunks1,7,127: availability, coordinates and
surface types were identical. On8400 directions, independent barrel-only and
wheel-only masks unioned stationwise had zero mismatches against the full code.

The fixed chord node bounds follow eligibility directly:
`h cosh(eta) <= h hypot(1,L/(R+h))` for barrels and
`h coth(eta) <= h hypot(1,Ro/(Z+h))` for wheels. Thus the sample interval stays
at most50mm regardless of ray batching;25mm mask inflation remains conservative.
No new blocker was found in this code amendment.

## Executed methods and limits

- Exact `git show REV:path` reads and SHA-256 comparisons for assigned inputs,
  field/geometry/energy primitives, policy, parent design and ADR sources.
- `python3 -B -m unittest tools.toroid_redesign.test_study -v` at each target:
  six, seven and eight tests respectively, all passing.
- Independent `coverage(config,.00625,.125,.05)` and the same-bank short5.7m
  barrel control, plus disabled-surface union controls and explicit regression.
- Field refinement used the source-matching prebuilt C++ backend via ctypes,
  then `toroid_sources(config,order=6/8/10,corners=32/64/96)` plus the fixed
  solenoid at the stated97 points. No new runtime or shared dependency installed.
- The reviewer inspected energy self/mutual accounting and the retained
  +0.17047% refinement /8.70e-9 relative reciprocity residual; it did not
  independently rerun the full energy integral.

The0.80m complete warm axial separation and lower ordinary vacuum fields
support the requested design direction. Cold assembly surplus is only about
3.03/1.91mm per side around the0.12×0.18m pack, requiring mechanical/thermal
assessment. Global vacuum30MJ/m³ closure supplies no installed or per-family
engineering certification. Conductor interior peak, NbTi operating margin,
nonlinear HCAL, forces/quench, S2 vessel access, finite panels, services/supports,
material transport and reconstruction remain unresolved.

This assessment supports a bounded DRAFT investigation with the corrected
counting semantics and explicit limits. It supplies no engineering acceptance.
