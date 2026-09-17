# ADR-006 — Global envelope and field hypotheses

- Status: DRAFT; created: 2026-09-16; updated: 2026-09-17, review round 1.
- Human owner: TBD; review: [PR #4](https://github.com/asalzburger/nodd/pull/4).
- Human technical sign-off: pending; no production implementation authorized.
- Related: [DES-003](../design/DES-003-global-envelopes.md), [ADR-001](ADR-001-upstream-baseline.md), [ADR-003](ADR-003-validation-and-artifact-policy.md), [development plan](../DEVELOPMENT_PLAN.md).
- Supersedes / superseded by: none; first-round E1 retained in Git.

## Context and review direction

Stage B defines a coherent global detector. The human review of PR #4 directs
14 TeV HL-LHC studies with tracker coverage |eta| < 4, calorimetry |eta| < 5
(extension where feasible), and muons |eta| < 3 with 3.5 as a stretch objective.
The final combined coverage comment supersedes the earlier calorimeter minimum
of eta 4. This directs the investigation; it does not approve proposed dimensions
or assert achieved performance.

Muon work investigates a standalone-compatible, potentially toroidal system as
the baseline study while retaining the other field architectures. Dedicated
spectrometer-magnet selection is deferred. E1's identification-first preference
is superseded. Agreement that an allocation is a starting baseline is not
technical sign-off. Detailed tracker layers, PCB composition and polygon choice
follow the envelope exercise.

DES-003 and its review inputs retain source locators, derived consequences and
open questions. **FACT:** SRC-ODD-UPSTREAM study revision
`c167363f3d4ad1540a577af99071283caf54f3a6`,
`xml/OpenDataDetector.xml` supplies a nominal central 3 T field. That source
constant is not evidence that the new coil reservation realizes the same field.

## Proposed decision

The following are **NODD DESIGN CHOICE — proposed; numerical design approvers:
none**. The human investigation directions above are distinguished from these
technical recommendations:

1. Use **E1-R1** as the next numerical envelope hypothesis. Retain central E1
   dimensions, reduce endcap ECal/HCal/muon parent apertures to the values in
   DES-003 and add detached forward calorimetry. Preserve E1 at commit
   `7bb7ff04a96b2038572d59904f8954a42777d7e6` for traceable comparison.
2. Use metre-based, axisymmetric enclosures with radial exclusions and z-reflection
   symmetry for this pass. If polygons are later used, corners must fit; a polygon
   itself is optional. Coordinate/identifier/readout contracts remain open.
3. Carry 3 T centrally as an NbTi study hypothesis, bracketed by 2 and 4 T. Decompose
   winding, reinforcement, cryostat, cooling and protection before claiming fit.
   The finite-current-sheet estimate in the physics review reveals substantial
   forward variation; do not model the entire tracker as validated uniform 3 T.
4. Preserve standalone-compatible muon host space and compare air-core toroidal,
   iron-free solenoidal/combined measurement and instrumented-return options.
   An outer coil may improve a combined fit but does not automatically provide
   independent momentum. No dedicated muon magnet or iron amount is selected.
   Evaluate upstream calorimeter punch-through before proposing added absorber.
5. Study separate barrel and forward timing hypotheses, with alternatives. Exact
   allocations compete with support/services and remain open. Ordinary spatial
   silicon readout does not itself supply precision timing.
6. Treat detached forward calorimetry as an instrumented study volume, not a full
   installed enclosure. Beam pipe, shielding, rear readout, supports and routes
   may require extra radius/length. Its downstream position cannot filter hadrons
   before upstream muon stations; reduced endcap holes require a physical depth
   and beam-line study. Overall dimensions remain lower bounds on required space.
7. Maintain allocation JSON, drawing and diagnostics consistently. Envelope
   crossings and full axial traversal are not material budgets or active coverage.
   Use a staged study catalogue and later full propagation through a common
   versioned field in simulation and reconstruction.

## Alternatives and consequences

| Option | Role | Principal unresolved issue |
| --- | --- | --- |
| E0 | Inherited ODD comparison | Existing physical assumptions |
| E1 | First-round envelope, retained in Git | Forward coverage shortfall |
| E1-R1 | Revised apertures and detached forward study volume | Beam aperture, downstream footprint and upstream muon filtering |
| E2 | External central solenoid | Bending leverage, return/stray field, support and increased dimensions |
| E3 | Independent outer spectrometer; toroidal baseline investigation | Coil/support sectors, field integral and station geometry; decision deferred |

E1-R1's boxes can host an E3 investigation; these labels do not make envelope and
magnet alternatives mutually exclusive. A compact forward insert is also retained
as an alternative, but its overlap with current muon hosts requires redesign.
An iron-free magnet is physically possible but changes the entire return-field
solution. Removing iron does not preserve the previous map. No option is yet
preferred by demonstrated nODD physics performance or magnet engineering.

## Verification and review gate

Review global space, smaller apertures, route ownership and minimal sufficient
supports now. Subsequent component work resolves layer/station geometry, material
composition and detailed fields. Magnet decisions may remain open provided their
reserved interfaces and implications are explicit; this round does not force a
premature topology selection.

DES-003 links allocation diagnostics and the muon/physics/software study catalogue.
Select spectra, vertex/pile-up scenarios and observable-specific criteria before
acceptance. No field solution, detector simulation, punch-through measurement or
performance acceptance is claimed here. Operational ATLAS/CMS evidence supplies
anchors, not validation of the nODD proposal.

Assign human reviewers and record the exact approved revision and conditions.
Neither a baseline-start comment nor merging this DRAFT advances it to SIGNED OFF
or authorizes production changes.
