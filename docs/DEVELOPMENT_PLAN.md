# nODD development plan: a technically credible ODD successor

- ID: PLAN-NODD-001
- Status: DRAFT — proposed execution plan, not design sign-off
- Created: 2026-09-16
- Human owner / review issue: TBD / not created
- Governing scope: [PROJECT](../PROJECT.md), [realism charter](charter/REALISM_CHARTER.md), [AGENTS](../AGENTS.md)
- Starting evidence: [ODD assessment](validation/ODD-realism-assessment.md), [literature coverage](validation/literature-coverage.md), [reading guides](../reference/guides/README.md)
- Current work: stage B architecture planning, authorized by the user on 2026-09-16; stage A treated as complete for progression. No production detector change is authorized by this plan.

## Progression decision — 2026-09-16

The user explicitly directed: “consider A done” on the basis of ODD's established
ColliderML baseline, and requested beginning B. Stage A is therefore closed for
planning progression; repeating the baseline programme is not a prerequisite for
architecture work. This supersedes the original A-before-B work queue below.

SRC-COLLIDERML-PAPER (arXiv:2512.15230v1, abstract and §§3–5) supplies public evidence
of ODD-based full simulation, digitization and reconstruction at high pile-up;
see the [versioned paper](https://arxiv.org/html/2512.15230v1). This is external
evidence, not a claim that nODD executed the checks in the original A proposal.

Retain the historical NOT RUN records. Selecting the exact comparison release,
configuration and assets is software provenance work to complete before a
comparison depends on it, not a reason to restart A. The study checkout and the
ColliderML production configuration must not silently be treated as identical.
No ADR/DES status or scientific acceptance is advanced by this planning transition;
remaining governance items and implementation sign-off requirements still apply.

## 1. Destination and success criteria

### Human-directed objectives

Evolve ODD into a new DD4hep detector through modification, replacement or
rewriting where justified. Preserve its recognizable role and broad features
as the next step in **TrackML → ODD → nODD**, without preserving accidental
implementation details or unsupported parameters. Give every component a
credible technical basis, including electronics, supports, cooling, cable routes,
magnetic field and detector-wide interfaces. Deliver a whole-detector **TDR**.
**nODD is a working name**, to be settled with the final report/release.

The organizing question is: **could this plausibly have been a built detector,
judged from simulation and performance?** We will require plausible assembly,
material and service arrangements and explicitly bounded response assumptions.
We will not certify manufacturing readiness or complete structural, thermal,
electrical, safety, installation or CAD engineering. A geometry that loads is
not by itself a technically credible detector.

### Proposed completion contract

At project completion, each maintained subsystem should have:

1. A public evidence dossier and reviewed design, including retained ODD choices.
2. A component and effective-material inventory linked to named parameters.
3. Defined envelopes, identifiers, readout, field and service interfaces.
4. Reproducible DD4hep factories/XML and the agreed generation provenance.
5. Quantitative geometry, material, acceptance and appropriate response validation.
6. A performance/applicability statement with uncertainties and known omissions.
7. A TDR chapter tied to the same accepted detector release and evidence.

These are proposed deliverables. Numerical requirements, reviewer assignments and
acceptance remain human decisions; this plan supplies none by implication.

## 2. What continuity with ODD means

| Preserve as project intent | Reassess through design | Freedom of implementation |
| --- | --- | --- |
| Public, reproducible, experiment-independent benchmark | Coverage, dimensions and barrel/endcap transitions | Refactor, replace or rewrite factories |
| General-purpose collider-detector organization | Pixel/outer-tracker families and actual readout assemblies | Introduce reusable component libraries |
| Tracking, calorimetry and muon capabilities | Calorimeter technologies, segmentation and longitudinal structure | Generate XML and appropriate factory code from reviewed inputs |
| Full simulation and useful reconstruction/algorithm interfaces | Magnet/return concept, material, supports, services and timing additions | Change identifiers/interfaces with explicit migration and validation |
| Comparability with the ODD lineage | All inherited approximations and performance assumptions | Preserve ODD separately as the reference control |

The architecture proposal must explain why its complete layout remains a
recognizable successor. It must also identify intentionally broken compatibility.
No exact ODD dimension or technology is frozen by this table. Using ATLAS/CMS
as evidence does not authorize assembling mutually incompatible pieces of them.

## 3. Starting position and evidence discipline

We have mapped ATLAS/CMS whole-detector papers, performed selected tracker/RD53
reading, and inspected the ODD source across subsystems. We have **not** read all
TDRs in detail, completed a component comparison, selected the production ODD
baseline, or run its geometry/simulation. The distinction determines the first jobs.

Use the cached literature in three passes:

- **Map:** identify the document/version, chapters and relevant figures/tables.
- **Extract for a decision:** answer a bounded engineering question with precise
  source/page locators, units, operating conditions and uncertainty.
- **Reconcile:** compare ATLAS, CMS and other relevant public technologies; separate
  TDR proposals from later production evidence and resolve conflicts explicitly.

Every dossier should state the physical purpose; active/passive components;
dimensions and tolerances relevant to simulation; electronics footprint and
inactive area; power/cooling/data assumptions; service routes; response model;
uncertainties; and what is explicit, effective or omitted.

A source saying “ODD uses X” establishes an upstream **FACT**, not that X is a
credible hardware choice. Carry the FACT → INFERENCE → NODD DESIGN CHOICE trail
through all inherited parameters as well as new ones. Avoid mixing the RD53A
prototype, experiment-specific successors, sensor active area and total die area.

## 4. Execution stages, dependencies and gates

These stages implement the existing M0–M7 roadmap. Subsystem work overlaps when
interfaces are ready; M3/M4/M5 are not a command to finish tracking before starting
calorimetry or muons. No calendar estimate is credible before baseline execution
and human-review availability are known. Estimate effort after those checkpoints.

### A. Establish the unchanged control — M0

**Closed for progression by user direction on 2026-09-16.** The original work
contract is retained below for traceability; it is not a list of locally completed
checks or a prerequisite to starting B.

**Work:** resolve ADR-001 baseline/import and ADR-003 environment/artifacts;
select the full-detector entry point and asset versions. Reproduce construction,
overlaps, counts, IDs, dimensions, material/mass and η/φ coverage. Sample the field
in tracking, calorimeter and muon regions. Map XML readouts to ACTS digitization
and identify the exact response and reconstruction configuration. Run feasible
Geant4/ACTS checks and preserve failures without changing the detector to hide them.

**Outputs:** immutable baseline manifest; reproducible commands; r–z/transverse
views; subsystem inventory; field/readout consistency report; baseline evidence
and disposition of ODD-G01–G04. Adapt M0-BASELINE explicitly for field and all-system
checks before execution. Complete the remaining M0 governance and review work.

**Exit:** humans review the baseline evidence, unresolved limitations and M0
completion. Build success alone does not complete M0. Source extraction and
requirements drafting can proceed alongside this work, without geometry changes.

### B. Define one coherent detector — architecture in M1

**Work:** define intended use cases and benchmark observables; propose coverage,
subsystem envelopes, magnet concept and service corridors. Compare architecture
alternatives with a short cost/benefit and compatibility analysis. Establish
coordinates, units, identifiers, material accounting, readout/digitization and
field conventions. Allocate space and service budgets provisionally, with owners
and uncertainty; refine them using component studies rather than inventing limits.

**Outputs:** full-detector architecture proposal; ODD continuity/change table;
interface register; requirements-to-validation matrix; cross-cutting ADR proposals;
initial TDR outline. Exact document IDs are allocated from the register when
created; proposed DES-001/002 keep their existing pixel/readout and support meanings.

**Exit:** reviewed architecture sufficient to bound initial component designs.
Freeze only the interfaces needed for the next implementation; changes follow
explicit amendments. Do not freeze the whole detector prematurely.

### C. Prove the component method — M1/M2

**First case:** trace an RD53-class chip into a sensor/readout module and realistic
local support/cooling/services, using ATLAS and CMS integration as two inputs.
Document die footprint, periphery, sensor active/inactive area, chip tiling,
hybridization, flex, thermal path and connections. Use effective representations
where their preserved physical quantities can be stated and tested.

**Outputs:** evidence dossier; proposed DES-001 module/readout and DES-002
support/cooling; component material inventory; interface table; acceptance plan;
first TDR component section. After M0 completion and design sign-off, implement
and validate the component before repeated structures.

**Exit:** an approved, reproducible example of the complete evidence → design →
implementation → validation chain, with explicit omissions. Do not extend the
pixel case indefinitely: its purpose includes testing a transferable method.

In parallel, prepare one calorimeter sampling/cassette case and one muon chamber
case. Their requirements must inform the specification/generation approach;
a pixel-specific schema must not become an accidental universal standard.

### D. Establish specification and generation — M1/M2, then iterative

Draft an ADR comparing parameterized XML with reusable factories, schema-driven
factory/XML generation, and the minimum handwritten extension points. Use the
pixel, calorimeter and muon cases to test what must be expressible. Avoid building
a general CAD language before those cases reveal the actual needs.

**Proposed contract:** named parameters with units and source/design links;
materials and mixtures; transforms and repetition; active/passive boundaries;
segmentation/IDs; interfaces and effective-model declarations. Treat generated
files as reproducible products of reviewed inputs. Decide ownership of handwritten
versus generated code, deterministic regeneration, validation and versioning.
An XML parameter driving a generic factory may be more appropriate than generating
a new C++ factory for every component; the ADR must settle this explicitly.

**Exit:** signed-off generation architecture; isolated authorized prototypes when
needed; repeatable output for representative technologies; source-to-output and
physical checks. No generator may silently supply unreviewed physical defaults.

### E. Develop complete subsystems — M3/M4/M5

Use the work packages below to progress from approved assemblies to repeated
structures and complete systems. Each package includes its services and response
contract, and contributes to the shared material and interface registers.

| Work package | Evidence/design questions | First independently reviewable output | Validation emphasis |
| --- | --- | --- | --- |
| WP-PIX: pixels | Which chip/sensor/module family is credible? How do power, data, cooling and inactive areas fit? | Module and support dossier/DES-001/002 | Material, active coverage, component counts, hit/readout mapping |
| WP-OUT: outer tracker | Strip geometry, stereo or paired sensors, hybrids, supports; are trigger-related functions part of the intended scope? | ATLAS/CMS technology comparison and one module design | Measurement dimensions, segmentation agreement, stereo transforms, material and crossings |
| WP-TIM: timing | Dedicated or integrated technology; coverage and timing assumptions; service impact | Timing use case and architecture options | Active crossings, passive material and explicitly modeled timing response |
| WP-ECAL: electromagnetic calorimetry | Active/absorber choice, module/cassette, readout, cooling and gaps | Sampling/cell and cassette dossier | Profiles, sampling fraction, leakage, transitions and calibrated response assumptions |
| WP-HCAL: hadronic calorimetry | Absorber, scintillator/sensor use, effective electronics/services and containment | Audit of ODD mixture accounting plus representative assembly | Material/depth, hadronic shower response, leakage and sensitivity to response model |
| WP-MU: muons | Technology, station roles, chamber/readout geometry, gas and field needs | Chamber dossier and station/field requirements | Active crossings, field integrals, chamber-response assumptions and acceptance |
| WP-MAG: magnets/interaction region | Coil/cryostat/return concept, field boundaries, beam pipe and shielding relevance | Coherent magnet/material/field options and interfaces | Field matching, material before calorimeters, muon bending and forward transport |
| WP-SVC: supports/services | Common supports, power/data/cooling/gas routes, component-to-route loads | Whole-detector service inventory and corridor map | Mass, directional material, clearances and no double counting |
| WP-SIM: simulation/reconstruction | Sensitive response, digitization, conditions and downstream contracts | Versioned benchmark/configuration specification | End-to-end consistency, uncertainties and intended use-case performance |

WP-SVC and WP-MAG start with architecture, not after active detector layouts are
full. Electronics belong in each subsystem dossier; shared service owners check
the combined loads and routes. WP-TIM must coordinate with global envelopes.

**Exit per subsystem:** approved design and interfaces; implemented geometry;
validation evidence and documented applicability; expert/human review. A subsystem
with incomplete response can be geometry-validated without claiming performance
acceptance. Record that distinction.

### F. Integrate and assess detector performance — M6

Assemble only reviewed components through staged configurations: component,
subsystem, neighboring-system interface, then full detector. Maintain an immutable
ODD control and candidate nODD configurations.

Use two complementary comparisons:

1. **Attribution:** hold event samples, physics settings, cuts and compatible
   response/reconstruction assumptions fixed where meaningful, so changes can be
   traced to geometry/material/field modifications. Explicitly document unavoidable
   migrations such as changed segmentation or identifiers.
2. **Best supported operation:** evaluate each detector with its reviewed response,
   calibration and reconstruction settings. Report those changes separately so
   retuning does not masquerade as a geometry improvement.

Progress from geantinos/material probes and single particles to representative
collisions and selected pile-up/condition scenarios. Select ranges, statistics,
seeds, tolerances and uncertainty treatment in validation specifications before
acceptance. Include difficult barrel/endcap transitions, service concentrations,
forward trajectories and cracks, not just central nominal trajectories.

**Outputs:** material/field/coverage maps; subsystem response evidence; integrated
tracking, shower, muon and timing results where supported; explained ODD–nODD
differences; computational cost and reproducibility report; applicability limits.

**Exit:** reviewed integrated evidence and disposition of ODD-G01–G10. A realism
improvement may reduce idealized performance; accept it on physical grounds when
it meets the reviewed requirements. Do not tune material to restore an old plot.

### G. Finalize TDR and release — M7

Freeze the detector/configuration/environment and regenerate the report figures
and tables from retained evidence. Check every normative parameter, physical
claim and headline performance result against its provenance and validation.
Complete expert reviews, limitations and release acceptance. Decide final naming.
Publish only under the repository's human authorization/review workflow.

**Outputs:** TDR; reproducible DD4hep/Geant4 release and agreed reconstruction
interfaces; source/parameter catalogue; benchmark inputs and artifact manifests;
ODD migration/comparison notes; known limitations and deferred engineering register.

**Exit:** identified human acceptance of the detector and report. TDR completion
must not erase uncertainty or imply unperformed engineering certification.

## 5. Interfaces and realism accounting

Maintain one shared interface register. For every boundary, name both subsystem
owners and record envelopes/clearances, coordinate conventions, traversing material,
services and routes, identifiers/readout, field assumptions, and validation.
Changes need both sides reviewed; the coordinator cannot silently resize a neighbor.

Maintain a component ledger with at least: component ID; subsystem; physical
function; source claims; material/size/count; active/passive role; power/cooling/data
assumptions where relevant; representation (explicit/effective/omitted); preserved
quantities; uncertainty; design/version; validation status; TDR section. Counts and
materials must roll up from components to assemblies to the full detector without
double counting services represented in mixtures.

Use a simulation-relevance test for effort allocation:

- Would this detail change material, active area, trajectory/field, shower behavior,
  response, clearance or service plausibility at the intended accuracy?
- If yes, represent it explicitly or justify an effective model and test it.
- If no, document the omission briefly and avoid manufacturing detail.

Start with geometric fit, mass/material, plausible connectivity and order-of-magnitude
load/space consistency. Escalate to specialist engineering evidence only where a
simulation conclusion depends on it. If a critical assumption is unsupported,
mark the affected design/performance claim conditional rather than inventing proof.

## 6. Stage B agent organization and responsibility boundaries

The user's structure comprises the project responsible, System Architect
coordinating tracker/calorimeter/muon technicians, project software
engineer, and publication/documentation office. On 2026-09-16 the user additionally
requested an explicit **Physics and Performance Validation** role. This records
organizational scope; it does not deploy agents or appoint human reviewers.

### Role mandates

| Role | Owns | Boundary / first stage-B deliverable |
| --- | --- | --- |
| Project responsible | Objectives, scientific use cases, requirements, priorities, decision/risk register and escalation to humans | Sets what must be achieved; asks for alternatives and resolves proposed tradeoffs. First output: architecture brief and ODD continuity requirements. Cannot grant human sign-off. |
| System Architect | Physical coherence: envelopes, interfaces, global layout, magnets/fields, beam pipe, shared supports/services and aggregate budgets | Coordinates subsystem proposals and owns cross-system consistency. First output: global concept options and interface register. Does not silently redefine performance requirements. |
| Tracker technician | Pixel/strip module technology, local electronics, supports, cooling and routes; provisionally dedicated timing hardware | First output: technology/options dossier and envelope/service requests. Tracker timing ownership is a proposal, with project-wide timing conventions coordinated centrally. |
| Calorimeter technician | EM and hadronic calorimetry, local electronics, cassettes/supports/cooling, gaps and active-medium response assumptions | First output: coupled ECal/HCal options and material/service requests. Split into bounded EM/HCal tasks when needed, retaining one integration owner. |
| Muon technician | Chamber technology, stations, local services/readout, backgrounds and response requirements | First output: chamber/station options and field/absorber requirements. Magnet/return material belongs to the System Architect, reviewed jointly. |
| Project software engineer | Specification/generation architecture, DD4hep/Geant4, digitization/reconstruction implementation, identifiers, environments, CI, provenance and reproducibility | Owns software execution, not unilateral choices of physical response or acceptance. First output: software/interface contract and comparison-baseline identity. Can delegate scoped implementation. |
| Physics and Performance Validation | Physics benchmarks, observables, response-assumption review, uncertainty treatment, ODD/nODD comparisons and scientific interpretation of results | Reports to the project responsible independently of implementation. First output: requirements-to-observables matrix and architecture validation criteria. Supplies review findings and acceptance recommendations; human acceptance remains separate. |
| Publication/documentation office | TDR structure, source catalogue hygiene, terminology, claim/version traceability, figures/tables and parent-repository/TDR revision consistency | Specialists remain responsible for correctness of their claims. First output: chapter/claim coverage matrix. Does not select detector parameters or infer approval from a merged document. |

### Main gaps to close

1. **Independent Physics and Performance Validation — role added.** This role
   reports directly to the project responsible and reviews work independently of
   its authors. It defines benchmark scenarios, observable definitions and proposed
   criteria before results are interpreted; distinguishes geometry, response and
   reconstruction effects; and records uncertainties, limitations and unexplained
   changes. Software engineering provides reproducible execution and artifacts,
   while this role assesses their scientific meaning. It cannot silently retune
   detector parameters, relax criteria or approve its own findings as human acceptance.
2. **Global services and passive material.** Give the System Architect explicit
   ownership of common supports, power/data/cooling/gas corridors and total material
   accounting. Subsystem technicians own local loads and routes up to a named
   handoff. No cable, cooling line or material allowance may fall between teams.
3. **Timing and forward boundaries.** Assign dedicated timing hardware explicitly
   (tracker proposed); timing response in calorimeters/muons stays with their owners.
   Put interaction-region material, shielding and unassigned forward interfaces
   under the System Architect until allocated. A three-subsystem chart alone
   leaves these areas uncovered.
4. **Response versus implementation.** Subsystem technicians propose credible
   response assumptions; software implements them; validation challenges them;
   the project responsible carries the scientific applicability statement to
   human review. This includes calibration, ageing, inefficiency and operating
   conditions when the intended claims depend on them.
5. **Decision authority and coordination overload.** Project responsible owns
   purpose/priorities; System Architect owns physical consistency; software owns
   execution. Disagreements become short alternatives with consequences, escalated
   to the responsible and then the human as necessary. The coordinator should not
   personally write all subsystem documents or approve its own technical claims.
6. **Provenance and TDR drift.** Authors supply verified locators/derivations;
   publication staff audit the links and presentation. TDR statements retain draft,
   inferred or validated status. Commit report changes in the TDR submodule and
   record the intended revision in the parent through the authorized workflow.

### Interface and change protocol

For each interface, record both endpoint owners, coordinate frame, envelope and
clearance, crossing materials/services, loads or capacities where relevant,
readout/identifier/field/time conventions, source/design versions, open questions
and validation method. The System Architect owns physical interfaces; the
software engineer owns their software representations; both reconcile the mapping.

A subsystem change request includes motivation, evidence, proposed parameters,
affected interfaces, material/performance implications, uncertainty and alternatives.
The other endpoint owners review it before it becomes an integration assumption.
The project responsible routes unresolved tradeoffs to the human decision maker.
Implementation follows applicable design approval; technical agents cannot approve
new physics merely because the software can represent it.

### Working model for agents

These are eight responsibility roles, including Physics and Performance Validation,
not a requirement for eight simultaneous processes. Start agents for bounded jobs, share exact input
commits and use non-overlapping file ownership or worktrees. Preserve mandates,
interfaces, decisions and handoffs in Git so a new agent instance can resume a role.

No agents are launched by this organization review. First stage-B assignments are:

1. Project responsible: use cases, successor features and architecture questions.
2. System Architect: provisional global layout/magnet alternatives and subsystem
   request template; all numerical assumptions remain sourced or explicitly open.
3. Three subsystem technicians: options, constraints, service demands and interface
   requests in that common format, using the existing literature evidence.
4. Software engineer: representation/readout/field contracts and exact comparison
   configuration provenance; do not reopen the accepted baseline exercise.
5. Publication office: TDR outline and evidence/claim coverage matrix.
6. Physics and Performance Validation: requirements-to-observables matrix and critique
   of the combined architecture before component implementation.

Integrate these into one architecture proposal and continuity/change matrix.
Human review selects among the physical alternatives. Naming a role “expert” does
not establish expertise or replace a named human domain reviewer.

## 7. TDR structure and continuous writing

Start the outline during architecture and grow chapters with each design:

1. Motivation, TrackML/ODD lineage, objectives and scope of credibility.
2. Requirements, use cases, overall layout and alternative concepts.
3. Coordinate/readout/identifier conventions and provenance methodology.
4. Interaction region, magnets, fields and detector-wide interfaces.
5. Pixel detector, outer tracker and timing (separate component sections).
6. Electromagnetic and hadronic calorimetry.
7. Muon system.
8. Common mechanics, electronics architecture, power/cooling/data/gas and routing.
9. Detector specification, DD4hep generation/implementation and software versions.
10. Simulation, sensitive response, digitization and reconstruction assumptions.
11. Geometry/material/acceptance validation and subsystem/integrated performance.
12. ODD comparison, uncertainties, limitations and deferred engineering work.
13. Reproduction, release configuration, conclusions and future developments.
14. Appendices: component/parameter ledger, source catalogue, validation matrix,
    review history and configuration/artifact manifests.

Every chapter separates source facts, derived estimates and nODD choices. Figures
and tables reference generating configurations and artifacts. Authors update the
chapter with design/implementation PRs; release editing should reconcile and polish
existing evidence rather than reconstruct lost history. Select document tooling
later based on citations, reproducible figures and export needs; no new dependency
or report framework is required to agree this plan.

## 8. Original work queue and current override

The user closed A for progression on 2026-09-16. The active next assignments are
the stage-B roles in section 6; retain the original queue below as history and
follow-up options, not an instruction to repeat baseline characterization.

These are proposed local task descriptions, not created issues or authorizations
to bypass M0. Begin the independent evidence tasks while baseline selection proceeds.

| Order / dependency | Task | Concrete output | Gap addressed |
| --- | --- | --- | --- |
| Start now, M0 | Prepare full-detector baseline candidate and environment matrix | Completed ADR-001/003 proposal fields with options, exact revision/entry/assets and execution recipe | ODD-G01 |
| Alongside selection | Extract ATLAS/CMS RD53 module comparison | Component/readout/service fact table, device-version distinctions and uncertainties | ODD-G05 |
| Alongside selection | Audit ODD material and measurement assumptions | HCal effective-mixture questions; XML/ACTS readout map; service inventory | ODD-G03/04 |
| Alongside selection | Map calo, muon, timing and magnet sources for bounded decisions | Technology/interface dossiers and missing production evidence, using existing PDFs first | ODD-G02/06/07/08/09 |
| After baseline prerequisites | Run full-detector M0 characterization | Retained results and explicit failures/unavailable checks; review-ready M0 report | ODD-G01–04 |
| Architecture drafts can overlap; approval after required review | Propose ODD successor concept and interfaces | Continuity/change matrix, envelope/magnet/service options, benchmark requirements and TDR outline | ODD-G02/06/09/10 |
| After interfaces and component evidence | Draft first pixel/support designs plus calo/muon cases | DES-001/002 drafts; independent assembly dossiers for other technologies | ODD-G05/07/08 |
| After generation decision, M0 exit and relevant sign-off | Implement first validated assembly and transferable generation path | Small implementation PR with tests and TDR evidence | Demonstrates the workflow |

The critical path is baseline/environment → architecture/interfaces → approved
representative assemblies and generation contract → subsystem integration →
full-detector evidence → TDR/release. Literature extraction, interface drafting and
TDR preparation overlap that path; production integration never precedes its gates.

## 9. Decisions reserved for human review

Review this programme and resolve the following at their natural checkpoints:

- M0: actual ODD baseline/import, supported tools, artifact retention and reviewers.
- Architecture: intended benchmark use cases, broad detector concept, coverage,
  magnet/return approach, timing role and definition of recognizable continuity.
- Component design: credible technology families, effective representations,
  response scope and measurable accuracy criteria.
- Generation: specification contract and handwritten/generated ownership.
- Validation/release: performance applicability, unresolved engineering limitations,
  TDR acceptance, final naming and publication authorization.

The current request establishes project objectives and asks for this plan. It does
not constitute approval of any as-yet unwritten detector design or ADR.
