# ATLAS/CMS whole-detector overview intake

- Date: 2026-09-16
- Related: ADR-005 (DRAFT); direct user-supplied references, no linked issue
- Branch: `m0/reference-reading-pilot`
- Base revision: `671bb0e81bf432dfc797bd47c4f5b94e374ebd85`
- Exact provenance/results: [JSON](overview-reading.json)

## Outcome

Acquired the two newly supplied overview papers using the existing downloader.
The first sandboxed attempt failed; the approved network retry succeeded.
Both receipts are retained without overwriting prior evidence:
[first attempt](../../reference/downloads-2026-09-16-overviews-attempt1.json),
[successful acquisition](../../reference/downloads-2026-09-16-overviews.json).
The user's download instructions were preserved unchanged by this task.

| Source | Pages | Bookmarks | Extraction seconds | Verified load seconds |
| --- | ---: | ---: | ---: | ---: |
| SRC-ATLAS-JINST-2008 | 437 | 258 | 7.710 | 0.0804 |
| SRC-CMS-JINST-2008 | 361 | 142 | 5.051 | 0.0583 |

Timings are single local measurements, not end-to-end reading speedups.
The existing pinned Python/PyMuPDF environment and reader were reused unchanged.
Exact source/tool hashes, versions and cache locations are in the JSON.

Both title pages were visually checked: publication date 2008-08-14, collaborations,
titles and journal identifiers. ATLAS PDF 31 / printed 1 and CMS PDF 29 / printed 2
were inspected to check body navigation. Four known-answer retrieval assertions
passed, as did contiguous page coverage for each source. No empty-text or
replacement-character pages were reported. This is not PDF-conformance validation.

## Reproduction

Use a new receipt name if acquiring again; the downloader refuses to overwrite
receipts and checks existing PDFs rather than replacing them.

```sh
python3 tools/reference_downloads/download.py --only ATLAS CMS --receipt reference/downloads-YYYY-MM-DD-overviews.json
reference/cache/venv/bin/python tools/reference_reading/read.py extract SRC-ATLAS-JINST-2008
reference/cache/venv/bin/python tools/reference_reading/read.py extract SRC-CMS-JINST-2008
reference/cache/venv/bin/python tools/reference_reading/read.py render SRC-ATLAS-JINST-2008 1 31
reference/cache/venv/bin/python tools/reference_reading/read.py render SRC-CMS-JINST-2008 1 29
```

The coverage/retrieval assertions run for this report are reproducible as follows:

```sh
reference/cache/venv/bin/python -B - <<'PY'
import json, sys
sys.path.insert(0, 'tools/reference_reading')
import read
for name, count, queries in [
    ('ATLAS', 437, [('Magnet system and magnetic field', 49),
                    ('Integration and installation', 287)]),
    ('CMS', 361, [('Superconducting magnet', 33),
                  ('Detector infrastructures and safety', 310)])]:
    _, directory, metadata = read.load_cache(read.ROOT, f'SRC-{name}-JINST-2008')
    pages = json.loads((directory / 'pages.json').read_text())
    assert [p['pdf_page'] for p in pages] == list(range(1, count + 1))
    for query, expected in queries:
        assert expected in [h['pdf_page'] for h in read.search(directory, query, 1000)]
PY
```

## Reading scope and next use

See the [ATLAS map](../../reference/guides/SRC-ATLAS-JINST-2008.md) and
[CMS map](../../reference/guides/SRC-CMS-JINST-2008.md) for sampled reading coverage.
Major chapters were mapped from bookmarks; no complete scientific review or
quantitative table extraction is claimed. Public/local byte equality was not
checked. Source PDFs, extracted full text and rendered pages remain ignored.

Use the whole-detector maps to frame later component questions, retaining a clear
boundary between original detector descriptions and upgrade TDRs. No detector
parameters, generator architecture, geometry or approval state were changed.
