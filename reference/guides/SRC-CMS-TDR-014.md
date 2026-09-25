# SRC-CMS-TDR-014 — CMS Tracker TDR reading map

- Status: MAPPED; selected RD53/module passages READ; four pages VISUALLY CHECKED
- Created: 2026-09-16
- Source SHA-256: `642f37707fbe2654c99ae3e9c116297c537d2f048370602ca7de92e5d79a1f54`
- Identity: The Phase-2 Upgrade of the CMS Tracker, CMS Collaboration,
  CERN-LHCC-2017-009 / CMS-TDR-014; verified on rendered PDF page 1.
- Title date: 2017-07-01; separate CERN cover stamp: 2018-10-22.
- Public record: <https://cds.cern.ch/record/2272264>. Direct inspection encountered
  a bot challenge. Public/local byte equality and public version number remain
  unverified; local identity and locators are sufficient for this reading pass.
- Catalogue: [manifest](../manifest.yaml); [validation](../../docs/validation/cms-tracker-reading.md).

## Scope and chronology

This supplies the CMS experimental input alongside the
[ATLAS Pixel TDR](SRC-ATLAS-TDR-030.md), with the [RD53A manual](SRC-RD53A.md)
as their shared prototype-chip reference. It is a first reading focused on RD53
usage and module integration, not a cover-to-cover scientific review.

The TDR distinguishes common ATLAS/CMS RD53 development from the eventual
experiment-specific chips (§10.2.2, PDF 242). It describes RD53A as a planned
half-array demonstrator (§4.2.2, PDF 81; §10.2.2.5, PDF 250–251). The 2018 cover
stamp does not make these passages evidence of completed production hardware.
The local RD53A manual is later, version 3.51 dated 2019-08-19.

## Whole-document map

All locations below are one-based physical PDF pages. Sampled body headers
agree with these numbers (74, 82, 251); no embedded page-label rules exist.
Chapter starts are mapped from bookmarks, not all read in detail.

| Chapter / topic | PDF start |
| --- | ---: |
| 1 HL-LHC and CMS Phase-2 upgrade | 11 |
| 2 Tracker overview | 17 |
| 3 Outer Tracker | 25 |
| 4 Inner Tracker | 71 |
| 5 Common mechanics and services | 89 |
| 6 Expected performance | 97 |
| 7 Organisation, planning and cost | 129 |
| 8 Radiation environment | 143 |
| 9 Outer Tracker additional information | 149 |
| 10 Inner Tracker additional information | 233 |
| 11 Common mechanics and services, additional information | 265 |
| 12 Material budget, local reconstruction and tracking | 273 |
| 13 Organisation details | 291 |
| Glossary / References / Collaboration | 315 / 325 / 337 |

## CMS RD53 and module routes

| Question for later extraction | Section / PDF pages | Key object |
| --- | --- | --- |
| How is the chip integrated into a module? | §4.2, 74; §10.1.1.1, 233 | Fig. 4.3; sensor, chips, flex and base strips |
| Which sensor evidence predates RD53A? | §4.2.1, 75–79; §10.2.1, 238–242 | Test-chip and irradiation context |
| What are the target chip requirements? | §4.2.2, 79–83 | Fig. 4.7, Table 4.4 on 82 |
| Where do electrical links become optical? | §4.2.2, 79–82 | Fig. 4.8 on 81; lpGBT integration |
| What is shared RD53 development? | §10.2.2, 242–243 | Common R&D versus experimental chips |
| What does the RD53A demonstrator establish? | §10.2.2.5, 250–251 | Fig. 10.20 on 251 |
| How are power, heat and failures coupled? | §4.2.2, 82–83; §10.2.2.6, 252–255 | Figs. 4.9, 10.21–10.25 |
| How are modules supported and serviced? | §4.4, 85 onward; chapters 5 and 11 | Service cylinders and cooling routes |
| Which performance inputs are assumptions? | §12.2.1, 276 | Table 12.4 and surrounding prose |

## Source observations to carry into the focused pass

These are **FACT** observations about what this TDR describes, with locators;
they are not adopted nODD parameters or evidence of present production status.

- **Module construction:** §4.2 / PDF 74 describes a bump-bonded sensor/chip
  assembly, a flex glued to the sensor and wire bonded to the chips, and base
  strips for mounting and heat removal. Figure 4.3 depicts two- and four-chip
  modules. The base-strip material is still under consideration in this passage.
- **Active area versus full chip:** PDF 74 and §10.1.1.1 / PDF 233 describe active
  chip dimensions; Table 4.4 / PDF 82 separately includes peripheral space in
  the chip size. Neither should be silently substituted for RD53A's die footprint.
- **Power and services:** PDF 82–83 puts chips in parallel within modules and
  modules in series in a power chain. PDF 81 places optical conversion away from
  the pixel modules. §10.2.2.6 / PDF 252–255 connects regulation, decoupling,
  current headroom and failure cases to thermal demands.
- **Prototype versus target:** Table 4.4 / PDF 82 gives the intended CMS pixel
  chip specifications; PDF 251 describes the smaller RD53A demonstrator with
  multiple analogue front-end variants for comparison. Treat these as different
  devices/stages when building a cross-source evidence table.
- **Simulation versus measurement:** PDF 276 says pixel digitization settings
  use extrapolations and RD53 recommendations/results. Table 12.4 is a simulation
  input table, not a set of measured production-chip performance results.

## Unresolved points and cautions

- Planned RD53A submission is July 2017 on PDF 81 and 242, but June 2017 on
  PDF 251. Preserve both locators; do not resolve the historical date from this
  TDR alone. This discrepancy does not block module navigation, but no submission
  date is adopted as a verified historical event.
- Reference [53] on PDF 328 is CERN-RD53-PUB-15-001 (specifications), not the
  CERN-RD53-PUB-17-001 implementation manual in our catalogue. It is only a
  bibliographic lead here; its contents have not been read or used as evidence.
- Sensor results can use earlier readout chips (§10.2.1, PDF 238 and 242). Do not
  attribute every pixel test result in this TDR to RD53A.
- Later production-chip and module qualification sources remain necessary before
  selecting implementation parameters. No nODD design choice or sign-off occurs.

## Reading and extraction coverage

All 353 pages were extracted; 160 bookmarks were retained. Text is empty on PDF
10 and 142, which were not visually inspected. No OCR was run. Text on plots
(e.g. PDF 250–251) has poor spatial ordering; inspect renders for quantitative use.
Tables were not transcribed into validated cells.

Selected reading covered PDF 71–74, 79–83, the opening of 85, 233, the opening of
238, the readout-chip passage on 242, 243, 250–255, 276 and reference [53] on 328.
Rendered pages 1, 74, 82 and 251 were inspected for identity, module drawing,
chip-specification context and demonstrator scope respectively. Navigation and
source observations are ready for a focused ATLAS/CMS/RD53A comparison; detailed
parameter verification remains a separate pass.

## Short-strip/strixel research addition — 2026-09-25

[DES-007](../../docs/design/DES-007-short-strip-modules.md) uses the Outer Tracker
as a macropixel/readout and repeated-module precedent. Printed/PDF pages 28,
37–38, 42 and 45 were read; Table 3.3 on page 37 was visually checked. The local
PDF hash still matches the catalogue. Page numbering in these locators is the
actual one-based PDF page, not an inferred offset from earlier reading maps.

PS-p: 100 µm × 1.467 mm cells, active 96 × 46.944 mm²; DC coupling and
bump-bonded MPA readout. The TDR prefers 200 µm physical sensor thickness, with
alternatives under study. Four staggered module surfaces form endcap rings.
These facts do not demonstrate ASIC compatibility with ODD's 75 µm × 0.5 mm
cells or support an nODD power estimate. The full PS module has two sensors and
a trigger function that DES-007 does not inherit. Later production choices
may supersede this TDR; they have not been silently substituted.
