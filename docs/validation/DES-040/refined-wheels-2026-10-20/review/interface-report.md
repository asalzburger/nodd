# CR-A1 — fixed interfaces, aperture and spacing

Read-only SysArch contribution at input revision
`5f42c4b9649619771e8d5ec70247c99b10d8e80f`. This is an explicitly supplied
role mandate, not a claim that a native custom profile loaded. DRAFT isolated
PROTOTYPE assessment; no human approval or engineering acceptance.

## Source and provenance

All eight assigned inputs were obtained with `git show REV:path`; their SHA-256
and byte counts are in `pr90-CR-A1-check.json`. Governing model facts below come
from that revision's `docs/design/DES-040-muon-chambers-frame.md` (selected-wheel
contract), `tools/muon_layout/wheels-config.json`, and
`docs/validation/DES-040/wheels-2026-10-20/candidate/geometry.json` keys
`magnetic_configuration`, `configuration.chambers`, `panels` and
`supports.members`. These are facts about a prototype, not independently
verified manufacturing or experimental facts. Calculations below are INFERENCES;
proposed larger bores and guard dimensions are unapproved NODD DESIGN CHOICES.

## Axial interfaces and moving the middle wheel

All coordinates are detector-global metres, with both signs reflected in z.

| Object | Centre / centreline | Finite warm/chamber faces |
|---|---:|---:|
| Inner wheel | 6.7456 | 6.4956–6.9956 |
| Middle wheel | 9.5000 | 9.2500–9.7500 |
| Outer wheel | 12.8000 | 12.5500–13.0500 |
| BT | centreline ends ±11.8000 | warm axial bound ±12.0500 |
| ECT positive | centre 9.5, half-length 2.2; ends 7.3/11.7 | warm bound 7.05–11.95 |
| Rear inner carrier | centre 12.3, depth .3 | 12.15–12.45 |

The inner wheel is before the ECT but within the BT inner-leg length. The middle
wheel lies inside both toroid axial ranges. The outer wheel is behind both.
Warm bounds are actual swept-coil bounds, not an invented filled annular vessel.

The HCAL back is 6.4412: inner-wheel front separation is .0544 m. Inner-wheel
back to ECT warm front is also .0544 m. With .05 m clearance on each side and
.5 m depth, permitted inner-wheel centre range is only 6.7412–6.7500 m; moving
the inner wheel within this slot cannot escape the BT legs.

Putting the middle wheel wholly after ECT warm plus .05 m requires its centre
at least 12.25; putting it after BT too requires at least 12.35. Independently
constructed prisms at those z positions give 72 support conflicts each against
the .05 m expanded frame, including `ECTP-rear/INNER/E00` and the rear spokes.
At 12.35 the middle also overlaps 36 current outer-wheel prisms.

Behind the rear carrier, the limiting centre is 12.75 (touching the .05 m
expanded boundary; strict separation needs slightly more). This overlaps the
current outer wheel. Keeping a .020 m axial interwheel gap then requires outer
centre at least 13.27 and outer far face at least 13.52, versus 13.05 now.
Even without the frame, a middle wheel after BT needs centre >=12.35 while one
before the fixed outer wheel with .020 m gap needs centre <=12.28. The fixed
envelope cannot accommodate both.

Current inner-to-middle / middle-to-outer centre gaps are 2.7544 / 3.3000 m;
total span is 6.0544 m. As a geometry-only constant-curvature diagnostic, the
middle-hit chord residual has factor `(z2-z1)(z3-z2)/2`. Its product is 9.08952
m² now, 7.89336 at middle z=10.90 (86.8402%), and 2.52198 at 12.35 (27.7460%).
The symmetric point 9.7728 raises this product by only .8187%. This is not a
momentum-resolution prediction. A shift changes where measurements sample the
nonuniform field and their bending kernel. New propagation and fitting, with
the retained field, material and response assumptions, is needed; added chamber
area does not imply momentum improvement.

## Three-family middle construction and its physical obstruction

BT phases are 0+30k degrees; ECT phases are 15+30k. At the entire current middle
slab the coil sweeps are straight radial-leg boxes. Warm .50 m normal by .60 m
tangent plus .05 m clearance gives normal half-width .30 and tangent half-width
.35. Relevant boxes are BT u=4.30–4.90 and ECT-inner u=.40–1.00; ECT outer
u=7.30–7.90 is beyond the middle bound 6.95. BT returns start beyond the slab.

A concrete conservative witness uses 15-degree sectors, .020 m normal seams,
depth .5, unchanged z and outer-corner radius 6.95:

| Family | Sector centre | Inner / outer base apothem | Inner / outer full base | Span |
|---|---|---|---|---|
| Full ECT-centred sector | 15+30k deg | 1.01 / 6.891839916 | .245765466 / 1.794483297 | 5.881839916 |
| Below BT slot | 0+30k deg | 1.07 / 4.29 | .261563766 / 1.109405850 | 3.22 |
| Above BT slot | 0+30k deg | 4.91 / 6.891839916 | 1.272654947 / 1.794483297 | 1.981839916 |

There are 36 prisms per end, exactly three dimension families. The 1.07 lower
base is needed because an adjacent ECT clearance corner rotated 15 degrees
projects to `1*cos15 + .35*sin15 = 1.056512492` along the BT-sector axis;
starting all shapes at 1.01 is unsafe. This witness passes fresh independent
whole-prism checks against 96 leg boxes, all 484 expanded frame members, 1128
other chamber prisms and every internal prism pair: zero conflicts. The .01 m
guard choices are explicit; exact minimum guards were not optimized.

This is an independently checked illustration, not the final generator's exact
recipe. The coordinator reports the implementation's BT-inner base as
1.066512492 rather than this check's rounded 1.07; its separate exact-revision
review owns that geometry. These bores do not achieve the nominal eta3 boundary. At middle
nearface z=9.25, eta3 radius is .923349519. For any phi, a nearest ECT leg is
within 15 degrees: its local u is .891887–.923350, within physical warm .45–.95,
and abs(v)<=.23899<.30. Thus the whole eta3 circle at this face is in the actual
ECT warm union. A particular midplane witness is
`(.915992206,.245439372,9.5)` at eta=3, phi=15; the independent exact rounded-loop
distance predicate identifies `endcap_plus/0` as occupied. Fixed-z full-depth
eta3 coverage is physically impossible, regardless of adding another shape.

A proposed small shift near z=10.90 also fails the ordinary three-family
normal-seam construction. At far face 11.15 the ECT inner rounded return has
clearance inner edge `1.3-sqrt(.30²-.05²)=1.004196011`. Its 15-degree projection
into the BT sector is 1.060565527; the eta3-compatible base apothem is only
1.055263383, short by 5.302 mm. The best nearby projection margin around
z=10.8806 remains -4.681 mm. A circular whole-slab aperture has at most about
.205 mm surplus there, insufficient for a 1 mm extra guard. These are static
prism/aperture constraints, not a claim that an eta3 ray hits the far-face coil:
the ray radius increases along z. Other chamber depth topologies were not
exhaustively searched.

## Eta3 aperture conventions

Use the nearest face `zn=abs(zc)-depth/2`; define `R3=zn/sinh(3)`. The chosen
implementation convention is the circumscribed polygonal aperture: inner base
apothem `u0=R3`, retaining no full-depth central-phi geometric extension beyond
eta3. Its corners necessarily over-open the hole slightly and reduce the
limiting eta near sector edges. Choosing the central plane instead would
over-open the nearest-face hole by another .024955392 m.

| Wheel | Chosen inner base apothem | Inner-corner radius | Corner eta limit |
|---|---:|---:|---:|
| Inner, 12 sectors | .648400988 | .668669386 | 2.969376530 |
| Middle, 24 sectors | .923349519 | .930054303 | 2.992800903 |
| Outer, 24 sectors | 1.252760699 | 1.262293808 | 2.992456900 |

The small corner-radius excesses over the eta3 circle are 20.268 / 6.705 /
9.533 mm. These are nominal aperture numbers; middle physical coil clearance
requires the separately reported larger bore.

A DISTINCT alternative would preserve eta3 coverage at sector corners at the
cost of small central-phi extension beyond eta3:

For half-sector angle alpha and normal half-seam delta=.01, the largest
eta3-compatible inner-corner radius has exact base apothem
`u0=cos(alpha)*sqrt(R3²-delta²)+delta*sin(alpha)` and half-width
`w=u0*tan(alpha)-delta/cos(alpha)`. Its corner norm is exactly R3. Simple straight
polygon edges cannot exactly match a circular eta boundary: this alternative
retains small extra central-phi coverage above eta3, separately from seams and
physical coils. It is not the selected implementation convention.

| Wheel | R3 nearest-face radius | Nominal base apothem | Max eta at sector centre |
|---|---:|---:|---:|
| Inner, 12 sectors | .648400988 | .628820961 | 3.030515627 |
| Middle, 24 sectors | .923349519 | .916701709 | 3.007190233 |
| Outer, 24 sectors | 1.252760699 | 1.243308849 | 3.007536251 |

The small polygon radial excesses at sector centres are 19.580 / 6.648 / 9.452
mm. These are nominal aperture values; the middle ECT obstruction remains
explicit and cannot be hidden by substituting a larger actual bore.

## Reproduction and limits

```
python3 -B interface-check.py \
  --repo /path/to/nodd \
  --revision 5f42c4b9649619771e8d5ec70247c99b10d8e80f \
  --output /tmp/inner-interface-check.json
```

Executed successfully with NumPy; JSON records source hashes, runtime versions,
dimensions, exact conflict counts and adverse witnesses. It imports no repository
code and writes only the requested scratch output. No ACTS, DD4hep, Geant4,
magnetic solver, response, mass or structural qualification was run or implied.
No repository/dependency/source files changed, no commits, nested agents or
external messages. The coordinator owns implementation, logging and integration.

Interface owners: SysArch owns magnet/frame/global clearance; MuonTech owns
chamber outlines and useful dimensions; SoftEng owns the prism/native mapping;
PhysVal owns interpretation and new transport/fit evidence. Design alternatives
remain (a) retain fixed z and report physical middle aperture loss, (b) revise
station/depth topology, or (c) revise toroid/frame/outer envelope under a new
human-directed design contract. None is signed off here.
