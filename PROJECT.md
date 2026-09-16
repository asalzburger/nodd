# nODD Project

## Project statement

**nODD** develops a more realistic, auditable, and publicly reproducible evolution of the OpenDataDetector (ODD). It retains ODD's value as an experiment-independent detector for full simulation and reconstruction studies with a coherent full-detector design: tracking, timing, electromagnetic and hadronic calorimetry, muon detection, magnets, supports, services, and the interfaces between them.

The intended result is not an ATLAS or CMS replica. It is a plausible open reference detector whose important choices can be traced to public evidence, explicit inference, or a documented nODD design decision and whose components are reviewed and signed off by relevant human experts.

## Current work

On 2026-09-16 the user directed that development-plan stage A be considered done,
using the established ODD/ColliderML baseline, and authorized stage B: coherent
full-detector architecture. See the [progression record and role proposal](docs/DEVELOPMENT_PLAN.md).
This moves architecture work forward without claiming that previously unexecuted
local checks passed or changing design/ADR sign-off states. Exact comparison
configuration provenance remains a software responsibility before it is used.

## Objectives and intended successor

The human-directed objective is to evolve ODD into a **new DD4hep-based detector**
through justified modification, replacement or rewriting of its components and
implementation. ODD is the starting point and retained comparison baseline, not
an immutable geometry or code architecture.

The result should remain a recognizable successor in the **TrackML → ODD → nODD**
chain: a public, experiment-independent detector for reproducible simulation,
reconstruction and algorithm research, with an ODD-like overall detector concept.
Continuity concerns its role and broad features; individual dimensions,
materials, technologies, factories and interfaces may change through reviewed
designs. Every retained component needs justification as well as every new one.

Every subsystem must receive credible technical foundations: sensors and active
media, readout electronics, modules/chambers/calorimeter assemblies, supports,
cooling, power, cables and routing, magnets/fields, and their shared interfaces.
An RD53-class chip and pixel module are the first example of this method, not the
project's sole realism target.

The theme is **a detector that could plausibly have been built**, assessed through
its physical consistency, simulation and performance. At this stage this means
credible component usage, space/material/service accounting and explicit operating
assumptions. It does not certify complete technical buildability, manufacturing,
structural or thermal engineering, installation procedures, or CAD-level design.
Unverified engineering assumptions must remain visible in the final results.

The final deliverable includes a **Technical Design Report (TDR)** describing the
whole detector, evidence and decisions, implementation, validation, performance,
approximations and unresolved engineering questions. Its chapters should develop
alongside the designs and simulations and be finalized against a reproducible
release. **nODD is a working title**; final detector and TDR naming will be decided
later without changing stable source/design identifiers.

The [development plan](docs/DEVELOPMENT_PLAN.md) translates these objectives into
work packages, review gates, subsystem priorities and proposed specialist-agent
roles. Its scheduling and technical proposals remain subject to review.

## Motivation

ODD evolved beyond the simplified TrackML detector by using a DD4hep-based full-simulation description. The [full-detector realism assessment](docs/validation/ODD-realism-assessment.md) identifies substantial existing tracker, calorimeter and muon structure, alongside gaps in component provenance, material/service accounting, magnet integration, precision timing and validated operating response. Its usefulness as an HL-LHC reference must be established per observable and configuration; source inspection alone does not establish quantitative accuracy.

nODD will assess and address these gaps across the whole detector, using the selected upstream baseline to establish what is already represented and what needs improvement. The objective is realistic use of components in a detector at simulation-relevant accuracy. CAD fidelity, manufacturing drawings and construction-ready engineering are not project deliverables.

The intended output is a reviewed detector specification that supports automatic generation of reusable DD4hep C++ factories and compact XML, followed by quantitative Geant4 and reconstruction validation. The generator architecture and numerical accuracy targets remain to be discussed and approved. Public evidence, documented approximations and human review govern both the specification and its implementation.

## Full-detector scope

The programme covers the following systems as parts of a common detector design.
Their technologies, dimensions and performance targets remain subject to evidence,
design review and sign-off; this scope does not select an experiment's layout.

| System | Design scope |
| --- | --- |
| Interaction region | Beam pipe, nearby passive material, apertures, forward clearances and shielding where relevant to transport and backgrounds |
| Inner tracking | Pixel, strip and other reviewed tracking technologies; sensors, readout, modules, repeated structures, barrel/endcap layout and acceptance |
| Timing | Dedicated timing layers or subsystems, placement and coverage, sensor/module construction, services and response assumptions |
| Electromagnetic calorimetry | Technology and absorber/active medium, cells or sampling layers, segmentation, modules, barrel/endcap transitions and readout representation |
| Hadronic calorimetry | Absorber/active medium, sampling structure, depth, segmentation, modules, containment, dead regions and interfaces |
| Muon system | Detection technology, chamber or module construction, station layout, readout segmentation, acceptance and integration with magnet/yoke structures |
| Magnets and return structures | Coils, cryostats, return yokes and their passive material; field definitions/maps and consistency between simulation and reconstruction |
| Common mechanics and services | Supports, mounting, cooling, power, data, gas where applicable, service corridors and transitions between subsystems |
| Integrated detector | Shared envelopes, clearances, segmentation/identifier conventions, material accounting, sensitive behavior and reconstruction interfaces |

An RD53-class pixel-module vertical slice remains the first concrete component
case for developing the workflow. It is one representative application of a
method that must also accommodate calorimeter sampling assemblies, muon chambers
and passive structures. It does not define the limits of the project or settle
the full-detector architecture.

Out of scope unless explicitly added through a reviewed design decision:

- exact reproduction of ATLAS, CMS or another experiment;
- manufacturing tolerances, transistor-level electronics and CAD detail without simulation relevance;
- confidential information as the sole normative basis of a public specification;
- accelerator design, civil engineering and complete facility systems beyond detector interfaces needed for simulation;
- production-quality digitization, trigger/DAQ emulation or full reconstruction for every technology in the first milestones;
- performance tuning without a reviewed physical rationale.

During M0, work remains limited to governance, literature, baseline
characterization and reproducible infrastructure. Expanding the programme does
not authorize production detector changes before design sign-off.

## Definition of realism

Realism is assessed independently across these dimensions:

| Dimension | Project expectation |
| --- | --- |
| Active elements | Credible silicon sensors, scintillators, gas gaps or other reviewed media, with dimensions and sensitive response appropriate to their use |
| Readout | Physical footprint, placement, segmentation, channel mapping and power class; electronics detail only where it affects simulation or integration |
| Assemblies | Tracker/timing modules, calorimeter cells or sampling assemblies, and muon chambers, including relevant interfaces and passive layers |
| Calorimetry | Absorber/active fractions, longitudinal and transverse segmentation, depth, cracks, dead material and shower-containment implications |
| Muon detection | Station/chamber geometry, active gaps, passive walls, segmentation and trajectories through intervening material and fields |
| Magnets and fields | Coils, cryostats and yokes represented consistently with the chosen field model and subsystem layout |
| Mechanics | Credible support cylinders, staves, disks, frames, calorimeter housings, chamber supports and shared load-bearing structures at simulation-relevant detail |
| Thermal and fluids | Cooling routes, coolant, thermal interfaces and relevant gas/fluid volumes; operating assumptions that constrain component placement and services |
| Power and data | Physically credible distribution, cables, fibres, connectors and service transitions, including documented effective representations |
| Layout and interfaces | Intentional envelopes, barrel/endcap topology, orientations, overlaps, clearances, cracks, transitions and service corridors |
| Acceptance | Quantified tracking/timing/muon coverage and calorimeter angular coverage, with explicit definitions of gaps and dead regions |
| Timing | Physical sensor and assembly geometry with explicit timing-response assumptions |
| Material | Reproducible composition, density, mass, radiation-length and interaction-length distributions across the detector |
| Simulation | Repeatable DD4hep/Geant4 transport and sensitive-hit behavior, with response/digitization assumptions stated separately |
| Reconstruction | ACTS-compatible tracking geometry and material/navigation interfaces where applicable; explicit calorimeter, timing and muon hit/cell interfaces for the selected downstream tools |

A detail is modeled explicitly when it materially affects geometry, clearance, material, services, thermal/electrical architecture, sensitive response, reconstruction, or validation. Otherwise it may be omitted or represented effectively, with the approximation documented. For example, a service bundle may use an envelope and effective composition when the relevant material distribution is preserved; calorimeter sampling layers may need explicit treatment to preserve shower development. The required fidelity is decided per physical observable, not by a uniform level of geometric detail.

“Good accuracy” must become measurable criteria for each component and the integrated detector. Geometry construction success alone does not establish adequate material, acceptance or response. Accuracy targets and uncertainties must be agreed before acceptance; no numerical tolerances are selected by this project statement.

## Guiding principles

1. **Repository as source of truth.** Designs, decisions, implementations, validation evidence, and sign-offs live in version control.
2. **Public provenance.** Normative choices should be defensible from public sources.
3. **Facts are not choices.** Every important claim is labeled as a sourced fact, an inference, or an nODD design choice.
4. **Design before production code.** Significant detector choices are reviewed before integration.
5. **Human authority.** AI assists research and implementation but cannot sign off a design.
6. **Representative components within a coherent architecture.** Establish shared detector interfaces early, then prove the workflow on small assemblies for each subsystem before scaling to full integration.
7. **Quantitative validation.** Geometry, material, fields, acceptance, identifiers, transport, response and reconstruction interfaces are tested against explicit criteria.
8. **Minimal faithful complexity.** Include engineering detail that changes relevant physics or software behavior; omit decorative complexity.
9. **Reproducibility.** Record versions, configurations, seeds, commands, tolerances, and reference data.
10. **Traceable change.** Intentional deviations from accepted baselines require a reviewed design amendment or ADR.

## Provenance model

Every important parameter or design statement uses one of three labels:

- **FACT:** directly supported by a public reference, with a precise locator.
- **INFERENCE:** derived from documented facts and assumptions, including uncertainty.
- **NODD DESIGN CHOICE:** selected by the project after considering alternatives and consequences.

The source catalogue is `reference/manifest.yaml`. Large PDFs are stored locally in an ignored directory and represented in the catalogue by stable identifiers, public links, metadata, and checksums.

Public ATLAS and CMS designs provide important technology and engineering evidence. Current production and integration publications may supersede or refine older TDR-era information. Source dates and versions therefore matter: a TDR is a major reference, not an eternal monolithic specification.

## Component hierarchy

The working hierarchy spans all detector technologies:

1. material definitions and physical operating assumptions;
2. primitive active/passive elements: sensors, absorbers, scintillator tiles, gas gaps, conductors and structural layers;
3. readout, segmentation, identifiers and local interfaces;
4. representative assemblies: tracker/timing modules, calorimeter sampling units or crystals, muon chambers, coil/yoke elements;
5. local support, cooling, power, data and other relevant services;
6. repeated structures: staves, rings, disks, calorimeter towers/sectors, chamber stations and support frames;
7. complete subsystems and their envelopes;
8. integration of tracking, timing, calorimetry, magnets, muons and shared services;
9. full-detector simulation and downstream reconstruction/validation.

Each level should be independently constructible and testable where practical.
Top-level envelope, field and service-interface requirements must constrain local
assemblies from the start; component development and system design inform each other.

## Detector specification and code generation

The intended workflow is:

`Public evidence -> reviewed detector specification -> generated DD4hep factories and XML -> Geant4 and reconstruction validation`

The specification should capture component composition, parameters and units,
placement/repetition, materials, sensitive regions, readout/identifiers, field
references, interfaces, provenance and explicit approximations. Generation should
preserve traceability to the reviewed inputs, be deterministic and record its
version and configuration. Generated output must remain inspectable and testable.

The schema, parameter language, template strategy, ownership of generated versus
handwritten code, and regeneration/review workflow are open design decisions.
Automatic generation does not replace scientific review or authorize unsigned
geometry. Validation must check the resulting physical detector as well as the
consistency of generated code with its input specification.

## Design lifecycle and states

| State | Meaning | Exit authority |
| --- | --- | --- |
| `DRAFT` | Proposal is being assembled; claims and open questions may be incomplete | Author |
| `TECHNICAL REVIEW` | Structure, feasibility, interfaces, provenance, and validation plan are reviewed | Assigned technical reviewer |
| `EXPERT REVIEW` | Domain experts assess physics and engineering credibility | Named expert reviewer(s) |
| `SIGNED OFF` | Design is authorized for production implementation | Named human approver(s) |
| `IMPLEMENTED` | Signed-off design is represented in code with required tests | Maintainer after PR review |
| `VALIDATED` | Acceptance criteria have been exercised and evidence recorded | Validation reviewer |
| `ACCEPTED` | Component or subsystem is approved as part of the maintained detector baseline | Project maintainer/board |

Design approval and production implementation normally use separate pull requests. Prototype work may precede sign-off only when explicitly labeled, isolated from the production configuration, and linked to its open design questions.

## Project artifacts

The planned repository structure is:

```text
AGENTS.md
PROJECT.md
README.md
docs/
  charter/
    REALISM_CHARTER.md
  design/
    TEMPLATE.md
    DES-NNN-short-name.md
  decisions/
    README.md
    ADR-NNN-short-name.md
  signoff/
    TEMPLATE.md
    DES-NNN-signoff.md
  validation/
reference/
  manifest.yaml
  pdfs/                    # local only; ignored by Git
components/
  pixel/
  strip/
  supports/
  services/
  timing/
  calorimeter/
  muon/
  magnets/
  interaction_region/
xml/
factory/
validation/
  geometry/
  material/
  acceptance/
  simulation/
  response/
  fields/
  acts/
  reference/
tools/
  detector_summary/
  material_scan/
  session_logging/
  reference_reading/
  generation/              # future; architecture to be agreed
logs/
  design/
  codex/
```

This is an intended structure, not a requirement to create empty directories. Add directories with the work that needs them and adapt names through an ADR if the imported ODD codebase requires a different layout.

## Design document expectations

Each `DES-*` proposal should be concise and reviewable, normally containing:

- metadata and status;
- scope and exclusions;
- requirements and acceptance criteria;
- source material;
- sourced facts;
- inferences and uncertainties;
- proposed nODD choices;
- dimensions, materials, interfaces, and identifiers;
- material-budget, acceptance, field and response implications as applicable;
- subsystem envelope, service and reconstruction interfaces;
- explicit/effective representations and the physical quantities they preserve;
- specification-to-code mapping and generation provenance when used;
- alternatives considered;
- risks and open questions;
- validation plan;
- named reviewers;
- links to sign-off, implementation PR, and validation evidence.

Cross-cutting decisions use `ADR-*` records containing context, options, decision, consequences, evidence, status, and approvers.

## Review and sign-off model

GitHub issues and pull requests are the initial review platform. A GitHub Project may provide the component dashboard. Repository rules and `CODEOWNERS` should require appropriate reviews for governed paths.

A sign-off record must identify:

- the exact design document commit or immutable version reviewed;
- reviewer name and role or expertise;
- review date;
- outcome and conditions;
- unresolved reservations;
- approval evidence, normally the linked pull-request review;
- later superseding decision, if any.

AI-generated approval text is not human sign-off. A merged document is not automatically signed off unless the required state and human approval record are present.

## Validation programme

### Baseline characterization

Before changing the imported detector, produce a reproducible ODD baseline containing:

- detector build and overlap results;
- `r-z` and transverse layout views;
- volume, placement, assembly, sensitive-element and readout-cell counts by subsystem;
- active area/volume, subsystem extents, barrel/endcap transitions and shared clearances;
- crossings and coverage versus `eta` and `phi`;
- material scans in `X/X0` and interaction lengths;
- subsystem masses and material composition where extractable;
- segmentation and identifier summaries;
- field configuration, magnet/yoke representation and transport/reconstruction consistency;
- Geant4 smoke tests and sensitive-hit output by subsystem;
- ACTS tracking conversion, navigation and material-mapping checks where applicable, plus the selected interfaces for other subsystems;
- representative single-particle metrics for tracking, calorimetry, timing and muons where feasible, separating transport, sensitive response, digitization and reconstruction assumptions.

The baseline must inventory all available upstream subsystems, including missing or provisional representations and untested interfaces. Mark inapplicable or unavailable checks with reasons; a tracker-only report cannot establish a full-detector baseline.

The baseline must record the upstream ODD revision and all relevant tool versions and configurations. It is a regression reference, not an immutable performance target.

### Component and integration gates

Every component or subsystem defines quantitative acceptance criteria in its design document. Relevant gates include:

- construction success;
- overlap tolerance;
- count and transform correctness;
- dimensional agreement;
- material and mass agreement;
- acceptance and crossings;
- identifier stability;
- Geant4 execution;
- field configuration and consistency across transport/reconstruction;
- calorimeter sampling/material structure, energy-deposition profiles, containment and leakage where relevant;
- muon active-gap crossings, station coverage and response assumptions;
- timing response assumptions and coverage;
- ACTS conversion/navigation where applicable and other selected hit/cell interfaces;
- specification-to-generated-output consistency and reproducibility;
- comparison with approved reference outputs.

Subsystem checks must include relevant interfaces: material before and between calorimeters, services passing through neighboring systems, muon trajectories through yokes, and field boundaries. Performance metrics such as energy or timing resolution require an explicit response/digitization model; geometry alone does not establish them.

Reference results may change only with an explained, reviewed, and traceable design change.

## Milestones

### M0 — Baseline and governance

- Establish repository instructions and project charter.
- Add design, ADR, validation, and sign-off templates.
- Establish the public source catalogue and local-PDF policy.
- Import or pin the selected ODD baseline.
- Build baseline characterization tools and CI entry points.
- Produce and review the initial geometry, material, acceptance, and conversion report.
- Configure issue/PR templates, `CODEOWNERS`, branch rules, and project tracking.
- Tag the reproducible upstream baseline.

**Constraint:** no production detector design changes during M0.

### M1 — Full-detector architecture and first component case

- Define detector-wide requirements, coverage, subsystem roles and envelope/interface constraints.
- Compare coherent technology and magnet-layout options using public references.
- Draft shared material, identifier, field and service conventions.
- Use the RD53-class pixel module as the first component case: proposed `DES-001` for module/readout and `DES-002` for local support/cooling.
- Develop a reviewed specification-to-code workflow; generator architecture remains an explicit decision.
- Obtain the required review/sign-off before production implementation; isolate any authorized unsigned prototypes.

### M2 — Representative subsystem assemblies

- Exercise the same evidence, specification, implementation and validation workflow on tracker/timing modules, calorimeter assemblies and muon chambers.
- Include realistic local supports and services and document effective material choices.
- Demonstrate reusable DD4hep factory/XML generation against reviewed input when the generation approach is approved.
- Validate each representative assembly before scaling to a subsystem.

### M3 — Tracking and timing systems

- Define pixel and outer-tracker families, technologies, layouts and barrel/forward coverage.
- Define timing technology, location, segmentation and response assumptions through reviewed choices.
- Integrate reviewed modules, repeated structures, supports and services within shared detector envelopes.
- Validate material, acceptance, timing assumptions and tracking/reconstruction interfaces.

### M4 — Electromagnetic and hadronic calorimetry

- Select technology, absorber/active structure, segmentation, depth and barrel/endcap organization through review.
- Integrate readout representation, housings, supports, services, cracks and transition regions.
- Validate geometry/material, sensitive cells and shower-development/containment observables with explicit simulation settings.
- Define downstream cell/hit interfaces and any digitization assumptions needed for the chosen validation scope.

### M5 — Muon system and magnet integration

- Select chamber technologies, station layout, acceptance, segmentation and local services through review.
- Implement reviewed coil, cryostat, return-yoke and shielding representations as needed by the common architecture.
- Validate station coverage, material, field consistency and representative muon transport/response.
- Check interfaces to calorimeters, supports and service routes.

### M6 — Full-detector integration

- Assemble reviewed tracking, timing, calorimeter, muon, magnet and interaction-region descriptions.
- Validate shared envelopes, clearances, field boundaries, service routes and material accounting without omissions or double counting.
- Exercise the selected Geant4 and downstream reconstruction chain across subsystem boundaries.
- Review differences from the upstream baseline and establish explained regression references.

### M7 — Detector validation and release

- Complete the agreed geometry, material, field, acceptance, response and reconstruction checks.
- Verify repeatable generation/builds from reviewed specifications and retained tool/input versions.
- Finalize and publish the whole-detector TDR, evidence, known approximations, applicability limits and release documentation against the reproducible release; agree the final detector name.
- Obtain identified human acceptance for the maintained full-detector baseline.

This roadmap supersedes the earlier tracker-centred M1–M6 outline. Milestones
after M0 are provisional planning stages, not approvals or rigid serial scheduling.
Calorimeter, muon and magnet requirements enter architecture work in M1 even if
implementation follows later. Existing design/source IDs retain their meanings.

## Initial literature set

The initial source catalogue should include at least:

| Topic | Core document |
| --- | --- |
| Whole-detector context | ATLAS and CMS 2008 JINST overviews, `SRC-ATLAS-JINST-2008` and `SRC-CMS-JINST-2008`, read alongside later upgrades |
| ATLAS calorimeters | LAr Phase-II TDR `ATLAS-TDR-027`; Tile Phase-II TDR `ATLAS-TDR-028` |
| CMS calorimeters | Barrel Phase-2 TDR `CMS-TDR-015`; endcap Phase-2 TDR `CMS-TDR-019` |
| Muon systems | ATLAS Phase-II TDR `ATLAS-TDR-026`; CMS Phase-2 TDR `CMS-TDR-016` |
| Magnets and common interfaces | Whole-detector descriptions and relevant public subsystem/construction references; catalogue additional sources as needed |
| ATLAS pixels | ITk Pixel TDR, `CERN-LHCC-2017-021` / `ATLAS-TDR-030` |
| ATLAS strips | ITk Strip TDR, `CERN-LHCC-2017-005` / `ATLAS-TDR-025` |
| CMS tracker | Phase-2 Tracker TDR, `CERN-LHCC-2017-009` / `CMS-TDR-014` |
| ATLAS timing | HGTD TDR, `CERN-LHCC-2020-007` / `ATLAS-TDR-031` |
| CMS timing | MTD TDR, `CERN-LHCC-2019-003` / `CMS-TDR-020` |
| Pixel readout | RD53A manual, `CERN-RD53-PUB-17-001`, plus later public ITkPixV2/CROC production material |
| Framework and simulation | DD4hep/DDG4/DDRec and Geant4 documentation matched to the selected versions |
| Reconstruction | ACTS documentation and ODD integration material, plus interfaces for selected calorimeter/timing/muon workflows |
| Baseline | OpenDataDetector repository, documentation, publications, and pinned revision |
| Historical basis | TrackML detector and dataset publications |

The [source catalogue](reference/manifest.yaml), [reading guides](reference/guides/README.md) and [ODD resource register](reference/guides/ODD-resources.md) record availability and verification state. A listed source is not proof of a verified parameter.

Later production, qualification, and integration papers should be added component by component. When later evidence supersedes a TDR value, record both and explain which version governs nODD.

## Roles

A person may hold several roles, but the action should remain explicit:

- **Design author:** assembles evidence and proposes the design.
- **Technical reviewer:** checks interfaces, feasibility, reproducibility, and implementation readiness.
- **Domain expert:** evaluates relevant sensor, electronics, mechanics, thermal, services, simulation, or reconstruction assumptions.
- **Approver:** records human authorization to implement or accept the design.
- **Implementer:** writes the DD4hep/software changes and tests.
- **Validation reviewer:** assesses whether acceptance criteria and regression evidence are sufficient.
- **Maintainer:** merges changes and protects the accepted baseline.

Codex and other AI agents are assistants, not approvers.

## ChatGPT, Codex CLI, and Git synchronization

The repository synchronizes work between human discussions, ChatGPT, local Codex, and GitHub:

- ChatGPT supports literature review, design exploration, proposal drafting, and review preparation.
- Codex CLI inspects the local repository, implements scoped work, runs tools and tests, and prepares commits or pull requests.
- GitHub carries the canonical documents, issues, reviews, sign-offs, code, validation evidence, and history.
- `AGENTS.md`, `PROJECT.md`, accepted `DES-*`/`ADR-*` records, and issues provide durable context. Do not depend on either AI client seeing the other client's conversation history.
- Begin each new AI session by reading the repository instructions and current issue/design documents.
- End significant sessions by committing or proposing durable updates and, when useful, adding a curated session record.

## Session and token logging

Ongoing curated logging is enabled at the user's request. See the
[session journal and commands](logs/README.md) and
[ADR-004 draft](docs/decisions/ADR-004-session-logging-and-traceability.md).
The implementation records available evidence and explicitly reports missing
usage data; it does not automatically capture every interactive client event.

For auditable AI-assisted work, store curated records rather than raw private transcripts or rollout files. A record may include:

- date, client, model, and session identifier where exposed;
- task and linked issue/design IDs;
- branch and commit SHA;
- user-visible prompts and responses selected for project relevance;
- commands and tool actions;
- files changed;
- decisions, assumptions, and unresolved questions;
- tests and validation results;
- exact input/output/cached/reasoning/total token counts only when exposed by the client.

Never estimate token counts and present them as exact. Remove secrets, personal data, private URLs, confidential collaboration content, and irrelevant system context before committing a record.

## Initial decisions still required

The following should be resolved during M0/M1 through design proposals or ADRs:

- upstream ODD version and import strategy: fork, subtree, submodule, or curated import;
- naming and versioning policy for nODD releases;
- physics/use-case requirements and coverage for tracking, timing, calorimetry and muons;
- subsystem technologies, envelopes, barrel/endcap transitions and shared service routes;
- magnet/return-yoke concept, field representation and transport/reconstruction consistency;
- initial pixel module family and RD53-class abstraction, and representative assemblies for other subsystems;
- calorimeter sampling/segmentation and muon chamber/station abstractions;
- detector specification schema, generation architecture and generated-code review policy;
- acceptable use and validation of effective materials;
- validation tolerances and reference-artifact storage;
- DD4hep, Geant4, ACTS and other selected downstream tools in a supported-version matrix;
- response/digitization scope and measurable accuracy criteria for each subsystem and their interfaces;
- expert-reviewer map and minimum sign-off requirements;
- public licensing and citation policy;
- CI platform, storage limits, and handling of large validation outputs.

## Immediate next steps

1. Review this full-detector scope and assign subsystem/interface reviewers.
2. Continue mapping the public literature and pinned ODD study source across all subsystems.
3. Choose and record the actual upstream baseline, entry points, required assets and supported environment through ADR-001/003.
4. Refine the M0 baseline specification for the selected full detector, with explicit applicability and missing checks.
5. Implement and run baseline characterization without changing detector geometry.
6. Review baseline evidence and complete M0 governance before advancing the milestone.
7. Draft the full-detector architecture/interface requirements and first component designs; discuss the generation approach before implementing it.
