# Open Data Detector — Technical Design Report

LaTeX source of the human-facing nODD technical report. This repository is a
submodule of the nODD workspace and is synchronised with an Overleaf project, so
**everything here must compile with `pdflatex` on Overleaf**: no `fontspec`, no
`--shell-escape`, no fonts or packages outside TeX Live.

## Build

```sh
latexmk -pdf main.tex        # produces main.pdf
latexmk -c                   # remove auxiliary files
latexmk -C                   # remove auxiliary files and main.pdf
```

Overleaf builds `main.tex` with pdfLaTeX and needs no other configuration.

## Layout

| Path | Contents |
|---|---|
| `main.tex` | Class, style, metadata, front matter, one `\include` per chapter. Nothing else. |
| `style/odd-tdr.sty` | **All** formatting: fonts, geometry, headings, running heads, captions, colours, the title page, `\TODO`. Heavily commented; each block is numbered. |
| `chapters/*.tex` | One file per chapter. |
| `figures/` | Figures, vector (PDF) wherever possible. |

## Adding a chapter

1. Create `chapters/<name>.tex`, starting with

   ```latex
   % !TeX root = ../main.tex
   \chapter{Title of the chapter}
   \label{ch:<name>}
   ```

2. Add one line to the main matter of `main.tex`, in reading order:

   ```latex
   \include{chapters/<name>}
   ```

`main.tex` already lists the planned chapters as commented-out `\include` lines; uncomment
one as it is written.

## House rules for the text

- **Never invent a number.** Public facts cite external literature with precise
  locators. Explain nODD design choices and their reasoning directly in the text;
  internal design records, PRs and generated inventories are not bibliography
  entries. Preserve those internal sources and their exact revisions in
  `data/pixel-provenance.json` and `data/pixel-editorial-provenance.json`.
  Undecided quantities remain explicitly unresolved.
- Tables use `booktabs` (`\toprule`, `\midrule`, `\bottomrule`) and **no vertical rules**.
- Units and numbers use `siunitx`: `\qty{34}{\milli\metre}`, `\qtyrange{100}{300}{\micro\metre}`,
  `\num{1.2e-3}`, `\unit{\tesla}`. Detector-specific units `\radlen` (X₀), `\intlen` (λ₀)
  and `\barn` are defined in the style file.
- Cross-references use `cleveref`: `\cref{ch:baseline}`, `\cref{fig:layout}`, `\cref{tab:radii}`.
  Label prefixes: `ch:`, `sec:`, `fig:`, `tab:`, `eq:`.
- Figures are vector (PDF) whenever the source allows it. Tables and plots that depend on
  detector parameters should be generated from their hashed source snapshot.
- Shorthands: `\pt`, `\abseta`, `\Xzero`, `\lambdazero`, `\code{...}` for XML tags,
  file paths and plugin names.

## Typography

Set in Palatino (`newpxtext`/`newpxmath`) with TeX Gyre Heros headings scaled to Palatino's
x-height, and Inconsolata for code. A4, single-sided, 11 pt on a 14.7 pt baseline, 150 mm
measure with 30 mm side margins and 25/28 mm top/bottom margins. The three things you are most likely to want to change —
the measure, the leading and the accent colour — are blocks (2), (3) and (5) of
`style/odd-tdr.sty`, each on a line of its own with a comment.

The title page uses the ODD emblem without its wordmark (`figures/odd-mark.pdf`, derived from
`odd-v6/logos/odd_tech_light.svg`); the full logo including the wordmark is kept as
`figures/odd-logo.pdf`.

## Do not

- **Do not push.** The remote is the Overleaf project; pushing is a manual, deliberate act.
- Do not reference files across the submodule boundary (`../odd-v6/...`). Copy what you need
  into `figures/`.

## Current pixel baseline (2026-10-06)

`chapters/tracker.tex` includes `chapters/pixel-detector.tex` and its external
bibliography. The barrel chapter, module illustrations, editorial routes and
review line numbers are preserved from the latest authored Overleaf revision.
The endcap now describes the current main baseline: four inner single-module
rings and two outer quad rings, with progressively removed inner single rings
on discs 5--9. Both sides use the reviewed integer support datums. The source
pattern has six physical module rings and eight radial chip rows; it is not an
eight-ring physical assembly. Engineering qualification remains open.

Build the full report or standalone pixel review extract with pdfLaTeX:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error pixel-detector.tex
```

Ordinary compilation is self-contained. It uses checked-in vector PDF figures
and generated numeric tables, with no Python, network, external checkout or
shell escape. For regeneration with Python and matplotlib:

```sh
python3 scripts/pixel_figures.py --endcap-only  # preserves authored barrel assets
python3 scripts/pixel_figures.py                # regenerates all recipe assets
```

Both commands verify the two bundled snapshot hashes. Current endcap drawings
and tables come from `data/pixel-endcap-baseline.json` and
`scripts/pixel_endcap_figures.py`; current source hashes and projection boundaries
are in `data/pixel-endcap-provenance.json`. `data/pixel-render-manifest.json`
records the regeneration mode, generators, matplotlib version and all retained
artifact hashes. PDF creation timestamps are suppressed. The carrier and service
hierarchy schematics remain applicable because their fixed interfaces are unchanged.

To refresh the current snapshot, use the explicit parent baseline at
`e50ae6def313cae3d9be62ff1e299569965c1b35`. First run its deterministic,
pure-Python exporter in an ignored output directory, then extract report data:

```sh
python3 /path/to/pinned/nodd/tools/pixel_detector_dd4hep/export.py \
  --output /path/to/ignored/export
python3 scripts/pixel_baseline_snapshot.py --source-root /path/to/pinned/nodd \
  --expected /path/to/ignored/export/expected.json
python3 scripts/pixel_figures.py --endcap-only
```

This does not run DD4hep, Geant4, ACTS or Spack. The extractor checks the current
config, module/chip totals and integer datums, and reconciles its model mass
with the retained main-integration native summary. Native validation retains
its actual dirty execution state and original hashes; the report's source
revision is not substituted for that execution state. Source data include all
nine positive-disc module placements, frozen faces/heights/IDs, cooling tracks,
fixed transport-cell bounds and model mass. The opposite endcap is reflected.

`data/pixel-layout.json` and `data/pixel-provenance.json` retain the original
PR37 snapshot as the immutable barrel source. Historical endcap fields in that
file are superseded by the separate current snapshot and are not used for the
endcap figures or tables. `scripts/pixel_snapshot.py` is the historical PR37
extraction recipe; ordinary current regeneration does not run it. Exact DES001
module input blobs and later DES012/013 barrel amendments retain their original
revisions and hashes. `data/pixel-editorial-routing.json` and its provenance
retain the authored barrel cable drawings. No input crosses the submodule
boundary during a TeX build, and no external reference PDFs are redistributed.

Public literature remains the only bibliography content. Internal design records,
Git revisions, producer hashes and validation identities stay in the data manifests.
The prose explains the selected geometry and its reasoning directly. Sensor
process, guards, active-map gaps, warm thermal margin, mount qualification and
fixed trunk/flange service packing remain open interfaces.

The sensor/grid illustration was removed from the manuscript at the user's request
on 2026-10-02. Its generated asset remains available, without being reinserted.
The accessible-edge module illustration and near-final barrel narrative are preserved.

## Full tracker review baseline (2026-10-07)

The tracker chapter now includes an overall layout/service overview, the unchanged
pixel manuscript, detailed short-strip and long-strip barrel/endcap sections, and
cross-system review priorities. `tracker-review.tex` builds the complete tracker
extract; `pixel-detector.tex` remains a pixel-only extract. `main.tex` is the full
report entrypoint. The title identifies a review baseline, without design sign-off.

The selected short-strip barrel uses +15 degree same-radius staves. The long-strip
barrel uses +12 degree structural stereo staves with 17 bearing stations. Endcaps
use the latest first-disc collector-clearance amendments and final wrapped
long-strip dielectric. Failed coverage, thermal, handling and packing screens are
retained explicitly. Independent compact masses and duplicated service cells are
not added together as an integrated tracker.

`data/tracker-baseline.json` freezes the strip inputs, representative layouts,
retained beam/service screens and true long-barrel solid sections. Its source
revision, input/producer/report hashes, original native execution identities and
projection boundaries are in `data/tracker-provenance.json`. The enclosing report
revision never replaces a native execution revision. Pixel snapshots and authored
pixel text/figures are byte-preserved. No reference manuscript figures are copied.

Regeneration is optional; normal pdfLaTeX compilation is self-contained:

```sh
python3 scripts/tracker_snapshot.py --source-root /path/to/pinned/nodd
python3 scripts/tracker_figures.py
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error tracker-review.tex
```

The extractor reads the recorded source revision (see the provenance manifest),
reconstructs only the deterministic short-endcap placement and intersects the
retained long-barrel inventory. It does not run DD4hep, Geant4, ACTS or optimization.
The figure recipe needs only bundled data, Python, NumPy and matplotlib; its eight
vector figures and generated disc table are hashed in
`data/tracker-render-manifest.json`. Public citations and internal provenance remain
separate. The user authorized updating this existing Overleaf report; ordinary
publication is part of that request and does not grant scientific acceptance.

## Editorial figures (2026-10-03)

The overview and barrel projection include the selected positive-side cable
routes. `data/pixel-editorial-routing.json` preserves the exact positive-terminal
records for all 82 staves and longitudinal records for column zero of all four
layers. Its hash and original routing-file identity are retained in
`data/pixel-editorial-provenance.json`; this is internal traceability.

Figure 2.3 pairs the material-stack drawing with an adapted accessible-edge panel
from the compact-module SVG in PR #8 at revision
`214747a3c83c140caa6c4ae9c3fb6486ac5cb825`. The adapted editable SVG preserves the
nominal film thicknesses while illustrating bond access. It omits the optional
two-chip module and study framing. Bump and bond shapes are explanatory only.
The report uses its checked-in vector PDF, requiring no SVG tool during TeX builds.
Optional conversion after editing the SVG uses librsvg:

```sh
rsvg-convert --format=pdf figures/pixel-module-edge.svg -o figures/pixel-module-edge.pdf
python3 scripts/pixel_figures.py
```

Internal decision IDs and provenance hashes belong in these source records, not
in the publication bibliography. No detector placements or material inputs were
changed by this editorial iteration.

## Review line numbers (2026-10-04 trial)

Both PDF wrappers enable continuous grey line numbers in the left margin of
main-matter text, including displayed equations. Front matter and figure/table
contents are not numbered; use figure/table numbers for those review comments.
The switch is in the house style. Add `\ODDreviewlinesfalse` after loading the
style in either document preamble to return to an unnumbered edition.

## Concise pixel edition (2026-10-09)

The pixel chapter now uses five subsections: modules/readout, barrel layout,
endcap layout, supports/cooling, and services/material representation. Compact
support, cooling and routing ledgers retain the simulation dimensions and
material topology; complementary panels share eight figure groups. The five
original sensor, barrel, ring, disc and material tables are preserved verbatim.
Other subsystem chapters, data snapshots, figure assets and generation recipes
are unchanged. The full report and standalone extract share the same chapter.

This editorial edition was reviewed as a separate local PDF and approved for
Overleaf publication. It does not change detector geometry or qualification.
The editorial source identity and preservation checks are recorded in
`data/pixel-shortening-provenance.json`. Native execution identities remain in
their original scientific manifests.
