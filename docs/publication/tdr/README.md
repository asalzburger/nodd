# nODD preliminary pixel TDR sources

Self-contained review manuscript, derived from the pinned Overleaf template
`7783ea3e3235c0fe9da641db3d303a6f211b3073`. The user explicitly selected
reviewing the TDR in a nodd PR on 2026-10-06. The `docs/tdr` submodule and its
gitlink remain unchanged; this PR does not publish or push to Overleaf.

`main.tex` includes a scope introduction, the updated pixel chapter and linked
immutable design/evidence references. It uses the inherited pdfLaTeX style and
logo assets. Formatting stays in `style/odd-tdr.sty`. All input/figure paths are
inside this directory. Generated tables, facts and vector PDFs document the
selected DES019 trimmed single/quad baseline, with its engineering limits.
Other TDR chapters remain outside this update.

Build from this directory using an existing TeX Live installation:

```sh
latexmk -pdf -file-line-error -halt-on-error -interaction=nonstopmode main.tex
```

The read-only [CI workflow](../../../.github/workflows/tdr.yml) uses
[latex-action v4](https://github.com/xu-cheng/latex-action), pinned to its resolved
commit, with TeX Live 2026 and pdfLaTeX. No shell escape or custom fonts are used.
Its artifact contains the compiled PDF and log; compilation alone does not
replace visual review. No TeX engine was installed on the user's Mac.

Regenerate figures/tables with Matplotlib in an existing environment:

```sh
python3 -B tools/tdr_baseline/generate.py
python3 -B tools/tdr_baseline/generate.py --check
```

Run these from the nodd root. The check uses only the standard library; it
verifies source hashes, table/fact content and every generated figure hash.
`evidence.json` distinguishes the model deliverable revision from the actual
dirty native execution revision/hashes. Earlier scientific evidence is preserved.

For a deliberate Overleaf update, review and copy `main.tex`, `style/`,
`chapters/`, `generated/` and `figures/` together; select `main.tex` and pdfLaTeX.
There are no references across the submodule boundary and no dependency on
running the generator in Overleaf. The review copy is an editorial artifact;
detector configurations and frozen reports remain the parameter source of truth.

The [retained compiled preview and review evidence](../../validation/DES-019-tdr/results.md)
contain the final 11-page PDF, exact CI/source/artifact hashes and visual QA.
