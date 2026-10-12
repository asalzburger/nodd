# Module reviewer summary

Build the committed three-page A4 reviewer PDF from its TeX source and presentation crops of the existing module SVG drawings:

```sh
python3 tools/module_summary/build.py
```

Requires Python 3, `rsvg-convert` (librsvg), `pdflatex` (with lmodern, geometry, graphicx, tabularx, array, booktabs, xcolor, hyperref and fancyhdr) and `pdfinfo` (Poppler). No dependencies are installed by the script.

The [source](../../docs/design/DES-001-review-summary.tex) links to the detailed proposal and source catalogue. The builder uses a temporary directory, preserves the original SVGs and rejects overfull boxes or a PDF exceeding three pages. It writes [the PDF](../../docs/design/DES-001-review-summary.pdf) only after those checks pass. Crop coordinates are presentation coordinates, not detector dimensions.

For visual checking, render all pages using `pdftoppm`; `pdfinfo -url` lists embedded links. The committed PDF has been checked for page count and readability. Building this reviewer artifact does not grant design approval or validate hardware.
