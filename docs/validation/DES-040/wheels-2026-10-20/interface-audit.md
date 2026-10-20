# W-A1 — front/rear endcap wheel interface audit

**Input:** `5674a7688319d6dd5179c04cd381cb59f48d36bb`, explicit SysArch fallback
mandate. Read-only prototype assessment, no design approval. No repository,
magnet, field, HCAL, support or shared-software changes were made.

**Conclusion:** a 500 mm first wheel with radial reach 0.7–5.45 m cannot sit
between the unchanged HCAL and the front of the unchanged endcap toroid.
The axial gap fails even with zero margins. Twelve sector gaps can reserve the
BT legs without modifying BT, but do not repair this axial incompatibility.
The outer wheel can clear the unchanged coils and frame after abs(z)=12.75 m
(an infimum), requiring a larger field-map/world domain.

## Pinned bounds and owners

| Interface | Exact retained bound | Endpoint owners / source |
|---|---|---|
| HCAL → first wheel | HCAL back abs(z)=6.4412 m | Calorimeter / MuonTech; DES039 lines37–40; MUON-001/results.md lines47–52 |
| ECT → first wheel | warm front abs(z)=6.55 m | Magnet / MuonTech; support-input.json lines153–161; ECT centre 9.25, half-z 2.45, warm normal half-width 0.25 |
| BT → first wheel | inner leg local r=4.35–4.85 m, tangent half-width0.30 m | Magnet / MuonTech; DES039 lines139–154 and geometry.json magnetic_configuration |
| Coils → outer wheel | ECT rear 11.95 m; BT rear 12.05 m | Magnet / MuonTech; DES039 lines139–154; support-input lines162–172 |
| Rear frame → outer wheel | inner hoops/spokes z=12.15–12.45 m | SysArch frame / MuonTech; support-input lines176–196; actual 484 retained member prisms |
| Field/world → new wheels | map abs(z)≤12.5 m; native world half-z 11.5 m | SoftEng / MuonTech; geometry.json magnetic_configuration.map; pinned propagation implementation |

All intervals refer to the **complete envelope**, not its centre. Signs reflect
to the other end. Chamber depth 0.500 m and coil/support clearance 0.050 m are
retained DES040 choices (`design.json:39,46–47`). A separate 0.050 m HCAL margin
below is a **provisional interface assumption**, not an existing design.json
clearance or a qualified service allowance.

## First wheel: unavoidable axial deficit

For wheel centre Z, depth d, HCAL margin h and coil clearance c:

`Z >= 6.4412+h+d/2`, while `Z <= 6.55-c-d/2`.

| Margins h / c | Available depth | Missing depth for 500 mm |
|---|---:|---:|
| 0 / 0 |108.8 mm|391.2 mm|
| 0 / 50 mm retained coil clearance|58.8 mm|441.2 mm|
| 50 mm provisional HCAL /50 mm coil|8.8 mm|491.2 mm|

With both 50 mm margins the contradictory centre bounds are **Z≥6.7412 m and
Z≤6.2500 m**. Reducing margins cannot produce a 500 mm space. Moving/shortening
barrel chambers does not change these endpoint bounds. The retained radius
includes HCAL/ECT overlap radii, e.g. r=2 m; an HCAL-clear trial wheel centred
6.7412 m contains an exact ECT warm witness at(r=2 m,phi=15°,z=6.8 m).

## BT-compatible 12-sector trapezoids: viable with explicit gaps

An uninterrupted annulus to R=5.45 m also crosses BT inner legs. At these z values
the legs are straight. Their conservative 50 mm-expanded local section is
`u in[4.30,4.90] m`, `|v|<=0.35 m`. Therefore reserve half-angle
`atan(0.35/4.30)=4.6533516°` around each BT plane phi=30°k.

A bounded example is 12 sector centres phi=15°+30°k with ±5° BT corridors:
each trapezoid compartment spans 20°, with no Boolean coil-shaped cutout.
This preserves full radial reach 0.7–5.45 m **inside each retained sector**,
without a BT change. It reserves one-third of azimuth before 20 mm module gaps;
it must not be called uninterrupted4π coverage.

Using the retained ≤1.5 m band size and20 mm radial gaps gives 4 bands and 48
whole trapezoids per wheel. The calculation checks physical radial spans
1.090–1.144 m, areas 0.490–1.831 m², and maximum outer width 1.873 m, satisfying
the stated 0.50 m span/0.25 m² area minima. All points remain outside the expanded
BT section because the entire trapezoid lies outside its angular cone. The BT
outer leg is radially beyond this first wheel. This solves **only BT clearance**;
the HCAL–ECT axial deficit remains. Continuous rear carrier hoops cannot be
avoided merely by comparable azimuthal gaps in the outer wheel.

## Bounded alternatives requiring an explicit choice

1. **Keep full first-wheel radial reach and use BT sector gaps; revise ECT
   axially.** Move its front warm boundary outward by more than 441.2 mm with
   retained coil clearance alone, or more than 491.2 mm with the provisional
   HCAL margin. These are geometric infima, not installed tolerance budgets.
   As an arithmetic example, moving only the front return centre from 6.80 to
   7.30 m while retaining its rear centre 11.70 m gives ECT centre 9.50 m,
   half-z 2.20 m and front warm skin 7.05 m. A wheel centre 6.7456 m then leaves
   54.4 mm at both HCAL and ECT. This is a changed magnetic source: recompute
   field/energy/cold allocation and review response/forces; do not retain or
   silently renormalize the old map. Front lugs must reach the new case skin
   (their current axial extent 6.45–6.55 becomes6.45–7.05 m in this example).
   At their r=5.8/6.8 m they remain radially beyond the first wheel; stress and
   load-path qualification are unresolved.
2. **Keep magnets, change radial reach.** Restrict the first wheel to an annulus
   R=4.92–5.50 m centred abs(z)=6.24 m, full envelope 5.99–6.49 m. Bounds prove 60 mm
   to ECT, at least 100 mm to all 484 support envelopes, and separation from the
   conservatively expanded BT inner sleeve whose radial maximum is 4.9124841 m.
   A 24-sector trapezoid has 0.532947 m physical radial span. This abandons the
   requested 0.7 m aperture and its forward station coverage; it is not an
   equivalent full-radial wheel. The earlier narrower outer radius 5.45 m would
   give only 0.483374 m actual span and is not the preferred bounded example.
3. **Change HCAL instead.** Keeping ECT fixed requires HCAL back ≤6.00 m with
   coil clearance alone, or≤5.95 m with the provisional HCAL margin. At fixed
   front 4.8832 m the latter depth is 1.0668 m rather than 1.558 m. Such a large
   calorimeter change requires its owner's physics/design decision. Translating
   that HCAL upstream by 491.2 mm would move its front to 4.392 m, into the
   barrel's 4.4832 m half-length in overlapping radial regions. It is not a
   harmless independent translation.

No BT change is needed for alternative 1 if the explicit sector gaps are accepted.
Without such corridors, BT must also change or radial reach must stop below
4.30 m. A pure axial ECT repair alone cannot clear an uninterrupted annulus.

## Outer wheel, barrel lengths and numerical domains

After coils alone, the centre infimum is 12.35 m, envelope 12.10–12.60 m.
It intersects the retained rear hoops/spokes and lugs. An actual hollow spoke
wall witness is(6.2422832,1.8175534,12.3)m in ECTP-rear/SPOKE00; it lies within
the proposed outer wheel and has local transverse coordinate0.14 m in a wall
whose outer/inner half-widths are0.15/0.13 m. This is not merely a centreline or
bounding-box clash.

For the unchanged frame, relevant support envelopes end at 12.45 m. Thus the
wheel front must exceed 12.50 m and its centre exceed 12.75 m for strict 50 mm
clearance; a rounded example 12.80 m has envelope 12.55–13.05 m. The outer carrier
ring extending to 12.50 m has minimum radius 9.15 m, outside R=8.45 m+clearance,
so does not tighten the inner-hoop/spoke bound. Shifting only the carrier rearward
would not automatically help: its axial ties can still cross a full radial wheel.

Where a wheel radially overlaps its corresponding barrel, retain the old 50 mm
full-envelope seam by `barrel_half_z <= wheel_centre_z-0.300 m`. For the example
first wheel 6.7456 m this gives B1 half-z ≤6.4456 m; the large-hole 6.24 m option
gives≤5.94 m. The outer after-frame infimum would permit B3 half-z≤12.45 m,
but an extension from 10.7 m crosses fixed BT return geometry and requires the
existing full-volume coil/support certificates and whole-panel exclusions.
No simple midplane extension proves clearance. Station spans/lever arms and
coverage must be recalculated rather than retaining the old 3 m claim.

The outer after-frame envelope reaches at least 13.00 m, exceeding the retained
map's 12.5 m and world's 11.5 m. Extend the map domain from the same sources if
only chambers move; if ECT changes, recompute the actual joint solution and
its masks. Choose a world beyond every new chamber corner and leave explicit
integration/interpolation margin inside the map. The old entrance half-z 6.50 m
can start **inside** a first wheel whose front is 6.4912 m; reselect/validate the
virtual entrance between HCAL and the first wheel, retaining strict masks.

## Actual checks and limits

Ran `python3 -B /private/tmp/pr90-wheels-A1-check.py` successfully. It reads/hashes
all 7 pinned inputs via git show, computes all 484 member prism vertex bounds and
exact projected convex-hull radial lower bounds, verifies the hollow spoke-wall
witness, exact rounded-sweep witnesses, contradictory axial inequalities,
large-hole alternative separation, and 12-sector trapezoid sizes. Results:
`interface-check.json`. No detector generator, map solver,
ACTS/DD4hep/Geant4 runtime, coverage scan or engineering load calculation ran.
Alternatives remain interface proposals for the human/endpoint owners; no
geometry change, response requirement or approval is inferred from this audit.
