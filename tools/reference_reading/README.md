# Reference reading pilot

Governed by [ADR-005](../../docs/decisions/ADR-005-reference-reading-pilot.md),
DRAFT, with explicit user authorization for this M0 pilot. See the
[measured report](../../docs/validation/reference-reading-pilot.md) and
[document guides](../../reference/guides/README.md).

## Environment

Python 3.10 or later and the pinned dependency in `requirements.txt` are required.
The pilot used Python 3.14.0 on macOS arm64. Create an ignored local environment:

```sh
python3 -m venv reference/cache/venv
reference/cache/venv/bin/python -m pip install -r tools/reference_reading/requirements.txt
```

Alternatively, with an existing uv installation:

```sh
uv --cache-dir /tmp/nodd-uv-cache venv --python python3 reference/cache/venv
uv --cache-dir /tmp/nodd-uv-cache pip install --python reference/cache/venv/bin/python -r tools/reference_reading/requirements.txt
```

The PyMuPDF package/API sources and license note are catalogued as
SRC-PYMUPDF-PACKAGE and SRC-PYMUPDF-DOCS. This dependency is used only by the
reference-reading tooling; no detector dependency changes are made.

## Extract, search, inspect

Run from the repository root:

```sh
reference/cache/venv/bin/python tools/reference_reading/read.py extract SRC-ATLAS-TDR-030
reference/cache/venv/bin/python tools/reference_reading/read.py extract SRC-RD53A
reference/cache/venv/bin/python tools/reference_reading/read.py search SRC-ATLAS-TDR-030 'Breakdown of material budget'
reference/cache/venv/bin/python tools/reference_reading/read.py search SRC-RD53A 'Floorplan and Organization'
reference/cache/venv/bin/python tools/reference_reading/read.py render SRC-RD53A 1 5 10
```

All page arguments and search results use **one-based PDF pages**. Embedded PDF
labels are separate nullable fields; neither of the original two pilot documents
supplies them, while the JINST overviews do.
Use the curated guides for printed-page mappings. In particular, RD53A's printed
contents are stale; do not use its contents page numbers as actual destinations.

Cache identity includes the PDF bytes, script hash, dependency/runtime versions
and settings. Re-running `extract` verifies existing artifact hashes and reports
a cache hit. Changed inputs produce a new directory; old caches remain. A
mismatched source hash or corrupt cache fails visibly without automatic repair.
Cache metadata itself is a local integrity index, not a signed trust anchor.

Each page has UTF-8 text and a JSON list of text blocks (bounding boxes and block
metadata). `pages.json` maps files to PDF pages, records character/empty-text
flags, raster image-reference counts and dimensions in PDF points. This is not
an inventory of all vector figures or validated table cells. `outline.json`
contains bookmarks as supplied by the PDF. `metadata.json` records provenance
and artifact hashes. Selected 120 dpi renders are regenerable aids; inspect at
higher resolution separately if labels are unreadable. Renders are outside the
text-artifact hash list and their command output provides individual hashes.

Search is case-insensitive literal phrase matching with whitespace and Unicode
compatibility normalization for ligatures. It returns at most one excerpt per
matching page, in page order, with a default limit of ten pages. It does not
rank relevance, join split hyphenated words, correct OCR, or parse equations.
Use `--limit` when the useful technical page follows contents/index matches.
No semantic/vector service, PDF upload, or OCR is involved.

## Verification

```sh
reference/cache/venv/bin/python -B -m unittest discover -s tools/reference_reading -p 'test_*.py' -v
reference/cache/venv/bin/python tools/reference_reading/check_pilot.py
python3 tools/session_logging/session_log.py validate
```

`check_pilot.py` requires the two catalogued local PDFs and current caches and
checks known-answer retrieval/page locations. Synthetic tests need neither PDF.
Raw text, renders and environments remain under ignored `reference/cache/`.
Commit only concise guides and measured evidence. Extracted text is a navigation
aid, not an approved detector fact or a substitute for the original page.
