# DES-004 — Calorimeter constraints on magnetic architectures

- Date: 2026-09-17; status: DRAFT research input; no technical sign-off.
- Context: [magnetic research plan](../../MAGNET_RESEARCH_PLAN.md),
  [DES-003 E1-R2](../DES-003-global-envelopes.md),
  [forward/services evidence](DES-003-calorimeter-review-1.md).
- Owner: Calorimeter Engineer; shared interfaces: System Architect and Muon Engineer.
- Scope: first candidate screen, not production geometry or a performance ranking.

## Evidence controlling the comparison

**FACT — SRC-ATLAS-JINST-2008**, §1.3.1, printed p. 8 / PDF p. 38:
the upstream solenoid and barrel electromagnetic calorimeter share a vacuum
vessel to reduce material. **INFERENCE:** an inner solenoid is an experimentally
credible architecture, but a credible coil/cryostat/support inventory matters for
photon conversions, electron showering and energy lost before the ECal.
Removing its material in a field-only study removes this disadvantage artificially.

**FACT — SRC-CMS-JINST-2008**, detector overview Fig. 1.1 and §2.1:
barrel electromagnetic and hadronic calorimeters lie inside the central solenoid,
with an external instrumented return structure. **INFERENCE:** an outer solenoid
moves its barrel material behind primary calorimetric measurements, while putting
a passive boundary between central calorimeter leakage and outer measurements.
Neither layout guarantees containment or equal muon performance.

**FACT — SRC-ATLAS-SOLENOID-2007**, §IV.A, PDF p. 2:
2 T required 7730 A in the installed detector versus 8000 A in air-core tests;
the paper attributes a 3.5% contribution to surrounding hadron-calorimeter iron.
**INFERENCE:** “no dedicated return yoke” is not an iron-free field model. Steel
absorbers and supports must enter a later nonlinear magnetic calculation. The
ATLAS percentage is evidence that the effect exists, not a correction factor for
nODD. A vacuum-current calculation verifies a diagnostic control only.

## Six candidates: calorimeter tradeoffs

All candidate definitions are **NODD DESIGN CHOICE — proposed**, with no approving
humans. The consequences below are **INFERENCE**, to be tested.

| Candidate | Position relative to calorimetry | Calorimeter/interface consequence |
| --- | --- | --- |
| MAG-01: inner solenoid, no dedicated yoke | Central ECal/HCal outside the coil | Count pre-ECal coil, cryostat and exits; HCal steel still modifies return/fringe field. Missing dedicated yoke does not remove leakage into muons. |
| MAG-02: inner solenoid plus iron return | Same pre-ECal boundary, additional downstream iron | Keep instrumented calorimeter depth distinct from uninstrumented return absorption; changed backscatter and muon filtering require joint simulation. |
| MAG-03: outer solenoid, no dedicated yoke | Diagnostic coil surrounds barrel and endcap central calorimeters | Less barrel pre-ECal coil material; larger field-exposed calorimeter volume and magnet supports. Calorimeter steel still participates magnetically; end services must cross or go around the coil assembly. |
| MAG-04: outer solenoid plus iron return | Central calorimeters inside, return outside | Additional passive leakage boundary and possible tail-catcher locations; do not credit yoke depth as measured calorimeter energy. Strongest pressure on outer space and service crossings. |
| MAG-05: inner solenoid plus air-core toroids | Central calorimeters outside inner coil, inside/between outer toroid structures | Retains inner-coil losses; discrete toroid coils/supports obstruct azimuthal service exits and produce nonuniform downstream material. Endcap calorimeter supports must coexist with toroid/endcap-muon access. |
| MAG-06: solenoid plus active return coils | Undefined until main/return coil positions are stated | Screen explicit inner-main and outer-main variants; return coils can add passive boundaries and interfere with exits. Do not label the option low-material without conductor, cryostat and support estimates. |

Detached forward calorimetry at absolute z 11.2–13.2 m is outside the meaning of
“central calorimeters inside the solenoid.” End fields and return structures can
still affect that region. Its supports, shielding and service footprints remain
separate interfaces; moving a central magnet must not silently consume them.

## MAG-03 diagnostic and envelope amendment

**NODD DESIGN CHOICE — proposed PROTOTYPE fixture:** current-sheet radius 4.5 m,
half-length 6.5 m, with a possible physical assembly reservation r=4.3–4.8 m and
half-length 6.8 m. These are research dimensions, not a conductor design. The
current sheet surrounds E1-R2 central calorimeter maximum r=4.2 m and endcap
absolute z=6.2 m. Its physical assembly reservation leaves only 0.1 m radially
between the calorimeter outer allocation and the assembly inner radius; it does
not prove a sufficient support/service corridor.

**INFERENCE:** that assembly overlaps the current muon barrel host beginning at
r=4.35 m, throughout its axial overlap. The current host cannot be retained
unchanged with this physical MAG-03 example. Request an explicit amendment
showing coil/end support, relocated first muon stations and a service handoff,
before claiming a physically integrated outer-solenoid option. A field-only curve
may be compared now if this conflict remains prominently labelled.

## Follow-up studies and deliverables

1. **Material before ECal:** produce separate eta/phi maps of radiation lengths
   from coil, cryostat, support and services, using a documented component or
   effective inventory. Compare inner/outer alternatives with fixed calorimeter
   response first, then candidate-specific material. Include coil ends and cracks.
2. **Calorimeter steel in the field:** hand the magnetic modeller coarse absorber
   and support regions, steel grades or uncertainty ranges, and volume fractions.
   Compare vacuum control with the resulting magnetic solution, without reusing
   vacuum linear-current scaling through saturated steel.
3. **Shower and leakage:** use physically allowed particle energies at each eta;
   report pre-ECal losses, energy deposited in instrumented calorimetry, escaped
   energy and energy in magnet/return structures separately. Compare leakage into
   muon stations and forward/central transitions. This requires Geant4, not ACTS
   trajectory propagation alone.
4. **Services and support:** maintain a route sketch from barrel end patch panels
   and endcap outer/rear handoffs through each magnet topology. Experimental
   anchors are CMS ECal §4.2/PDF119 and CMS-TDR-019 §4.5/PDF64–65; the latter
   explicitly coordinates calorimeter/timing/muon routes. Model minimum sufficient
   support and aggregate material; detailed cable CAD is outside this increment.
5. **Field-exposed response:** record vector-field ranges at active media and
   electronics locations. Check the eventual photosensor/active-medium choices
   against those ranges rather than assuming all calorimeter response is invariant.

No numerical field, shower or detector-construction result is asserted by this
memo. No new source or material recipe is introduced; mixture details remain
later component work and must not disappear from inherited material accounting.
