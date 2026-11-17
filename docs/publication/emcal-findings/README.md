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
intervals. Figure3 redraws retained values; the review-update Figure1 derives fine bins from the retained matched ledgers with the predeclared bootstrap. No transport or calibration is repeated. Figure2 is a vector schematic
using declared layout/route seeds, with unequal axis scales; it is not a native
geometry/installed-pipe or material-clearance proof. Existing scientific evidence
remains unchanged. The report uses ECAL yellow and HCAL orange consistently.

Rendered pages are visually checked after the last change. Text extraction,
PDF links and page boundaries are checked separately. Public PDF and provenance
are curated here; local renders/output duplicates stay ignored. Detailed source
and result assessment lives in the paired SESSION-2026-11-15-emcal-findings
journal. The source studies retain their own validation, uncertainty, artifact
and engineering limits.

## PR145 review update - 2026-11-17

The [human review comment](https://github.com/asalzburger/nodd/pull/145#issuecomment-6951330371)
selects ALLEGRO-style LAr with a 400 mm warm gap as the nODD ECAL working baseline.
The report and [baseline-selection record](../../design/inputs/ECAL-baseline-selection-2026-11-17.md)
now state that choice explicitly. Full connected-service/collar and combined-union
qualification remain separate; the old combined exporter/drawings retain their
800 mm integration control.

[One SVG comparison](response-comparison.svg) shows the requested four series.
Its relative raw-response width is sample SD(R)/mean(R), R=H/Etrue, versus |eta|.
It is a sigma(E)/E response-width proxy, not intrinsic fixed-energy resolution.
The three matched 10k saved-hit samples use uniform 0.05-wide bins (136-189
primaries/bin), all zeros, and 1000 shared whole-primary bootstrap replicates
with seed13001000. ODD is explicitly shown only as its retained 20 GeV/c,
fixed-phi, 200-event eta0/1/2 reference markers and source intervals. There is
no matched broad-spectrum ODD curve in the retained evidence. No calibration
samples or complete-deposit A values are substituted for saved-hit H.

`response_comparison.py` uses NumPy only to derive the compact
[bin statistics](response-comparison.json) from the three hash-bound local
ledgers. It uses ReportLab for the SVG and the same drawing embedded in page4.
The [render receipt](response-comparison.render.json) binds data, producer and SVG.
It cross-checks all ten previously retained fine LAr H bins and intervals.
No new transport is performed; per-event ledgers remain ignored.

From a checkout in the original workspace, with the retained inputs available:

```sh
python3 -B docs/publication/emcal-findings/response_comparison.py derive \
  --siw-original ../nodd-ecal10k/build/ecal10k/production12/event-summary.jsonl \
  --siw-staggered ../nodd-ecal10k/build/ecal-staggering/production12/event-summary.jsonl \
  --lar400 ../nodd-lar-gap-10k-response/build/lar-gap10k/reaudit/candidate/derived-events.jsonl
# Python with the existing ReportLab/pypdf packages:
python3 -B docs/publication/emcal-findings/response_comparison.py render
python3 -B docs/publication/emcal-findings/build_report.py \
  --output output/pdf/em-calorimeter-findings.pdf
```

On a different host, pass the actual ledger paths; their hashes are mandatory.
Rendering from the committed compact JSON does not require the raw inputs or NumPy.
The updated PDF remains eight pages, including references. Earlier source/run
receipts remain immutable; the new evidence manifest adds the comment and figure
hashes instead of relabelling old validation as a new integrated-detector proof.

[Review-update QA receipt](review-update-2026-11-17.json) records this revision.
`review-delta.json` remains the historical 2026-11-15 cosmetic-only assessment;
it does not describe the substantive 2026-11-17 review response.
