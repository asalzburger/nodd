# Reference catalogue and local PDFs

The [manifest](manifest.yaml) is the catalogue. It is JSON-formatted YAML 1.2,
readable with Python's standard `json` module. Entries distinguish acquired files from verified bibliographic metadata. The
ATLAS Pixel TDR, CMS Tracker TDR and RD53A manual now have identity checks and
[reading guides](guides/README.md); other supplied labels remain unverified.
No detector parameter claims have yet been adopted.

The user supplied [download instructions](pdfs/sources.md). These use CERNBox
share links; downloaded bytes stay in the ignored `pdfs/` directory. The
[acquisition receipt](downloads-2026-09-15.json) records the instruction-file hash,
per-file acquisition/check time, byte size and SHA-256 without copying share URLs.
The instructions themselves remain as supplied in the existing staged changes.

## Reproduce acquisition

From the repository root, choose a new receipt filename for each run:

```sh
python3 tools/reference_downloads/download.py --receipt reference/downloads-YYYY-MM-DD-run.json
```

Use `--only ATLAS-TDR-030 CMS-TDR-014` to select labels. The tool follows the
supplied URL conversion, uses HTTPS, rejects non-PDF headers and mismatched
Content-Length, and publishes each finished file without overwriting an existing
file. Existing files are hashed and explicitly recorded as local, not freshly
verified against the server. Receipts are never overwritten. Failed downloads
produce a nonzero exit and a sanitized error entry; partial files are removed.
Network access is required. A new receipt does not automatically replace the
catalogue's pinned hashes; compare and explain any differences before updating it.

```sh
python3 -B -m unittest discover -s tools/reference_downloads -p 'test_*.py' -v
```

## Verification limits and follow-up

All 14 supplied shares were acquired on 2026-09-15. Acquisition checks covered
PDF headers, response byte counts and hashes. The subsequent
[reading pilot](../docs/validation/reference-reading-pilot.md) extracted the
Pixel TDR and RD53A manual and checked selected rendered pages, including their
titles. The [CMS extension](../docs/validation/cms-tracker-reading.md) adds the
Tracker TDR and RD53 module context. Other acquired PDFs retain the initial
verification limits.

Before citing detector parameters, verify each document's title, collaboration,
report identifiers, version/date, canonical public publication URL and precise
page/section locators. Record license information when known. Auth-free download
access alone does not establish redistribution rights. No PDF redistribution is
authorized by this catalogue and no detector parameters have yet been adopted.

The subsequently supplied CMS MTD TDR (`CMS-TDR-020`) was acquired as
`pdfs/CMS-MTD-TDR.pdf`; its [separate receipt](downloads-2026-09-15-cms-mtd.json)
records the updated instructions hash. All five initially requested TDR labels
now have local files. CMS MTD title-page verification remains pending.
The extra reports/manuals are retained under their supplied labels for later
identification; their acquisition does not expand detector design scope.

## Read and reuse

Start with the [document maps](guides/README.md) and follow the
[extraction/search/render commands](../tools/reference_reading/README.md).
Full text and page images stay under ignored `reference/cache/`; curated guides,
provenance and measured evidence live in Git.

## Whole-detector overviews

The newly supplied 2008 ATLAS and CMS JINST papers were acquired on 2026-09-16,
identified from their title pages and extracted into reusable caches. Their
[reading maps](guides/README.md) distinguish the original detector configurations
from later upgrades. See the [intake report](../docs/validation/overview-reading.md)
for source checks, receipts and coverage limits.

## OpenDataDetector resources

The [ODD resource register](guides/ODD-resources.md) maps the public source,
releases, documentation, presentations and related datasets. It records a
revision-specific ignored study checkout and downloaded reading PDFs. This is
source discovery; selection/import of the nODD baseline remains under ADR-001.
