# M0-CMS-TRACKER-READING — CMS Tracker TDR extension

- Date: 2026-09-16
- Governing proposal: [ADR-005](../decisions/ADR-005-reference-reading-pilot.md), DRAFT
- Issue: none; direct user request to read CMS before focused extraction
- Branch: `m0/reference-reading-pilot`
- Base commit: `671bb0e81bf432dfc797bd47c4f5b94e374ebd85`; prior pilot changes present
- Evidence: [machine-readable results](cms-tracker-reading.json)
- Output: [CMS reading guide](../../reference/guides/SRC-CMS-TDR-014.md)

## Outcome and provenance

The existing reader extracted all 353 pages and 160 bookmarks. The catalogue's
source checksum was verified, local title/identifiers were visually checked, and
four selected renders inspected. This extends the two-source pilot without
changing its code or replacing its earlier evidence.

Python 3.14.0, PyMuPDF/MuPDF 1.28.2; exact source and reader hashes are in the JSON.
The single local extraction took 5.794 seconds; verified cache reuse took 0.0963
seconds. These measure extraction/reuse only, not scientific reading speed.
No stochastic calculation or random seed applies.

Four literal retrieval checks passed (expected page must be among returned hits):

| Query | Expected PDF page |
| --- | ---: |
| high density interconnect | 74 |
| Pixel readout chip specifications | 82 |
| large scale demonstrator chip | 251 |
| Shunt-LDO and on-detector powering | 252 |

All page indices were contiguous from 1 through 353. No replacement-character
pages were reported; PDF 10 and 142 have empty extracted text. Neither empty
page was visually checked. No OCR or full PDF-conformance validation was run.

## Commands and reproduction

From the repository root with the existing pinned environment:

```sh
reference/cache/venv/bin/python tools/reference_reading/read.py extract SRC-CMS-TDR-014
reference/cache/venv/bin/python tools/reference_reading/read.py extract SRC-CMS-TDR-014
reference/cache/venv/bin/python tools/reference_reading/read.py search SRC-CMS-TDR-014 RD53 --limit 100
reference/cache/venv/bin/python tools/reference_reading/read.py render SRC-CMS-TDR-014 1 74 82 251
```

The following assertions were run successfully against the cached source:

```sh
reference/cache/venv/bin/python -B - <<'PY'
import json, sys
sys.path.insert(0, 'tools/reference_reading')
import read
_, directory, metadata = read.load_cache(read.ROOT, 'SRC-CMS-TDR-014')
pages = json.loads((directory / 'pages.json').read_text())
assert [p['pdf_page'] for p in pages] == list(range(1, 354))
for query, expected in [('high density interconnect', 74),
                        ('Pixel readout chip specifications', 82),
                        ('large scale demonstrator chip', 251),
                        ('Shunt-LDO and on-detector powering', 252)]:
    assert expected in [h['pdf_page'] for h in read.search(directory, query, 1000)]
PY
```

Rendered pages 1, 74, 82 and 251 were opened and inspected: title/date/stamp,
module interfaces, target chip specifications, and RD53A demonstrator context.
These are selected checks; a render succeeding alone is not evidence of review.

## Reading limits and unresolved questions

The guide records exact reading coverage and separates proposed chip requirements,
prototype descriptions, earlier-chip measurements and simulation assumptions.
The TDR's planned submission dates disagree; both locators remain recorded and
no historical submission date is selected. Current production qualification is
outside this source's demonstrated scope.

Direct access to the public CDS record/files encountered a bot challenge. Local
PDF access was sufficient for this task. Search-index metadata was not used to
assign a public version or redistribution license; those and byte equality remain
unverified. The local cover date and stamp are recorded separately.

No detector geometry, material, reconstruction settings or sign-off changed.
No detailed cross-experiment parameter table is claimed. The next focused pass
can use the ATLAS and CMS maps with the later RD53A manual, then identify which
production sources are needed. See the [session record](../../logs/codex/SESSION-2026-09-16-cms-tracker-reading.md)
for documentation/logging checks and the changed-file inventory.
