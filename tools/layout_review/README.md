# ECAL reviewer entry

This tool publishes an existing-design summary, not a TDR or new detector model.
The dedicated documentation branch contains frozen layout inputs and source
locators; it does not import either open ECAL implementation stack.

docs/layouts/review/brief.json is the common prose/table/caption/link source.
The generator writes the exact GitHub PR description to
docs/layouts/review/ecal-layout-review.md, and a four-page PDF with the same
content and drawings. Keep the GitHub description equal to the retained Markdown;
do not add an independent summary which can drift from the PDF.

~~~sh
python3 -B tools/layout_review/draw.py
python3 -B tools/layout_review/build.py --markdown-only
# Existing bundled reportlab/pypdf and an existing LiberationSans font directory:
python3 -B tools/layout_review/build.py --font-dir /path/to/fonts
python3 -B tools/layout_review/build.py --check
# Requires the pinned component Git objects (fetch PRs 64, 70, 71, 73, 74 first):
python3 -B tools/layout_review/build.py --check-sources
~~~

Drawing export uses existing rsvg-convert. PDF generation/checking uses existing
reportlab, pypdf and Pillow; no package is added to the detector software chain.
Markdown generation and source checks use standard Python. PDF images are
retained at sufficiently high resolution; both plots use the same metre scales,
with circular LAr radii and sector-centre polygon apothems explicitly separated.

content-check.json binds common content, Markdown, PDF, renderer and image
hashes, requires exactly four PDF pages, matches all prose/table/caption strings
and public hyperlinks, and preserves pagination as presentation. Visual QA
must still render and inspect all four pages; text extraction is insufficient
for checking layout fidelity. Component source hashes are checked against their
pinned Git objects, never silently replaced by working-tree proposal changes.
The PDF uses an invariant build timestamp for reproducibility; its stated
snapshot date and pinned revisions identify the actual review content.
