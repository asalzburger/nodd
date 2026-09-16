# M0-READING-PILOT — ATLAS Pixel / RD53A extraction pilot

- Status: CHARACTERIZATION; human review pending
- Date: 2026-09-15
- Governing proposal: [ADR-005](../decisions/ADR-005-reference-reading-pilot.md), DRAFT
- Branch: `m0/reference-reading-pilot`
- Issue: direct user task; no linked issue
- Exact base SHA, environment, input/tool hashes, timings and render hashes:
  [machine-readable evidence](reference-reading-pilot.json)
- Author: Codex-assisted pilot; no human sign-off recorded

## Result

All 561 pages were processed into reusable local page-text/block caches. Major
sections were mapped in [two curated guides](../../reference/guides/README.md).
Selected contents, opening passages and rendered pages were checked. This is
not a cover-to-cover scientific review or an accepted detector baseline.

| Measurement | ATLAS Pixel TDR | RD53A manual |
| --- | ---: | ---: |
| Physical PDF pages | 482 | 79 |
| Bookmark entries | 285 | 0 |
| Pages with empty extracted text | 17 | 0 |
| Pages with replacement characters | 0 | 0 |
| Initial extraction, seconds | 7.034 | 1.008 |
| Verified cache reuse, seconds | 0.116 | 0.017 |

These are single local measurements using Python 3.14.0 and PyMuPDF/MuPDF
1.28.2 on macOS arm64. They include source hashing and, on reuse, artifact
integrity checks; they exclude interpreter startup. OS file caches may be warm.
No inference about total reading time or token savings is made.

## Reading and quality findings

- Pixel TDR: local title page gives creation date 2018-06-15; public ATLAS index
  gives submission date 2018-07-10. Report ID includes 2017. Record these distinct
  dates rather than assuming the report-number year identifies this edition.
- RD53A: title page identifies version 3.51, 2019-08-19, a prototype manual.
  The university index date differs; the actual PDF version date is retained.
- Neither PDF supplies embedded page labels. RD53A's contents destinations are
  stale: Introduction points to printed page 1 but starts on printed page 3 / PDF 4.
  Actual headings and footers govern the guide. All RD53A footers on PDF 2–79
  were automatically checked against PDF-page-minus-one.
- Pixel bibliography: printed contents says 432; actual heading/bookmark is at
  printed 421 / PDF 443. The guide uses the heading, not that contents value.
- Pixel cover text has duplicated glyphs. Two sampled empty-text pages (2, 480)
  are visually blank; the other 15 remain flagged, not presumed blank.
- Table text and diagram labels are searchable, but spatial interpretation
  requires rendering. No numeric detector parameter has been extracted into a
  FACT/design record. No OCR, structured table extraction or full PDF-conformance
  checker was run.

## Visual checks actually performed

| Source | One-based PDF pages | Purpose |
| --- | --- | --- |
| Pixel TDR | 1, 3 | Cover/title, report IDs, collaboration and license |
| Pixel TDR | 2, 480 | Sampled empty-text pages are blank |
| Pixel TDR | 15, 199, 217 | Contents and body heading/printed-page navigation |
| Pixel TDR | 224 | Table 8.2 location and table layout versus extracted text |
| RD53A | 1 | Title, identifier, version and prototype scope |
| RD53A | 2, 4, 6 | Contents mismatch, actual headings and printed footers |
| RD53A | 5, 10 | Figure orientation and mixed schematic/table extraction limits |

Other rendered pages are marked as uninspected in the JSON evidence. Some
checks used the earlier cache before search normalization was added; final
renders use the same PDF bytes and rendering settings. No source content changed.

## Reproduction and checks

See [tool commands](../../tools/reference_reading/README.md). The exact extraction
commands are `read.py extract SRC-ATLAS-TDR-030` and `read.py extract SRC-RD53A`,
run with `reference/cache/venv/bin/python tools/reference_reading/read.py` from
the repository root. Each was repeated to measure verified reuse. Use `render`
with the page lists above to reproduce the inspected images. The JSON lists the
final cache paths, tool identities and artifact hashes. Cache keys change when
the extractor, interpreter, library or source changes; previous keys are retained.

Executed successfully:

- Seven synthetic-PDF unit tests: extraction/reuse, corruption detection, source
  mismatch, configuration invalidation, literal and ligature search, page rendering.
- `check_pilot.py`: contiguous page coverage and four known-answer retrieval checks.
  The material-table query locates Pixel PDF 224; hybridization locates PDF 199.
  RD53A floorplan search returns contents PDF 2 and actual PDF 6; power table PDF 8.
  These tests establish basic retrieval, not broad search recall or relevance ranking.

No random seed or numerical detector tolerance applies. Network access was
needed only for dependency installation and public metadata checks; extraction
and cache operations ran locally. PDFs and generated caches remain ignored.

## Follow-up

The pilot is ready for the user's focused engineering pass. Create exact
source-backed claim records then, preserving prototype/production distinctions
and relevant table context. Human review of ADR-005, the guides and evidence
remains pending. CDS catalogue access was blocked by a bot challenge; accessible
ATLAS and university public pages supplied the metadata checks. Public/local
PDF byte equality has not been established.
