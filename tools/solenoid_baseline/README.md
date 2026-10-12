# DES-026 solenoid baseline — PROTOTYPE

Isolated sizing/illustration only. No production detector, material, field or
reconstruction configuration is changed. See [the design](../../docs/design/DES-026-tracker-solenoid-baseline.md).

`model.py` adapts PR6 `tools/magnetic_study/sizing.py` at
`d2437a7d84dbd02eed098c2a6341c5447cc42701`: homogeneous current normalization
and all-space Neumann energy with analytic axial integration. Axial field is
integrated analytically across the radial pack. No other PR6 layouts are imported.
The source catalogue records original file hashes.

NumPy is the existing prototype-controls dependency
(`tools/tracker_layout/requirements-controls.txt`). Plotting reuses existing
Matplotlib; no dependency installation was needed. Locally an existing
`reference/cache/envelope-venv` provided NumPy 2.5.3 / Matplotlib 3.11.2.

```sh
python -B tools/solenoid_baseline/run.py
python -B -m unittest discover -s tools/solenoid_baseline -p 'test_*.py' -v
python -B tools/solenoid_baseline/tracker_snapshot.py --expected "$tracker_expected_json"
MPLCONFIGDIR=/tmp/nodd-mpl python -B tools/solenoid_baseline/plot.py
```

The expected tracker JSON is an ignored DES025 exporter product. Regenerate it,
if needed, using `python tools/tracker_dd4hep/export.py --output build/solenoid-tracker-input`;
this is source export, not native DD4hep validation. Extraction rejects source
hash mismatches. Committed grouped bounds let the figure be rendered without
that large local input. Group bounds deliberately omit passive tracker geometry.

Outputs carry input/code hashes. `run.py` also records actual Git execution
revision/dirty state; enclosing publication commits do not replace those values.
The conditional 7.2 m cold mass sizes to 143.174 MJ and 1.558656 m vessel outer
radius; retain 1.64 m assembly reservation. Historical 6.6 m results are a control,
not a tracker-compatible variant. No critical-current, structural or protection
qualification is implied by numerical convergence.
