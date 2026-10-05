# SESSION-2026-09-17-pixel-modules — RD53 pixel-module alternatives

## Scope and evidence

Contemporaneous curated record. Started from clean main
60ef36631849f4d7525324550f1d2a8a17ef67fe, on branch
`design/rd53-pixel-modules`. Exact client/thread identity, conversation start time,
and token counts are unavailable. Related IDs: DES-001, DES-003, ADR-006, issue #7.
M0 is not declared complete; this is design drafting only.

## Selected conversation

User request (paraphrase): start Tracker design with pixel modules around the RD53
chip in hand; Tracking Engineer may delegate two alternative designs; prioritize
reusable structures, few types, low material and realism. Public ATLAS/CMS TDRs
may inform a stand-alone proposal. Draw both options and involve Project Coordinator
in a balanced recommendation.

Assistant clarification: identify the exact stock RD53 variant and revision.
User asked which question remained open; assistant explained that die, matrix,
pad and services depend on that identification. No inventory answer yet recorded.

## Decisions and outcomes

Tracking Engineer delegated independently to compact and quad module agents.
Their inputs and original SVG schematics are integrated in DRAFT DES-001.
Project Coordinator independently reviews comparative tradeoffs and programme
priority. AI role recommendations do not confer human approval.

Conditional RD53A examples cite manual v3.51, which explicitly gives 11.6 mm
height; CDS abstract gives 11.8 mm. Neither becomes a certified stock dimension.
Preserve discrepancy and require inventory drawings. Public assembly paper adds
real quad manufacture/testing precedent, without importing experiment geometry,
source numerical qualification criteria, or implying nODD hardware validation.

Dashboard tracks TASK-C-PIX as active drafting in parallel with architecture.
Stage B dependencies still govern final interfaces/family selection and integration.
No production geometry, materials or reconstruction configuration changed.

## Commands and validation

- `git fetch origin main`, branch inspection and `git switch -c design/rd53-pixel-modules`.
- `gh issue create --title 'Design reusable RD53 pixel-module alternatives' --body-file /tmp/nodd-pixel-issue.md`: initial sandbox network failure; escalated retry succeeded, issue #7.
- Public manual browsed; screenshot and arXiv web fetch failed. Public arXiv PDF
  download: sandbox DNS failure, escalated retry succeeded. Optional PyMuPDF
  inspection failed (module unavailable); installed `pdftotext -layout` succeeded.
  Public paper title, assembly/tests and PDF7 license/results inspected. No PDF committed.
- Initial dashboard validation/tests ran before Coordinator file existed and failed
  on that missing declared deliverable. Repeat after completion is recorded below.
- Session-logging unit suite: 15 tests passed.
- Both SVGs parsed as XML and have accessible title/description. These are original
  not-to-scale concept schematics; no engineering dimensions inferred from pixels.

Final repeat: dashboard validation passed (11 tasks, 8 documents, 3 existing formal
review rounds); build succeeded; dashboard 25 tests passed. All four design Markdown
files local links exist, both SVG XML parses and whitespace checks pass.

## Changes and revision links

Changed-file inventory and actual completed check results are in the paired JSON.
The enclosing Git history identifies the result revision without self-reference.

## Follow-up

Identify stock chip/revision, human inventory owner and reviewers; define pixel
volume, fluence/rate/lifetime and service boundary conditions; quantify routed BOM,
material maps, sensor seams, yield and thermal comparisons. Human design approval
must precede production integration. No hardware or detector-performance acceptance claimed.

Session validator initially rejected lowercase check-status values; corrected to
PASS/FAIL, then validated all29records. No exact token counts available.
