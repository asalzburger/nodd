# Reference reading guides

These are source-navigation records for the first pilot, not signed-off designs.
Each guide is tied to the PDF SHA-256 in the [catalogue](../manifest.yaml).
Use [the extraction commands](../../tools/reference_reading/README.md) to retrieve
and render the cited pages. Recheck the guide if the source hash changes.

- [OpenDataDetector resources](ODD-resources.md): source code, versions, manuals, talks and simulation/reconstruction routes.
- [ATLAS overview, 2008](SRC-ATLAS-JINST-2008.md): whole-detector architecture.
- [CMS overview, 2008](SRC-CMS-JINST-2008.md): whole-detector architecture.
- [ATLAS Pixel TDR](SRC-ATLAS-TDR-030.md): detector context and component chapters.
- [CMS Tracker TDR](SRC-CMS-TDR-014.md): RD53 development and CMS module/services context.
- [RD53A manual](SRC-RD53A.md): prototype ASIC architecture and corrected navigation.
- [Pilot validation](../../docs/validation/reference-reading-pilot.md): actual
  extraction, cache reuse, retrieval checks and reading coverage.

## Coverage vocabulary

- **EXTRACTED:** software processed the page; does not mean a person/agent read it.
- **MAPPED:** heading/topic and location identified from contents/bookmarks/text.
- **SKIMMED:** opening passages read for scope, not detailed evidence verification.
- **READ:** specified passages read in context; does not imply independent validation.
- **VISUALLY CHECKED:** specified rendered page inspected for a stated purpose.
- **FACT VERIFIED:** reserved for a later exact claim with its locator and context.

This pilot extracts every page, maps the major sections, skims representative
openings, and checks selected rendered pages. It does not claim a cover-to-cover
scientific review. The next pass will focus on the user's engineering questions.

## Initial cross-source routes

| Topic | ATLAS Pixel TDR route | CMS Tracker TDR route | RD53A route |
| --- | --- | --- | --- |
| Module context and interfaces | Chapters 4, 7, 8 | §4.2; §10.1.1.1 | Sections 1, 2, 4 |
| Sensors and readout scope | Chapters 5, 6 | §4.2.1–4.2.2; §10.2 | Sections 5–9 |
| Power and services | Chapters 11, 13, 14 | §4.2.2; §10.2.2.6; chapters 5, 11 | Section 3, pin tables in 11 |
| Validation and limitations | Chapter 8 QA, chapters 19–21 | §10.2 test context; §12.2 simulation inputs | Sections 10–11, appendices A–C |

These routes are editorial priorities, not nODD technology choices. Exact page
locations and version caveats are in the individual guides.
