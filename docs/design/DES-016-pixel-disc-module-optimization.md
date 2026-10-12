# DES-016 — RD53 pixel disc module optimization

- Status: DRAFT — isolated PROTOTYPE study; no design sign-off or baseline replacement.
- Created: 2026-10-05.
- Review: [issue #38 overlap comment](https://github.com/asalzburger/nodd/issues/38#issuecomment-5981583892).
- Inputs: DES-001 RD53i matrix fixtures, DES-013 retained finite-module layout,
  DES-014 supports/services and DES-015 preliminary combined pixel prototype.

## Contract before the search

| ID | Classification | Requirement or choice |
| --- | --- | --- |
| DO-C01 | NODD DESIGN CHOICE, revised explicit user direction 2026-10-05 | Prefer at most 15% silicon overlap; allow up to 20% where needed to retain hermetic coverage with local radial/tangential axes. This supersedes the earlier 10% Cartesian study. Report both repeated silicon area divided by the projected union and divided by the summed installed silicon area. Use the stricter former quantity for selection, including a separate annulus-only limit. Report installed silicon outside the unchanged annulus. |
| DO-C02 | NODD DESIGN CHOICE | Preserve the nominal active annulus r32.3..181.4550267061104 mm, nine discs per end and existing disc datums. The position amendment is a separate PR. Do not reduce the acceptance region or silently crop sensor outlines to achieve the target. |
| DO-C03 | NODD DESIGN CHOICE | Explore single, double and quad RD53i assemblies to reduce the severe inner-radius overlap of the original quad-only layout. Retain each 20.0 by 19.2 mm active matrix, 50 micrometre pitch, 0.15 mm sensor, inherited 0.2 mm inactive interchip gap and 1 mm occupied module thickness. Any narrower guard is explicitly unqualified; retain the inherited 0.5 mm guard as a control. No new ASIC functionality, seamless chip joints or trapezoidal active pixels is assumed. |
| DO-C04 | NODD DESIGN CHOICE, revised explicit user direction 2026-10-05 | Retain the 18-single innermost polar ring. Arrange further singles, doubles and quads in concentric rings, with one matrix axis tangential and the other radial at each physical module centre. Compare family choices, integer phi populations and radial ring spacing. Screen active rectangles, inactive interchip seams, physical sensor outlines and occupied module bodies separately. Check coverage independently of overlap and retain rejected controls. |
| DO-C05 | NODD DESIGN CHOICE | Finite z offsets and nonzero luminous vertices require their own straight/curved-track checks. Native ACTS target propagation validates finite sensitive-plane intersections and identifiers against the analytic oracle; it is not a claim of global ACTS navigation, material response or reconstruction. |
| DO-C06 | NODD DESIGN CHOICE | Recompute power chains, links, heat, half-ring circuit count, coolant feed/return and collector/trunk footprints with DES014/010 scenario inputs. Do not scale a quad count as though it were a single-chip module. Keep reference and adverse scenarios, packing failures and hydraulic/thermal qualification limits visible. |
| DO-C07 | NODD DESIGN CHOICE | Retain the full preliminary barrel and all original evidence as controls. Study outputs and proposed sensitive planes are isolated under tools/pixel_disc_optimization and docs/validation/DES-016. Baseline integration and a revised detailed support/thermal design need human review. |

All candidate dimensions, placement policies and numerical controls are recorded
in the executable study inputs. Public matrix/material facts remain those in
DES-001/014 and reference/manifest.yaml. This study adds choices and derived
geometry/service estimates, without new externally established design facts.


## Superseded Cartesian proposal and engineering boundary

The reproducible study selects328 single modules per disc:18 inner polar modules
and310 Cartesian modules. It retains the original active matrices and nominal
annulus, with a0.1mm guard and20.4×21.4mm occupied body including ASIC periphery.
These slimmer guard/service allowances are **NODD DESIGN CHOICES, unqualified**;
the0.5mm inherited guard is retained as a failing control. The first-disc lattice
pitches19.55×18.75mm use0.45mm overlap reductions; farther discs scale that
reduction by615.2/abs(z), preserving the328 indices. Five1.2mm spaced levels,
body conflict colouring and on-axis vertex compensation are **NODD DESIGN
CHOICES**. All18 body/overlap screens and continuous straight coverage
certificates pass. Native ACTS is a finite supporting-plane audit, not global
navigation validation. [Results](../validation/DES-016/results.md) pin the actual
code, inputs and runtime.

The body radius grows to about212mm. The inherited r188.5mm support, local
service bands, r192mm trunk and thermal feet require a redesign. New module
count increases chains and command/data bundles despite reducing chips/heat.
All inherited shared-trunk packing scenarios fail; this is explicit evidence
for the next architecture review, not permission to integrate a broken service
model. No design sign-off or production replacement is recorded. Full DD4hep
implementation follows review of guard/ASIC assembly feasibility, new local
support/cooling/routing, readout aggregation, collector and last-disc adapter.

Provenance: matrix/pitch/sensor thickness and conditional heat proxy are inherited
from DES001/010; body/guard, tiling, levels, compensation, grouping and envelope
reserves are NODD DESIGN CHOICES. Areas, containment, counts, heat, tube/cable
cross-sections and packing failures are INFERENCES from those executable inputs.
Area tolerances, polygon resolution, colouring padding and subdivision limits
are numerical screening controls, not fabrication tolerances. No externally
qualified hardware performance is introduced by this proposal.

## Radial revision contract — 2026-10-05

The user rejected global x/y alignment because pixel measurement axes should
have a stable relation to transverse and longitudinal track coordinates,
especially for rectangular pixels. The revised isolated study will compare
single, double and quad module rings and keep the innermost ring. Tangential
and radial axes are fixed at each module centre; finite module width still
introduces a bounded local angular departure elsewhere on a module. An
anisotropic pixel covariance control will expose this departure without
claiming a fitted-track resolution or a sensor-response validation. Square
50 micrometre pixels remain the current RD53i fixture; a rectangular-pixel
control is a test hypothesis, not a new hardware specification.

Shared double/quad sensors do not imply seamless active response. The search
must retain individual active matrices and explicit gaps, count shared silicon
outlines once, colour whole occupied assemblies, and group services by physical
module family with both module and chip chain limits. The preferred overlap
limit is 15%, with a hard 20% ceiling as authorized by the user. Coverage,
body clearance and the unchanged annulus cannot be relaxed to meet a budget.

The original results under `docs/validation/DES-016/` remain a dated control.
New geometry, native audits and figures will be retained under its
`radial-revision/` subdirectory. This is a revision of PR41; the positioning
PR40 and production compact are outside its implementation scope.

## Superseded nine-ring radial proposal

The [new retained results](../validation/DES-016/radial-revision/results.md) select
359 singles per disc in nine concentric rings, with the innermost18-module ring
retained. Physical axes are tangential/radial at module centres; an anisotropic
binary-pitch covariance control and finite corner departures are retained.
Thirty-six bounded candidates include tangential/radial doubles, quads and mixed
policies with individual inactive chip seams. The tested larger/mixed variants
leave gaps and/or exceed20%; this does not exclude every possible mixed design.

The first-disc whole-silicon overlap is15.593%, annulus-only17.478%; the worst
across all distances is19.483%. Continuous straight on-axis luminous coverage,
body separation and matched native ACTS checks pass. No candidate certified
coverage within the preferred15% tier for both metrics. The selected arrangement
uses the authorized20% ceiling. Current square-pixel matrix fixtures are unchanged;
the25×100micrometre covariance control is a test hypothesis, not new hardware.
Maximum corner departure17.435degrees remains, mainly at the preserved inner ring.
This is geometric measurement evidence, not fitted-track resolution.

The0.1mm guard and slim single-body envelope remain unqualified; the0.5mm guard
control fails20%. Maximum body radius202.035mm exceeds the original support.
Homogeneous half-ring service groups need30 power chains and18 cooling circuits;
all inherited shared-trunk scenarios still fail. Guard/sensor, support, cooling,
readout aggregation and collector/trunk review remain prerequisites to adoption.
Production compact and the independent whole-mm positioning PR remain unchanged.

## Service-radius amendment — 2026-10-05

**DO-C08 — NODD DESIGN CHOICE, explicit human direction:** keep the revised
disc inside the inherited cable/service bounds, removing the outermost ring if
needed. The nine-ring radial proposal above is retained as a superseded control.
Use DES014's r188.5 mm local plate and DES015's r192..231.7 mm effective trunk;
preserve the r190 mm collector boundary and the r222 mm flange necks. Do not
widen, move inward or claim more packing capacity for these service reservations.
Remove whole rings whose occupied bodies exceed the local plate at any of the
nine distances. Preserve all surviving module identifiers, axes, centres and
axial levels from the nine-ring proposal. Keep the original nominal annulus as
the coverage target and explicitly measure any acceptance loss; removed silicon
must not be hidden by cropping the target or weakening its certificate.

**DO-C09 — NODD DESIGN CHOICE, conditional interface reservation:** check the
OD2.8 mm local tube envelopes and an 18 by 8 mm pickup-land bounding rectangle
against the same local radial limit. The old quad-specific +16 mm land offset is
a rejected inheritance control for slim singles. A single's provisional land may
be reserved wholly within its occupied silhouette: its outboard edge matches
the body edge, giving offset 0.9 + 21.4/2 - 8/2 = 7.6 mm. This is a geometric
reservation, not a qualified thermal contact, machined foot or routed pipe.
Count all surviving modules/chips, physical chains and both hydraulic legs;
report normal-trunk and flange-neck packing failures. Thermal/support interface
engineering and detailed flex/bend routing remain open within the fixed bounds.

New evidence will be retained in `docs/validation/DES-016/service-radius/`.
The Cartesian and nine-ring radial evidence, original annulus, disc positions,
production compact and independent PR40 remain unchanged.

## Current bounded proposal — eight radial rings

The [service-radius results](../validation/DES-016/service-radius/results.md)
remove the 63-module outer ring and retain 296 singles in eight rings. All
surviving transforms and the 18-module inner ring are unchanged. Maximum reserved
radius is 183.388628 mm: 5.111372 mm inside the plate and 6.611372 mm inside the
r190 service boundary. Local tube and conditional pickup-land bounds fit too;
the old quad-specific land offset is retained as an incompatible control.

The unchanged original annulus has 2.5245–3.3284% uncovered projected area in
the sampled vertices/distances. Direct counterexamples invalidate full-annulus
hermeticity. Worst silicon overlap is 18.476%. Native ACTS agreement retains all
54 added edge-track misses, rather than counting a successful transport audit as
coverage. The fixed trunk and flange-neck reference utilizations remain 1.318×
and 1.785×, with adverse failures retained. Further engineering and coverage
restoration must respect the fixed radial interfaces. No sign-off is recorded.
