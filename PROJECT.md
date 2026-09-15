# nODD Project

## Project statement

**nODD** develops a more realistic, auditable, and publicly reproducible evolution of the OpenDataDetector (ODD). It retains ODD's value as an experiment-independent detector for full simulation and reconstruction studies while moving its tracker, timing systems, supports, services, and material description closer to credible modern collider-detector engineering.

The intended result is not an ATLAS or CMS replica. It is a plausible open reference detector whose important choices can be traced to public evidence, explicit inference, or a documented nODD design decision and whose components are reviewed and signed off by relevant human experts.

## Motivation

ODD evolved beyond the simplified TrackML detector by using a DD4hep-based full-simulation description. It remains less realistic than contemporary HL-LHC detector designs in several areas, including module construction, electronics, supports, powering, cooling, services, material distribution, global layout, and dedicated forward timing.

nODD will close those gaps without importing unnecessary CAD complexity or collaboration-confidential information. It will provide reusable DD4hep components, an evidence-backed design history, quantitative validation, and a human approval chain.

## Initial scope

The first programme focuses on:

- silicon tracking modules, beginning with a realistic RD53-class pixel-module vertical slice;
- local mechanical support;
- cooling and thermal interfaces;
- powering, data flexes, cables, connectors, and service routing;
- realistic material definitions and effective-material policies;
- barrel and forward tracker layout, including deliberate pseudorapidity coverage;
- a dedicated high-granularity forward timing subsystem based on public LGAD-era designs;
- DD4hep/Geant4 simulation compatibility;
- ACTS geometry conversion, material mapping, navigation, and reconstruction-facing validation;
- governance, provenance, expert review, and sign-off infrastructure.

Initially out of scope unless added through an accepted design decision:

- exact reproduction of ATLAS, CMS, or another experiment;
- transistor-level ASIC detail or arbitrary CAD detail with no simulation relevance;
- use of confidential collaboration information as the normative public specification;
- wholesale redesign of calorimeter or muon systems;
- production-quality digitization for every technology in the first milestones;
- performance tuning that is not grounded in a reviewed detector design.

## Definition of realism

Realism is assessed independently across these dimensions:

| Dimension | Project expectation |
| --- | --- |
| Active sensor | Credible technology, dimensions, thickness, pitch, segmentation, and sensitive response |
| Readout | Realistic ASIC footprint, thickness, material, tiling, and power class |
| Module | Sensor, ASIC, bump/interface, adhesive, flex/hybrid, passives, and mounting representation |
| Mechanics | Credible carbon structures, foams, facesheets, glues, rings, staves, disks, and fixtures |
| Thermal | Cooling pipe, plate, or channel geometry; coolant; and thermal-interface material |
| Power and data | Credible local conversion or serial-powering elements, bus tapes, cables, fibres, and connectors |
| Services | Explicit routing and transition regions with defensible effective representations |
| Layout | Intentional barrel/endcap topology, orientations, clearances, transitions, and technology regions |
| Acceptance | Quantified pseudorapidity and azimuthal coverage and sensitive measurements per trajectory |
| Timing | A physical timing subsystem with credible sensor/module geometry, not only timestamps on hits |
| Material | Reproducible mass, radiation-length, and interaction-length distributions |
| Simulation | Geometry and response compatible with repeatable DD4hep/Geant4 studies |
| Reconstruction | Stable conversion and navigation behavior in ACTS-compatible workflows |

A detail is modeled explicitly when it materially affects geometry, clearance, material, services, thermal/electrical architecture, sensitive response, reconstruction, or validation. Otherwise it may be omitted or represented effectively, with the approximation documented.

## Guiding principles

1. **Repository as source of truth.** Designs, decisions, implementations, validation evidence, and sign-offs live in version control.
2. **Public provenance.** Normative choices should be defensible from public sources.
3. **Facts are not choices.** Every important claim is labeled as a sourced fact, an inference, or an nODD design choice.
4. **Design before production code.** Significant detector choices are reviewed before integration.
5. **Human authority.** AI assists research and implementation but cannot sign off a design.
6. **Vertical slices before global redesign.** Prove the complete workflow on one pixel module before scaling it across a tracker.
7. **Quantitative validation.** Geometry, material, acceptance, identifiers, simulation, and conversion are tested against explicit criteria.
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

The working hierarchy is:

1. materials;
2. sensor and readout primitives;
3. module elements such as bumps, adhesive, flex, passives, and thermal interfaces;
4. complete module families;
5. local support, cooling, power, and data services;
6. repeated structures such as staves, rings, and disks;
7. subdetector layouts;
8. global tracker and timing integration;
9. full-detector simulation and reconstruction integration.

Each level should be independently constructible and testable where practical.

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
xml/
factory/
validation/
  geometry/
  material/
  acceptance/
  simulation/
  acts/
  reference/
tools/
  detector_summary/
  material_scan/
  session_logging/
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
- material-budget and acceptance implications;
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
- volume, placement, module, and sensitive-element counts;
- sensitive area and detector extents;
- crossings and coverage versus `eta` and `phi`;
- material scans in `X/X0` and interaction lengths;
- subsystem masses and material composition where extractable;
- segmentation and identifier summaries;
- Geant4 smoke tests;
- ACTS conversion, navigation, and material-mapping checks;
- representative single-particle or reconstruction metrics when feasible.

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
- ACTS conversion and navigation;
- comparison with approved reference outputs.

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

### M1 — Realistic pixel-module vertical slice

- `DES-001`: sensor, RD53-class readout, bump/interface, adhesive, flex/hybrid, passives, and powering assumptions.
- `DES-002`: local support, thermal interface, cooling, and mechanical attachment.
- Obtain expert review and human sign-off.
- Implement reusable DD4hep component prototypes.
- Validate a single module.
- Build and validate a small stave or ring demonstrator.
- Record material, geometry, response, and ACTS conversion evidence.

### M2 — Pixel module families and local structures

- Define credible inner/outer and barrel/forward module families.
- Implement reviewed staves, rings, disks, supports, cooling, and local services.
- Validate transitions, clearances, material, and acceptance.

### M3 — Outer tracker technology

- Compare credible strip, macro-pixel/strip, and hybrid reference concepts.
- Select technologies through a signed-off design/ADR.
- Implement and validate module families and their support/service structures.

### M4 — Global tracker layout

- Define requirements for coverage, measurement count, lever arm, occupancy, transitions, services, and material.
- Propose and review the barrel/endcap layout.
- Integrate signed-off components and validate the complete tracker.

### M5 — Forward timing

- Define coverage, sensor technology, segmentation, module construction, support, cooling, and services.
- Implement a physical high-granularity timing subsystem.
- Validate geometry, material, acceptance, timing response assumptions, and integration clearances.

### M6 — Detector-level validation and release

- Complete global geometry, material, simulation, and reconstruction-facing validation.
- Review deviations, limitations, and known approximations.
- Publish reproducible reference outputs and release documentation.
- Obtain human acceptance for the maintained detector baseline.

Milestone numbering after M1 is provisional and may be refined through project planning without weakening the design and sign-off gates.

## Initial literature set

The initial source catalogue should include at least:

| Topic | Core document |
| --- | --- |
| ATLAS pixels | ITk Pixel TDR, `CERN-LHCC-2017-021` / `ATLAS-TDR-030` |
| ATLAS strips | ITk Strip TDR, `CERN-LHCC-2017-005` / `ATLAS-TDR-025` |
| CMS tracker | Phase-2 Tracker TDR, `CERN-LHCC-2017-009` / `CMS-TDR-014` |
| ATLAS timing | HGTD TDR, `CERN-LHCC-2020-007` / `ATLAS-TDR-031` |
| CMS timing | MTD TDR, `CERN-LHCC-2019-003` / `CMS-TDR-020` |
| Pixel readout | RD53A manual, `CERN-RD53-PUB-17-001`, plus later public ITkPixV2/CROC production material |
| Framework | Current DD4hep manuals and release documentation |
| Reconstruction | Current ACTS documentation and ODD integration material |
| Baseline | OpenDataDetector repository, documentation, publications, and pinned revision |
| Historical basis | TrackML detector and dataset publications |

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
- target tracker and timing pseudorapidity coverage;
- initial pixel module family and RD53-class abstraction;
- acceptable use and validation of effective materials;
- validation tolerances and reference-artifact storage;
- DD4hep, Geant4, and ACTS supported-version matrix;
- expert-reviewer map and minimum sign-off requirements;
- public licensing and citation policy;
- CI platform, storage limits, and handling of large validation outputs.

## Immediate next steps

1. Review and approve this operating model.
2. Add the realism charter and document templates.
3. Populate `reference/manifest.yaml` with the core public literature.
4. Choose and pin the upstream ODD baseline.
5. Write the M0 baseline-characterization specification.
6. Implement baseline tooling without changing detector geometry.
7. Review the baseline report, tag M0, and begin `DES-001`.

