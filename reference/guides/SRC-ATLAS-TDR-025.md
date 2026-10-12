# SRC-ATLAS-TDR-025 — ITk Strip reading maps

## DES-007 short-strip reading

- Read: 2026-09-25; selected passages only, not cover-to-cover verification.
- Title: Technical Design Report for the ATLAS Inner Tracker Strip Detector.
- Collaboration: ATLAS; identifiers CERN-LHCC-2017-005 / ATLAS-TDR-025.
- Local cover stamp: 2017-04-15; publication date not independently resolved.
- Public record: <https://cds.cern.ch/record/2257755>.
- Local SHA-256: `f1ce247fb807a37b0e9065c02764f39f041fc66d266c824828cad9b2915d2bff`.
- 556 PDF pages; copy remains ignored. Direct CDS access challenged; catalogue
  acquisition downloaded and hash verified, not asserted identical to current CDS bytes.

| Topic | Printed / one-based PDF page | Use |
| --- | --- | --- |
| Tracker modules and local support | 92 / 118, 94 / 120 | Six sensor geometries, nine modules per petal side, support and electronics context |
| Sensor technology | 101 / 127 | n+-in-p, AC-coupled strip precedent; not a strixel electronics solution |
| Segmentation and prototype edges | 102 / 128 | 75.5 µm pitch; 24.1/48.2 mm strips; ATLAS12 inactive edges |
| Sensor specifications | 103 / 129, Table 6.1 | 300–320 µm physical thickness |
| Sensor families | 104 / 130, Table 6.2 | Six endcap types and varying 69–84 µm pitches; visually checked table |

[DES-007](../../docs/design/DES-007-short-strip-modules.md) classifies each adopted
claim. The 0.5 mm nODD cell is a separate design choice based on ODD: ITk's
24.1 mm “short strip” is not evidence for a ready-made readout at that length.
Six endcap sensor types establish the ring-specific alternative, not a required
nODD ring count. Prototype edge sizes are not universal HV-clearance guarantees.

## DES-008 long-strip reading

- Read: 2026-09-25; selected passages only, not cover-to-cover verification.
- Title: Technical Design Report for the ATLAS Inner Tracker Strip Detector.
- Collaboration: ATLAS; CERN-LHCC-2017-005 / ATLAS-TDR-025.
- Local cover stamp: 2017-04-15; publication date not independently resolved.
- Public record: <https://cds.cern.ch/record/2257755>.
- Local SHA-256: `f1ce247fb807a37b0e9065c02764f39f041fc66d266c824828cad9b2915d2bff`.
- 556 PDF pages; local copy ignored. Selected text and hash rechecked; CDS
  access challenged, so current public/local byte equality is unverified.

| Topic | Printed / one-based PDF | Use in DES-008 |
| --- | --- | --- |
| Stereo and local support | 92 / 118 | ±26 mrad barrel module rotations, ±20 mrad endcap implant stereo; common carbon-fibre supports and embedded cooling |
| Module families | 94 / 120 | Distinguish a single-sided module from a pair across a support |
| Sensor technology | 101 / 127 | AC-coupled n+-in-p and 300–320 µm thickness precedent |
| Dimensions and segmentation | 102 / 128 | 96.640×96.669 mm², 75.5 µm pitch and 48.20 mm long-strip rows; ATLAS12 edges |
| Sensor specifications | 103 / 129, Table6.1 | Physical thickness range; no nODD radiation qualification implied |
| Endcap families | 104 / 130, Table6.2 | Six outline families; no adoption of their sensor masks |

[DES-008](../../docs/design/DES-008-long-strip-modules.md) classifies adopted
facts and proposed alternatives. Physical die rotation and implant stereo have
different occupied envelopes. A common stave/petal sandwich is not evidence
for a ready-made standalone nODD sandwich module. The geometrically convenient
96 mm continuous strip is longer than the sourced 48.2 mm ITk strip row and
requires electronics/noise/occupancy review.

The parallel [DES-007 study in PR21](https://github.com/asalzburger/nodd/pull/21)
uses this source for short-strip context, pinned here at
`17d84a4c92916a49929db3c5e75684e51bf613b7`. Its separate source observations
should be preserved when reconciling the two branches.
