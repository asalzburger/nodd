# M0 baseline characterization specification

- ID: M0-BASELINE
- Status: DRAFT
- Created: 2026-09-15
- Human owner / validation reviewer: TBD
- Issue: TBD
- Related decisions: [ADR-001](../decisions/ADR-001-upstream-baseline.md), [ADR-003](../decisions/ADR-003-validation-and-artifact-policy.md)

## Objective and boundary

Characterize a pinned upstream ODD detector reproducibly before any production detector changes. Record observed behavior, limitations, and known defects without altering geometry, materials, segmentation, sensitive behavior, or reconstruction configuration to obtain a desired result.

This is a proposed measurement contract, not an executed report or an approved baseline. Concrete commands depend on upstream and tool selection and must be added before execution. Tooling can be developed during M0 within repository constraints.

## Prerequisites

- Resolve upstream repository, full revision, import method, detector entry point, and required assets through ADR-001.
- Record licenses and public source entries in `reference/manifest.yaml` once created.
- Select the supported environment and tool versions through ADR-003.
- Define sampling, units, numerical tolerances, and acceptance criteria with human review. Do not infer approval from this draft.
- Inventory existing upstream tests and commands before writing new tools.

## Planned measurements

All command interfaces below are planned; no executable names or successful runs are asserted.

| Check ID | Measurement / planned tool interface | Required outputs | Acceptance definition still needed |
| --- | --- | --- | --- |
| M0-B01 | Parse selected compact description and construct detector using upstream build/loading tools | Build and construction logs, command exits, entry point | Supported build/configuration and construction success criteria |
| M0-B02 | Run geometry overlap checker on pinned geometry | Full findings, locations, penetration measures, checker settings | Tolerance, numerical treatment, and review of upstream findings |
| M0-B03 | Render r-z and transverse layout views | Images, view configuration, units, subsystem legend | View coverage and inspection criteria |
| M0-B04 | Traverse geometry and summarize volumes, placements, modules, sensitive elements, extents, and sensitive area | Machine-readable counts and dimensions, definitions of unique versus placed objects and area accounting | Counting conventions, subsystem mapping, and comparison criteria |
| M0-B05 | Sample trajectories versus eta and phi; record sensitive crossings and coverage | Sampling definition, trajectories, crossing distributions, coverage plots | Origin, trajectory/field assumptions, grid, boundary handling, and coverage criteria |
| M0-B06 | Scan directional radiation and interaction lengths | X/X0 and interaction-length integrals, path limits, subsystem/material contributions | Sampling, path definitions, convergence checks, and numerical tolerances |
| M0-B07 | Extract subsystem masses and material composition where supported | Mass/composition tables, density units, accounting conventions, unsupported cases | Treatment of nested volumes and mixtures; consistency tolerances |
| M0-B08 | Summarize segmentation and identifiers | Readout definitions, encoding, uniqueness/stability findings, sampled mappings | Expected identifier domains and stability comparison procedure |
| M0-B09 | Run DD4hep/Geant4 single-particle smoke tests | Particle setup, seeds, event logs, exit status, sensitive-hit summary | Particles, energies, directions, event count, and success criteria |
| M0-B10 | Exercise ACTS conversion, navigation, and material mapping | Conversion logs, surface/count summaries, navigation results, mapping artifacts | Supported integration, configuration, sampling, and comparison criteria |
| M0-B11 | Obtain representative single-particle or reconstruction metrics where feasible | Configuration, metric definitions, statistical uncertainties, plots | Feasibility, sample definition, and reviewed scope |

## Reproducibility record

For each run, record:

- project and upstream full commit SHAs, branch, and dirty-tree state with a retained patch or precise change inventory;
- UTC execution timestamps, platform, compiler, DD4hep, ROOT, Geant4, ACTS, and other relevant dependency versions;
- build options, environment setup, input/configuration paths and hashes, detector entry point, and required data versions;
- exact commands and working directories, exit codes, seeds or an explicit not-applicable explanation;
- sampling definitions, units, tolerances, and governing review references;
- artifact paths/locations, SHA-256 hashes, sizes, and generating check IDs.

Exclude credentials, private URLs, and confidential data from committed evidence.

## Results and review

Use [REPORT_TEMPLATE.md](REPORT_TEMPLATE.md). For every check, distinguish execution status from acceptance: a successful command does not establish physical validity. Record `NOT RUN`, `BLOCKED`, or `NOT APPLICABLE` with a reason when needed; use `PASS` only against defined criteria and actual successful results.

Unexplained overlaps, material changes, acceptance loss, or identifier instability require human direction under [AGENTS.md](../../AGENTS.md). Preserve findings and do not repair upstream geometry during M0. Document tool limitations separately from measured detector behavior.

The initial characterization has no approved regression reference. Human reviewers must assess results and limitations before establishing one. Subsequent baseline changes require retained prior evidence and reviewed justification.

## Completion and open decisions

Baseline review requires a pinned source state, reproducible commands, retained artifacts, results or explicit reviewed dispositions for all checks, and identified human validation review. Baseline characterization alone does not complete all M0 governance tasks.

Open: upstream selection, tool matrix, commands, thresholds, sampling, artifact storage, reviewers, and review issue. No numerical acceptance limits have been selected here.
