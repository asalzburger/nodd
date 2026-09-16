# ODD resource discovery and reading intake

- Date: 2026-09-16
- Phase: M0; ADR-001/003/005 remain DRAFT
- Issue: none; direct user request to find/register ODD resources and download print-only material
- Source guide: [ODD resources](../../reference/guides/ODD-resources.md)
- Results: [JSON](odd-resource-intake.json)
- Source snapshot: [77 file hashes and revision](../../reference/odd-study-snapshot-2026-09-16.json)

## Outcome

Registered 21 sources: the ODD repository/archive and historical presentation
lead, three presentation PDFs, two TrackML papers, ACTS source/documentation/paper,
DD4hep source/manuals, Geant4 and Key4hep documentation, and ColliderML
paper/library/production/documentation/data resources. Four PDFs (107 pages) were
downloaded, hash-checked and extracted using the existing pinned reader. HTML
resources are registered for web reading; no bulk dataset or container download.

A clean shallow ODD checkout was inspected at
`c167363f3d4ad1540a577af99071283caf54f3a6`. It remains under ignored reference cache;
no source was imported into the production project and no baseline selected.
The source's MPL-2.0 license was read. Tags and CI configurations were inspected,
but no build, geometry construction, overlaps, Geant4 or ACTS checks were run.

## Acquisition and limitations

Initial network operations failed inside the sandbox; explicitly approved retries
succeeded. Retained receipts:

- [ODD slide attempt](../../reference/downloads-2026-09-16-odd-attempt1.json)
  and [successful downloads](../../reference/downloads-2026-09-16-odd.json).
- [TrackML attempt](../../reference/downloads-2026-09-16-trackml-attempt1.json)
  and [successful download](../../reference/downloads-2026-09-16-trackml.json).

The temporary acquisition scripts reused `tools/reference_downloads/download.py`
via its `download(url, destination)` function, which checks PDF headers, hashes
and response byte counts and does not overwrite existing files. Public PDF URLs
and exact resulting hashes are retained in receipts and source entries.

The ACAT 2021 event returned 403 through the web tool; the historical link is
registered as unverified rather than inventing attachment metadata. Some GitLab,
GitHub and documentation web views failed; Git transport successfully provided
the primary ODD code, while working public HTML documentation supplies reading
routes. The ACTS tag-specific full-chain GitHub page was not inspected successfully;
no claim about its contents is made. No inaccessible source governs a design.

## Actual checks

- Four known-answer retrieval checks passed, with expected physical PDF pages:
  CHEP “The Level of Detail” / 5; CTD “ACTS & OpenDataDetector” / 5;
  tutorial “Detector Geometry Setup” / 22; TrackML “Throughput phase” / 1.
- Contiguous page indices checked across all 107 pages; each cache reloaded with
  source/provenance/artifact hash verification. Extraction flags retained in JSON.
- All 77 retained upstream file hashes rechecked; unique catalogue IDs and every
  local PDF checksum in the manifest verified.
- Visually inspected the three presentation title pages and CHEP PDF 5; selected
  reading coverage is specified in the guide. TrackML title was text-checked only.
- Documentation/logging checks and session validation are recorded in the session
  pair. No software implementation changed; no new tests were added.

## Reproduce study access

For a new local checkout (do not overwrite an existing study directory):

```sh
git clone https://gitlab.cern.ch/acts/OpenDataDetector.git reference/cache/upstream/OpenDataDetector
git -C reference/cache/upstream/OpenDataDetector checkout --detach c167363f3d4ad1540a577af99071283caf54f3a6
git -C reference/cache/upstream/OpenDataDetector status --short
```

The original acquisition used `git clone --depth 1` and inspected its actual HEAD.
The full-clone recipe above permits selecting the recorded revision after the
upstream default branch moves. Source snapshot identity is independent of branch.

To reacquire a PDF, use its `download_url` and `local_file` in the catalogue with
the existing `download` helper, retaining a new receipt; compare the resulting
SHA-256 with the catalogue before accepting it. Never replace an existing receipt.
For cached reading:

```sh
reference/cache/venv/bin/python tools/reference_reading/read.py extract SRC-ODD-CHEP-2023
reference/cache/venv/bin/python tools/reference_reading/read.py extract SRC-ODD-CTD-2023
reference/cache/venv/bin/python tools/reference_reading/read.py extract SRC-ACTS-ODD-TUTORIAL-2025
reference/cache/venv/bin/python tools/reference_reading/read.py extract SRC-TRACKML-THROUGHPUT
reference/cache/venv/bin/python tools/reference_reading/read.py search SRC-ODD-CHEP-2023 'The Level of Detail'
```

Full scientific reading, framework compatibility, material-map/field consistency
and baseline acceptance remain pending. This task supplies navigation and evidence
for those next steps; it does not implement them.
