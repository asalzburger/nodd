# Pixel TDR generated assets

`generate.py` reads frozen DES017/018 layouts and DES019 native evidence, without
importing the geometry producers or changing scientific inputs. It generates
the per-disc single/quad/chip/circuit table, measured-result macros, and vector
disc/longitudinal figures under `docs/publication/tdr/`.

Matplotlib is needed only to regenerate figures. `--check` is standard-library
only and verifies exact source and generated-asset hashes. Figures use nominal
ring radii for the longitudinal plot and actual frozen compensated active-area
corners for face views. Figure captions distinguish projections from collisions
and preserve coverage qualifications.

The manuscript and generated assets are self-contained for pdfLaTeX. No
Overleaf mutation, scientific rerun, or design approval is performed.
