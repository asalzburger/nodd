# Job output analysis

Output inspection, plots and independent validation entry points belong here.
Generated data stays under the ignored repository build directory.

## Documentation plots with unrooted

[Issue #95](https://github.com/asalzburger/nodd/issues/95) requests
[unrooted](https://github.com/asalzburger/unrooted) for future documentation plots.
The source is pinned to `728465dce0c5cd5b876e67392e3858de6e982d05`
(`0.1.0rc1`, MIT). Python 3.11 or newer is required. The optional Plotly backend
is included for interactive HTML; Matplotlib supplies PNG, PDF and SVG figures.

Run from the nODD repository root in a separate environment:

```sh
python3.11 -m venv software/build/unrooted-venv
software/build/unrooted-venv/bin/python -m pip install -r software/analysis/requirements-unrooted.txt
software/build/unrooted-venv/bin/python -I software/analysis/unrooted_smoke.py
source software/build/unrooted-venv/bin/activate
unrooted --help
```

With uv, use `uv venv --python 3.11 software/build/unrooted-venv`, followed by
`uv pip sync --python software/build/unrooted-venv/bin/python software/analysis/requirements-unrooted.txt`.
The dedicated environment is independent of the node-bound ACTS/Spack runtime.
All dependencies are pinned in the generated requirements file; Git is needed
to obtain the exact upstream source. This adds no submodule or C++ ROOT dependency.
The local installation on 2026-10-23 used CPython 3.11.15 on macOS arm64; other
platforms are not qualified by that local run. The universal requirements also
resolve Python 3.12+ packages, without claiming those runtimes were tested locally.

The smoke check writes synthetic ROOT input, compares loaded values, variances
and edges exactly, checks the installed source revision, loads the bundled ODD
palette, renders an overlay with a ratio, saves PNG/PDF/SVG and self-contained
Plotly HTML, and exercises CLI help and PNG export. Results and package versions
go to `build/unrooted-smoke/validation.json`; generated plots are in that same
ignored directory. Fixture data is arbitrary test data and carries no detector
performance claim. The [retained installation report](../../docs/validation/unrooted-installation.json)
records the actual local run. Artifact hashes identify that run; binary figure
metadata and ROOT file identifiers need not be identical on regeneration.

For an existing histogram:

```sh
unrooted --input path/to/results.root --draw hist:histogram_name --output build/figure.pdf
unrooted --input path/to/results.root --draw hist:histogram_name --backend plotly --output build/figure.html
```

Use the [upstream plotting guide](https://asalzburger.github.io/unrooted/user-guide/plotting/)
for overlays and point clouds. Plotly HTML embeds JavaScript and needs no extra
export runtime; static figures here use Matplotlib. No Plotly static-export
dependency is installed. Use `deactivate` before returning to the ACTS environment.

To deliberately update the upstream source, change `requirements-unrooted.in`,
then regenerate pins with uv and rerun the smoke check:

```sh
uv pip compile --universal --python-version 3.11 software/analysis/requirements-unrooted.in --output-file software/analysis/requirements-unrooted.txt
```
