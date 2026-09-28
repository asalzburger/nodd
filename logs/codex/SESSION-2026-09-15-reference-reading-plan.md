# SESSION-2026-09-15-reference-reading-plan — Reusable reference reading

## Scope and evidence

Planning consultation during M0; no PDF extraction or scientific reading was
performed. The starting revision and clean initial working tree are recorded
in the paired JSON. The reference guide reports 14 acquired PDFs whose title
pages and bibliographic metadata still need verification.

## Selected conversation

User, exact: "Now, there's a lot of material to read (and there will be more), all
the TDRs, etc."

User, exact: "Suggest how you would scan this and make it available for later
passes (that should be quicker)."

Assistant proposal, paraphrased below: extract once, retain searchable local
caches, and maintain concise evidence maps and verified claims in Git. Later
passes retrieve relevant original pages rather than relying solely on summaries.

## Proposed workflow

1. Inventory/title-page verification: confirm identity, edition, dates, canonical
   public URLs and licensing metadata. Preserve supplied-label discrepancies.
2. Mechanical extraction: cache text page by page, document structure, page
   labels and figure/table references. Record source SHA-256, extractor version
   and settings; use selective OCR/rendering for failed or visual extraction.
3. Broad triage: produce a concise map for each source, with useful chapters,
   project topics, page locators, extraction limitations and explicit reading
   coverage. A mapped or searched section is not a fully reviewed section.
4. Focused evidence reading: begin with the pixel-module vertical slice; read
   relevant pages across pixel/tracker TDRs and RD53 manuals. Verify dimensions,
   tables, figure annotations and footnotes against rendered originals.
5. Curate stable claim IDs in Git: source ID/hash, page index and printed page,
   section/table/figure, value/units, context, applicability, uncertainty,
   verification method and provenance classification. Only checked source
   statements become FACT records; derivations and choices remain separate.
6. Maintain cross-source topic maps, contradictions and supersession links.
   Distinguish planned/TDR, prototype, measured, and production evidence rather
   than automatically promoting the newest or best-looking number.
7. Query workflow: topic map, candidate passages, original-page verification,
   then a reusable claim/design update. Summaries are navigation aids, not the
   normative source. Keyword search is the first index; semantic indexing is
   deferred unless measured retrieval misses justify it.

## Storage and invalidation

Proposed Git artifacts: `reference/manifest.yaml`, `reference/guides/`,
`reference/claims/`, `reference/topics/`, extraction tooling and session records.
Proposed ignored, regenerable artifacts: `reference/cache/` containing extracted
text, page renders, OCR and search indexes. No full-text or figure redistribution
is implied. These directories are proposals, not created by this consultation.

Cache keys include source bytes, extractor/version and configuration. Summary
provenance includes input hashes and method/model/prompt version when exposed.
PDF replacements get new hashes; retain prior evidence and flag dependent claims
for rechecking rather than silently relinking them. Extractor-only changes do
not automatically invalidate source facts; assess whether their locators or
extraction evidence changed. Track stale guides and indexes separately.

## Validation and measurement plan

Pilot on the ATLAS pixel TDR plus RD53A manual. Check page coverage, heading
boundaries, table reading order and printed-page mapping on selected original
pages. Include known-answer retrieval questions to measure whether the index
finds the right evidence. Measure extraction/retrieval elapsed times, cache
hits, unresolved extraction failures and usage only when actually exposed.
Do not present a speedup or token-saving estimate as measured evidence.

## Outcomes and follow-up

This is an unapproved infrastructure proposal, not a detector design or a claim
that the PDFs have been read. No dependencies installed, cache/index built,
source claims extracted or approval states changed. If implemented, first draft
an ingestion/reading ADR and pilot a small corpus before scaling to all sources.

## Commands and changes

- `git status --short --branch`: clean main at task entry.
- Read `reference/README.md` for current acquisition/verification state.
- Created this narrative and paired JSON with the session logging CLI.
- Session validation is run after completing the record; no detector tests apply.

Exact client version, model identity, token counters and start time are not
available. No commit or push is performed by this consultation.

## Token usage recovered — 2026-09-24

Recovered local client-reported counters for 1 disjoint turns: **348,040 input** and **2,105 output** tokens. Cached input and reasoning output are subsets, not additions. Request-to-task matching and counter evidence are retained in [the recovery inventory](../usage/USAGE-2026-09-24-local.json).

This dated correction supersedes earlier statements that token counts were unavailable for these turns. Original narrative and limitations are preserved. It does not establish complete coverage across machines; unmatched and branch-only turns remain explicit in the inventory.
