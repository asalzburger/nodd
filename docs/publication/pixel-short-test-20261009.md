# Local shortened pixel TDR test

- ID: PUB-PIXEL-SHORT-TEST-2026-10-09
- Date: 2026-10-09
- Status: LOCAL EDITORIAL TEST — for human review
- Authored TDR source: `279d882179e93b56e522fd6b390c965f6ab18e84`.
- Parent checkout: `1b18f2fd728edc2085cf222957e35d53c04d7c9a`.
- Evidence: [compiled comparison and byte hashes](pixel-short-test-20261009.json).

The full TDR is 31 pages instead of 36. The standalone pixel extract is
13 pages instead of 17. Only the pixel chapter is shortened. It now has five
subsections and eight figure groups, compared with thirteen figure environments.
Module/readout geometry and placement inventories remain explicit. Supports,
cooling and routing are consolidated into compact parameter ledgers.

Five original tables are byte-identical: sensor dimensions, barrel population,
endcap rings, disc stations and material representation. All other chapters,
figure assets, data, generated placement rows and producer files are preserved.
The copied document wrappers identify the local editorial test and control
float placement. The original submodule stays clean at its authored revision.
Scientific execution hashes and approval status are unchanged.

## Review files

All outputs are local under `output/pdf/tdr-short-test-20261009/`:

- `nodd-tdr-short-test.pdf`: full report.
- `nodd-pixel-short-test.pdf`: pixel extract.
- `nodd-tdr-short-test-source.zip`: editable, self-contained source project.
- `pixel-detector-short.tex`: shortened chapter (requires the source project).
- `README.md` and `comparison.json`: build instructions and file inventory.

The source archive builds with `latexmk -pdf main.tex` or
`latexmk -pdf pixel-detector.tex`. This test used the repository's pinned
TeX Live compiler image, linux/amd64, pdfTeX 1.40.29 and latexmk 4.88.
Original and shortened versions compiled with the same compiler. All four
builds passed without LaTeX warnings, undefined references or overfull boxes.
All final PDF pages were rendered and visually inspected.

This is a local presentation test. The Overleaf sources and PR #59 were not
changed or pushed. Review the shortened chapter before authorizing its transfer
to Overleaf. No detector-performance or engineering acceptance is implied.
