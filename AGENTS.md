# AGENTS.md

## Purpose

This repository develops **nODD**, a more realistic, publicly reproducible evolution of the OpenDataDetector (ODD). The detector description is intended for full simulation with DD4hep and for downstream reconstruction and validation with ACTS-compatible tooling.

This file defines mandatory instructions for Codex and other automated contributors working anywhere in this repository. More specific `AGENTS.md` files may add constraints for a subtree, but must not weaken these rules.

## Current project phase

The project begins in **M0 — Baseline and Governance**.

Until M0 is explicitly completed:

- Do not change detector geometry, materials, segmentation, sensitive-detector behavior, or reconstruction configuration.
- Work only on project governance, design templates, source cataloguing, baseline-characterization tools, tests, and reproducible development infrastructure.
- Treat any geometry example as an isolated prototype unless a signed-off design document authorizes integration.

## Source of truth

The Git repository is the canonical project record. Chat transcripts, local notes, generated summaries, and external task systems are supporting material only.

Before starting work:

1. Read this file and any more specific `AGENTS.md` in the affected subtree.
2. Read `PROJECT.md`.
3. Read the relevant design document (`DES-*`), architecture decision record (`ADR-*`), validation specification, and linked issue.
4. Inspect the current branch, working tree, and relevant tests.
5. Preserve unrelated user changes. Never discard or overwrite them.

When instructions conflict, follow this priority:

1. Explicit human instruction for the current task.
2. The nearest applicable `AGENTS.md`.
3. Accepted `DES-*` and `ADR-*` documents.
4. `PROJECT.md` and repository-wide conventions.

Report unresolved conflicts instead of guessing.

## Scientific and engineering principles

- nODD is a public, experiment-independent reference detector informed by technologies that have been built or credibly engineered for modern collider experiments.
- Do not silently turn nODD into a copy of ATLAS, CMS, or another experiment.
- Prefer publicly citable information. Internal collaboration material may be used for private sanity checks only; it must not be the sole normative basis for a public design parameter.
- Model details because they affect geometry, clearance, material, services, thermal or electrical architecture, sensitive response, reconstruction, or validation—not merely because they exist in engineering CAD.
- Do not tune geometry or material merely to obtain a desired performance plot. Document the physical rationale first.
- Use explicit effective representations only when the omitted detail and the preserved physical quantities are documented.

## Provenance requirements

Every nontrivial detector parameter, material definition, component choice, or layout requirement must be classified in its design document as exactly one of:

- **FACT** — stated by a public source. Record the source identifier and precise location such as section, page, table, figure, or data record.
- **INFERENCE** — derived from one or more facts. Record the derivation, assumptions, and uncertainty.
- **NODD DESIGN CHOICE** — selected by this project. Record the rationale, alternatives, consequences, and approving humans.

Do not introduce unexplained numbers. Values used only for a test fixture must be clearly named as test values and must not leak into the production detector description.

Each referenced source must have an entry in `reference/manifest.yaml` containing, where applicable:

- stable project source ID;
- title and authors or collaboration;
- document number, DOI, report number, or arXiv identifier;
- public URL;
- publication/version date and access date;
- local filename and SHA-256 when a local copy is used;
- license or redistribution note when known;
- design facts supported by the source.

Large reference PDFs belong in the ignored local reference directory and must not be committed unless redistribution and repository policy explicitly permit it.

## Design and sign-off workflow

Substantial changes follow this lifecycle:

`DRAFT -> TECHNICAL REVIEW -> EXPERT REVIEW -> SIGNED OFF -> IMPLEMENTED -> VALIDATED -> ACCEPTED`

Rules:

- Create or update a `DES-*` document before implementing a new detector component, material model, service model, or layout.
- Use an `ADR-*` for cross-cutting or difficult-to-reverse decisions such as target pseudorapidity coverage, technology selection, coordinate conventions, or validation policy.
- Keep design approval and production implementation in separate pull requests unless a human maintainer explicitly approves an exception.
- Codex may draft documents, summarize evidence, propose alternatives, implement signed-off designs, and produce validation evidence.
- **Codex must never approve a design, record human sign-off, or advance a document to `SIGNED OFF` or `ACCEPTED`. Only an identified human reviewer may do that.**
- A request to explore an unsigned design must be labeled `PROTOTYPE`. Prototype code must be isolated, must not be wired into the production detector, and must state what remains unsigned.
- Implementation pull requests must reference the governing design document and issue.
- If implementation reveals that an accepted dimension, material, or requirement is impractical, stop and propose a design amendment. Do not silently change it in code.

## DD4hep implementation rules

For component work, proceed from small reusable units toward assemblies:

1. material definitions;
2. primitive component or layer;
3. sensor and readout elements;
4. module assembly;
5. local support, cooling, power, and data services;
6. stave, ring, disk, or other repeated structure;
7. subsystem integration;
8. full-detector integration.

For each implementation:

- Use explicit DD4hep units for all dimensional and physical quantities.
- Keep parameters named and centralized; avoid unexplained numeric literals.
- Reuse component factories and parameterized structures where that improves traceability and consistency.
- Preserve stable identifiers and document identifier schemes.
- Separate sensitive and passive volumes deliberately.
- Document any homogenized or effective material, including composition, density, represented components, normalization target, and validation method.
- Avoid overlapping, coincident, zero-thickness, or numerically fragile placements.
- Do not change an accepted detector parameter during refactoring.
- Keep geometry construction deterministic and reproducible.
- Prefer the smallest independently testable change.

## Required validation

Every new or changed geometry component requires validation appropriate to its scope. At minimum, consider:

- successful compact-description parsing and detector construction;
- geometry overlap checks at an agreed tolerance;
- expected volume, placement, and sensitive-element counts;
- dimensions and transforms against the signed-off design;
- mass and constituent material checks;
- directional material scans in radiation and interaction lengths;
- sensitive crossings and acceptance versus `eta` and `phi`;
- stable identifier checks;
- DD4hep/Geant4 execution smoke test;
- ACTS geometry conversion and navigation checks when applicable;
- regression comparison with an approved reference artifact.

Validation output must record the commit SHA, configuration, tool versions, random seed where relevant, commands, and tolerances. Do not update reference outputs simply because a test fails. Explain and review the physical or technical reason for every intentional baseline change.

## Code and change discipline

- Inspect existing conventions before adding dependencies, directories, abstractions, or build options.
- Make focused changes. Do not combine unrelated cleanup with scientific modifications.
- Add or update tests with the implementation.
- Run the narrowest relevant checks first, followed by the required integration checks.
- Never report a test as passed unless it was actually run successfully.
- Clearly distinguish verified results from expected behavior when dependencies or data prevent a test from running.
- Do not weaken tests, tolerances, linters, or CI gates to make a change pass without documented human approval.
- Do not delete, rewrite, or regenerate accepted evidence without preserving traceability.
- Never commit credentials, access tokens, private URLs, personal information, raw model rollouts, or collaboration-confidential material.
- Avoid destructive Git operations. Do not force-push, rewrite shared history, or discard local work unless a human explicitly authorizes the exact action.

## Documentation conventions

- Design proposals: `docs/design/DES-NNN-short-name.md`
- Architecture decisions: `docs/decisions/ADR-NNN-short-name.md`
- Sign-off records: `docs/signoff/DES-NNN-signoff.md`
- Validation specifications and reports: `docs/validation/`
- Source catalogue: `reference/manifest.yaml`
- Curated session records: `logs/`

Documents must use stable IDs, ISO dates (`YYYY-MM-DD`), SI/DD4hep units, and repository-relative links. State uncertainties and unresolved questions explicitly.

## Work reporting

At the end of a task, report:

- the outcome;
- files changed;
- design/ADR/issue IDs affected;
- tests and validation actually run, with results;
- provenance added or changed;
- assumptions and unresolved questions;
- any requested action requiring human review or sign-off.

For significant AI-assisted sessions, prepare a curated session record when requested. Record prompts, outcomes, commands, changed files, commit/branch, and token counts only when the client exposes exact counts. Never invent token usage, and do not commit raw private model state or chain-of-thought.

The user has requested ongoing logging for this project. For each significant
task, create or update a paired session record using [the logging workflow](logs/README.md).
Record selected user-visible requests, corrections, outcomes, relevant commands,
actual checks, starting revision and changed files. Keep missing measurements
explicit. Before completing the task, run
`python3 tools/session_logging/session_log.py validate` and report any failures.
Use a new project session ID for a new bounded task, even in the same client
thread; never duplicate token observations across records. This workflow does
not authorize collecting private client state or granting human sign-off.

## Magnetic sizing constraints

For all current and future magnetic candidates, apply the review-directed
[DES-004 sizing policy](docs/design/inputs/DES-004-magnet-sizing-review.md) and
[machine-readable constants](tools/magnetic_study/sizing-policy.json):
`RCMi = 1.065 RVi + 0.0072 m`, `U = (30 MJ/m³) Vcold`, and
`RVo = RCMo + 1.75 (RCMi − RVi)` (the expert's undefined `RCM` is provisionally
interpreted as `RCMi`; confirmation remains open). State cold-mass and vessel
axial lengths separately; do not infer an axial scaling from these radial rules.
Maintain homogeneous winding-pack current density. Require the magnitude of the
**complete central field** to be at most 5 T; 1–4 T is the preferred study range.
This central cap does not certify peak conductor field or NbTi operating margin.

Use computed stored field energy, not a uniform-bore energy proxy. Iterate winding,
current normalization and cold-mass size consistently. For nonlinear iron, coupled
coils or non-solenoidal geometry, obtain the complete energy/field solution and
an applicable cold-volume allocation; do not certify compliance from an isolated
vacuum coil. Missing inputs must remain explicit blockers. Apply the checks to
all active layouts; preserve dated historical fixtures as controls, clearly
superseded. Changes to these review constraints require explicit human direction.
No numerical study or CI pass grants detector design approval.

## Node-specific software workflows

Before relying on the local ACTS Spack installation for DD4hep/Geant4 builds,
runtime or source-level work, read the [acts-spack skill](skills/acts-spack/SKILL.md)
and run its node preflight. The [node registry](skills/acts-spack/references/nodes.json)
records only verified nodes and distinguishes installed libraries/runtime from
full source trees. Warn the user when the current node or requested capability
is unavailable or unverified before proceeding with dependent work. Recheck
actual paths and required runtime behavior; a recorded hostname or the
`ACTS_SPACK_SETUP` flag alone is not proof of availability. Add other nodes only
after testing them. Do not install or modify shared dependencies merely to make
the preflight pass.

## Pull-request naming and conflict resolution

Effective 2026-09-22 by explicit human instruction, every new or open PR title
must use exactly one of these case-sensitive prefixes, a colon, one space and
a nonempty description:

| Prefix | Scope |
| --- | --- |
| `Magnet System: <description>` | Magnets, field configurations and return structures |
| `Tracker: <description>` | Pixel/strip modules, tracker layouts and tracking-system design |
| `Calorimeter: <description>` | Electromagnetic and hadronic calorimeter work |
| `Muon System: <description>` | Muon detectors, stations and system design |
| `Global: <description>` | Detector-wide design, envelopes and shared interfaces |
| `Software: <description>` | New software capabilities, tools, skills and validation methods |
| `Infrastructure: <description>` | Repository workflow, CI, dashboard, logging and maintenance |

Choose the area of the principal deliverable; use `Global` for detector-wide
work and `Software` for reusable software capability even when demonstrated
with one subsystem. This replaces `chore: ...` / `chore(scope): ...` for PR
titles; it does not require renaming closed PRs or historical commits.
Infrastructure remains excluded from scientific progress tracking as below.

When resolving merge conflicts, preserve both independent contributions by
default, especially session logs. Keep distinct session pairs and merge record
arrays by stable ID; do not concatenate JSON documents or duplicate token
observations, IDs, reviews or checks. Reconcile edits to the same record against
their evidence, retaining exact review revisions and approval boundaries. Do not
silently choose one side when facts conflict. Validate merged logs and dashboard
records and run relevant checks before pushing. Use ordinary merges; do not
rewrite shared history or treat a conflict-resolution merge as design approval.

## Dashboard maintenance

The project dashboard must stay current with every project change. For each
non-infrastructure PR, update `project/tracking.json` or `project/reviews.json`
in the same PR with the affected work, dependencies, next actions, deliverables, reviews or
evidence. Update the curated record date. Review requests and decisions retain
exact target revisions and evidence; do not infer human approval from a merge.
After merge, reconcile the PR/merge metadata in the next tracking update when
it is available. Missing information stays explicitly unknown.

Use `Infrastructure: <description>` titles for repository/workflow maintenance
PRs. **Infrastructure PRs are excluded from project progress tracking:** do
not add chore work items, review rounds or PR entries, and do not count them as
milestone or scientific progress. They still require logging, relevant checks
and a successful dashboard build; tracking corrections may accompany an
infrastructure PR without tracking that PR itself. Scientific designs, detector changes and
validation evidence must not be classified as infrastructure to bypass updates.

Run `python3 -B tools/dashboard/build.py validate` and the relevant dashboard
checks before completing project work. CI checks PR naming and project tracking
updates and rebuilds/publishes the dashboard after every successful main-branch push.
See [the tracking workflow](project/README.md) and
[dashboard build/deployment guide](tools/dashboard/README.md).

## Stop conditions

Stop and ask for human direction when:

- the requested implementation has no signed-off design and is not explicitly a prototype;
- a required source is inaccessible or contradictory;
- the only available evidence is non-public;
- reviewer identity or approval state is ambiguous;
- a change would invalidate an accepted requirement or reference result;
- validation shows unexplained overlaps, material changes, acceptance loss, or identifier instability;
- completing the task would require credentials, permissions, publication, or destructive actions not explicitly authorized.

