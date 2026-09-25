# SESSION-2026-09-16-reading-pr — Reading infrastructure PR

## Request and scope

User, exact: “ok, let's make this a PR as it is a good break point.”
Prepared the accumulated M0 reference-reading work for publication on the existing
branch. Initial changes in paired JSON cover all preceding pilot work and the
user's newly supplied public-reference download instructions. No unrelated work
was discarded. No detector design approval is implied by creating a PR.

## Review and preparation

Reviewed the reader implementation, accumulated diff and documentation. Updated
the PR description to cover all five documents (1,712 pages), the source maps,
provenance, literature coverage assessment and curated session records. Corrected
the documentation index and page-label wording to reflect the expanded scope.
PDFs, caches, renders and environment files remain ignored. ADR-005 remains DRAFT.
No linked issue; direct human task authorization.

## Validation

All 26 automated tests passed: 7 reader, 15 logging/document-link and 4 downloader.
Re-ran all 12 known-answer retrieval checks across five documents, contiguous
page coverage and RD53A footer checks. Cache/source verification passed.
Whitespace checking passed. Exact commands/results are in paired JSON.
GitHub lookup initially failed in the sandbox; approved retry found no existing
PR for the branch. Fetched origin successfully before publication.

## Publication

Committed the reviewed changes as `ec6413d` and pushed the branch to origin.
Created [PR #2](https://github.com/asalzburger/nodd/pull/2) against `main`; it remains
open for human review. This publication record is added in a follow-up commit.
Session validation passed for all 11 records. Token usage and client/model details
are unavailable.
The preceding task records preserve per-task changed files and provenance; this
record captures preparation and publication, not a second reading of the papers.

## Token usage recovered — 2026-09-24

Recovered local client-reported counters for 1 disjoint turns: **2,111,885 input** and **4,069 output** tokens. Cached input and reasoning output are subsets, not additions. Request-to-task matching and counter evidence are retained in [the recovery inventory](../usage/USAGE-2026-09-24-local.json).

This dated correction supersedes earlier statements that token counts were unavailable for these turns. Original narrative and limitations are preserved. It does not establish complete coverage across machines; unmatched and branch-only turns remain explicit in the inventory.
