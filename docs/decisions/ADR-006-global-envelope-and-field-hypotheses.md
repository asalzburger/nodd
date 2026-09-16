# ADR-006 — Global envelope and field hypotheses

- Status: DRAFT; created: 2026-09-16.
- Human owner / issue: TBD / proposal PR discussion; no separate issue.
- Human approval evidence: pending; no production implementation authorized.
- Related: [DES-003](../design/DES-003-global-envelopes.md), [ADR-001](ADR-001-upstream-baseline.md), [ADR-003](ADR-003-validation-and-artifact-policy.md), [development plan](../DEVELOPMENT_PLAN.md).
- Supersedes / superseded by: none.

## Context and evidence

Stage B requires a coherent detector proposal. Tracker, calorimeter and muon
requests compete for magnet, support and service space. DES-003 collects sourced
facts and their precise locators, derived consequences, proposed dimensions and
open questions. Keeping ODD's broad character does not require preserving every
dimension or its unsolved physical assumptions.

**FACT:** SRC-ODD-UPSTREAM study revision
`c167363f3d4ad1540a577af99071283caf54f3a6`,
`xml/OpenDataDetector.xml` defines a nominal central field of 3 T. Its envelope
and calorimeter factories use conventions documented in DES-003. These facts
establish the inspected implementation, not magnet feasibility or nODD targets.

## Proposed decision

All following items are **NODD DESIGN CHOICE — proposed, approving humans: none**:

1. Use DES-003 candidate E1 as a numerical hypothesis for discussion: retain an
   ODD-like tracker/inner-solenoid/calorimeter/muon ordering, enlarge interface and
   calorimeter space, and initially retain the overall outer detector scale.
2. Use axisymmetric metre-based enclosures with outer radii bounding all corners,
   radial inner exclusions and z-reflection symmetry for this planning pass.
   These are not active-surface or imported polygon conventions. A full
   coordinate/identifier/readout contract remains open.
3. Carry 3 T as a nominal tracker comparison value only. Do not inherit an outer
   field or assert a physical field map. Require a coherent coil/cryostat/return
   proposal and common field identity for transport and reconstruction.
4. Begin with tracker-assisted muon identification/trajectory matching. Independent
   muon momentum measurement requires a separate justified field/material/space
   choice. No muon efficiency or resolution is implied.
5. Keep dedicated timing, forward calorimetry, beam-pipe profile, return material
   and detailed service routes explicitly unallocated. Their eventual volumes and
   material may require changes to E1.
6. Maintain machine-readable allocations, derived drawing and diagnostics together.
   Their agreement is reproducibility evidence, not scientific acceptance.

## Alternatives and consequences

| Option | Benefit | Cost |
| --- | --- | --- |
| E0: ODD control | Direct lineage comparison | Existing physical assumptions remain unproven |
| E1: expanded inner coil | Preserves broad ordering and makes integration space explicit | Dead material before ECal and reduced muon host space |
| E2: external coil | Reduces upstream coil material | Larger magnet/support/return and changed muon envelopes |
| E3: independent outer spectrometer | Separate momentum measurement | New bending-field and space requirements |

E1 is not yet preferred on demonstrated physics or engineering grounds. The
coverage mismatch between forward tracking and the shown calorimeter/muon
allocations must be resolved through use cases and options. Metre-scale envelopes
cannot substitute for radiation/interaction lengths, active crossings or field
integrals. Empty drawing space cannot be treated as proven service capacity.

## Verification and decision gate

DES-003 links the current rectangle/straight-ray diagnostic and staged software
plan. Before accepting an architecture, review magnet ordering and muon function,
forward requirements, shared services/material accounting, polygon dimensions and
calorimeter depth scenarios. Select physical observables and acceptance criteria
before quantitative validation. No field solution, detector simulation or
performance acceptance is claimed by this ADR.

Assign human technical/domain/validation reviewers and record an exact reviewed
revision with conditions. Discussion or merging this DRAFT does not advance it
to SIGNED OFF or authorize production geometry changes.
