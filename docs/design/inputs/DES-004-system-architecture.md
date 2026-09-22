# DES-004 — System Architect input

**2026-09-22 scope update:** MAG-06 is withdrawn from active study following
[expert review](DES-004-magnet-expert-review.md). New main-solenoid studies use
finite homogeneous winding packs; the earlier sheet calculations and MAG-06
recommendations below are historical. Enclosure allowances remain unverified.

- Date: 2026-09-17; status: DRAFT; numerical approvers: none.
- Scope: candidate space contracts, not production geometry or magnet approval.
- Context: [research plan](../../MAGNET_RESEARCH_PLAN.md), [DES-003](../DES-003-global-envelopes.md), [candidate cards](../DES-004-magnetic-configurations.md).

## 1. Reference and invariant comparison

E1-R2 at `cb654ee91457b22d899a898faf2c8bf6e0fc275e`, merged through PR #4,
is the reference allocation. Its JSON and proposal remain unchanged by this
research. PR progression does not imply approval of the numerical magnetic
alternatives below. Preserve tracking to absolute eta 4, calorimetry to 5 and
muons to 3 with 3.5 stretch as investigation objectives for 14 TeV collisions.

**FACT about the project record:** DES-003's allocation table reserves tracker
r=0.025–1.140 m, |z|≤3.150 m; inner magnet r=1.240–1.640 m, |z|≤3.550 m;
central HCal maximum r=4.200 m and endcap extent |z|≤6.200 m; muon barrel
r=4.350–6.762 m, |z|≤7.200 m. Detached forward calorimetry occupies a study
volume r=0.120–1.500 m, |z|=11.200–13.200 m. Those are inherited project
allocations, not demonstrated occupied-volume bounds or performance.

**NODD DESIGN CHOICE:** compare candidates first at Bz(0)=+3 T with the same
tracking allocation and diagnostic measurements. Then compare conductor, energy,
material, force and space demands. Normalize only the central field; do not claim
that equal normalization yields equal field leverage or equal resources.

## 2. MAG-01: use the reference shell without silently filling it

**NODD DESIGN CHOICE:** use a thin uniform current sheet at R=1.415 m,
half-length h=3.300 m, matching the midpoint and axial allowance of the
[solenoid space budget](DES-003-solenoid-space-budget.md). It lies inside the
reference assembly; the current sheet does not itself model conductor thickness,
cryostat, support or material. Positive azimuthal current gives positive central
Bz in a right-handed cylindrical convention.

**INFERENCE:** the finite-sheet on-axis formula gives
`NI = 2 B0 sqrt(R²+h²)/μ0 ≈ 17.144 MA-turn`, using B0=3 T and
μ0≈4π×10⁻⁷ H/m. This determines only ampere-turns. Turn count, cable current,
critical-current margin and energy extraction remain unknown. Excluding points
within 0.120 m of an ideal current sheet is a **NODD DESIGN CHOICE for numerical
diagnostics**, not a physical clearance, cryostat boundary or validated field-map
domain for particle transport.

## 3. MAG-03: explicit outer-coil amendment

**NODD DESIGN CHOICE:** define the first outer-solenoid diagnostic to surround
**both barrel and endcap central calorimeters**. Detached forward calorimetry is
excluded from “central”. Use R=4.500 m and h=6.500 m, normalized to +3 T centrally.
This deliberately larger magnetic volume tests extended combined-measurement
leverage, not an equally resourced substitute for MAG-01.

Proposed space request, **all NODD DESIGN CHOICE; human approval pending**:

| Amendment | Reference | Requested study allocation | Rationale / unresolved consequence |
| --- | --- | --- | --- |
| Outer magnet assembly | No such assembly | r=4.300–4.800 m, |z|≤6.800 m | Contains nominal current sheet and candidate support/cryostat space; decomposition not established |
| Central HCal-to-coil radial interval | HCal ends at 4.200 m | 4.200–4.300 m | 0.100 m planning interface, not verified services capacity |
| Muon barrel host inner radius | 4.350 m | 4.950 m | Avoids direct assembly conflict and leaves proposed 0.150 m interface |
| Muon barrel host outer radius | 6.762 m | Retain initially | Host thickness falls from 2.412 to 1.812 m; stations/supports may force expansion |
| Muon endcap host entrance | |z|=7.200 m | Retain initially | 0.400 m beyond proposed assembly end; not a complete end-support or service solution |

The sheet extends 0.300 m beyond the central calorimeter z maximum; the assembly
extends another 0.300 m. These round allowances have no engineering precision.
The proposed 0.500 m radial assembly thickness is a reservation, not a scaled
coil design or a claim of equal structural margin to MAG-01. End packs must be
annular and checked against calorimeter supports; no solid closure disk across
the calorimeter aperture is implied.

**INFERENCE:** the same formula requires approximately **37.747 MA-turn** for
MAG-03. The increased ampere-turns and magnetic volume make a resource comparison
essential; central-field equality alone cannot rank the alternatives.

Removing MAG-01's inner coil in MAG-03 does not move calorimeters inward in the
first comparison. Its former shell becomes an explicitly unused allocation;
optimizing the layout is a separate amendment. Material absent from the vacuum
diagnostic must not be mistaken for a realizable material saving.

### Barrel-only outer alternative

An outer coil surrounding only the barrel would have different axial extent and
field at the central endcaps. **NODD DESIGN CHOICE:** retain this as MAG-03-B,
with length and end interfaces **TBD**. Do not borrow the full-central candidate's
6.500 m half-length, predicted forward field or resources while calling it
barrel-only. Its comparison requires a separate explicit card and geometry.

## 4. Return systems and shared interfaces

**INFERENCE:** no dedicated return yoke does not mean no ferromagnetic material.
Central HCal steel, support structures and any later shielding can redirect flux;
the vacuum models deliberately omit that response. They are diagnostic controls,
not physical detector maps. MAG-02/04 require material identity, nonlinear B–H
curves, gaps and saturation studies before field comparison. MAG-05 needs discrete
toroid coil/support sectors; an ideal continuous toroid cannot establish service
gaps or muon acceptance. MAG-06 needs return-coil placement/current and an explicit
stray-field objective before it becomes numerically specified.

| Interface | Accountable owner / partner | Required information |
| --- | --- | --- |
| Tracker/inner magnet | Architect / tracker | Field through forward disks, aggressive host aperture, timing association, outgoing services |
| Magnet/calorimeters | Architect / calorimeter | Pre-ECal material, end structures, field exposure, routes and leakage accounting |
| Return/toroid/muon host | Architect / muon | Coil/yoke gaps, independent measured surfaces, scattering and usable bending |
| Cryogenic/current routes | Architect / all subsystem owners | Named chimneys, penetrations and shared sectors; local shell is not the complete system |
| Physical field/software map | Architect / software | Coordinates, sign, units, bounds, interpolation, omitted materials and map identity |

No dedicated absorber is added to improve plots. Establish calorimeter leakage
and punch-through before deciding whether extra material is physically warranted.
The detached forward volume cannot filter hadrons before upstream muon stations.

## 5. Next review and verification

Review the candidate/amendment definitions and common measurements before ranking.
Then establish numerically verified fields and propagation, followed by material
and resource studies. Human selection and production implementation remain later
gates; no candidate wins by this memo. New source needs: none for these initial
space choices. MAG-06's eventual technical precedent dossier remains open.

Verification: read the merged project allocations and prior source-located inputs;
recomputed ampere-turn examples with Python. No magnet solver, propagation,
engineering model or simulation was run for this input. Parent session records
the contribution and subsequent tool checks separately.
