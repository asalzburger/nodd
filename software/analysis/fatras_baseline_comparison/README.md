# Old/new baseline muon resolutions

PROTOTYPE characterization of two frozen detector baselines with the maintained
native Fatras, geometric digitization and truth-associated Kalman fit. See
[native execution](README_native.md) for the independent 50,000-event current
calibration and eight 20,000-event performance runs. The four values are fixed
**transverse momenta** 1, 5, 10 and 100 GeV, not total momentum. Both baselines
use the same generated events, Bz=3 T, uniform eta[-4,4], full phi, origin and
random muon charge. Performance seed42042; independent training seed142042.

The new geometry uses its independently trained 2 mm short-strip errors; the
old geometry retains its verified original 0.5 mm calibration. No resolution or
pull tuning is performed. Source, geometry, factories, maps, output hashes and
every observed written measurement variance are checked during reduction.

`analyze.py` joins generated particles, selection, fit audit and perigee fits
through the maintained audited reader. Native zero-barcode partial fits are
retained under its guarded primary-provenance rule. Missing outcomes stay in
the generated-event denominator. No residual, pull, tail, charge or fit-quality
cuts are applied. Residuals are fit minus truth; phi is wrapped. Pulls use the
maintained truth-minus-fit convention; derived pT and signed curvature include
theta–q/p covariance. Time has no detector measurement and is omitted from the
resolution comparison.

The plotted resolution is half the central empirical68.268949% interval of
each baseline's finite fits in eight |eta| bins of width0.5. A minimum30 values
is required. Plots give 400-bootstrap sampling standard errors; ratios use
400 paired **generated-event** resamples, preserving each baseline's own fit
losses, with pointwise percentile95% intervals. Common-finite-fit ratios are
additional diagnostics, not the primary comparison. Calibration/model errors
are not included. The binwise evidence also retains 32 signed-eta bins, bias,
median, SD, full RMS, pull statistics, counts and Wilson95% fit/charge intervals.

Full reduction requires a committed analysis source. With the existing local
analysis interpreter (numpy2.4.6, awkward2.14.0, uproot5.7.7, Matplotlib3.11.2):

```sh
analysis_python=../nodd-unrooted/software/build/unrooted-venv/bin/python
analysis_tool=software/analysis/fatras_baseline_comparison
output=docs/validation/fatras-baseline-comparison
analysis_revision=$(git rev-parse HEAD)
"$analysis_python" -B "$analysis_tool/analyze.py" \
  --input build/fatras-baseline-comparison/performance \
  --output "$output/profiles.json.gz" --bootstrap 400 \
  --source-revision "$analysis_revision"
"$analysis_python" -B "$analysis_tool/retain.py" \
  --input build/fatras-baseline-comparison --output "$output"
"$analysis_python" -B "$analysis_tool/plot.py" \
  --data "$output/profiles.json.gz" --output "$output/figures"
"$analysis_python" -B -m unittest discover \
  -s "$analysis_tool" -p 'test_*.py' -v
```

`--partial` is for ignored local diagnostics only. To replot committed results,
only `profiles.json.gz` and the analysis Python are needed; native dependencies
are unnecessary. Full hash/measurement/error/paired-truth checks require local
ROOT files. Keep these ROOT files, event dumps, caches and large logs ignored.
`retain.py` copies only configuration, scalar checks, provenance and counts.

Read the final [report](../../../docs/validation/fatras-baseline-comparison/README.md)
before interpreting the figures. The baselines change geometry, material and
readout together; this is not an isolation of service savings or strixel pitch.
Truth seeding/association does not measure pattern-recognition efficiency.
Mapped material's single-phi averaging and locality/conversion limitations also
limit physical interpretation; the plots do not establish detector acceptance.
