# Selected balanced tracker TDR — 2026-10-29

This self-contained full-tracker review edition describes the human-selected
balanced working simulation baseline. The pixel system has barrel datums at
31.5/57/96/182 mm and ten discs at each signed end. Existing logical disc IDs
are preserved; added ID10 is at |z|=950 mm and repeats donor-disc-2 local
geometry. The current integrated tracker has 46,250 sensitive elements.
Engineering qualification and fresh candidate-specific material/response
validation remain separate from baseline selection.

`main.tex` builds the complete report; `tracker-review.tex` builds the complete
tracker extract and `pixel-detector.tex` the pixel extract. All input/figure paths
are internal to this directory. Use pdfLaTeX, no shell escape or external fonts:

```sh
latexmk -pdf -file-line-error -halt-on-error -interaction=nonstopmode main.tex
```

This is a parent-owned PR review artifact imported from the exact current TDR
revision recorded in `source-import.json`. It does not publish to Overleaf or
change `docs/tdr`. The separate preliminary `docs/publication/tdr` edition is
preserved. The import manifest records all original source hashes. Strip
chapters, six strip figures and the strip disc table remain byte-identical.

Current pixel geometry, routing, inventories and tables are generated from the
maintained canonical balanced pixel exporter. Historical snapshots and recipes
remain under their original names as provenance controls; they are not current
balanced geometry. Current extraction lives in `data/balanced-baseline.json`,
with source and native evidence identities in `data/balanced-provenance.json`.
`data/balanced-render-manifest.json` hashes the current manuscript and assets.
Public references support unchanged module technology; internal source/native
identities remain in manifests rather than the bibliography.

From the nODD root, after generating canonical pixel and tracker exports:

```sh
python -B docs/publication/tracker-baseline-2026-10-29/scripts/balanced_snapshot.py \
  --expected build/balanced-baseline/source-pixel/expected.json \
  --compact build/balanced-baseline/source-pixel/pixel-detector.xml \
  --materials build/balanced-baseline/source-pixel/materials.xml \
  --tracker-expected build/balanced-baseline/source-tracker/expected.json \
  --render
python3 -B docs/publication/tracker-baseline-2026-10-29/scripts/balanced_snapshot.py --check
```

Rendering needs the existing NumPy/Matplotlib environment. The standalone check
uses only the Python standard library and verifies source/asset fingerprints,
exact tables, current snapshot identity and unchanged strip controls. Extraction
and rendering perform no native geometry or simulation execution. Native
construction, transforms, overlaps, material identities and geometry conversion
are assessed separately. PDF compilation and visual inspection are separate
checks; their retained results belong in validation evidence.

The DD4hep assembly explicitly retains modules, passive stacks, cooling,
collectors and station-following rail slots within fixed envelopes. Global pixel
trunk, bypass and rear inventories remain reference controls without renewed
cumulative capacity qualification. The Fatras comparison uses separately
qualified relocated effective profiles and a homogeneous added-disc material
layer; it is not a replacement for detailed DD4hep material or a fresh Geant4 map.
