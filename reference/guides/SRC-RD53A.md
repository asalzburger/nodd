# SRC-RD53A — RD53A manual reading map

- Status: MAPPED; selected openings SKIMMED; sampled pages VISUALLY CHECKED
- Created: 2026-09-15
- Source SHA-256: `0af1ba92f3d47f8da3a584c21392c5dbce62f9d1fa3d50268d8618c628c4f81e`
- Identity: The RD53A Integrated Circuit, CERN-RD53-PUB-17-001.
- Local version: 3.51, 2019-08-19, verified on rendered PDF page 1.
- Public PDF with matching title/version: recorded in [manifest](../manifest.yaml).
  Public/local byte equality was not tested.

## Scope and version caution

The abstract and introduction describe a prototype with deliberate design
variants, not the final experimental production chip. The manual is a companion
to a separate specifications document (reference [1] on PDF 79); do not conflate
the implementation manual's report ID with the specifications' report ID.
No device dimensions or performance numbers are adopted as nODD requirements.

## Corrected navigation

There are 79 physical PDF pages, no bookmarks and no embedded page-label rules.
The actual body footer is PDF page minus one. The printed contents on PDF 2–4
contains stale destinations: e.g. Introduction is listed as page 1 but actually
starts at printed page 3 / PDF 4. Use the actual-heading table below.

| Section / topic | Actual PDF start | Actual printed start | Later use |
| --- | ---: | ---: | --- |
| 1 Introduction | 4 | 3 | Scope, prototype/production differences |
| 2 Floorplan | 6 | 5 | Functional placement and interfaces |
| 3 Power distribution | 8 | 7 | Supply, regulation, isolation and load model |
| 4 Pads and alignment | 15 | 14 | Physical electrical/mechanical interfaces |
| 5 Analog front ends | 18 | 17 | Deliberate prototype variants |
| 6 Digital matrix | 28 | 27 | Buffering and processing organization |
| 7 Digital bottom/clocks | 33 | 32 | Control, reset, clocks and triggers |
| 8 Analog bottom | 40 | 39 | Bias, monitoring and calibration |
| 9 I/O and configuration | 45 | 44 | Protocols and programming |
| 10 Test functions | 58 | 57 | Test-specific functionality |
| 11 Reference tables | 62 | 61 | Pin/register/address lookups |
| A Radiation tolerance | 75 | 74 | Design assumptions and test context |
| B Design methodology | 77 | 76 | Design flow; contains unfinished prose |
| C Known quirks | 78 | 77 | Prototype caveats and test interpretation |
| References | 79 | 78 | Underlying specifications and related sources |

Locators were obtained from actual headings and footers in extracted pages,
with selected visual checks. They are source-navigation observations, not
verified scientific parameter claims.

## Figures and tables to revisit

- Figure 1: PDF 5 / printed 4, physical orientation and layout labels.
- Table 1: PDF 8 / printed 7, power-supply table.
- Figure 5 and Table 2: PDF 10 / printed 9, regulator diagram and interface table.
- Figure 8: PDF 15 / printed 14, pad drawings.
- Reference tables begin on PDF 62 / printed 61.

## Extraction and reading limitations

All pages have text, but that does not establish completeness. Marginal line
numbers are retained and can interfere with paragraph reading. The mixed
schematic/table page at PDF 10 demonstrates that extracted diagram labels lose
their spatial meaning. Tables are plain text, not validated cell structures.

Compatibility normalization in search handles ligatures; raw cached extraction
is preserved. Search may return the stale contents before the actual chapter.
The guide uses heading-based destinations to avoid this ambiguity. No OCR or
full equation/table transcription was performed.

A public index labels this manual with a July date, while the actual local and
public PDF title pages say August. The PDF's explicit version date governs this
file's record. Appendix B includes an unfinished-text placeholder on PDF 77;
version numbering alone must not be treated as proof of finalized documentation.
