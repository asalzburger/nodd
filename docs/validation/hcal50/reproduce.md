# Reproduce the standalone 50 GeV pion study

Use the reverified existing acts-spack runtime via software/env/run.sh. Recorded
native packages: DD4hep1.38/3yd4hz3, Geant411.4.3/wfg55xi, Python3.14.5,
ROOT6.40.04. No shared dependency is installed or changed. Existing analysis
Python has NumPy2.5.4 and Matplotlib3.11.2. Full data stay ignored and local.

Frozen transport/factory implementation:
`464dab316ac7d27d0c0f79ac89f6eb8960a703ca`; later auditor lifecycle and
aggregate/plot revisions retain their own hashes. Geometry, sample, library,
producer and readback identities accompany the evidence.

Run from the repository root. Use fresh output directories; preserve failed
attempts. The tested macOS library suffix is dylib; use the actual suffix on
another supported node.

```sh
python3 -B tools/hcal_response/export.py --output build/hcal50/geometry
software/env/run.sh cmake -S prototypes/hcal_response -B build/hcal50/factories -G Ninja
software/env/run.sh cmake --build build/hcal50/factories --parallel 3
software/env/run.sh cmake -S software/analysis/hcal_response -B build/hcal50/audit -G Ninja -DCMAKE_BUILD_TYPE=Release
software/env/run.sh cmake --build build/hcal50/audit --parallel 3
python3 -B software/analysis/hcal_response/transport.py prepare \
  --geometry build/hcal50/geometry --output build/hcal50/sample \
  --events 10000 --input-seed 20261120
```

Run serial/MT24-event controls with the same sample/seed before production:

```sh
software/env/run.sh python3 -B software/analysis/hcal_response/transport.py run \
  --sample build/hcal50/sample --output build/hcal50/serial24-final \
  --geometry-library build/hcal50/factories/libnODDHCALResponsePrototype.dylib \
  --audit-library build/hcal50/audit/libnODDHCALResponseAudit.dylib \
  --events 24 --threads 1 --seed 202650001 --max-step-mm 5 --reserve-gib 30
software/env/run.sh python3 -B software/analysis/hcal_response/transport.py audit \
  --sample build/hcal50/sample --run build/hcal50/serial24-final
```

Repeat with fresh mt24-final and threads12, audit that output, then compare:

```sh
python3 -B software/analysis/hcal_response/transport.py compare \
  --first build/hcal50/serial24-final --second build/hcal50/mt24-final \
  --output build/hcal50/serial-mt.json
software/env/run.sh python3 -B tools/hcal_response/native.py \
  --directory build/hcal50/geometry \
  --library build/hcal50/factories/libnODDHCALResponsePrototype.dylib \
  --output build/hcal50/native-clean.json
```

Require all gates and a clean native exit. The earlier full native process
completed its numerical checks but aborted during ROOT interpreter teardown;
that failure is retained separately. The corrected auditor uses the existing
single-thread/explicit-cleanup lifecycle without changing scientific checks.

```sh
software/env/run.sh python3 -B software/analysis/hcal_response/transport.py run \
  --sample build/hcal50/sample --output build/hcal50/production12 \
  --geometry-library build/hcal50/factories/libnODDHCALResponsePrototype.dylib \
  --audit-library build/hcal50/audit/libnODDHCALResponseAudit.dylib \
  --events 10000 --threads 12 --seed 202650001 --max-step-mm 5 --reserve-gib 30
software/env/run.sh python3 -B software/analysis/hcal_response/transport.py audit \
  --sample build/hcal50/sample --run build/hcal50/production12
```

The production auditor adds an independent physical-centre check after
transport. Its source hash differs from the frozen launch runner and is retained
explicitly; geometry, transport policy and saved hits are unchanged.

Every positive sensitive-step deposit must close to native hit sums during
transport. Saved readback validates every primary, cell address, carrier parent,
collection, position and layer/energy sum. It permits documented floating-point
persistence rounding; inspect the observed residual maxima in the retained
readback rather than calling them exact. Serial/MT controls separately require
identical saved per-cell addresses, energies and positions.

```sh
plot_python=/Users/salzburg/Documents/work/installed/acts-nodd/pyvenv/bin/python
MPLCONFIGDIR="$PWD/build/hcal50/mpl" "$plot_python" -B \
  software/analysis/hcal_response/analyze.py analyze \
  --run build/hcal50/production12 --output build/hcal50/analysis \
  --bootstrap 1000 --seed 13001000
MPLCONFIGDIR="$PWD/build/hcal50/mpl" "$plot_python" -B \
  software/analysis/hcal_response/analyze.py plot \
  --summary docs/validation/hcal50/summary.json --output build/hcal50/replot
MPLCONFIGDIR="$PWD/build/hcal50/mpl" "$plot_python" -B docs/validation/hcal50/draw_fit.py
python3 -B -m unittest discover -s tools/hcal_response -p 'test_*.py' -v
"$plot_python" -B -m unittest discover -s software/analysis/hcal_response -p 'test_*.py' -v
```

Raw width, mean response, histograms, longitudinal statistics and covariance
can be replotted from summary.json alone. Independent ID, geometry membership,
worker and energy-closure checks require full native/run artifacts. The fixed
energy is total energy, with pion mass0.13957039 GeV explicitly included when
deriving the primary momentum.
