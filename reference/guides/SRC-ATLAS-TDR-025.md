# SRC-ATLAS-TDR-025 — ITk Strip reading map for DES-007

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
