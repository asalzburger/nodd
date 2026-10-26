# Geant4 material profiles with unrooted

Analyze an existing Geant4 `material_tracks` recording of the DES-024/025
beam-pipe/tracker prototype. No particles are simulated and no geometry is
changed. The [retained report](../../../docs/validation/geantino-material-profiles/README.md)
describes the measured 100,000-track scan and its applicability limits.

Reproduce the figures without ROOT, DD4hep or the large recording, using the
[pinned unrooted environment](../README.md#documentation-plots-with-unrooted):

```sh
software/build/unrooted-venv/bin/python -B software/analysis/material_profiles/plot_profiles.py \
  --data docs/validation/geantino-material-profiles/profiles.json \
  --output build/material-profiles
```

This checks the common track counts, populated bins and additive component means,
then writes PNG/PDF/SVG, self-contained Plotly HTML and CSV for eta, |eta| and phi.
The eta overview is split by subdetector and sensitivity; separate panels use a
local vertical scale for each subdetector. HTML legend toggling is disabled
because hiding a precomputed layer would not recompute the other boundaries.

## Categorize a recording

First follow the [node-specific runtime verification](../../../skills/acts-spack/SKILL.md).
Run the native stage in that ROOT/DD4hep environment with explicit paths:

```sh
python3 -B software/analysis/material_profiles/categorize.py \
  --input /path/to/nodd-tracker.root \
  --compact /path/to/tracker/tracker.xml \
  --factory /path/to/libnODDBeamPipe.dylib \
  --factory /path/to/libnODDPixelBarrel.dylib \
  --factory /path/to/libnODDShortStripBarrel.dylib \
  --factory /path/to/libnODDShortStripEndcap.dylib \
  --factory /path/to/libnODDLongStrip.dylib \
  --output build/material-profiles-native
```

Use the platform's actual factory suffix (`.so` on Linux). The tested native
runtime is macOS arm64 ROOT 6.40.04/DD4hep 1.38; Linux native execution is untested.
`--limit N` is a diagnostic subset. The classifier expects this tracker's volume
prefixes and a beryllium pipe; it is not a general arbitrary-detector classifier.
It reads the latest TTree cycle. Partial/mismatched classification fails before
being accepted for plotting. Keep native ROOT files and caches under `build/`.

Then use the isolated unrooted environment, independently of the native runtime:

```sh
software/build/unrooted-venv/bin/python -B software/analysis/material_profiles/export_profiles.py \
  --input build/material-profiles-native/profiles.root \
  --expected-tracks 100000 --output build/material-profiles-native/profiles.json
software/build/unrooted-venv/bin/python -B software/analysis/material_profiles/plot_profiles.py \
  --data build/material-profiles-native/profiles.json --output build/material-profiles
```

The export checks every native component's count, mean and variance against
an independent per-track reduction. Every track fills every component, including
zero contributions. Means therefore share a denominator and can be stacked.
unrooted receives additive `Histogram` snapshots of those means without profile
spread bounds. Its independent-component uncertainty is disabled: the band uses
the separately filled per-track total and includes component covariance.

The recorder positions are Geant4 **pre-step** positions. The lookup uses
`position + 0.5 * length * direction`. The synthetic `mat_s/e` midpoint is the
pre-step position, not the interior of this Geant4 material step. See the report
for the density check, rounding-cell search and sensitivity-allocation bound.
