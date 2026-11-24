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

## Current tracker working prototype (2026-11-24)

The tracker combines the balanced pixel geometry with the selected 75 µm × 2 mm
strixels, redesigned short-strip modules, five endcap rings reaching the sampled
703 mm target, and the retained long-strip geometry. There are 4,752 short-strip
endcap sensors and 46,682 sensitive planes in 54 signed logical groups. The
current short-strip trunk is r=717–781.5 mm and the collector reaches 781.5 mm.
The current material map, sensitive crossings and truth-associated fits are
summarized in the report. Engineering qualification, realistic response and
current-geometry pattern recognition remain open.

`main.tex` builds the full report; `tracker-review.tex` builds the tracker extract.
Both compile from the bundled TeX, tables and vector figures using pdfLaTeX,
without Python, a parent checkout or shell escape. No compiled report is committed.
The pixel and long-strip geometry data and figures retain their individual source
identities; the long-strip chapter's short-strip interface clearance is updated.
Historical balanced snapshots and publication receipts are dated controls, not a
claim that the changed manuscript remains byte-identical to their reviewed PDF.

Current tracker geometry/provenance are `data/tracker-baseline.json` and
`data/tracker-provenance.json`. The latter distinguishes exact source extraction,
the combined exported inventory and separate native evidence. The balanced pixel
snapshot remains `data/balanced-baseline.json`; it is preserved as the current
pixel geometry reference, not the current complete-tracker inventory.

From the nODD root, after generating the current combined compact:

```sh
python3 -B docs/tdr/scripts/tracker_snapshot.py \
  --source-root "$PWD" \
  --tracker-expected build/short-strip-redesign/combined-native/detector/tracker/expected.json
python3 -B docs/tdr/scripts/tracker_figures.py
python3 -B docs/tdr/scripts/tracker_snapshot.py --check
```

Snapshot extraction/checking needs the Python standard library and the named
parent producers; drawing additionally needs NumPy and Matplotlib. Regeneration
does not run native simulation. The five geometry vector figures and strip-disc
table are hashed in `data/tracker-render-manifest.json`; unchanged pixel and
long-strip figures are retained. Source and execution evidence for the current
DD4hep integration belong to the parent repository's DES-043 records.

The scoped changed-component mass proxy and conditional temperature/power screens
in the text do not establish a measured tracker mass, a complete X/X0 map, a
qualified ASIC/harness/module or tracking performance. The current review overlay and reproduction recipe are
`docs/publication/tracker-baseline-2026-11-24` in nODD. The separately dated
November 3 receipt retains its original publication identity. Publication
does not grant design SIGNED OFF or ACCEPTED status.

Current findings use the DES043 geometry from source `62f60563`: the fresh
100,000-ray Geant4/ACTS material comparison, matched sensitive-volume crossings,
and Fatras truth-fit comparison. Whole-baseline changes are mixed; the earlier
approved GBTS/CKF benchmark keeps its 46,250-plane/Gaussian-response scope.
Exact parent evidence and plot hashes are recorded with the review overlay.
