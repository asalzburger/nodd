# Pixel barrel longitudinal coverage prototype

[DES-013](../../docs/design/DES-013-pixel-barrel-z-coverage.md) compares the frozen
working baseline with transverse bond/periphery orientation and close z packing.
It does not modify the DD4hep default or grant design approval.

From the repository root, use Python with NumPy:

```sh
python3 -B -m unittest discover -s tools/pixel_z_coverage -p 'test_*.py' -v
python3 tools/pixel_z_coverage/study.py --output reference/cache/NEW-pixel-z
```

Each case gets a complete deterministic layout, inventory, whole-body and
outward-support clearance checks, primary and total-p sensitivity coverage,
compressed per-track counts, and selected native audit tracks. The configuration
freezes the input hash, scenario choices and sampling seeds. Existing case outputs
are never overwritten. `--case CASE` selects cases; `--probe` makes a small,
explicitly labelled development sample. The 0.2 mm target is not a sensor spec.

For ACTS, follow the [node-specific skill](../../skills/acts-spack/SKILL.md), run
its preflight, and verify the native sensitivity and step-size bindings. On the
verified node the executed setup is:

```sh
source /Users/salzburg/cernbox/configs/acts/acts_setup.sh
acts run acts-nodd
source /Users/salzburg/Documents/work/installed/acts-nodd/pyvenv/bin/activate
export PYTHONPATH="/tmp/acts-python-step-size-overlay/python:${PYTHONPATH:-}"
python tools/pixel_z_coverage/study.py --output reference/cache/NEW-pixel-z \
  --native-only --acts-source /Users/salzburg/Documents/work/dev/acts-nodd \
  --runtime-manifest /tmp/acts-python-step-size-overlay/manifest.json
python -B -m unittest discover -s tools/module_layout -p 'test_acts_validate.py' -v
```

The temporary overlay is node-specific; see the existing
[module-layout workflow](../module_layout/README.md) to recreate it or replace
it with an equivalent clean installation. Its library reuse and dirty sister
source must not be presented as a clean rebuild. Missing bindings stop native
validation; analytic coverage is not relabelled as ACTS execution.

Render portable vector drawings and the comparison tables without Matplotlib:

```sh
python3 tools/pixel_z_coverage/diagnostics.py --run reference/cache/NEW-pixel-z
python3 tools/pixel_z_coverage/report.py --run reference/cache/NEW-pixel-z \
  --output reference/cache/NEW-pixel-z-report
```

For a future sensor update, regenerate the governing baseline and review its
new hash, model provenance and chip/periphery convention before editing the
study input. Do not merely bypass the hash guard. Guards are anisotropic here;
active chip areas and internal dead seams are preserved. Transverse support
screens do not recalculate detailed cable routing, mounting rings or hydraulics.

In the same ACTS shell, run the explicit 1 µm inside/outside z-edge controls and
common z = −11/0/+11 mm seam rays on all six complete geometries:

```sh
python tools/pixel_z_coverage/native_seams.py --run reference/cache/NEW-pixel-z \
  --acts-source /Users/salzburg/Documents/work/dev/acts-nodd
```

`acts-seams/` retains these separately from the original sampled native audit.
Each edge has an explicit expected inside/outside classification in addition to
the oracle comparison; no sensor bound or native tolerance is enlarged.

Before committing evidence, losslessly archive the large generated summaries and
native reports (round-trip bytes are verified before removing the expanded copy):

```sh
python3 tools/pixel_z_coverage/archive.py --run reference/cache/NEW-pixel-z
```

The report renderer accepts either `.json` or `.json.gz`. Retained archives can
be inspected with Python's `gzip` module or `gzip -dc FILE.json.gz`; native audit
reruns write a fresh expanded report, which can then be archived again.
