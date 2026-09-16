# DES-003 input: calorimeter envelopes and interfaces

- Date: 2026-09-16
- Status: DRAFT; subsystem advice for the global proposal, not sign-off
- Role: calorimeter subsystem technician
- Scope: envelopes, depth rationale and interfaces; no production geometry change
- Governing context: [PROJECT](../../../PROJECT.md), [development plan](../../DEVELOPMENT_PLAN.md), [ODD assessment](../../validation/ODD-realism-assessment.md)

## 1. What the inherited geometry establishes

**FACT — SRC-ODD-UPSTREAM**, revision
`c167363f3d4ad1540a577af99071283caf54f3a6`,
`xml/OpenDataDetectorEnvelopes.xml`, constants `ecal_*` and `hcal_*`:

| Subsystem | Inner/outer radial parameters (m) | Axial parameters (m) |
| --- | --- | --- |
| ECal barrel | 1.250 / 1.500 | half-length 3.050 |
| ECal endcaps | 0.315 / 1.500 | absolute z 3.200–3.450 |
| HCal barrel | 1.600 / 3.436 | half-length 3.450 |
| HCal endcaps | 0.355 / 3.436 | absolute z 3.600–5.436 |

These are polygonal XML parameters, not circular clearances. **FACT:** in
`factory/calorimeter/ODDPolyhedraBarrelCalorimeter_geo.cpp`, `create_detector`
sets face widths to `2*r*tan(pi/16)` and outer apothem to inner radius plus
stack thickness. **INFERENCE:** corner radius is apothem times
`sec(pi/16) = 1.019591`: constructed ECal outer apothem 1.4924 m means corners
at 1.52164 m; HCal 3.436 m means corners at 3.50331 m. Endcap factory
`ODDPolyhedraEndcapCalorimeter_geo.cpp` instead converts XML outer radius by
`cos(pi/16)` before constructing staves: its input outer radius is circumradius,
while its inner radius is apothem. Thus one common conversion is incorrect.
A conservative ECal corner-to-HCal-inner-circle clearance is 0.07836 m, not
0.10 m; exact aligned polygon clearance requires the phi geometry.

**FACT — same source**, `xml/detectors/CalorimeterECal.xml`, layer/slice elements:
48 repeats of 5.05 mm. **INFERENCE:** these give **0.2424 m** normal sampling-stack thickness, including
91.2 mm of tungsten alloy. The nominal 0.250 m radial allocation leaves only
7.6 mm relative to this stack. This arithmetic does not demonstrate space for
cassettes, cooling manifolds or support skins. **FACT:** the barrel gap parameter
is zero; endcap gap is 2.5 mm.

**FACT — same source**, `CalorimeterHCal.xml` and materials `siPCBMix`:
36 repeats of 30 mm steel, 16 mm PCB mixture, 3 mm scintillator and 2 mm air.
**INFERENCE:** these sum to **1.836 m**, exactly the nominal radial depth. The PCB mixture alone contributes
57.6 cm at 5.05077 g/cm³, approximately **291 g/cm²**. Its copper mass fraction is
0.818763. This must be treated as substantial passive material, not an incidental
board allowance. Air labelled for services supplies neither coolant nor cable mass.

**INFERENCE:** retain these stacks as a comparison case, not a justified bill of
materials. Removing the dense mixture without replacing its physical function
could sharply reduce depth; adding services could double-count an existing effective
representation. A component inventory is needed before either change.

## 2. Experimental anchors, with their limits

**FACT — SRC-ATLAS-JINST-2008**, §1.3, printed p. 8 / PDF p. 38:
ATLAS reports electromagnetic depth greater than 22 radiation lengths in the
barrel and 24 in endcaps; instrumented calorimetry approximately 9.7 nuclear
interaction lengths in the barrel and 10 in endcaps. Additional outer support
brings the central total to 11. These are different accounting boundaries.
The same page describes the upstream solenoid/common calorimeter vacuum vessel
and deliberate minimization of dead material.

**FACT — SRC-CMS-JINST-2008**, §4.2, printed p. 92 / PDF p. 119:
CMS barrel crystals start near radius 1.29 m, have length 0.230 m and depth
25.8 radiation lengths. Rear services converge to an external-end patch panel;
mechanical gaps exist despite quasi-projective crystal axes. §5.1, printed p. 123 /
PDF p. 150 gives central HB absorber depth 5.82 interaction lengths, with the
preceding ECAL adding approximately 1.1. CMS also has an outer calorimeter: HB
alone is not an appropriate full-detector depth target.

**FACT — SRC-CMS-TDR-019**, §1.4, PDF/printed p. 17, Figs. 1.5–1.6 pp. 18–19:
the dated HGCAL design has 0.34 m CE-E thickness, approximately 26 radiation
lengths and 1.7 interaction lengths. Total CE-E/CE-H plus upstream moderator is
10.7 interaction lengths. Cooling plates, absorber plates and module bases have
explicit material roles. This is the local 2018 TDR design, not a claim about the
latest installed/final design.

**INFERENCE:** an initial comparison band of roughly **24–30 radiation lengths**
for ECal and **9–11 interaction lengths** for the combined instrumented calorimeter
is reasonable for studying ODD-like high-energy calorimetry. These are screening
bands derived from the examples above, not accepted requirements or guaranteed
containment. Contributions from support, coil and uninstrumented absorber must be
reported separately. Energy, particle species, incidence, upstream interactions,
cracks and response determine leakage and resolution. Geant4 energy/angular scans
must test the eventual specification.

## 3. Concrete space request to the System Architect

**NODD DESIGN CHOICE — PROPOSED, approving humans: none.** Option C0 retains
the inherited dimensions in section 1 as planning reservations and the inner-coil
ordering. It is the least disruptive starting option, conditional on finding
credible magnet/support/service space; no proof of buildability is implied.

Option C1 expands the calorimeters and moves the coil outside them. Use the following
rounded allocations as one candidate, contingent on a solenoid outside the
calorimeters and reconciliation with tracker/timing requests:

| Allocation | Radial range (m) | Absolute z range (m) |
| --- | --- | --- |
| ECal barrel | 1.35–1.70 | 0–3.25 |
| ECal endcap, each side | 0.30–1.70 | 3.40–3.75 |
| HCal barrel | 1.80–3.80 | 0–3.75 |
| HCal endcap, each side | 0.35–3.80 | 3.90–5.90 |

These are allocation rectangles for the global r–z study, not active-face or
polygon definitions; their outer radii are requested maximum enclosure radii. A
16-sided barrel must fit its corners within them, reducing face-normal space. The ECal's 0.35 m allocation accommodates a compact sampling
concept with more packaging room than ODD; HGCAL's 0.34 m example demonstrates
scale, not interchangeability. The HCal's 2.00 m allocation is a rounded expansion
of ODD's 1.836 m stack. The ECal nominal increase over ODD is 0.10 m and HCal 0.164 m; corner clearance consumes part of that increase. Neither figure proves that the depth band fits. The 0.10 m
radial ECal/HCal corridor and 0.15 m axial transition allowances reserve space for
review; they are not inferred engineering clearances. Services/supports may need
more space or redistribution. Central coordination must assign ownership and
material once, including endcap supports and withdrawal routes.

**INFERENCE:** for a ray from the origin, `eta = asinh(z/r)`. The candidate inner
endcap entrance edges correspond approximately to eta 3.12 (ECal) and 3.11
(HCal). Thus studying calorimetry to approximately absolute eta 3 is geometrically
plausible, but not established by these boxes. Rays can encounter barrel tails,
endcap edges, air corridors or reduced depth. Scan path length per material versus
eta/phi and displaced production z; do not label front-face reach as hermeticity.
Coverage beyond this range needs a separate forward calorimeter/shielding decision.

## 4. Coil-order decision and review questions

**FACT:** ODD puts the 1.16–1.20 m solenoid upstream of its ECal; ATLAS demonstrates
an upstream coil with carefully integrated material, while CMS puts its barrel
calorimeters inside a larger coil (SRC-CMS-JINST-2008, overview Fig. 1.1).

**INFERENCE:** an external coil reduces unmeasured pre-ECal material but enlarges
magnet bore and changes stored-energy, support and return-field demands. Preserving
ODD's inner coil may be viable, but its realistic cryostat/services cannot be
squeezed into the existing thin shell without evidence. Compare both before fixing
the tracker/ECal boundary. C1 also conflicts with ODD’s muon start at radius 3.536 m: a coil outside 3.80 m requires moving muons and budgeting its return structure. The space request above must change if the inner-coil
option is selected; it cannot silently absorb a magnet into its service allowance.

Questions for global review:

1. What photon/electron/jet energies and leakage observables define sufficient depth?
2. Is calorimetry beyond absolute eta 3 required for forward jets/missing momentum?
3. Which coil order and return structure best balance calorimeter losses and muons?
4. What exactly does ODD's dense HCal mixture represent, and who validates its mass?
5. Where do barrel/endcap services leave without projective low-depth corridors?
6. Which supports are structural allocations versus instrumented calorimeter mass?
7. How will polygon corners, cracks and staggered boundaries alter circular envelopes?

Validation in this pass: local source/PDF text inspection and arithmetic only.
No DD4hep construction, field calculation or shower simulation was performed.
