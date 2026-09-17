# DES-003 — Conservative solenoid space reservation

- Date: 2026-09-17.
- Status: **DRAFT — space budget only**, no technical sign-off.
- Scope: replace the unsupported 0.20 m total solenoid shell with an explicit
  provisional allowance. Detailed magnetic design is deferred to a separate study.
- Context: [DES-003](../DES-003-global-envelopes.md), [physics review 1](DES-003-physics-review-1.md), [ADR-006](../../decisions/ADR-006-global-envelope-and-field-hypotheses.md).
- Governing field hypothesis: 3 T at the origin, not 3 T uniformly throughout the
  tracker. Human numerical approvers: pending.

## Recommendation for the global drawing

**NODD DESIGN CHOICE — proposed:** reserve **1.24 ≤ r ≤ 1.64 m,
|z| ≤ 3.55 m** for the solenoid/cryostat assembly. This is a **0.40 m radial
allocation and 7.10 m total length**. Compared with the previous reservation,
add 0.20 m radially outward and 0.20 m at each end, retaining the tracker-facing
radial boundary. “Conservative” means generous planning space relative to the
thin-coil hypothesis; it is not an established upper bound on the eventual magnet
or an engineering safety factor.

The following subdivision explains the allowance. **Every allocation is a
NODD DESIGN CHOICE**, not a measured thickness or an instruction to fill the
space with solid material:

| Radial allocation | Interval [m] | Width [m] | Intended contents |
| --- | --- | --- | --- |
| Inner cryostat and interface space | 1.24–1.34 | 0.10 | Warm inner wall, vacuum/thermal insulation, shield and support clearances |
| Cold assembly | 1.34–1.49 | 0.15 | Winding, stabilizer, mechanical reinforcement, cooling and protection integration |
| Outer cryostat and support space | 1.49–1.59 | 0.10 | Thermal/vacuum insulation, outer vessel and local support interfaces |
| Unassigned integration margin | 1.59–1.64 | 0.05 | Space to redistribute after initial magnet layout; no material assigned |

**NODD DESIGN CHOICE — proposed axial budget:** allow the cold assembly to
|z|≤3.30 m, with **0.25 m at each end** for end reinforcement, connections,
thermal/vacuum closure and local installation clearance. The 0.25 m is a rounded
planning allowance; it is not derived from an end-force design. The axial end
packs remain annular: this proposal does not add a solid disk across the bore.
Radial and axial allowances describe one assembly, not masses to be added twice.

Chimneys, current-lead/cryogenic connections and external supports will need
named local routes out of this enclosure. Their remote volumes are **not**
claimed to fit in the 50 mm margin or represented as a complete cylindrical
layer. The System Architect must keep those routes open in shared corridors.

## Evidence behind the scale

**FACT — SRC-ATLAS-SOLENOID-2007**, abstract and Table I, PDF1: the commissioned
2 T ATLAS solenoid has approximately 2.4 m coil diameter, 5.3 m length and a
45 mm cold assembly, with 39 MJ stored energy. It uses aluminium-stabilized
NbTi and a shared calorimeter cryostat. Its thin cold mass is therefore not a
standalone cryostat-width benchmark. **FACT — SRC-CMS-JINST-2008**,
§2.1/PDF33 and Table2.1/PDF35: the 4 T CMS magnet has a 6.3 m cold bore,
312 mm cold-mass radial thickness and 2.6 GJ stored energy. Both establish
built NbTi detector-magnet precedent; neither is the proposed nODD magnet.
These sources are already registered in the [catalogue](../../../reference/manifest.yaml).

**INFERENCE — rough mechanical similarity only:** magnetic pressure scales
as B², and a simple thin cylindrical support model gives required load-bearing
thickness proportional to B²R at fixed allowable stress. Applying that scaling
to the **whole benchmark cold-mass thickness**, as an explicitly crude proxy,
gives about 0.12 m from ATLAS and 0.08 m from CMS at 3 T and R≈1.415 m.
The different results expose the approximation: the cold mass is not entirely
load-bearing, reinforcement/conductor structures differ, and end loads and
cryogenic material properties have not been matched. These are not independent
engineering estimates or lower bounds.

**NODD DESIGN CHOICE:** round the larger proxy upward to a **0.15 m cold-assembly
allowance**, then reserve another **0.25 m** for cryostat/interfaces and unassigned
margin rather than treating 0.15 m as the entire magnet. This is the rationale
for carrying 0.40 m in the global study. It replaces false precision with a
visible space budget, while leaving the physical material budget unresolved.

## Back-of-envelope consistency checks

**INFERENCE — diagnostic model:** use a uniform thin current sheet at the cold
assembly midpoint R=1.415 m, with illustrative winding length L=6.60 m. Ignore
iron, winding thickness, end shaping and service penetrations. The finite-solenoid
relation `B0=μ0 NI/[2 sqrt(R²+(L/2)²)]` gives **NI≈17.14 MA-turn** for B0=3 T.
Spread across the full 0.15 m cold-assembly radial allowance, that is an average
**17.3 A/mm²** over its longitudinal cross-section. If only 0.10 m is available
for winding, the average becomes **26.0 A/mm²**. Neither is superconducting
strand current density: insulation, stabilizer, reinforcement and fill factor
must still be accounted for. No critical-current margin is inferred.

At 3 T, `p=B²/(2μ0)≈3.58 MPa`. For an illustrative 50 mm effective structural
thickness, `pR/t≈101 MPa`. This is a force scale, **not** a demonstrated stress
or allowable strength. The full 150 mm cold assembly must not be counted as
structural metal without its composition. A uniform-field bore-energy proxy,
`p π(1.24 m)²L`, is approximately **114 MJ**; actual stored energy requires
integration of the full field, including its exterior. End forces, stability,
quench energy extraction and thermal insulation remain outside this calculation.

These checks support a credible planning scale, not a decision that the magnet
fits or is safe. Increasing the space allocation does not remove the forward
field variation identified in the earlier physics review.

## Consequences for adjacent envelopes

**INFERENCE:** the enlarged coil overlaps the old ECal barrel reservation
starting at r=1.50 m. Keeping the former 0.06 m external separation would require
**ECal barrel rmin≥1.70 m**. The ECal outer boundary and the HCal/muon boundaries
must then be renegotiated if their current depths/clearances are to be retained;
one cannot merely move the ECal inner face and shrink its available depth.

The new |z|=3.55 m end overlaps the old ECal endcap entrance at |z|=3.45 m in
radius. **NODD DESIGN CHOICE — proposed simple-envelope option:** move that
entrance to **|z|≥3.65 m**, reserving 0.10 m for the axial interface. This is a
rounded space allowance, not proof of room for all services. A shaped endcap
recess is an alternative, but it would require an explicit interface definition
and directional depth check. Propagate changes through HCal, timing, support and
forward coverage; do not hide the overlap by changing drawing order.

## Boundary of this decision

The present decision is solely how much space to carry into the detector-wide
proposal. Detailed conductor choice, winding arrangement, field quality/return,
cryostat structure, protection, chimney placement and material inventory belong
to the **next separate magnet research task**. Its outcome may enlarge or reduce
this reservation through a reviewed amendment. No DD4hep magnet material or
field implementation is authorized by this memo.

Verification: existing primary-source facts checked against the earlier verified
input; numerical current, pressure, energy and similarity scales recalculated
with Python. No field solver, structural model or simulation was run. The parent
session records this bounded contribution.
