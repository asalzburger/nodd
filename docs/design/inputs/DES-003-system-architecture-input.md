# DES-003 input — System architecture synthesis

> First-round input retained for traceability. The [2026-09-17 review update](../DES-003-global-envelopes.md) supersedes conflicting recommendations.

- Date: 2026-09-16; status: DRAFT; approving humans: none.
- Role: System Architect, coordinating the three subsystem requests.
- Scope: global reservations and interfaces only; no production implementation.
- Governing context: [PROJECT](../../../PROJECT.md), [plan](../../DEVELOPMENT_PLAN.md), ADR-001/003 (DRAFT).
- Inputs: [tracker](DES-003-tracker-envelope-input.md), [calorimeters](DES-003-calorimeter-envelope-input.md), [muons](DES-003-muon-envelope-input.md). Their source IDs and precise locators are retained; all cited sources resolve in the [catalogue](../../../reference/manifest.yaml).

## 1. Recommendation and limits

**NODD DESIGN CHOICE — proposed:** use candidate E1, an expanded ODD-like
inner-solenoid layout, as the first negotiation drawing. Preserve the tracker
scale, barrel/endcap organization and overall muon outer dimensions. Expand the
tracker/magnet/calorimeter interface and calorimeter allocations; move the inner
muon boundary outward accordingly. This deliberately changes ODD where its
available space has no demonstrated support/service justification.

This is a concrete hypothesis for testing, **not an engineering-closed envelope**.
Rounded extra space is a design choice, not evidence that particular services,
coils or sampling stacks fit. Enclosures include packaging; active depths are
smaller. No density, coil current, chamber technology or layer count is fixed.

**FACT:** the pinned ODD study revision is
`c167363f3d4ad1540a577af99071283caf54f3a6` (SRC-ODD-UPSTREAM).
Its calorimeter factories use different barrel/endcap polygon radius conventions;
its thin solenoid and narrow service gaps do not establish integrated magnet
engineering. See subsystem input locators. Its study geometry and the ColliderML
production configuration remain distinct until their identities are reconciled.

## 2. Candidate E1: numerical allocation

All table entries are **NODD DESIGN CHOICE — proposed, human approval pending**.
Units are metres. Positive-z entries mirror to negative z. Outer radii are maximum
circular enclosures, including polygon corners; inner radii are circular exclusion
boundaries. Touching edges transfer allocation ownership, not permission for
coincident physical surfaces. Boxes are reservations, not sensitive volumes.

| Allocation | r min | r max | \|z\| min | \|z\| max |
| --- | ---: | ---: | ---: | ---: |
| Tracker assembly | 0.025 | 1.140 | 0 | 3.150 |
| Tracker outer support/service study band | 1.140 | 1.240 | 0 | 3.150 |
| Solenoid plus cryostat/support reservation | 1.240 | 1.440 | 0 | 3.350 |
| Coil/ECal radial interface | 1.440 | 1.500 | 0 | 3.350 |
| ECal barrel | 1.500 | 1.860 | 0 | 3.300 |
| ECal endcaps | 0.315 | 1.860 | 3.450 | 3.810 |
| ECal/HCal barrel interface | 1.860 | 1.960 | 0 | 3.810 |
| HCal barrel | 1.960 | 4.000 | 0 | 3.810 |
| HCal endcaps | 0.355 | 4.000 | 3.960 | 6.000 |
| Calorimeter/muon radial interface | 4.000 | 4.150 | 0 | 7.200 |
| Muon/return-structure barrel host | 4.150 | 6.762 | 0 | 7.200 |
| Muon/return-structure endcap hosts | 0.54073 | 7.000 | 7.200 | 10.270 |

The tracker service band is a shared space request: cables, cooling and supports
must compete for it. Timing remains **UNALLOCATED**, with a possible claim on
this band pending a fit study. No timing acceptance is prescribed. The forward
gap between tracker end at 3.150 m and ECal start at 3.450 m remains unassigned
integration space, not instrumentation or an assured continuous service corridor;
coil and support end structures must be reconciled there. Forward apertures require a separate
beam-pipe/shielding profile; the tracker inner reservation is not a pipe design.

The axial transitions ECal 3.300–3.450 and HCal 3.810–3.960, and the space behind
the HCal endcaps up to the muon endcaps, remain architect-owned integration zones.
They are neither assumed empty air nor assigned wholesale to services. Sector
routes, end supports, shielding and displaced transition faces require proposals.
The muon barrel/endcap allocation meets at 7.200 m without a certified clearance.

### Why these numbers are worth testing

**NODD DESIGN CHOICE:** retain the tracker allocation requested by its owner. Add
0.100 m radially for a service trade study and open a 0.300 m axial integration
gap before ECal, replacing
ODD's unproven 0.020/0.050 m nearest-boundary differences. Allocate 0.200 m radially
for the magnet assembly as a deliberately visible placeholder. Its feasibility,
material and end structures remain critical open questions.

The calorimeter normal-depth allocation must survive polygon corners. **INFERENCE**
using ODD's 16-sided barrel construction, with inner face apothem at the circular
exclusion radius: `t = r_outer*cos(pi/16) - r_inner`. E1 permits approximately
0.3243 m ECal and 1.9631 m HCal face-normal thickness, versus the inherited
0.2424/1.836 m sampling stacks. The remaining approximately 0.0819/0.1271 m is
only a space comparison: it is not a validated packaging allowance or proof of
adequate shower depth. Endcap radius conventions must be handled separately.

**NODD DESIGN CHOICE:** choose the enlarged ECal/HCal enclosures to admit this
comparison while retaining ODD's compact whole-detector scale. Preserve the outer
muon dimensions initially, but reduce available barrel host thickness by moving
its start from 3.536 to 4.150 m. This is a real cost: chamber stations and return
structures must be reallocated; inherited station locations cannot simply transfer.

**INFERENCE:** entrance-edge geometry gives `asinh(z/r)` approximately 3.09 for
ECal and 3.11 for HCal. This supports investigating calorimetry near absolute eta
3; it does not demonstrate full shower depth, hermeticity or efficiency there.
Tracking studies near eta 4 therefore leave a forward calorimetry decision open.

## 3. Magnet and muon contract

**NODD DESIGN CHOICE:** start with tracker-assisted muon identification and
trajectory matching. Independent muon momentum measurement is not a requirement
in this candidate. Use a nominal **3 T** central tracker field as a proposed
comparison hypothesis (inherited FACT: SRC-ODD-UPSTREAM,
`xml/OpenDataDetector.xml`, `Field_nominal_value`, line 24), not a solved magnet;
neither a spatially constant tracking field nor ODD's outer-field number proves
a physically consistent global field.

The System Architect owns coil, cryostat, supports and return concept. Muon host
space is jointly negotiated for chambers, services and any return structure;
it is not simultaneously available in full to each. A return-yoke or air-return
proposal must account for end paths and fringe field. Transport/reconstruction
must consume the same versioned field. Field polarity, integral and gradients
require a cross-cutting ADR before implementation.

## 4. Alternatives to keep live

| Option | Benefit | Main unresolved cost |
| --- | --- | --- |
| E0: inherited ODD allocations | Clean geometry-scale control; smallest change | Existing magnet/service gaps and effective calorimeter material remain unjustified; use true polygon enclosures |
| E1: proposed expanded inner coil | Keeps ODD ordering; makes integration space explicit | Coil material upstream of ECal; larger calorimeters compress muon host; no magnet closure |
| E2: calorimeter input C1, external solenoid | Removes coil from pre-ECal material; permits coupled inner calorimetry | Coil beyond 3.80 m calorimeter enclosure needs new radial/axial allocation, muon/yoke redesign and magnet study |
| E3: independent external muon spectrometer | Independent momentum measurement | Additional field, coils/supports and lever arm; cannot assume inherited host dimensions suffice |

No option is signed off. Compare E1/E2 first using pre-ECal material, shower
leakage, magnet plausibility and muon role; do not choose solely by drawing fit.

## 5. Interface ownership and priority questions

| ID | Endpoint owners | First required handoff |
| --- | --- | --- |
| IF-01 | Architect ↔ tracker | Beam-pipe profile, first active radius, supports and forward aperture |
| IF-02 | Tracker ↔ architect | Local-to-shared power/data/cooling handoff; timing request; no double counting |
| IF-03 | Architect ↔ calorimeter | Coil/end structure, upstream material and field; service exit corridors |
| IF-04 | ECal ↔ HCal, architect coordinating | Depth accounting, staggered transitions, common supports and electronics routes |
| IF-05 | Calorimeter ↔ muon/architect | Leakage/shielding, service paths, return structure and first station placement |
| IF-06 | Architect ↔ software | Versioned enclosure/radius conventions, field coordinates/units and exclusions |
| IF-07 | All technicians ↔ physics | Active surfaces, independent measurements, material scenarios and coverage definitions |

Resolve first: (1) inner versus outer coil and required muon role; (2) credible
magnet/service inventories; (3) forward calorimetry/shielding scope; (4) whether
calorimeter depth survives realistic material/packaging; (5) transition and sector
coverage from multiple vertices; (6) whether the reduced muon host suffices.
Each can force envelope revision. The coordinator must retain the alternatives
and route unresolved coupled choices to human review.

Verification: synthesized the three source-located inputs; checked polygon-depth
and eta arithmetic with Python. No field solution, DD4hep construction, material
transport or performance simulation was performed. Parent session records this
contribution; this memo supplies neither acceptance criteria nor human approval.
