# DES019 TDR compile and visual review

- Date: 2026-10-06
- Status: PASS for manuscript compilation and visual review; preliminary DRAFT
- Sources: [editable manuscript](../../publication/tdr/README.md)
- Evidence: [validation.json](validation.json), [compiled preview](pixel-tdr.pdf), [compile log](compile.log.gz)

The final manuscript at `dda70e5709e1668dfe98e555dddda8efbccd13a8`
compiled with pdfLaTeX / TeX Live 2026 in hosted run
[37443298638, job112201993926](https://github.com/asalzburger/nodd/actions/runs/37443298638/job/112201993926).
It succeeded at 2026-10-06T09:31:05Z. The 11 A4 pages were rendered at105 dpi
using Poppler and individually inspected. Tables, figures, labels, citations,
page numbering and paragraph reading order are legible, without clipping or
missing glyphs. The compile gate found no overfull boxes or undefined references.
The failed initial table-alignment attempt and its correction remain in the
shared session record; the successful preview does not erase that attempt.

Source and artifact SHA-256 values are retained in validation.json. Subsequent
closeout changes affect tracking/logs/README/evidence only; this preview represents
the pinned manuscript inputs, not an enclosing metadata commit. Model source,
native execution and manuscript revisions are deliberately distinct.

Hosted project regression/dashboard run37443298649 on the same manuscript head
passed at2026-10-06T09:35:39Z; deployment was skipped. Standard-library generated
asset/source checks also pass. This does not rerun the DD4hep native workflow.

The report documents the unchanged barrel and trimmed radial single/quad endcaps,
module frames/readout, local support/cooling/mounting and fixed service limits.
Coverage gaps, guard/warm thermal failures, service overpacking and manufacturing
questions remain visible. This manuscript is a review copy; no Overleaf push,
production integration, design approval or full-detector acceptance is claimed.

The public compiler log is stored as byte-preserving gzip to retain its native
whitespace without introducing text-diff whitespace errors. Its compressed and
decompressed hashes are recorded independently.
