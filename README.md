# nODD

nODD develops a more realistic, publicly reproducible evolution of the
OpenDataDetector for DD4hep simulation and ACTS-compatible reconstruction.
See the [project scope](PROJECT.md), [development plan](docs/DEVELOPMENT_PLAN.md)
and [documentation index](docs/README.md).

The [TDR outline](docs/publication/TDR-outline.md) and
[publication plan](docs/publication/publication-plan.md) organize chapters,
evidence and review inputs as the detector design develops.

## Agent roles

Use these short address names when referring to the project's eight agent roles.
The [development plan](docs/DEVELOPMENT_PLAN.md#6-stage-b-agent-organization-and-responsibility-boundaries)
defines their full mandates and responsibility boundaries.

| Address name | Role | Responsibilities |
| --- | --- | --- |
| `ProRes` | Project responsible | Objectives, scientific use cases, requirements, priorities, decision/risk register and escalation to humans. |
| `SysArch` | System Architect | Global layout, envelopes, interfaces, magnets and fields, shared supports and services, and aggregate budgets. |
| `TrackTech` | Tracker technician | Pixel/strip technology, local electronics, supports, cooling and service routes; provisionally dedicated timing hardware. |
| `CaloTech` | Calorimeter technician | Electromagnetic and hadronic calorimetry, local electronics, supports, cooling, gaps and response assumptions. |
| `MuonTech` | Muon technician | Chamber technology, stations, local services and readout, backgrounds, and field/absorber requirements. |
| `SoftEng` | Project software engineer | Specification and code generation, DD4hep/Geant4, digitization and reconstruction, identifiers, environments, CI and reproducibility. |
| `PhysVal` | Physics and Performance Validation | Independent physics benchmarks, observables, response review, uncertainties, ODD/nODD comparisons and scientific interpretation. |
| `PubDoc` | Publication/documentation office | TDR structure, source catalogue, terminology, claim/version traceability, figures and tables, and TDR revision consistency. |

These are responsibility roles, not a requirement for eight simultaneous agent
processes. Only identified humans may grant design sign-off or acceptance.

## Human review 

Guidelines for human review can be found in [REVIEW.md](REVIEW.md) 

## Final sign-off

The final human sign-off authority is **`asalzburger-review`**, assigned by the
user on 2026-09-18, wherever the project workflow requires it, including formal
M0 closure. See [ADR-002](docs/decisions/ADR-002-review-and-signoff-policy.md)
for the assignment and remaining review-policy questions. Each approval requires
an explicit human decision for an exact reviewed revision.

## Node-specific software

The [ACTS Spack skill](skills/acts-spack/SKILL.md) checks the
[verified node registry](skills/acts-spack/references/nodes.json) before using
preinstalled DD4hep/Geant4. It warns about unavailable nodes or capabilities;
runtime availability and full source availability are recorded separately.
