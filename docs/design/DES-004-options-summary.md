# DES-004 — Magnetic layout evaluation: team proposal

- Status: DRAFT
- Date: 2026-09-17; **research recommendations, not human sign-off**.
- Reading length: two-page equivalent; six linked one-page proposals below.
- Basis: [candidate definitions](DES-004-magnetic-configurations.md), E1-R2,
  public experimental/concept evidence and explicitly limited diagnostic calculations.

## Page 1 — Recommendation and technical comparison

**Executive summary.** Continue all six options through a bounded evaluation,
with **MAG-05 and MAG-02 as the first standalone-muon research pair**. Use MAG-01
and MAG-03 to establish the simpler solenoidal/combined-measurement alternatives.
Retain MAG-04 as the operationally grounded outer-solenoid/iron comparison,
subject to a serious return-space investigation. Give MAG-06 a finite-coil
feasibility screen before investing in detailed engineering. This is a **NODD
DESIGN CHOICE — proposed work priority**, not a performance ranking or elimination.
No intrinsic physical showstopper has been demonstrated for an entire topology.
Several present assumptions cannot be carried into an integrated detector.

| One-page proposal | Team assessment | Next decisive evidence |
| --- | --- | --- |
| [MAG-01: inner solenoid, no dedicated yoke](options/DES-004-MAG-01.md) | Smallest change to E1-R2; retains pre-ECal coil material and uncertain independent muon information | Forward tracker response and actual fringe-field information between muon measurements |
| [MAG-02: inner solenoid + iron return](options/DES-004-MAG-02.md) | Credible compact alternative for independent muons; modest flux-area demand does not prove useful station bending | Steel/endcap allocation, nonlinear field and bending-versus-scattering comparison |
| [MAG-03: outer solenoid, no dedicated yoke](options/DES-004-MAG-03.md) | Less upstream barrel coil material; larger magnetic volume, current and integration demand | Compatible stations, combined/standalone information and resource consequences |
| [MAG-04: outer solenoid + iron return](options/DES-004-MAG-04.md) | Built topology precedent, but the current host is under strong return-area pressure | Solved flux partition and plate/gap/field tradeoff, with explicit envelope alternatives |
| [MAG-05: inner solenoid + air-core toroids](options/DES-004-MAG-05.md) | Strong reason to investigate unconstrained muons; sectors and forward transitions may consume the available space | Joint 3D coil, station and service allocation before a performance claim |
| [MAG-06: active return coils](options/DES-004-MAG-06.md) | Public design precedent; iron mass is exchanged for coils, supports and coupled-force risks | Finite main/return/end coils meeting spatial and external-field objectives |

**FACT — historical anchors:** ATLAS's solenoid and toroids and CMS's solenoid
and instrumented return establish credible technologies, not nODD performance.
The [4th Concept proposal](https://arxiv.org/abs/0708.0142v2) is catalogued as
SRC-FOURTH-CONCEPT-2007: §2.3/PDF5 and Fig.5/PDF6 describe opposed solenoids and
end coils. It is a design concept, not an operating HL-LHC detector. Its quoted
forward reach does not establish the nODD muon objective. Exact experimental
locators appear in each option proposal and the existing source ledger.

**INFERENCE — useful common scales:** the retained vacuum controls require about
17.14 versus 37.75 MA-turn and give 1.77 versus 2.74 T on axis at z=3.15 m,
for inner versus outer solenoids normalized to 3 T centrally. Neither axis sample
is an eta-4 track measurement. A common uniform-field winding-bore energy proxy
is about 149 MJ versus 2962 MJ; it exposes scale, but is neither full stored
energy nor a rigorous bound. The [reproducible screen](../validation/DES-004-option-screen.json)
records its assumptions; its radius convention differs from the earlier warm-bore
114 MJ proxy.

Calorimeter, tracker and muon consequences must be considered together. Inner coils
add upstream shower material. Outer coils move that boundary behind central
calorimeters but reduce external measurement space. Toroids avoid a mandatory
bulk iron return but introduce coil/support sectors. Calorimeter steel affects
**every** physical field model, including options without a dedicated yoke.

## Page 2 — Blockers, discussion outcome and next work

**Established incompatibility:** the proposed MAG-03/04 assembly r=4.30–4.80 m
intersects the unchanged muon host starting at 4.35 m. The existing study already
requests a 4.95 m entrance. It is impossible to retain both overlapping allocations
as occupied components; the amendment or another layout is necessary. The
r=4.50 m diagnostic surface also cannot count as a physical chamber in that coil.
This blocks unchanged-envelope integration, not further research into outer coils.

**Conditional resource warnings:** in a flat-field approximation, the outer coil
carries 190.85 Wb. Returning all of it through the entire 4.95–6.762 m muon
annulus would require an average 2.86 T even before chamber gaps reduce steel
area. At trial means of 1.5–2 T, the required area is 127.23–95.43 m² versus
66.67 m² available. These are diagnostic fields, not selected steel operating
limits. Physics challenged treating this as a saturation proof: actual bore flux,
calorimeter return and exterior leakage must be solved. Investigate altered
return paths, field targets, station allocations and outer radius explicitly.

For the MAG-06 outer-main variant, a uniform −1.5 T active-return annulus requires
an ideal outer radius 7.79 m if it begins at the zero-thickness main sheet, or
8.06 m if it begins at the proposed 4.95 m muon entrance. Both exceed the present
barrel host. This condition rejects that particular uniform-annulus fit, not all
active-return systems; finite/end-coil solutions and other variants remain open.

**Missing evidence, not demonstrated impossibility:** MAG-05 has no allocated
3D toroid/station/service solution; MAG-02/04 have no validated nonlinear steel
field; MAG-06 lacks a finite-coil solution. The existing ACTS checks establish a
working propagator, not six comparable detector models. No fit covariance,
alignment assumptions or quantitative standalone acceptance requirement is frozen.
Consequently there is no defensible resolution ranking yet.

**Team discussion outcome:** the muon office's preference for MAG-05 is retained
as research priority, with MAG-02 as the necessary material-bearing comparator.
Physics rejected equating smaller flux demand with better muon measurements and
rejected declaring MAG-04 impossible from average-field arithmetic. Calorimetry
requires restoring coil material and steel response before interpreting apparent
gains. The tracker office requires vector-field propagation and actual forward-disk
measurement leverage to eta 4; central field and endpoint samples cannot rank
tracking. Architecture requires visible amendments and separate fixed-fixture
versus physically compatible comparisons. Software distinguishes an available solver
from a verified nODD solution. These qualifications govern every recommendation.

**Next actions.** The coordinator should obtain human priorities for unconstrained
standalone versus combined muons, momentum/angular coverage, allowable losses,
and willingness to expand the envelope. The architect and subsystem engineers
can meanwhile prepare coarse steel/coil/station/service alternatives. Software
should validate a nonlinear steel benchmark and a finite/discrete-coil benchmark,
then provide continuous fields to ACTS. Physics should freeze common measurements,
material scenarios and failure denominators before fits; preserve missing crossings
and separate vertex-constrained results. Publication should retain the evidence
and rejected assumptions. No present blocker prevents this research programme;
none of these proposals authorizes production integration.

Supporting reviews: [Physics](inputs/DES-004-option-physics-review.md) and
[Software](inputs/DES-004-option-software-review.md). All proposals remain unsigned.
