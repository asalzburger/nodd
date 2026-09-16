# SRC-ATLAS-TDR-030 — ATLAS Pixel TDR reading map

- Status: MAPPED; selected openings SKIMMED; sampled pages VISUALLY CHECKED
- Created: 2026-09-15
- Source SHA-256: `14ec26bfb376c7a7a6fba2d06819a30b3ef6dc378508911ae7e90c3a8833dd12`
- Identity: title/report IDs and ATLAS Collaboration checked on PDF page 3.
- Local edition: page 3 says created 2018-06-15; cover text carries 2018-07-10.
  The public ATLAS TDR index identifies 2018-07-10 as the submission date.
  The report identifier contains 2017; it is not the date of this local edition.
- Source/public-index details and license locator: [manifest](../manifest.yaml).

## Navigation

All PDF numbers below are one-based. The document has 482 physical PDF pages,
285 bookmarks, and no embedded page-label rules. For the mapped body pages,
printed Arabic page = PDF page minus 22; this is a checked mapping for this
file, not a generic rule. Front matter uses other labels (PDF 15 is printed ix).

The table is a concise editorial map derived from the source's contents,
bookmarks and chapter openings. It introduces no detector parameter choices.

| Chapter / topic | PDF start | Printed start | Later use |
| --- | ---: | ---: | --- |
| 1 Introduction | 23 | 1 | Scope and maturity of the proposal |
| 2 Layout and simulation | 25 | 3 | Geometry context and modelling assumptions |
| 3 Tracking/physics performance | 61 | 39 | Performance context, not a tuning target |
| 4 Technical overview | 113 | 91 | Start here for interfaces and architecture |
| 5 Sensors | 153 | 131 | Technology alternatives and prototype tests |
| 6 Front-end chips | 175 | 153 | Requirements and prototype/production distinction |
| 7 Hybridization | 199 | 177 | Bare-module assembly and quality control |
| 8 Modules | 217 | 195 | Components, assembly, material accounting |
| 9 CMOS alternative | 233 | 211 | Alternative development path |
| 10 Data acquisition/control | 259 | 237 | Data paths and interface context |
| 11 Power, grounding, DCS | 281 | 259 | Power architecture and service implications |
| 12 Common electronics | 293 | 271 | Shared monitoring/protection interfaces |
| 13 Local supports | 303 | 281 | Mechanical, thermal and local-service scope |
| 14 Services | 335 | 313 | Cables and cooling beyond local structures |
| 15 Common mechanics | 341 | 319 | Envelopes, interfaces, cooling research |
| 16 Surface integration | 357 | 335 | Assembly and commissioning constraints |
| 17 Installation | 371 | 349 | Experiment-specific integration context |
| 18 Decommissioning | 393 | 371 | Historical/experiment-specific context |
| 19 Production/schedule | 409 | 387 | Planned production, not current status |
| 20 Costing | 429 | 407 | Historical costing assumptions |
| 21 Risks | 439 | 417 | Decisions still open at the document date |
| Bibliography | 443 | 421 | Follow original evidence |
| Collaboration list | 455 | 433 | Attribution |

## Useful entry points for a later focused pass

- Section 4.3: PDF 115 / printed 93, module overview.
- Section 6.3.3: PDF 189 / printed 167, changes from RD53A to production.
- Section 7.2: PDF 201 / printed 179, assembly processes.
- Section 8.2.2: PDF 221 / printed 199, module flex.
- Section 8.2.5: PDF 223 / printed 201; Table 8.2 is on PDF 224 / printed 202,
  material accounting. The section start and table page must not be conflated.

These are navigation locators. Values and material representations have not
been promoted to FACT records or nODD requirements.

## Extraction and reading limitations

Cover text contains duplicated glyphs despite a legible rendered cover. Some
bookmarks lose mathematical symbols. The printed contents entry for the
bibliography points to 432, while the heading actually starts at printed 421
(PDF 443); prefer the heading/bookmark, not that contents value.

Seventeen pages have no extracted text; PDF 2 and 480 were visually checked and
are blank. Other zero-text pages remain flagged, not automatically classified
as blank. No OCR was run. Tables and figure positions require the rendered page;
text alone does not preserve all spatial relationships.

Contents pages and selected chapter openings were read for orientation.
The pilot report specifies rendered-page checks. This remains a TDR-era design
and prototype evidence source; later production literature must be compared
before choosing the representation for nODD.
