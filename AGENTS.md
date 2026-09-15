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

## Stop conditions

Stop and ask for human direction when:

- the requested implementation has no signed-off design and is not explicitly a prototype;
- a required source is inaccessible or contradictory;
- the only available evidence is non-public;
- reviewer identity or approval state is ambiguous;
- a change would invalidate an accepted requirement or reference result;
- validation shows unexplained overlaps, material changes, acceptance loss, or identifier instability;
- completing the task would require credentials, permissions, publication, or destructive actions not explicitly authorized.

