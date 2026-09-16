# PR title

Add reusable literature reading tools and ATLAS/CMS source maps

## Summary

The reference collection had download checksums but no reusable page text or
navigation maps. Add a pinned local PDF reader with extraction, literal search,
selected rendering and hash-verified cache reuse, plus guides for five documents:
ATLAS Pixel TDR, CMS Tracker TDR, RD53A manual, and the ATLAS/CMS JINST overviews
(1,712 pages in total).

The guides record source versions, physical/printed page mappings, reading
coverage and caveats, including RD53A's stale contents and the distinction between
TDR requirements, prototype hardware and simulation assumptions. Whole-detector
maps and a literature-coverage assessment frame realistic component use for
simulation. Source metadata, overview acquisition receipts and curated session
records preserve provenance; PDFs, full text, renders and environments stay ignored.

## Scope and governance

- M0 infrastructure and literature work, on `m0/reference-reading-pilot`.
- ADR-005 remains DRAFT; related logging workflow: ADR-004.
- Direct user requests; no linked issue.
- No detector geometry, material, reconstruction configuration or sign-off changes.
- DD4hep/XML generation remains a future discussion.

## Validation

- 7 synthetic reader tests, 15 logging/document-link tests and 4 downloader tests.
- 12 known-answer retrieval checks across the five local documents, with
  contiguous page coverage and the original RD53A footer checks.
- Source/cache hash verification and selected rendered-page inspections.
- Session-record validation and `git diff --check`.

Exact results, source/tool versions, hashes and measured timings are retained in:

- [Original pilot](reference-reading-pilot.md) and paired JSON.
- [CMS Tracker extension](cms-tracker-reading.md) and paired JSON.
- [Overview intake](overview-reading.md) and paired JSON.

These are extraction and sampled-reading checks, not a complete scientific review.
No OCR, validated table transcription or public/local PDF byte comparison is
claimed. PyMuPDF licensing is recorded in the catalogue. Review cache provenance,
page navigation and reading limits before the next focused evidence pass.
