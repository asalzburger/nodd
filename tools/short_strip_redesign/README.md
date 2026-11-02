# DES043 short-strip redesign prototype

Dimensioned proposed baseline SS-2MM-SVC-01, governed by
[DES043](../../docs/design/DES-043-short-strip-service-redesign.md).
This directory is isolated from detector construction. `inputs.json` classifies
proposed dimensions/requirements via DES043; source-model inputs are hash-pinned
to merged PR109. It does not amend old DES020/021 controls.

Python ≥3.11, standard library only, no seed/event input:

```sh
python3 -B -m unittest discover -s tools/short_strip_redesign -p 'test_*.py' -v
python3 -B tools/short_strip_redesign/model.py
python3 -B tools/short_strip_redesign/verify.py
```

For plots use the pinned scientific plotting stack:

```sh
python3 -m venv build/short-strip-redesign/plot-venv
build/short-strip-redesign/plot-venv/bin/pip install numpy==2.4.6 matplotlib==3.11.2 'unrooted @ git+https://github.com/asalzburger/unrooted.git@728465dce0c5cd5b876e67392e3858de6e982d05'
build/short-strip-redesign/plot-venv/bin/python tools/short_strip_redesign/plot.py
```

The existing local DES042 analysis venv was used for this execution; no dependency
or shared ACTS installation changed. Exact versions/output hashes are in the
figure manifest. PNG/PDF metadata excludes timestamps. Font/rendering versions
can affect pixels; use numerical replay as the cross-platform check, and the
same plotting stack for byte checks. The default compact outputs are
`docs/validation/DES-043/summary.json` and `figures/`; no raw run files exist.
`model.py --output PATH` and `plot.py --summary PATH --output DIRECTORY` support
independent replay. Plot source plus summary hashes detect stale figures.

`diagnostics.py` implements finite-plane radial interval unions, planar cooling
centreline length and interloop separation, and a Cu-only azimuth-average
longitudinal-trunk diagnostic. It does not use DD4hep, Geant4 or ACTS. Detailed
complete solid overlaps, hardware performance and complete tracker material
remain outside its scope; see the qualification matrix in the validation report.

The [native recipe](../../docs/validation/DES-043/README.md#native-reproduction-recipe)
constructs explicit modules, cold-petal windows, saddles, tubes, rails and mounts
with the unchanged generic DD4hep factory. Native build products remain local;
`curate_native.py` retains aggregate evidence. `--full` / `NODD_RED_FULL` enables
all12discs; default mirroredfirstpair contains792sensors.

Run the repeatable barrel interfaces separately:

```sh
python3 -B tools/short_strip_redesign/barrel_interfaces.py --source-revision HEAD --output build/short-strip-redesign/barrel-interfaces.json
```

The full thermal screen explicitly charges the50µmASIC bond atκ≥1.2W/m/K
and an additional upstream leakage-path budget≤0.5K/W. The adverse0.333K
margin is conditional; these are requirements to verify, not qualified cold data.
