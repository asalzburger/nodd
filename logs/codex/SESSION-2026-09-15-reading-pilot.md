# SESSION-2026-09-15-reading-pilot — ATLAS Pixel and RD53A pilot

## Scope and evidence

User-authorized M0 reference extraction and broad reading/map pilot. The initial
working tree had the previous planning-session pair untracked; it was preserved.
The starting revision and file inventory are recorded in the paired JSON.

## Selected conversation

User, exact: "I agree with this plan, go ahead with the first step, ATLAS Pixel TDR
and RD53A manual."

User, exact: "Also suggest (if you can't create) a new local git branch and a PR
description associated with it. Let's run this as a test case. Once read through
we will go by (3.) of your plan focussing it."

Assistant, paraphrase: create a local branch, build reusable local extraction and
page rendering, map both documents, check identity/quality, and prepare a PR
body. Keep focused engineering fact extraction for the next user-directed pass.

## Decisions, findings and outcomes

- Created branch `m0/reference-reading-pilot`. Sandbox branch creation first failed;
  an approved retry succeeded. No commit, push or remote PR was performed.
- Added ADR-005 as DRAFT; direct task authorization does not confer formal sign-off.
- Installed pinned PyMuPDF 1.28.2 in an ignored local environment. The first
  package install failed on sandbox DNS; approved network retry succeeded.
- Extracted all 482 Pixel TDR and 79 RD53A pages with text blocks, outlines,
  nullable embedded labels, quality flags and hash-verified reusable caches.
- Added literal search with whitespace/ligature normalization and selected renders.
  The normalization change produced new cache identities; initial caches were
  retained. Final measurements refer to the final extractor hash.
- Mapped major sections, skimmed selected openings, visually checked 14 selected
  pages across the documents. This is not a full scientific cover-to-cover review.
- Verified local document identity/version, added public source metadata and
  identified stale contents destinations, duplicated cover text and table/diagram
  extraction limits. The guides retain exact PDF and printed-page locators.
- Pixel: creation 2018-06-15, submission 2018-07-10, report ID includes 2017.
  RD53A: v3.51 dated 2019-08-19; actual title date differs from public index label.
  Record differing metadata explicitly; no design parameter is chosen from it.
- CDS pages returned bot challenges. Public ATLAS and university pages were
  accessible; public/local PDF byte equality was not asserted.
- Added report JSON/Markdown, reader commands, document guides and a local PR body.

## Commands and actual results

- `git switch -c m0/reference-reading-pilot`: initial exit 128 (sandbox); approved retry exit 0.
- `uv --cache-dir /tmp/nodd-uv-cache venv --python python3 reference/cache/venv`: exit 0; Python 3.14.0.
- `uv --cache-dir /tmp/nodd-uv-cache pip install --python reference/cache/venv/bin/python -r tools/reference_reading/requirements.txt`: initial exit 2 (DNS); approved retry exit 0, PyMuPDF 1.28.2.
- `reference/cache/venv/bin/python tools/reference_reading/read.py extract SRC-ATLAS-TDR-030`: exit 0; 482 pages, 285 bookmarks, 17 empty-text pages.
- `reference/cache/venv/bin/python tools/reference_reading/read.py extract SRC-RD53A`: exit 0; 79 pages, no bookmarks, no empty-text pages.
- Repeated those commands: verified cache hits, about 0.116 s and 0.017 s;
  final first extraction about 7.034 s and 1.008 s. Single local runs, not token savings.
- `read.py render` used page lists retained in the report, using the same venv
  Python and script path as above. Selected images inspected via the image-view tool.
- `reference/cache/venv/bin/python tools/reference_reading/check_pilot.py`: exit 0;
  four known-answer retrieval checks plus contiguous coverage and RD53A footer checks.
- `reference/cache/venv/bin/python -B -m unittest discover -s tools/reference_reading -p 'test_*.py' -v`: final seven tests passed.
- `python3 -B -m unittest discover -s tools/session_logging -p 'test_*.py' -v`: 15 tests passed, including documentation links.
- `python3 -B -m unittest discover -s tools/reference_downloads -p 'test_*.py' -v`: four tests passed.
- `git diff --check`: exit 0.
- Git exclusion checks over current cache files and pilot PDFs: all ignored;
  `git ls-files -- reference/cache/ 'reference/pdfs/*.pdf'` returned no tracked files.

## Changes, provenance and review

See the paired changed-file inventory. Source PDF bytes/receipts are unchanged.
The manifest updates SRC-ATLAS-TDR-030 and SRC-RD53A identity and public references;
adds SRC-PYMUPDF-DOCS, SRC-PYMUPDF-PACKAGE, SRC-ATLAS-TDR-INDEX and
SRC-UNIGE-ITK-INDEX for implementation and metadata provenance. No detector FACT
records, DES parameters or approval states changed. ADR-005 awaits human review.

The machine-readable report retains base commit, branch, configuration, source
and extractor hashes, cache metadata hashes, timings and render hashes. Result
commits remain empty until a commit exists. The local PR description is in
`docs/validation/reference-reading-pilot-pr.md`.

## Follow-up and limitations

Proceed next with the user's focused engineering questions using the maps and
original-page checks. Empty-text pages other than sampled blanks, complete table
semantics, OCR need and public/local byte equality remain unresolved. Exact client
version, model identity, thread/turn IDs and token counters are not exposed.
Session validation is repeated after completing this record.
