# SESSION-2026-09-16-full-detector-scope — Expand project scope to full detector design

## Scope and evidence

Contemporaneous curated record on 2026-09-16, on `main` starting at
`2f1cd77357568412780f53fef387693e23326330`. The paired JSON inventories
pre-existing ODD resource discovery changes; these were preserved. Exact token
counts, client version and conversation start time are unavailable.

Context: M0, ADR-001/003/004/005 and the baseline specification. No ADR,
design approval or issue state was changed by this task.

## Selected conversation

User (exact quote): “Before anything, expand the PROJECT.md - which is very tracker centric - to full detector design”

Earlier user direction (paraphrase): aim for realistic component use rather than
CAD/manufacturing accuracy, with eventual automatic DD4hep factory and compact
XML generation and Geant4 validation; discuss generator architecture later.

Assistant outcome (summary): expanded the project statement, scope, realism
criteria, component hierarchy, validation and provisional roadmap across all
detector systems, retaining the first pixel-module case within that wider scope.

## Decisions and outcomes

- Cover the interaction region, tracking, timing, electromagnetic and hadronic
  calorimetry, muons, magnets/fields, mechanics, services and shared interfaces.
- State a reviewed specification → generated DD4hep factories/XML → simulation
  and reconstruction validation workflow; leave schema and generator choices open.
- Establish simulation-relevant fidelity and observable-specific accuracy targets
  without inventing numerical tolerances or selecting detector technologies.
- Replace the provisional tracker-centred roadmap with full-detector M1–M7
  stages. Architecture work includes all systems from M1; stages are not rigid
  serial scheduling. Proposed DES-001/002 retain their pixel-case meanings.
- Broaden validation to calorimeter showers/containment, muon coverage, fields,
  subsystem interfaces and response assumptions alongside tracking checks.
- Link existing public source registers. No scientific parameters or new source
  facts were extracted, and no new manifest entries were needed.
- Preserve M0 restrictions and human sign-off gates. Scope authorization is not
  design sign-off; production geometry and reconstruction remain unchanged.

## Commands and validation

- Inspected repository instructions, project statement, relevant draft governance,
  branch, working tree and diff.
- `python3 -B -m unittest discover -s tools/session_logging -p 'test_*.py' -q`:
  15 tests passed, including documentation links.
- `git diff --check`: passed.
- Session schema validation is recorded in the paired JSON after execution.

These checks validate documentation/logging structure, not detector performance.

## Changes and revision links

Changed [PROJECT.md](../../PROJECT.md) and this session's Markdown/JSON pair.
The JSON contains the exact inventory. No commit or PR was created.

## Follow-up

Review the provisional full-detector roadmap. Select and characterize the ODD
baseline under M0. Technology choices, numerical accuracy targets, generator
architecture and subsystem designs still require dedicated proposals and human
review/sign-off before production implementation.

## Token usage recovered — 2026-09-24

Recovered local client-reported counters for 1 disjoint turns: **1,054,133 input** and **6,092 output** tokens. Cached input and reasoning output are subsets, not additions. Request-to-task matching and counter evidence are retained in [the recovery inventory](../usage/USAGE-2026-09-24-local.json).

This dated correction supersedes earlier statements that token counts were unavailable for these turns. Original narrative and limitations are preserved. It does not establish complete coverage across machines; unmatched and branch-only turns remain explicit in the inventory.
