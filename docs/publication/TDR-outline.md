# PUB-TDR-001 — Technical Design Report outline

- Status: **DRAFT — documentation frame for review**, not a detector design or publication approval.
- Created: 2026-09-22.
- Editorial lead: `PubDoc`; technical input owners are listed below. Human chapter owners remain unassigned.
- Work item: `TASK-B-PUB` in the [tracking register](../../project/tracking.json).
- Governing scope: [PROJECT](../../PROJECT.md), [development plan, section 7](../DEVELOPMENT_PLAN.md#7-tdr-structure-and-continuous-writing).
- Delivery and review sequence: [PUB-PLAN-001](publication-plan.md).

This is the proposed documentation frame for the **whole detector**. It expands
the development plan into chapters, sections and subsections that can be written
incrementally as designs and evidence mature. Chapter numbering is editorial;
the `PUB-*` identifiers remain stable when the report is reorganized. This outline
does not select detector parameters, restart paused studies or grant sign-off.

The intake snapshot is parent revision
`bb1f2dd512cd56b8c7e52679350ea843d8e3f0ff`, with the TDR submodule pinned to
`7783ea3e3235c0fe9da641db3d303a6f211b3073`. Its
main file (`docs/tdr/main.tex`, available with the submodule initialized) includes
only an introduction chapter, currently a
heading, and comments listing prospective chapters. The frame below is reviewed
in the parent repository first; the [migration gate](publication-plan.md#tdr-source-and-revision-workflow)
governs later LaTeX work. No Overleaf publication is implied.

## Front matter

Provide a draft/release label; fixed revision date for released editions; detector,
report and evidence revisions; authors and contributions once agreed by humans;
abstract; executive summary; reading guide; contents; and lists of figures,
tables and abbreviations. The executive summary must distinguish demonstrated
results from intended capabilities and state the report's applicability limits.
Final detector naming, authorship and publication venue remain open.

## 1. Motivation, scope and baseline

Lead: `ProRes`; inputs: `PubDoc`, `SoftEng`, `PhysVal`.

### 1.1 Scientific purpose and users

#### 1.1.1 Public simulation, reconstruction and algorithm research

State the intended users, benchmark questions and experiment-independent scope.

#### 1.1.2 Credibility and exclusions

Define physical plausibility and the limits of engineering claims; distinguish a
reference detector from an experiment-specific performance prediction.

### 1.2 TrackML, ODD and nODD continuity

#### 1.2.1 Baseline identity and inherited capabilities

Record source/configuration/environment identity and distinguish the inspected
ODD study snapshot from the approved comparison configuration.

#### 1.2.2 Retained, replaced and deferred components

Maintain a continuity/change table with physical motivations, evidence and the
relevant design decisions. Summarize the ODD realism assessment without turning
source inspection into executed validation.

## 2. Requirements, use cases and global architecture

Lead: `SysArch`; requirement owner: `ProRes`; independent assessment: `PhysVal`.

### 2.1 Operating scenarios and measurable requirements

#### 2.1.1 Beam, luminous region, backgrounds and operating assumptions

Separate fixed human directions from unresolved scenario definitions. Document
which claims depend on pile-up, radiation, occupancy or lifetime assumptions.

#### 2.1.2 Requirements-to-observables matrix

Map each requirement to an observable, sampling domain, proposed criterion,
uncertainty and review record. Carry the fixed tracker `|eta| < 4` requirement
from DES-005 as a human-directed choice, with beamspot and performance criteria
still outstanding; do not equate nominal angular reach with achieved coverage.

### 2.2 Detector concept and interfaces

#### 2.2.1 Envelopes, transitions and interface allocations

Provide linked longitudinal/transverse views, host versus active bounds, shared
clearances, handoff surfaces and explicit capacity uncertainties.

#### 2.2.2 Alternatives and selection arguments

Compare ODD-guided concepts and justified departures, retaining reasons for
rejected candidates and dependencies on field, material and performance evidence.

## 3. Conventions, provenance and configuration control

Lead: `SoftEng` and `PubDoc`; physical conventions reviewed by `SysArch`.

### 3.1 Common technical conventions

#### 3.1.1 Coordinates, units, transforms and alignment

Specify origins, handedness, local/global transforms, angles, symmetries and
alignment representation through reviewed contracts rather than implicit defaults.

#### 3.1.2 Readout, identifiers and timing conventions

Define segmentation and identifier ownership, mapping stability and common time
reference; distinguish geometry identifiers from reconstruction identifiers.

### 3.2 Traceability of claims and changes

#### 3.2.1 Facts, inferences and nODD choices

Apply the provenance model with precise public source locators, derivations,
uncertainties and named approval evidence where required.

#### 3.2.2 Design, implementation, evidence and report revisions

Explain lifecycle states, immutable review targets, generation provenance and the
parent/TDR revision pair. A document merge or successful executable is not approval.

## 4. Interaction region, magnets and magnetic fields

Lead: `SysArch`; inputs: `MuonTech`, `TrackTech`, `SoftEng`, `PhysVal`.

### 4.1 Interaction region and forward interfaces

#### 4.1.1 Beam pipe, shielding and clearances

Document beam-pipe/material assumptions, occupied envelopes and forward exclusions.

#### 4.1.2 Forward subsystem and service handoffs

Identify detached calorimetry, tracking, timing and muon interfaces, including
unallocated support/readout/shielding space.

### 4.2 Magnet concepts and implementation

#### 4.2.1 Solenoid, cryostat, returns and dedicated muon-field alternatives

Compare physical space/material budgets, supports, cooling and protection
assumptions. Keep field strength hypotheses distinct from engineered coils.

#### 4.2.2 Field representation and validation

Record provider/map identity, domains, interpolation, symmetries, units,
transport/reconstruction consistency and uncertainty in field integrals.

## 5. Tracker and dedicated timing

Lead: `TrackTech`; integration: `SysArch`; evidence: `SoftEng`, `PhysVal`.

### 5.1 Tracker system architecture

#### 5.1.1 Pixels, short strips/strixels and stereo long strips

Describe subsystem roles, measured coordinates, barrel/endcap boundaries and
motivated alternatives using DES-005's staged comparison programme.

#### 5.1.2 Layer placement and forward coverage

Record candidate layer tables, active masks, tiling, overlaps, transitions,
beamspot dependence and information content; retain comparison assumptions.

### 5.2 Pixel modules and assemblies

#### 5.2.1 Sensors, readout chips and module interfaces

Consume the existing DES-001 pixel work through pinned interfaces; distinguish
chip, sensor, bare module and installed assembly.

#### 5.2.2 Supports, services and repeated structures

Describe mounting, cooling, power/data terminations, staves/rings/disks and
material accounting up to the shared-service handoff.

### 5.3 Strip modules and assemblies

#### 5.3.1 Short strips/strixels and readout

Document sensor/readout options, dead regions, granularity, occupancy and local
services when their component evidence becomes available.

#### 5.3.2 Stereo outer long strips

Document stereo geometry, paired measurement interpretation, supports and
ambiguities; do not substitute ideal two-coordinate measurements without evidence.

### 5.4 Timing options and tracker verification

#### 5.4.1 Timing-capable layers and dedicated alternatives

Compare no-timing, integrated and separate options, including forward reach,
hardware/material cost and credible response. Hardware ownership is provisional.

#### 5.4.2 Tracker evidence and applicability

Summarize parametric, navigation, material and reconstruction evidence by maturity;
cross-reference the full methods in chapters 10–12.

## 6. Electromagnetic and hadronic calorimetry

Lead: `CaloTech`; inputs: `SysArch`, `SoftEng`, `PhysVal`.

### 6.1 Electromagnetic calorimeter

#### 6.1.1 Active media, absorber and representative assembly

Establish technology provenance, sampling/segmentation, readout and operating
assumptions before describing the full barrel/endcap arrangement.

#### 6.1.2 Integration, response and validation

Cover transitions, upstream material, services, calibration, noise and leakage;
identify the evidence required for electron/photon claims.

### 6.2 Hadronic and forward calorimetry

#### 6.2.1 Sampling assemblies, segmentation and forward options

Separate source-supported assembly designs from envelope reservations and deferred
technology choices. Record effective-material limitations where applicable.

#### 6.2.2 Shower containment and cross-system effects

Evaluate cracks, dead material, punch-through, readout/service routing and impacts
on jets, missing momentum and muon backgrounds within the supported scope.

## 7. Muon system

Lead: `MuonTech`; field/interface input: `SysArch`; assessment: `PhysVal`.

### 7.1 Chambers, stations and services

#### 7.1.1 Technology, measured coordinates and local readout

Document chamber/gas/sensor options, segmentation, efficiency, resolution and
background assumptions with their source and operating scope.

#### 7.1.2 Station layout, supports and coverage

Resolve barrel/endcap/forward transitions, alignment, services, shielding and
field-dependent station requirements.

### 7.2 Measurement modes and verification

#### 7.2.1 Identification, combined fits and standalone momentum

State the distinct requirements of each mode and compare return-field and
dedicated-magnet options without assuming one provides the other's capability.

#### 7.2.2 Material, field-integral and performance evidence

Record scattering, punch-through, acceptance and response limitations and link
the corresponding transport/reconstruction evidence.

## 8. Common mechanics, electronics and services

Lead: `SysArch`; local inputs: `TrackTech`, `CaloTech`, `MuonTech`.

### 8.1 Shared physical integration

#### 8.1.1 Supports, installation envelopes and alignment interfaces

Describe plausible load paths, reserved clearances and assembly constraints;
flag unverified structural, thermal and installation engineering explicitly.

#### 8.1.2 Power, cooling, gas and data distribution

Connect local loads/terminations to named shared routes; document volumes,
materials, routing assumptions and unresolved capacities.

### 8.2 Aggregate accounting and effective representations

#### 8.2.1 Mass, material, power and service budgets

Reconcile component-to-system totals and uncertainties without double counting
material or losing services between owners.

#### 8.2.2 Homogenization and omitted detail

State constituents, density, normalization targets, preserved quantities and
observable-dependent validation for each effective representation.

## 9. Detector specification and software implementation

Lead: `SoftEng`; design consistency: `SysArch` and subsystem owners.

### 9.1 Specification and generation contract

#### 9.1.1 Parameter schema, provenance and component hierarchy

Define the selected specification interface once reviewed; keep unselected
schema/generation choices visible as open decisions.

#### 9.1.2 DD4hep construction and deterministic generation

Document reusable factories, XML, sensitive/passive separation, generation
ownership and checks against signed-off designs.

### 9.2 Supported environments and interfaces

#### 9.2.1 Versions, builds and node-dependent capabilities

Record tool/package/data identities, build recipes and runtime versus source
availability. A local dependency smoke test is not full-detector validation.

#### 9.2.2 ACTS and other reconstruction interfaces

Describe geometry conversion, surfaces/layers, material/field providers and
navigation checks; distinguish prototype binding probes from production support.

## 10. Simulation, response, digitization and reconstruction

Lead: `SoftEng`; physical response inputs: subsystem owners; review: `PhysVal`.

### 10.1 Progressively detailed simulation

#### 10.1.1 Parametric estimates and ACTS studies

State estimator validity, analytic controls, surface approximations, sampling and
what each stage can establish before full simulation becomes available.

#### 10.1.2 DD4hep/Geant4 transport and sensitive response

Record physics configuration, cuts, field transport, hit formation, input samples,
seeds and the tested detector/backend versions.

### 10.2 Measurement and reconstruction assumptions

#### 10.2.1 Digitization, calibration, inefficiency and timing

Describe noise, thresholds, response models, occupancy, ageing and operating
conditions only to the extent supported by the intended claims.

#### 10.2.2 Tracking, calorimetry, muons and combined reconstruction

Separate truth-seeded studies from pattern recognition and integrated object
reconstruction; state algorithm configurations and truth/selection definitions.

## 11. Geometry, material and performance validation

Lead: `PhysVal`; execution/evidence retention: `SoftEng`; input owners as relevant.

### 11.1 Geometry and physical consistency

#### 11.1.1 Construction, overlaps, counts, identifiers and transforms

Present actual checks, tolerances, failures and dispositions against reviewed
requirements and configurations.

#### 11.1.2 Directional material, fields and sensitive crossings

Show subsystem contributions, sampling/convergence, eta/phi dependence, beamspot
effects and distinctions between host-envelope reach and active acceptance.

### 11.2 Subsystem and integrated performance

#### 11.2.1 Tracking, timing, calorimeter and muon observables

Report only supported resolutions, efficiencies, fake rates, response and
uncertainties with explicit selections and reviewed criteria.

#### 11.2.2 Combined observables and computational behavior

Evaluate cross-system effects, intended physics benchmarks, runtime and memory
where measured; document absent workflows instead of filling plots by assumption.

## 12. ODD comparison, uncertainties and engineering limits

Lead: `PhysVal`; baseline identity: `SoftEng`; physical interpretation: `SysArch`.

### 12.1 Controlled comparisons

#### 12.1.1 Matched configurations and attribution of changes

Record what is held fixed and what differs in geometry, material, field, response
and reconstruction; preserve rejected hypotheses and independent controls.

#### 12.1.2 Statistical and systematic uncertainty

Separate sampling error, model assumptions, missing inputs and sensitivity to
plausible alternatives. Explain improvements and degradations physically.

### 12.2 Scope of conclusions

#### 12.2.1 Supported applications and unsupported extrapolations

Tie headline claims to actual evidence and operating ranges.

#### 12.2.2 Deferred engineering and unresolved risks

Retain missing design inputs, review conditions and future tests, with owners and
effects on conclusions; avoid implying complete buildability certification.

## 13. Reproducible release and outlook

Lead: `SoftEng` and `PubDoc`; priorities/acceptance routing: `ProRes`.

### 13.1 Release identity and reproduction

#### 13.1.1 Detector, report, environment and artifact manifests

Provide exact parent/TDR revisions, configuration hashes, source/data identities,
commands, retained artifacts and instructions for recreating figures/tables.

#### 13.1.2 Independent reproduction and release limitations

Record who checked which supported environment, actual outcomes and outstanding
conditions; keep human acceptance distinct from successful builds.

### 13.2 Conclusions and future work

#### 13.2.1 Evidence-backed conclusions

Answer the chapter 2 use cases within the reviewed scope and uncertainty.

#### 13.2.2 Prioritized extensions and publication metadata

List deferred capabilities, future comparison needs, citation/license information
and approved naming once decided; publication requires separate human authorization.

## Appendices

| Appendix | Contents | Lead |
| --- | --- | --- |
| A | Component and parameter ledger; units, provenance, uncertainty, design and approval references | `SysArch` + subsystem owners |
| B | Public source catalogue, precise locators, reading/verification state and bibliography | `PubDoc` |
| C | Requirement-to-validation matrix, configurations, seeds, commands, tolerances and artifact checksums | `PhysVal` + `SoftEng` |
| D | Interface, readout/identifier and effective-material contracts | `SysArch` + `SoftEng` |
| E | Exact-revision review history, conditions, alternatives and supersession map | `PubDoc` + `ProRes` |
| F | Environment/release manifests, glossary and reproducible figure/table recipes | `SoftEng` + `PubDoc` |

## Common subsystem content contract

Chapters 4–8 use the same evidence progression within the sections above:
requirements and interfaces; public technology evidence and alternatives;
materials/primitive elements; sensor/readout; representative assembly; local
supports/services; repeated structures; system integration; response assumptions;
validation; limitations and pending decisions. The structure follows the
repository's component-to-system implementation hierarchy without implying all
steps have been executed.

Every subsystem draft includes a parameter/provenance table, an interface table,
an explicit/effective/omitted-material account, a requirements/evidence table and
an open-input table. Proposed drawings carry draft labels. Generated plots and
tables identify input configurations, code/tool versions, commands and artifacts.
Unavailable evidence is written as an open item, never an invented result.

## Chapter and claim coverage at intake

This is a coverage index, not a declaration that the indexed claims are proved.
It describes the intake revisions above. Each later quantitative claim needs its
own source locator or calculation/validation artifact and exact configuration;
the row identifiers provide stable starting references for that ledger.

| Coverage ID / chapters | Claim family and available evidence | Recorded maturity / missing input | Input owner |
| --- | --- | --- | --- |
| PUB-C01 / 1, 13 | [Project objectives](../../PROJECT.md), [development programme](../DEVELOPMENT_PLAN.md) | Human-directed scope and stage-B progression; final naming, authorship and release acceptance pending | `ProRes`, `PubDoc` |
| PUB-C02 / 1, 12 | [ODD realism assessment](../validation/ODD-realism-assessment.md), [static inventory](../validation/odd-realism-evidence.json), [ADR-001](../decisions/ADR-001-upstream-baseline.md) | Assessment and ADR DRAFT; source inspection is not full simulation; approved comparison configuration still needed | `SoftEng`, `PhysVal` |
| PUB-C03 / 2, 4, 8 | [DES-003 E1-R2](../design/DES-003-global-envelopes.md), [envelopes](../design/DES-003-envelopes.json), [ADR-006](../decisions/ADR-006-global-envelope-and-field-hypotheses.md), [review register](../../project/reviews.json) | DES/ADR remain DRAFT; recorded envelope baseline review has bounded scope, not complete engineering or performance acceptance | `SysArch` + subsystem owners |
| PUB-C04 / 2, 5, 10–12 | [DES-005](../design/DES-005-tracker-system-plan.md) and its four role inputs | DRAFT staged programme; fixed system coverage direction, but no selected layer layout, agreed beamspot distribution or complete numerical performance criteria | `SysArch`, `TrackTech`, `PhysVal`, `SoftEng` |
| PUB-C05 / 5.2 | DES-001: [pinned pixel draft linked by DES-005](https://github.com/asalzburger/nodd/blob/d237f146b578915cc032b30efa50044cf6344d5f/docs/design/DES-001-rd53-pixel-modules.md), [issue #7](https://github.com/asalzburger/nodd/issues/7), [PR #8](https://github.com/asalzburger/nodd/pull/8) | Separate DRAFT input; not present in the parent intake tree. Reconcile its next consumed revision. Bare module material is not the complete installed layer budget | `TrackTech` |
| PUB-C06 / 4.2, 7.2 | DES-004: [pinned magnetic draft linked by DES-005](https://github.com/asalzburger/nodd/blob/040337c2d6129014655a7534e0ea79c6ef693bc2/docs/design/DES-004-magnetic-configurations.md), [PR #6](https://github.com/asalzburger/nodd/pull/6), [muon-field issue #9](https://github.com/asalzburger/nodd/issues/9) | Separate DRAFT input; not present in the parent intake tree. Candidate fields, engineering and standalone/combined evidence must be assessed separately | `SysArch`, `MuonTech`, `PhysVal` |
| PUB-C07 / 5.3–5.4 | [Tracker technology input](../design/inputs/DES-005-tracker-system-tracktech.md) | Planning constraints; complete short-strip, long-strip and timing component designs and validated response are missing | `TrackTech` |
| PUB-C08 / 6 | [Calorimeter envelope input](../design/inputs/DES-003-calorimeter-envelope-input.md), [review input](../design/inputs/DES-003-calorimeter-review-1.md) | Envelope/design study inputs, not a signed-off assembly or validated calorimeter response; technology/service/performance details remain | `CaloTech`, `PhysVal` |
| PUB-C09 / 7 | [Muon envelope input](../design/inputs/DES-003-muon-envelope-input.md), [review input](../design/inputs/DES-003-muon-review-1.md) | Envelope/design study inputs; chamber/station response, detailed backgrounds and field-dependent performance remain | `MuonTech`, `SysArch`, `PhysVal` |
| PUB-C10 / 4.1, 8 | [System architecture input](../design/inputs/DES-003-system-architecture-input.md), [solenoid space budget](../design/inputs/DES-003-solenoid-space-budget.md) | Provisional allocations; engineered beam pipe, supports, routing and aggregate load/material budgets incomplete | `SysArch` + subsystem owners |
| PUB-C11 / 3, 9 | [PROJECT generation proposal](../../PROJECT.md#detector-specification-and-code-generation), [DES-005 software input](../design/inputs/DES-005-tracker-system-softeng.md) | Proposed contracts; generator/schema and complete production geometry/conversion not selected or validated here | `SoftEng` |
| PUB-C12 / 9.2, 13 | [ACTS Spack workflow evidence](../../skills/acts-spack/references/workflow.md), [node registry](../../skills/acts-spack/references/nodes.json) | Local dependency/runtime/build checks recorded on one node; full source trees unavailable, portable complete detector simulation unproved | `SoftEng` |
| PUB-C13 / 10–11 | [M0 baseline specification](../validation/M0-baseline-specification.md), [ADR-003](../decisions/ADR-003-validation-and-artifact-policy.md), [DES-003 diagnostics](../validation/DES-003-envelope-diagnostics.json) | DRAFT validation contract plus bounded envelope diagnostics; these do not establish sensitive crossings, full transport or integrated physics performance | `PhysVal`, `SoftEng` |
| PUB-C14 / 3, appendices | [Source catalogue](../../reference/manifest.yaml), [reading coverage](../validation/literature-coverage.md), [ADR register](../decisions/README.md) | Catalogue/selected reading evidence exists; source presence is not verification of every parameter. ADR-001–006 remain DRAFT | `PubDoc`, claim authors |
| PUB-C15 / 3, 13, appendix E | [ADR-002](../decisions/ADR-002-review-and-signoff-policy.md), [review register](../../project/reviews.json), [human review guide](../../REVIEW.md) | Final authority `asalzburger-review` assigned; exact scope/revision approvals and outstanding expert assignments remain explicit | `ProRes`, `PubDoc` |

Evidence on separate proposal branches is an intake dependency, not silently
part of this report's reviewed configuration. PubDoc must refresh those snapshots
when consuming the work and preserve their draft/prototype status. Additional
software or layout studies enter the relevant rows only after their versions,
scope and actual checks have been reconciled.
