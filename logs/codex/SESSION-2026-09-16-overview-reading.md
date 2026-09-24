# SESSION-2026-09-16-overview-reading — ATLAS/CMS overview intake

## Request and scope

User, exact: “Ok, the new ATLAS/CMS JINST overview papers are loaded”.
Continued the established reference-intake workflow using the new entries in the
user's download instructions. Preserved that file and all prior working changes.
Start commit, branch and initial changes are captured in paired JSON.

## Outcomes and provenance

Downloaded the two papers with the existing downloader. Initial sandboxed network
attempt failed; approved retry succeeded. Both receipts remain in Git-visible
files. Local PDF filenames are ATLAS.pdf and CMS.pdf, source IDs are
SRC-ATLAS-JINST-2008 and SRC-CMS-JINST-2008. Titles, collaborations, journal IDs
and publication date were checked on rendered title pages; SHA-256 checksums are
in the catalogue and receipts. No public/local byte equality claim is made.

Extracted 437 ATLAS and 361 CMS pages, mapped major chapters and skimmed selected
opening passages. Visually inspected ATLAS PDF 1/31 and CMS PDF 1/29. Added reading
guides and separate validation evidence. Updated the coverage assessment and
ADR-005 draft scope. No scientific parameters, geometry, generator design or
human approval state changed. No commits or remote publication were made.

## Commands and validation

Exact download commands and results are in paired JSON. Extraction/render commands
and reproducible retrieval assertions are in the
[overview report](../../docs/validation/overview-reading.md).
Four known-answer retrieval checks, contiguous page coverage and verified cache
loading passed. Fifteen logging/document-link tests passed; whitespace checks
passed. Session validation result is recorded in paired JSON.
No extraction or downloader implementation changed, so their existing synthetic
suites were not rerun. Full text, PDFs and renders remain ignored local artifacts.

## Limits and follow-up

These papers describe the original 2008 detector configurations. Use later upgrade
TDRs for RD53-era designs. Whole-document mapping is not a cover-to-cover review.
Read targeted sections for physical facts and justified simulation approximations
before choosing parameters. Exact token counts and client/model details are not
available. ADR-005 remains DRAFT; no sign-off requested by this intake task.

## Token usage recovered — 2026-09-24

Recovered local client-reported counters for 1 disjoint turns: **1,458,733 input** and **5,830 output** tokens. Cached input and reasoning output are subsets, not additions. Request-to-task matching and counter evidence are retained in [the recovery inventory](../usage/USAGE-2026-09-24-local.json).

This dated correction supersedes earlier statements that token counts were unavailable for these turns. Original narrative and limitations are preserved. It does not establish complete coverage across machines; unmatched and branch-only turns remain explicit in the inventory.
