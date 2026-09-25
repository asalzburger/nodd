# SESSION-2026-09-16-odd-resources — ODD resource discovery

## Request and scope

User, exact: “Next step is to get familiar with the Open Data Detector - try to
find all necessary resources and either register where they are (and download
them for reading if print-style-only)”.

Started on main with a clean working tree after merge of PR #2. Start revision
is captured in paired JSON. Read repository rules, PROJECT.md, ADR-001/003 and
the M0 baseline specification. The task authorizes public resource discovery and
reading; no baseline selection, detector implementation or publication inferred.

## Outcomes

Registered 21 resources spanning ODD source/releases, presentations, TrackML
history, ACTS interfaces, DD4hep/Geant4/Key4hep documentation and ColliderML
paper/software/data. Downloaded and extracted four PDFs totalling 107 pages;
HTML resources are registered for web reading. Kept exact titles rather than
search snippets: the CTD deck is a combined GNN + CKF study, not an ODD manual.

Cloned a clean read-only study copy of ODD under ignored reference cache and
recorded revision c167363f3d4ad1540a577af99071283caf54f3a6 plus 77 file hashes.
Inspected README, LICENSE, CMake, XML steering, source inventory and CI. The
current study source contains muon factories, unlike older talks describing future
work. Recorded version and field-configuration differences requiring attention
before a reproducible baseline is selected. No geometry defect or runtime
incompatibility is asserted without testing.

Added the resource guide and intake evidence, updated navigation and ADR-001's
source-discovery context without selecting its baseline or advancing status.
All changes remain uncommitted on main. No remote PR or message sent.

## Commands, checks and limitations

- Web research followed canonical CERN GitLab, Indico, Zenodo, ACTS/DD4hep/Geant4,
  arXiv and public project pages. ACAT 2021 direct access returned 403; recorded
  as an optional historical lead with unverified attachments. Some web views
  failed; Git transport supplied the primary source successfully.
- `git clone --depth 1 https://gitlab.cern.ch/acts/OpenDataDetector.git reference/cache/upstream/OpenDataDetector`
  failed under sandbox DNS restrictions; approved retry succeeded.
- `git -C reference/cache/upstream/OpenDataDetector ls-remote --tags origin`
  read public tag references with approval. Study snapshot is not a release choice.
- Temporary download scripts imported the existing downloader's `download`
  function for explicit public URLs. Initial sandbox attempts failed; approved
  retries succeeded. Four receipts retain failure and success evidence without
  overwriting records. Exact URLs/hashes are in the catalogue and receipts.
- Existing reader extracted and reloaded all four PDFs. Four expected-page query
  assertions, contiguous page coverage, 77 source file hashes, unique catalogue
  IDs and every local manifest PDF checksum passed.
- Inspected three title-page renders and CHEP PDF 5; selected passages are listed
  in the guide. TrackML title text checked, full reading deferred.
- Fifteen logging/document-link tests passed and whitespace checks passed.
  Final session validation result is in paired JSON.

No code implementation changed and no upstream code was executed. No detector
build, Geant4 run, ACTS conversion or baseline acceptance check was performed.
No bulk datasets or container images downloaded. Exact token counters and detailed
client/model identity were unavailable; no estimates are recorded.

## Follow-up

Read source and overview together, trace representative components and prepare a
version-consistent baseline candidate under ADR-001 and ADR-003. Resolve the
geometry/field/material-map/reconstruction configuration as a unit. The study
snapshot and source license observation are evidence for review, not human approval.

## Token usage recovered — 2026-09-24

Recovered local client-reported counters for 1 disjoint turns: **5,082,191 input** and **15,189 output** tokens. Cached input and reasoning output are subsets, not additions. Request-to-task matching and counter evidence are retained in [the recovery inventory](../usage/USAGE-2026-09-24-local.json).

This dated correction supersedes earlier statements that token counts were unavailable for these turns. Original narrative and limitations are preserved. It does not establish complete coverage across machines; unmatched and branch-only turns remain explicit in the inventory.
