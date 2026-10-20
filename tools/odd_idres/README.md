# Reproducible ODD IdRes documentation study

See the [results, figures, data dictionary and source map](../../docs/validation/ODD-idres/README.md).
This is an isolated ideal-surface characterization of existing prototypes; it
does not construct or change a production detector.

- `prepare.py`: pinned ODD extraction and current prototype JSON reduction.
- `run.py`: one IdRes process per field; full numeric output retention, independent
  hit/material cross-checks and measurement-only covariance controls.
- `plot.py`: regenerate SVGs from committed JSON, without IdRes or detector runtimes.
- `verify.py`: retained hashes, complete grids, CSV/JSON agreement and SVG parsing.
- `test_study.py`: technology-count semantics, incidence, stereo response,
  aperture invariants and failed-input checks.

Run from the repository root. Geometry preparation and verification use Python
3.10+ standard library. Numerical controls need the repository's pinned NumPy;
plotting needs the existing Matplotlib plotting requirements. The recorded run
used Python 3.14.6, NumPy 2.5.3 and Matplotlib 3.11.2. Exact execution versions are
also in the provenance/figure manifests. No ACTS/Spack setup is needed.

```sh
python3 -B tools/odd_idres/prepare.py
python3 -B -m unittest discover -s tools/odd_idres -p 'test_*.py' -v
python3 -B tools/odd_idres/verify.py
MPLCONFIGDIR=build/odd-idres-mpl python3 -B tools/odd_idres/plot.py
```

See the results document for building/running the externally supplied IdRes
revision and for optional source extraction. Never pass several field values to
one IdRes process: the earlier adapter records a shared-field-table defect.
