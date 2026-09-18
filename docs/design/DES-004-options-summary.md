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
with an enlarged muon host for a return-space investigation. Give MAG-06 a finite-coil
feasibility screen before investing in detailed engineering. This is a **NODD
DESIGN CHOICE — proposed work priority**, not a performance ranking or elimination.
No intrinsic physical showstopper has been demonstrated for an entire topology.
Several present assumptions cannot be carried into an integrated detector.

| One-page proposal | Team assessment | Next decisive evidence |
| --- | --- | --- |
| [MAG-01: inner solenoid, no dedicated yoke](options/DES-004-MAG-01.md) | Smallest change to E1-R2; retains pre-ECal coil material and uncertain independent muon information | Forward tracker response and actual fringe-field information between muon measurements |
| [MAG-02: inner solenoid + iron return](options/DES-004-MAG-02.md) | Credible compact alternative for independent muons; modest flux-area demand does not prove useful station bending | Steel/endcap allocation, nonlinear field and bending-versus-scattering comparison |
| [MAG-03: outer solenoid, no dedicated yoke](options/DES-004-MAG-03.md) | Less upstream barrel coil material; larger magnetic volume, current and integration demand | Compatible stations, combined/standalone information and resource consequences |
| [MAG-04: outer solenoid + iron return](options/DES-004-MAG-04.md) | Built topology precedent; enlarged host addresses the initial return-area warning | Solved flux partition and plate/gap/field tradeoff, with explicit envelope alternatives |
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

**Envelope adaptation agreed for research:** the outer coil conflicts with the
unchanged 4.35 m muon entrance, so its candidates use 4.95 m. The muon engineer
and coordinator now propose outer barrel radii 6.762, 7.50, 7.50, 10.00, 9.00 and
8.85 m for MAG-01 through MAG-06 respectively. These are explicit resource changes,
not revisions of E1-R2. [Current allocations and drawings](DES-004-magnetic-configurations.md#candidate-specific-muon-envelopes)
retain the full barrel/endcap definitions. The r=4.50 m diagnostic surface still
cannot represent a chamber inside the outer coil.

**Return-space response:** the original flat-field/all-flux screen required
127.23–95.43 m² at trial mean return fields 1.5–2 T, versus 66.67 m² in the old
outer-coil host. MAG-04's expanded host now reserves illustrative radial magnetic
slots totalling 129.94 m², with measurement/service gaps. MAG-06 instead reserves
4.95–8.10 m for return-field measurements, 8.10–8.60 m for the return coil and
8.60–8.85 m for outer routes/supports. Its measurement annulus has 129.14 m²;
returning the flat-bore flux there would average 1.478 T. These are capacity
screens, not solved fields or steel specifications. Actual flux, saturation,
packing, calorimeter return and exterior leakage remain to be calculated.

**Coordinated reuse of inner-coil space:** MAG-03/04/06 now move barrel ECal to
r=1.30–1.66 m and endcap ECal outer radius to 1.66 m; barrel HCal starts at
1.76 m and retains r=4.20 m outside. Tracker/services, axial limits, outer coil
and muon hosts remain fixed. This preserves nominal ECal depth and gains 0.40 m
of HCal assembly capacity. Tracker, calorimeter and muon engineers reconciled
constraints in the [architecture memo](inputs/DES-004-inner-space-reallocation.md).
A 5,201-direction prompt-ray scan found no reduced ECal/HCal summed host path;
material, shower, segmentation and service adequacy remain unverified.

**Remaining integration concern:** MAG-02–06 endcaps stop at |z|=10.9 m, leaving
0.30 m before the unchanged detached forward-calorimeter host. This is not a
verified service/shielding gap. MAG-04/06 end-field closure and useful measurements
have not been demonstrated within their now-stepped allocations. The upstream
section starts at 6.35 m for inner solenoids and 6.95 m for outer solenoids,
inside the barrel; only the wider section starts at the barrel back. Trial
0.15 m interfaces and the retained 0.40 m aperture need review, particularly
eta=3.5 entrance in the inner family. Further expansion may still be needed. MAG-05 still needs discrete toroid/station/service sectors. No topology
is rejected merely for needing more space; its increased resource demand must
remain visible. A baseline-update issue will follow only after a layout is chosen.

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
and acceptable resource costs. Candidate host expansions now provide explicit
inputs for steel/coil/station/service studies. Software
should validate a nonlinear steel benchmark and a finite/discrete-coil benchmark,
then provide continuous fields to ACTS. Physics should freeze common measurements,
material scenarios and failure denominators before fits; preserve missing crossings
and separate vertex-constrained results. Publication should retain the evidence
and rejected assumptions. No present blocker prevents this research programme;
none of these proposals authorizes production integration.

Supporting reviews: [Physics](inputs/DES-004-option-physics-review.md) and
[Software](inputs/DES-004-option-software-review.md). All proposals remain unsigned.
