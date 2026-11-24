# Tracker TDR baseline refresh — 2026-11-24

This review edition updates the current Tracker TDR without changing geometry.
It corrects completed integration/material work still described as pending,
adds three existing current-geometry plots with compact findings, and refreshes
five geometry figures with the fixed subsystem colors. The older GBTS/CKF
benchmark retains its earlier geometry and response scope.

The refreshed report has 34 pages (previously 32); the tracker extract has 30
(previously 28). New plots account for most of the added space. Material and
truth-fit changes are mixed, and their model limits remain beside the results.
The source overlay is approximately 390 kB; unchanged TDR assets and large
reference-run payloads are not duplicated in this PR.

`manifest.json` binds the input TDR revision, all original/result source hashes,
current geometry producers, evidence, imported plots and qualified findings.
The geometry remains DES043: 46,682 sensitive planes, 54 signed groups, 120 ACTS
volumes and 75 µm × 2 mm strixels. No native simulation was rerun for this edit.
The separately dated November 3 publication receipt remains unchanged.

From the nODD root, initialize `docs/tdr`, check the review artifact, and assemble
a new complete source directory:

```sh
git submodule update --init docs/tdr
python3 -B docs/publication/tracker-baseline-2026-11-24/review.py
python3 -B docs/publication/tracker-baseline-2026-11-24/review.py \
  --output build/tracker-tdr-2026-11-24
cd build/tracker-tdr-2026-11-24
latexmk -pdf -file-line-error -halt-on-error -interaction=nonstopmode main.tex tracker-review.tex
```

Assembly reads the pinned committed TDR, preserves dirty submodule files and
requires a new output directory. The resulting report builds with ordinary
pdfLaTeX, without Python, network access or shell escape. Replotting the five
geometry figures uses `scripts/tracker_figures.py` with NumPy 2.4.6 and
Matplotlib 3.11.2. The three result figures are unchanged copies of their
hash-bound parent evidence; their original generation recipes remain there.

Validation: the material retained-evidence suite passes 3 tests, the crossing
suite 2, and the Fatras analysis/native-contract suite 8. Both PDF builds pass,
with no overfull boxes or undefined references. The existing font substitutions
and underfull table warnings remain. Page rendering and specialist assessments
are recorded in the task journal and `validation.json`.

This is a reviewable source update. The configured Overleaf main branch and
parent gitlink remain at the published input until separately authorized
publication. No engineering sign-off or performance acceptance is implied.
