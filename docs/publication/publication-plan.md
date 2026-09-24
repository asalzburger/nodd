# PUB-PLAN-001 — Continuous TDR drafting and publication plan

- Status: **DRAFT — proposed publication process for review**.
- Created: 2026-09-22.
- Editorial lead: `PubDoc`; programme coordination: `ProRes`.
- Work item: `TASK-B-PUB`; chapter frame and evidence map: [PUB-TDR-001](TDR-outline.md).
- Final human sign-off authority: `asalzburger-review`, as assigned in [ADR-002](../decisions/ADR-002-review-and-signoff-policy.md).

The immediate deliverable is a reviewable whole-detector documentation frame and
an ordered writing programme. The eventual deliverable is a TDR tied to a
reproducible detector release, with its assumptions, evidence and unresolved
engineering limitations intact. Drafting can start now; completion depends on
the design, implementation and validation gates in the
[development plan](../DEVELOPMENT_PLAN.md).

This task does not resume the user's paused tracker-layout exploration. Existing
pixel, magnetic and software work supplies versioned inputs when available;
planning chapter slots does not authorize new detector implementation, new
external communications or publication.

## Responsibilities and editorial contract

| Role | Contribution | Boundary |
| --- | --- | --- |
| `PubDoc` | Maintain structure, claim/evidence index, terminology, source locators, figure/table conventions and report/repository revision consistency | Cannot select parameters, certify technical claims or record human approval |
| `ProRes` | Prioritize chapter work, assign human ownership, resolve scope/authorship/venue questions and route decisions | Publication and detector acceptance require identified human decisions |
| `SysArch` | Chapters 2, 4 and 8; subsystem interfaces, aggregate budgets and physical consistency | An envelope reservation is not proof of active coverage or service capacity |
| `TrackTech`, `CaloTech`, `MuonTech` | Relevant subsystem chapters, component evidence and physical response assumptions | Each owns the correctness and limitations of its technical contributions |
| `SoftEng` | Chapters 3, 9, 10 and 13; implementation, executable recipes, environments and retained artifacts | Software success does not establish physics acceptance |
| `PhysVal` | Chapters 11 and 12, requirements/observables and independent interpretation | Review scope and uncertainty must match actual evidence; human acceptance remains separate |

These are input ownership roles, not appointments of human reviewers or authors.
Reuse the named tracker reviewer coverage in DES-005 only within its recorded
expertise; publication-wide and other subsystem expert assignments remain open.

Every technical contribution supplies the intended chapter/claim IDs, applicable
DES/ADR state and exact revision, concise proposed text, its source locators or
derivation, relevant configuration and artifact identities, and unresolved inputs.
The contribution states whether a result is proposed, prototyped, executed or
reviewed and links the applicable approval separately. Design lifecycle, evidence
execution status and editorial readiness are independent fields.

## Proposed delivery sequence

These gates are ordered by evidence dependencies, not calendar promises. They
can overlap between chapters; a missing detector input need not prevent writing
the methods and limitations that are already known.

| Gate | Work and deliverable | Readiness evidence / decision |
| --- | --- | --- |
| PUB-G0 — Frame review | Review this plan, chapter/subsection outline, ownership and claim coverage matrix; link them from the repository and dashboard | Human review of scope and priorities at an exact PR revision. Completion means an agreed frame, not a completed TDR or approved design |
| PUB-G1 — Foundational draft | Draft purpose/lineage, provenance, current requirements, architecture context and reproduction method; create subsystem sections using the common contract | Each present-tense technical assertion has a source or is explicitly a proposal; open inputs are assigned. Resolve LaTeX migration questions below before changing the submodule |
| PUB-G2 — Design dossiers | Write subsystem sections incrementally as component/design inputs arrive, integrating pixel work first and retaining candidate comparisons | Each consumed design has a pinned revision and recorded state; interface/material/response gaps remain visible; numerical claims have facts, derivations or reviewed choices |
| PUB-G3 — Evidence chapters | Add parametric estimates, ACTS studies, material/field controls, then DD4hep/Geant4 and reconstruction evidence as available | Reproducible artifacts, configurations, uncertainty, failed/not-run checks and independent interpretation. Prototypes cannot be presented as production validation |
| PUB-G4 — Integrated technical review | Reconcile all chapters to one detector/configuration; review shared interfaces, requirement coverage, aggregate budgets and headline conclusions | Named technical/domain/validation reviews of exact revisions; conditions and unresolved claims recorded. Design and production gates remain those of AGENTS/PROJECT |
| PUB-G5 — Release candidate | Freeze parent and report revisions, regenerate release figures/tables, build the report and test retained reproduction recipes | Claim audit, configuration/artifact manifest, source/license check and actual independent reproduction outcomes; unsupported claims removed or qualified |
| PUB-G6 — Human acceptance and publication | Present final detector/report/evidence revisions and outstanding limitations to the assigned authority; execute the separately authorized release/publication actions | Explicit human acceptance/sign-off where required and explicit publication authorization. A merge, successful PDF build or agent recommendation does not satisfy this gate |

M7/stage G remains the eventual report/release milestone. This initial M1/stage B
frame can be complete while all later gates remain pending.

## Priority queue and first writing increments

| Priority / increment | Scope | Required inputs / immediate next action |
| --- | --- | --- |
| P0 — Reviewable frame | PUB-G0; outline, ownership, claim/evidence map and documentation PR category | Review chapter coverage and priorities; assign human editorial and technical reviewers without presuming their availability |
| P1 — Write what is already traceable | Chapters 1, 3, introductory parts of 2 and 13; appendices B/E | `PubDoc` assembles repository scope, provenance, review conventions and configuration method; `ProRes`/`SoftEng` reconcile baseline identity and open decisions |
| P1 — Architecture and pixel dossiers | Chapters 2, 4–5 and 8, beginning with existing DES-003/005 and DES-001 inputs | `SysArch` reconciles global allocation scope; `TrackTech` supplies an exact pixel input revision and complete-vs-partial material boundary. Await separately authorized layout results |
| P2 — Close unrepresented subsystem inputs | Sections 5.3–5.4, chapters 6–8 and common service interfaces | Commission bounded source/requirements dossiers for short strips, long strips, timing, calorimeters, muons and shared services; decide ownership before claiming completeness |
| P2 — Methods before result claims | Chapters 9–11 | `SoftEng`/`PhysVal` document staged methods and verified capabilities, record missing benchmarks/criteria, and define artifacts needed for later evidence |
| P3 — Integrate demonstrated results | Chapters 11–12 and executive-summary results | Requires reviewed material, field, response and performance studies plus a controlled ODD comparison; draft methods/limitations can advance earlier |
| P4 — Publication candidate | Chapter 13, front matter, appendices and final figure/table set | Requires integrated technical review, accepted release scope, pinned report/configuration, reproduction and explicit human publication decision |

Technical PRs should deliver a short TDR update or a precise claim/delta handoff
with their evidence. `PubDoc` integrates accepted editorial changes incrementally;
it must not copy an evolving branch as though it were the final detector. Use
`Documentation: <description>` when the principal deliverable is the TDR,
publication material or documentation frame. Technical/design deliverables retain
their relevant system or software prefix and their required tracking updates.

## Unavailable inputs and follow-up decisions

The items below limit future content, not the ability to review this outline.

| Input or decision | What cannot be concluded yet | Owner / next discriminating action |
| --- | --- | --- |
| Approved comparison baseline and operating samples | Quantitative ODD–nODD gains and supported benchmark conditions | `SoftEng` + `PhysVal`: pin detector/entry/assets/environment, sample definitions and matching rules through the existing baseline/validation process |
| Numerical acceptance criteria, beamspot distribution and uncertainty policy | Achieved tracker coverage/performance or full-detector acceptance | `PhysVal` + `ProRes`: obtain scenario/criterion decisions before ranking results |
| Tracker layout studies currently on wait | Selected layer arrangement or ranked proposal conclusions | `ProRes`: retain the pause; consume results only when work is resumed and evidence is reviewed |
| Complete component/support/cooling/readout/routing inputs | Installed material budgets, capacity or engineering feasibility | Subsystem owners + `SysArch`: reconcile local terminations and shared routes, with explicit missing contributions |
| Magnetic engineering and candidate field maps | Realized central/forward field or standalone muon performance | `SysArch` + `MuonTech` + `PhysVal`: distinguish control fields from physical candidates and validate map domains/field integrals |
| Calorimeter, muon, strip and timing technology/response dossiers | Complete subsystem chapter designs or response predictions | Respective subsystem owners: supply public evidence, alternatives, representative assemblies and applicability limits |
| Production DD4hep/Geant4 detector and reconstruction integration | Full simulation, integrated reconstruction or performance claims | `SoftEng`: local Spack readiness is one input; validate the actual signed-off detector/configuration and supported interfaces separately |
| Review ownership, final name, authorship, venue, licensing and release format | Final report acceptance, credits or publication schedule | `ProRes` + `PubDoc`: present concrete choices at the relevant gates; final authority remains `asalzburger-review` |

First review should settle chapter coverage, the initial writing increments and
human review ownership. Tooling migration can be decided next. Venue, final
name and author list need not block technical drafting, but must be resolved
before publication. No date is promised before input and review availability
are known.

## Claim and figure acceptance checklist

Before a claim enters the release candidate, its author and `PubDoc` check:

- Stable claim/requirement ID, report location and input owner.
- Exactly one provenance category per nontrivial parameter/choice: `FACT`,
  `INFERENCE` or `NODD DESIGN CHOICE`, with the required locator, derivation or
  rationale and approval evidence. Execution/approval status is recorded separately.
- Exact source/design/configuration revisions; operating domain; assumptions,
  uncertainty and limitations; corresponding review decision where required.
- For calculated/measured results: commands, tool versions, seeds or explicit
  non-applicability, samples, tolerances, raw/result artifact identities and outcomes.
- For plots/tables: generating recipe, input/output hashes, axis definitions,
  units, selections, uncertainty, and a caption that states what is demonstrated.
- Public citation and redistribution rights for included material; no private
  normative evidence, confidential content or unexplained numerical placeholders.

At PUB-G5, `SoftEng` runs the selected report build, checks cross-references and
bibliography, and exercises the supported reproduction recipe. `PubDoc` audits
claims and remaining TODOs; `PhysVal` reviews scientific interpretation. The
actual outcomes, exceptions and reviewers are retained. None of these future
checks is claimed as run by this planning task.

## TDR source and revision workflow

The canonical review frame currently lives in `docs/publication/` in the parent
repository. The existing `docs/tdr/README.md` (available with the submodule
initialized) requires pdfLaTeX-compatible
Overleaf sources and says **“Do not push.”** This task therefore leaves the TDR
submodule and its remote unchanged. Parent-repository PR publication is separate
from updating or publishing the Overleaf report.

Before migrating the reviewed structure, `PubDoc` and `SoftEng` should prepare a
concrete migration change that:

1. Maps chapters/sections to `chapters/*.tex`, stable labels and the existing
   `main.tex` include structure; preserves useful introduction content and treats
   the older commented chapter list as a scaffold to reconcile.
2. Resolves inherited template references to `PLAN.md`, `docs/spec/` and
   `assets/literature/manifest.yaml`, which do not describe this parent's canonical
   evidence layout. Use the project's actual design/source records; do not create
   duplicate scientific sources of truth just to satisfy those template paths.
3. Selects how to copy or generate bibliography data, tables, figure assets and
   a small provenance manifest into the submodule. Its build must not depend on
   paths outside the submodule; preserve source IDs, precise locators and hashes.
4. Builds with the existing pdfLaTeX/TeX Live conventions, no shell escape, and
   records the actual build result. Confirm a supported local/CI environment
   before relying on it; this plan introduces no new TeX dependency.
5. Records the parent **evidence revision** used for generation, commits the
   report locally through the reviewed workflow, then records the report commit
   in the parent gitlink. The subsequent parent integration commit is a distinct
   identifier; do not try to embed its own future hash in itself.
6. Obtains explicit authorization for the remote publication step, then ensures
   the referenced report commit is available through the authorized workflow
   before merging a parent pointer that others must be able to fetch.

The release manifest should contain the evidence/configuration parent revision,
TDR revision, parent integration revision, generated-artifact hashes and the
applicable human review/publication decisions. A report built from a different
detector revision must not silently replace an accepted PDF or its evidence.

## Review request

Review this proposed scope, chapter/claim coverage, priorities and delivery gates.
Approval of this documentation frame would authorize the agreed writing process;
it would not sign off detector parameters, close M0, accept performance results
or authorize Overleaf/public release. Record the exact reviewed revision and any
conditions through the existing review workflow.
