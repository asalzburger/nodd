# SESSION-2026-09-16-resource-coverage — Subsystem literature coverage

## Scope and selected conversation

User clarification, paraphrased: the two RD53 inputs mean ATLAS and CMS use in
their designs. User asked whether equivalent resources exist for strips,
calorimeters and muons. This task assessed availability; it did not authorize
subsystem implementation or a full extraction campaign.

## Outcomes

Inspected the catalogue, local PDF title text and selected contents bookmarks.
Identified already-local ATLAS/CMS strip, calorimeter and muon upgrade sources,
plus two RD53C manuals. Recorded available material, verification limits and
missing construction/qualification evidence in
[the coverage assessment](../../docs/validation/literature-coverage.md).
Existing uncommitted reading-pilot changes were preserved. No source metadata
verification state or sign-off was advanced. No commits or downloads were made.

## Commands and checks

Used Python/json to inspect the catalogue and pinned PyMuPDF to read title pages
and selected outlines. Web search checked official TDR indexes and original
calorimeter source availability. An exploratory CMS search used a guessed report
number; local title inspection established CMS-TDR-016 as the muon report.
No guessed identifier was added to the catalogue.

Ran session validation and the logging/document-link tests; results are recorded
in paired JSON. This was a documentation assessment, with no geometry tests.

## Provenance and follow-up

Start revision, branch, initial changes and changed files are in paired JSON.
Exact token counts and client/model metadata are unavailable. The assessment
links the existing source catalogue and public ATLAS TDR index. Source-reading
coverage remains limited to the explicitly identified title/outline checks.

Begin further extraction with local sources; collect missing construction and
production references per subsystem. ADR-005 remains DRAFT; no human sign-off
is requested for this availability assessment.
