# DES-004 — Reallocate the absent inner-solenoid space

- Date: 2026-09-18; status: **DRAFT — unsigned candidate layout amendment**.
- Roles: Project Coordinator/System Architect, reconciled with tracker and calorimeter engineers; conditional concurrence from the muon engineer.
- Scope: MAG-03, MAG-04 and MAG-06 outer-main-solenoid variants only.
- Context: [DES-004](../DES-004-magnetic-configurations.md), [original reference](../DES-003-global-envelopes.md), [magnet space requests](DES-004-system-architecture.md), [muon coordination](DES-004-envelope-coordination.md).
- Numerical approving humans: pending. No production implementation or baseline replacement.

## 1. Recommended allocation

**NODD DESIGN CHOICE — proposed:** use the missing inner-coil space to bring
ECal inward while preserving its nominal thickness and increase barrel HCal host
depth. Retain the tracker, its shared interface, the existing outer magnet and
current stepped muon hosts. This exploits a real topological difference between
inner- and outer-coil candidates without silently changing every subsystem.

This is a candidate-specific optimized layout. It must remain distinguishable
from the earlier fixed-calorimeter comparison and from E1-R2. MAG-01/02/05 retain
their inner coil and current calorimeter allocations. MAG-06 here means its
outer-main-coil branch, not an additional inner-main variant.

All numerical allocations below are **NODD DESIGN CHOICE — unsigned**; metres,
cylindrical radius and mirrored absolute-z intervals. They are enclosures including
packaging, not uniformly instrumented material.

| Region | Previous r min–max | Proposed r min–max | Absolute z, unchanged |
| --- | --- | --- | --- |
| Tracker assembly | 0.025–1.140 | 0.025–1.140 | 0–3.150 |
| Tracker shared interface | 1.140–1.240 | 1.140–1.240 | 0–3.150 |
| ECal barrel | 1.700–2.060 | **1.300–1.660** | 0–3.500 |
| ECal endcaps | 0.180–2.060 | **0.180–1.660** | 3.650–4.010 |
| HCal barrel | 2.160–4.200 | **1.760–4.200** | 0–4.010 |
| HCal endcaps | 0.200–4.200 | 0.200–4.200 | 4.160–6.200 |

The ECal endcap outer radius must change together with the barrel. Retaining
2.060 m while moving the full HCal barrel inward to 1.760 m would overlap their
allocations at |z|=3.650–4.010 m. Plotting order cannot resolve that conflict.

Unchanged outer-main assembly: r=4.300–4.800 m, |z|≤6.800 m; diagnostic current
sheet R=4.500 m, half-length 6.500 m. Unchanged detached forward study volume:
r=0.120–1.500 m, |z|=11.200–13.200 m. No new coil normalization or field-control
identity follows from this amendment alone.

## 2. What the released space buys, and what it does not

**INFERENCE:** the nominal barrel ECal width remains 0.360 m; HCal grows from
2.040 to 2.440 m, gaining 0.400 m. The named tracker-to-ECal interval remains
0.060 m beyond the 0.100 m tracker interface; the ECal/HCal radial interval
remains 0.100 m. These are planning gaps, not demonstrated service capacities.

The gain is proposed **HCal assembly capacity**, not a passive-service dumping
ground or an instruction to fill 400 mm with steel. Calorimeter engineering must
allocate absorber, active layers, supports, readout and cooling consistently.
Neither additional interaction lengths nor improved containment is established.
ECal's smaller radius also changes circumference, available module area, angular
cell size and shower occupancy; preserving millimetres of depth does not preserve
granularity or response automatically.

**INFERENCE — conditional polygon example:** for an optional 16-sided barrel,
normal depth `r_max*cos(pi/16)-r_min` becomes about **0.3281 m ECal** and
**2.3593 m HCal**, versus 0.3204/1.9593 m previously. Moving ECal inward slightly
reduces the corner penalty; this does not allocate packaging or require polygons.

Keeping the larger HCal outer radius retains the original main-coil and muon
interfaces. A compactness optimization instead could reduce overall coil radius,
but would change field normalization, resources, muon space and the comparison
contract. It is an alternative requiring a new explicit coil diagnostic.

## 3. Tracker and timing trade

The tracker engineer recommends retaining r≤1.140 m and |z|≤3.150 m initially.
The same assembly allocation permits meaningful comparisons without inventing new
layers. The aggressive 25 mm inner host remains; it is not an active-layer radius.
Timing capability in the outermost tracker remains the baseline investigation;
forward timing and shared-service fit remain unresolved.

**NODD DESIGN CHOICE — deferred sensitivity variant:** grow tracker outer radius
to 1.340 m, move the 0.100 m shared interface to 1.340–1.440 m, and start ECal
at 1.500 m after a 0.060 m interface. This divides the released radial allowance
between tracker growth and calorimeter movement. It requires a new layer/support
layout and material study; no current evidence selects it over the recommendation.

**INFERENCE:** at fixed |z|=3.150 m, the cylindrical outer-boundary corner changes
from eta≈1.741 at r=1.140 m to eta≈1.590 at r=1.340 m. Extra barrel radius does
not establish better forward coverage or eta-4 timing. A prompt eta-4 trajectory
at that z has r≈0.1154 m, far inside either outer boundary. These ray identities
are not reconstructed-track performance.

## 4. Axial transitions and ray screening

Retain all calorimeter z limits. Removing a cylindrical inner solenoid does not
release an entire forward disk: tracker exits, timing, supports and calorimeter
services still compete for the |z|=3.150–3.650 m integration region. The barrel/
endcap transition widths remain 0.150 m for ECal and HCal.

**INFERENCE from allocation geometry:** smaller ECal radius moves its barrel/endcap
transition to larger absolute eta. The calorimeter engineer's prompt-ray scan
finds full barrel traversal through approximately eta 1.491, first endcap
intersection near 1.529 and full endcap axial traversal from approximately 1.615.
Partial barrel crossings continue to approximately 1.716. These are box-boundary
landmarks, not acceptance edges or material depths.

The coordinator's independent scan of eta=0–5.2 in steps of 0.001 found no decrease
in **summed ECal- or HCal-host path length** against the previous layout. This
supports the enclosure proposal as a first geometric screen; generated validation
artifacts and commands are recorded by the parent task. Summing separated host
segments can hide dead gaps and different sampling directions. The scan does not
model phi cracks, displaced vertices, curved particles, shower spread, sensitive
layers, composition or effective material. It is not a hermeticity or containment
acceptance test. The endcap inner holes and forward calorimeter are unchanged.

## 5. Magnet, muon and service consequences

Retain MAG-03/04/06 outer-main field controls for the vacuum comparison, but do
not claim that the **physical** field is unchanged: moving ferromagnetic absorber
and changing its inventory modifies flux, saturation and forces. Material-aware
solutions must consume the revised calorimeter shape and specified composition.

The outer magnet envelope, HCal back face and stepped muon entrances remain fixed.
The muon engineer conditionally concurs: no new direct host conflict arises,
with the upstream outer-family muon step still beginning at |z|=6.950 m.
Station hosts therefore need not move simply because ECal moved.
Additional barrel calorimeter capacity might change leakage, scattering and energy
loss; it does not validate punch-through suppression or authorize reduced muon
instrumentation. The detached forward calorimeter remains downstream of muons.

The architect owns shared corridors and handoffs; calorimeter and tracker owners
retain local service inventories. Shared annuli are not simultaneously available
to cables, support and timing at their full width. Pre-existing coil-service routes
are removed only where the physical inner coil is absent; outer-coil and forward
routes remain necessary. Preserve minimal sufficient supports explicitly.

## 6. Alternatives and next decision

- Keep the previous fixed layout as the comparison control, with released inner
  coil space unused. This isolates magnetic topology from detector optimization.
- Retain the larger ECal endcap with a stepped HCal collar rather than the smaller
  endcap above. This is geometrically possible but needs its own shapes and tests;
  it is not equivalent to overlapping rectangular boxes.
- Grow the tracker or reduce the outer-coil radius as separate optimizations, with
  new measurement/material or field/resource comparisons respectively.

Review the recommended bounds and their ownership now. Technology, segmentation,
material and field studies may later justify amendments. No baseline-update issue,
human sign-off or production change is created by this memo. Parent session owns
reproducible diagrams, numerical checks, dashboard updates and publication.
