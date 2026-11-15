# EM calorimeter findings - concise review

PUB-EMCAL-2026-11-15. Eight pages including references. [PDF](review.pdf).
The report follows ODD, realistic nODD Si-W and ALLEGRO-style LAr, including
physical staggering/calibration limits, updated service routing and reduced-gap
response. Per explicit project direction on 2026-11-15 it treats routing plus
the400mm warm gap as merged/adopted working configuration. Engineering
qualification and the scope of actual evidence remain distinct. No geometry,
calibration or simulation changes are made by this documentation task.

`build_report.py` is the editable source. It reads immutable Git blobs at
79a967aa3fe78a525f15ede780c26be0cd73aeae and historical calibration/control source
3ebafd340b0e084c5e42e57123de115e3f489244. The latter reports are absent from the
current tree; no current file is substituted. Fetch that immutable commit from
origin if it is missing locally. `evidence.json` records every input hash,
builder identity, source checkpoint and delivered PDF hash.

## Reproduce and inspect

The executed environment is the preinstalled Codex bundled Python3.12.14 runtime,
ReportLab4.4.9 and pypdf6.21.4; Poppler26.05.0 renders the review. No package was
installed. A local Python with the same packages can reproduce the PDF:

```sh
python3 -B docs/publication/emcal-findings/build_report.py \
  --output output/pdf/em-calorimeter-findings.pdf
pdfinfo output/pdf/em-calorimeter-findings.pdf
pdftoppm -scale-to 1600 -png output/pdf/em-calorimeter-findings.pdf build/emcal-findings/qa/page
```

Create the ignored QA output directory first. The builder refuses any page
content overflow, requires exactly8pages (within the user's10page limit),
checks all footer page numbers and rejects nonfinite/out-of-axis vector-chart
intervals. Figures1/3 are vector redraws of retained bin values and percentile
endpoints; no statistical inference is repeated. Figure2 is a vector schematic
using declared layout/route seeds, with unequal axis scales; it is not a native
geometry/installed-pipe or material-clearance proof. Existing scientific evidence
remains unchanged. The report uses ECAL yellow and HCAL orange consistently.

Rendered pages are visually checked after the last change. Text extraction,
PDF links and page boundaries are checked separately. Public PDF and provenance
are curated here; local renders/output duplicates stay ignored. Detailed source
and result assessment lives in the paired SESSION-2026-11-15-emcal-findings
journal. The source studies retain their own validation, uncertainty, artifact
and engineering limits.
