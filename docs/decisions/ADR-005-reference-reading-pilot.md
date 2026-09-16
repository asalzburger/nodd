# ADR-005 — Reusable reference reading pilot

- Status: DRAFT
- Created: 2026-09-15
- Human owner: TBD
- Issue: None; direct user request for this pilot
- Related: [ADR-004](ADR-004-session-logging-and-traceability.md)
- Approval evidence: Pending; task authorization does not constitute ADR sign-off

## Context and scope

The user authorized a first extraction/reading pass on the ATLAS Pixel TDR and
RD53A manual, followed later by focused engineering questions. This is M0
literature infrastructure; no detector design parameters are selected here.

On 2026-09-16 the user extended this pilot to the CMS Tracker TDR to provide
a second experimental input on RD53 usage before the focused pass. See the
[CMS reading report](../validation/cms-tracker-reading.md). ADR status remains DRAFT.

## Proposed decision

**NODD DESIGN CHOICE:** use a pinned PyMuPDF environment for local page-text,
outline and page-label extraction, plus selected page rendering. Its API is
documented by source SRC-PYMUPDF-DOCS in the source catalogue. Keep source PDFs,
full extracted text, renders and the environment ignored; commit tools, curated
guides and compact validation evidence. Alternatives are a text-only extractor
plus a separate renderer, or manual reading without reusable extraction.

Key caches by PDF SHA-256, extraction script hash, Python/PyMuPDF/MuPDF versions
and extraction settings. Verify artifact hashes on reuse. A source mismatch or
corrupt cache is an error; never silently replace accepted evidence. New inputs
produce new cache directories. Store one-based PDF page numbers separately from
embedded PDF page labels, which must not be assumed to equal printed labels.
Keep text blocks with bounding boxes to aid checking reading order.

Extract all pages, then inspect title/contents pages and representative technical
pages. A document map is not a claim that every paragraph has been scientifically
reviewed. Text extraction, page inspection, and fact verification have distinct
coverage records. No OCR is included in this pilot; flag empty/problematic text.

## Verification and next step

Use synthetic PDF tests for provenance, cache reuse/corruption, page indexing,
search and rendering. Run the two actual PDFs and retain commands, environment,
page counts, selected visual checks, retrieval checks and measured timings in
[the pilot report](../validation/reference-reading-pilot.md).

The next human-directed pass will use the guides to pose focused engineering
questions, verify exact source locators and create fact/inference/design records.
Open: human review, OCR need on future sources, and broader platform validation.

## Whole-detector context extension (2026-09-16)

The user supplied the ATLAS/CMS JINST overview papers after clarifying the
simulation-realism objective. The existing workflow was reused for acquisition,
identity checks, extraction and chapter maps; see the
[overview intake report](../validation/overview-reading.md). This does not select
a detector design or generator architecture; ADR status remains DRAFT.
