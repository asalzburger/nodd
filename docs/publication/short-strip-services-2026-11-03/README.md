# Tracker TDR update — short-strip services, 2026-11-03

This record accompanies the actual current ODD-TDR working tree at `docs/tdr`.
It updates its short-strip chapter, tracker inventory/layout/services, interface
review and affected figures/tables for the human-requested DES-043 integration.
The current Overleaf source input is
`a8892c21938486b995831684076492a1c925fb1b`; the parent assignment input is
`2c1bfe02e87f201abcd1e461a554d951bdc7f56e`. They are different repositories and
must not be substituted for each other's execution or publication identity.
The integration source is frozen at
`d6c4d0ddfa9e14129a3f4c426fced7c4cee0dcc4`. The dated
`tracker-baseline-2026-10-29` parent snapshot remains frozen. Publication and
journal metadata may be uncommitted; the provenance separately checks whether
any extraction input differs from the integration source revision.

The current geometry has 8,064 barrel and 4,752 endcap strixels, with
75 µm × 2 mm readout. Five endcap rings at
289.5/381.25/473/564.75/656.5 mm define the sampled 703 mm outer target; the
finite active corner reaches 704.909 mm and the active gap to long strips is
82.335 mm. The combined exported inventory is 46,682 sensitive planes in
54 signed logical groups. The module, service and qualification boundaries
are summarized in `claims.json` and the actual TDR provenance snapshot.

Reproduce from the parent root after the combined exporter has generated its
compact and expected inventory:

```sh
python3 -B docs/tdr/scripts/tracker_snapshot.py \
  --source-root "$PWD" \
  --tracker-expected build/short-strip-redesign/combined-native/detector/tracker/expected.json
python3 -B docs/tdr/scripts/tracker_figures.py
python3 -B docs/tdr/scripts/tracker_snapshot.py --check
cd docs/tdr
latexmk -pdf -file-line-error -halt-on-error -interaction=nonstopmode main.tex
latexmk -pdf -file-line-error -halt-on-error -interaction=nonstopmode tracker-review.tex
```

NumPy/Matplotlib are needed only for optional drawing regeneration. Ordinary
pdfLaTeX compilation is self-contained. Keep compiled reports, page images,
logs and full geometry inventories local; publish source, resulting plots and
compact claims/provenance only. Neither source extraction nor a PDF build is
native geometry, material, thermal/hydraulic or reconstruction validation.

The actual TDR result is `80a6c998cb9002d0d116bd8c4a414193e904bbd2`. Both report builds and figure checks passed. After the user's explicit “Yes, publish to Overleaf main” reply, the commit was published as a fast-forward from `a8892c2`. A separate remote-reference read verified that main points to this exact result at 2026-11-03T10:34:12Z. The parent gitlink and `claims.json` record that published source identity. Native integration outcomes retain their separate parent evidence identities.
