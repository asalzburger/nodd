# SESSION-2026-11-04-baseline-comparison-pr — Publish baseline comparisons

## Scope and evidence

Start:c68158971970f29fa42741a028973dfe79d10574, branch
`codex/baseline-material-comparison`; clean worktree. Fetched main remains
62f6056395e0dfee0c7985cf24e88dc9919c4e2d, with ten unpublished commits containing
material mapping, crossing counts and Fatras comparisons. Scope: record the
current map, publish the package, account for available interactions and prepare
for human merge. No merge, new simulation, geometry change or runtime-default
replacement requested. DES-025, DES-043, ADR-003 and the three completed baseline
comparison tasks govern the evidence.

## Selected conversation

User, exact: “Please make a PR out of this - it confirms the 2 mm to be good.

Record the new material map.
Accounting and merge preparation.”

Assistant, paraphrase: publish the qualified whole-baseline results and current
map with accounting and checks. Record the user's support for retaining the
2 mm choice without inventing a formal design sign-off or claiming every
performance observable improves. Central relative-pT widths and forward100GeV
full tails remain visible.

## Decisions and implementation

The current averaged map is already retained, not merely local storage. Add a
named map record bound to source62f6056, compact/material/five-factory hashes,
compressed/decompressed map hashes, portal selection, inventories and independent
training/validation seeds. Preserve the old map and runtime defaults. Add an
analysis index and offline CI checks/replotting for all three comparisons.
The map record does not promote engineering or production acceptance.

Scientific data, simulation sources and original figure artifacts remain
unchanged from the separate assessments already recorded. A bounded SoftEng
review will inspect the new registration/verifier/CI at its committed revision.

## Actual checks and remedies

- Native-source/geometry/map/Fatras full-data and separate PhysVal checks are
  preserved in the three prior journals and reports; no native reruns here.
- New offline map verifier initially referenced `total_material_bins`; actual
  native report key is `material_bins`. Corrected the reader, preserving native
  evidence. Subsequent verifier passes67keys/8650bins/2003zero-thickness slabs.
- 19 material tests (including2new identity/grid rejection checks),5 hit tests
  and8 Fatras tests pass in the existing plotting environment:32 total.
- All three figure-replay commands completed successfully to ignored build
  outputs; original plots were not overwritten.
- Git main fetch completed; no upstream changes or conflicts observed.

## Accounting collection

The connected app inventory verifies this chat as
01a15e18-aee8-7080-a61e-ed35d0448960. Explicit read_thread calls recover the
three completed main turns for material/hits/Fatras and their corresponding
SoftEng/PhysVal child turns. Only allowlisted visible messages and operation
metadata will be curated; reasoning, arbitrary tool arguments/results and
private client state are excluded. Exact token counters and execution model
are not exposed by these app responses. Keep canonical usage arrays empty;
never create placeholder zero/all-null usage entries just to satisfy ledger
matching. The active publication turn's finalized counters are unavailable.
Counterless message evidence is retained separately with explicit account and
parent/child relationships; no allocation or double counting.

## Publication and closeout

PR number, public snapshot, source/blob audit, interaction synchronization,
required validators, hosted CI and merge-readiness state are recorded below
once observed. Only the user may grant formal design acceptance; merge itself
would not supply it.
