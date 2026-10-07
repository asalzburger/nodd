# DES-022 — long-strip barrel structural sandwich

- Status: DRAFT
- Created: 2026-10-07
- Scope: isolated PROTOTYPE; human approval pending.
Governing task: detailed long-strip barrel and endcap in separate PRs; the cooled
material between the sensors must be the stave, with quantified anchor spacing.
Dependencies: [DES-008](DES-008-long-strip-modules.md), [DES-011](DES-011-service-constrained-tracker-optimization.md),
[strip services dossier](inputs/DES-010-strip-services.md), DES-020/021 prototypes.
No production detector is changed. Historical analytical bodies remain controls.

## Facts and derivation

**LS-F01 FACT:** DES-008 F03/F04, SRC-ATLAS-TDR-025 printed92/PDF118 and
section6.1 printed101–103/PDF127–129: paired strip sensors and cooled common
CFRP supports are credible architectures. Sensor/electronics qualification is
experiment specific. DES-010 SS-F01–08 provides precise support/bus/pipe locators.
A 5 mm foam core is distinct from its skins, adhesive, bus and sensor glue.

**LS-F02 FACT:** SRC-MIT-SANDWICH-2015, transcribed lectures16–17 PDF3–4:
skins carry bending and the core carries shear; total deflection contains both.
PDF9 lists wrinkling, shear, debonding and indentation failure modes. None of
those modes is qualified by a static deflection calculation.

**LS-I01 INFERENCE:** ideal simply supported uniform-load deflection is
`5 q L^4/(384 EI) + q L^2/(8 S)`. We use only CFRP skins for EI, with their actual
parallel-axis spacing including skin glue; silicon/bus/glue stiffness receives
no credit. S is the core shear modulus times its net section after four pipe
bores, times a conservative 5/6 shear factor. With concentrated components we
also bound each span by moving its full discrete weight to the worst midpoint:
`P L^3/(48 EI) + P L/(4 S)`. End service boards are individually loaded.
These are independent simply supported span bounds; releasing continuity
provides an engineering screen, not an FEA solution or a sag guarantee.

## Unsigned nODD choices (all numerical prototype inputs)

**LS-C01 NODD DESIGN CHOICE:** inherit radii840/1060 mm and ideal half-length
1287.333333333 mm from the frozen DES-011 selected layout. Tilt12 degrees is the
starting phi hypothesis; test actual complete-component clearance. Two 96×96×0.3
mm active sensors, 0.5 mm guard, 80 micrometre pitch, physically rotated ±20 mrad;
1200 strips/face and one measured coordinate per sensor. Every pair has two face
IDs; both faces of that same pair are required for a coverage hit. New local IDs
are isolated from production. Track fixtures retain |eta|≤4, vertex z±150/0 mm,
pT1 and10 GeV, B0/4 T, both charges; compare on the unchanged ideal cylinders and
old DES-011 finite planes. These are finite vacuum samples, not response studies.

**LS-C02 NODD DESIGN CHOICE:** a continuous 5 mm carbon-foam core, 0.1 mm glue
and 0.2 mm CFRP skins per face, spans z±1320 mm. It IS the structural stave;
no second hidden load-bearing rail is credited. A 124 mm width leaves one
mounting edge and a separate hybrid/bus edge. Two 2.5 mm OD titanium U circuits
per half-stave (0.14 mm wall, CO2 density proxy1 g/cm³) have legs at u±10/±30 mm.
Four bores are subtracted from foam. U bends of 10 mm centre radius return near
the centre, separated in u; exits and circuit labels are explicit. Each circuit
serves nine of the eighteen complete pairs in its half; the existing13-pair
limit is retained rather than assigning18 to one loop. Hydraulic balancing,
pressure/fittings and bend manufacture remain unqualified.

**LS-C03 NODD DESIGN CHOICE:** 36 rows fit the fixed active endpoints; adjacent
rows alternate outward lifts on BOTH faces. Pickup/glue/Si on low rows is
0.1 mm pickup plus0.1 mm spreader/0.2 mm glue/0.3 mm Si, high rows1.6 mm pickup plus the same spreader/glue/Si, giving sensor mid-plane separations
6.7/9.7 mm. This explicitly replaces the infeasible old5 mm gap. The continuous
core stays centred between every pair. 42×42 mm graphite pickups leave neighbour
low sensors clear. Guard frames are physically rotated with the active die.
Hybrids at the positive-u edge and insulated Cu buses connect each face to its
end board; 12-pair harnesses count complete pairs once. Effective electronics
preserves specified constituent volume, not a qualified ASIC model.

**LS-C04 NODD DESIGN CHOICE:** support stations use an inner CFRP bearing ring
and an edge mounting web, on the inward shingle edge with two potted contact lands/bolts, separated6 mm. The opposite edge is free to avoid a web through the neighbouring shingle; torsional stiffness requires FEA. One central station fixes
z; the others slide longitudinally. Mounts support both sensor faces through
this same core/skin sandwich. CFRP/epoxy/Ti inserts are explicit material fixtures.
The minimum count is searched against a 50 micrometre displacement screen:
40 micrometres reserved for gravity, 10 for joint/support compliance. Worst-case
CFRP E70 GPa, core G5 MPa and gravity load factor2; compare E100/140, G10/20 and
factor1. Station spacing, footprint clearance and end overhangs are audited.
The nominal ring/load transfer structure requires global FEA; torsion, thermal
bow, vibration, adhesive fatigue and insertion loads remain open. Recommendations
must state these qualifications rather than claiming a measured modulus.

**LS-C05 NODD DESIGN CHOICE:** constituent densities inherited from the DES-020
material fixtures: Si2.329, Cu8.96, PI1.42, epoxy2, CFRP1.73, carbon foam0.2,
graphite2.21, Ti4.51, aluminium2.70 g/cm³; CFRP carbon mass fraction0.70.
E/G values are coupon hypotheses, not material datasheet facts. Include all
sensors, guards, skins, pickups, electronics, buses, pipes, coolant, inserts and
end boards in the mass/load ledger. Support rings are ground structure, not
stave payload. Full discrete loads and continuous loads are separated.

**LS-C06 NODD DESIGN CHOICE:** barrel collection at each z end precedes the
first long-strip disc. Fixed longitudinal corridor r1144–1169 mm from DES-011;
service collection reserves real cable length and R50/R25 cable/pipe turns.
Reference packing75% phi/50% packing; adverse50%/40% with25% spare. Benchmark
13.4/3.6 mm power/fibre and8/12 mm trunk OD (DES-010 SS-F10/11) are comparison
fixtures. Count both faces' power once per complete pair; electrical sizing,
CO2 pressure drop, connector CAD and global combined endcap packing remain open.
Report failures in the fixed corridor; never enlarge it to obtain a pass.

The endcap will be DES-023 in a separate stacked PR. Its carrier is likewise the
sandwich between paired sensors. Refer to the validation report for actual
selected populations, anchor results, native checks and limitations.

**LS-I02 INFERENCE:** at r1060 mm, B4 T and pT1 GeV, transverse incidence can reach asin(r/(2R)) +12° ≈51.5°. A9.7 mm stereo pair then needs about12.2 mm extra phi overlap; stereo corner projection needs additional margin. Reserve20 mm phi margin. At barrel-end slopes the two-plane z displacement also consumes row overlap;36 rows provide27.1 mm projected z overlap. The28-row/6 mm phi margin control failed paired coverage and is retained.42 mm pickups clear neighbouring low sensor planes; the full96 mm thin graphite spreader supports/distributes load. Silicon edge bending, thermal bow and interface spreading require qualification.

**LS-I03 INFERENCE:** the exact first-traversal helix launch azimuth to a face endpoint is `atan2(y,x) - asin(k*rho/2)`. Intersect both faces’ endpoint intervals, not just a linear incidence displacement. At1060 mm,4 T/1 GeV, high pairs and a47 mm usable half-width give0.06226 rad common launch interval (at least102 staves). Reserve32 mm phi margin to cover stereo-dependent corners;20 mm was insufficient and is retained as a second rejected control. This fixes geometric parallax rather than assuming two independent sensor hits form a pair.

**LS-C07 NODD DESIGN CHOICE:** power uses two3 mm² Cu LV conductors plus0.14 mm²
HV wire, provisional0.3 mm radial insulation on LV and1.2 mm insulated HV OD,
in a6 mm gross bundle; each12-pair harness carries up to88.8 W at11 V, including
the separate2 W leakage proxy per pair. With4.1 m one-way internal+reserved-tail
length and resistivity0.018 ohm mm²/m (unsigned conservative20°C fixture), LV
loop drop is0.397 V and return drop0.199 V against1/0.2 V screens from DES-010.
A1.4× warm-resistivity control fails the return screen. Dielectric/HV rating,
converter response, fault current, conductor strain and connector heads require
qualification.6 mm is a dimensioned hypothesis, not a cable procurement spec.
Fibre bundle3.6 mm OD contains48 coated0.25 mm fibres, glass0.125 mm, outer jacket
0.3 mm; two fibres per face per pair is an unsigned two-way link allocation.
Constituent Cu/PI/silica volumes and air voids are conserved.13.4/3.6 mm CMS gross
bundle remains a separate benchmark control; no automatic channel-count scaling
or understated converter/leakage power is used. Cooling trunk dimensions remain
8/12 mm OD,6/10 mm ID; adverse packing remains an explicit failure if found.

**LS-I04 INFERENCE:** include the potted-land foam removal in the net shear section, without crediting epoxy/Ti stiffness. An independent continuous Timoshenko mesh uses actual point loads, free support rotations and10/20 mm refinement. Compare it to the released-span screen; do not call the latter an exact multispan solution. Ground-ring/joint compliance remains the separate10 µm allocation and must be verified by FEA/coupons.
