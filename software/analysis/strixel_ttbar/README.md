# Fatras ttbar + 200 pileup strixel comparison

This isolated DES042 **PROTOTYPE** compares local-v strixel lengths
0.5/1/1.5/2 mm using 100 paired events per length. The hard process is the
ACTS guide's qqbar-only ttbar (`Top:qqbar2ttbar=on`) at 14 TeV, with exactly
200 `SoftQCD:all=on` pileup interactions per event. This is not the full
qqbar+gg ttbar mixture.

The guide is matching ACTS355ea
`Examples/Scripts/Python/full_chain_odd.py`. Its generation/vertex setup is
used with the maintained nODD tracker, fixed effective material and constant
3 T field. Pixel-only GBTS uses the `pt4-nominal-triplet` profile with a common
±1m z0 window matching the guide's selected vertex region, instead of the
single-particle control's ±15mm. Geometry/ROI, graph cuts and tracking-filter
window agree. This adaptation precedes the100-event sample; all other seeder,
all-system CKF, muon hypothesis and ambiguity settings remain fixed. Only
systems4/5 local-v Gaussian sigma scales with length; doMerge=False. Physical
cell sharing, cluster merging, electronics occupancy and services/material
changes are not modeled by this response scan.

## Native environment and task-owned component

Run the acts-spack node preflight first. A changed registry fingerprint is an
unverified installation, not a successful runtime check. The recorded node
requires actual imports/build checks; do not alter shared dependencies.

The existing ACTS build does not include its Pythia8 Python component. The new
task-owned sidecar compiles a hash-checked copy of the matching upstream Pythia
generator against already installed Pythia8@8.317. Its single code change
checks `next()` success and aborts the whole event on failure, without retry
or resampling. Task-owned origin tags and sample/audit code retain the complete
native sample. It requires the existing exact pybind11 3.0.4 headers
(internals11), matching the native runtime; the current default view can expose
a different version. Use a fresh zsh and task-owned build directory:

```sh
python3 /Users/salzburg/.codex/skills/acts-spack/scripts/preflight.py --require-sources
source software/env/truth_tracking.sh
nodd_ttbar_pybind_prefix=$(spack location --install-dir py-pybind11@3.0.4)
nodd_ttbar_pythia_prefix=$(spack location --install-dir pythia8@8.317)
cmake -S software/source/ActsExamples/StrixelPileup \
  -B build/strixel-ttbar-native -G Ninja \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DNODD_ACTS_SOURCE="$PWD/../nodd-software-layout/software/submodules/acts" \
  -DNODD_ACTS_BUILD="$PWD/../nodd-software-layout/build/acts" \
  -DPython_EXECUTABLE="$PWD/../nodd-software-layout/build/pyvenv/bin/python" \
  -Dpybind11_DIR="$nodd_ttbar_pybind_prefix/share/cmake/pybind11" \
  -DPYTHIA8_INCLUDE_DIR="$nodd_ttbar_pythia_prefix/include" \
  -DPYTHIA8_LIBRARY="$nodd_ttbar_pythia_prefix/lib/libpythia8.dylib"
cmake --build build/strixel-ttbar-native --parallel 2
cmake -S software/source/ActsExamples/StrixelPileupSafeFatras \
  -B build/strixel-ttbar-safe-fatras -G Ninja \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DNODD_ACTS_SOURCE="$PWD/../nodd-software-layout/software/submodules/acts" \
  -DNODD_ACTS_BUILD="$PWD/../nodd-software-layout/build/acts" \
  -DPython_EXECUTABLE="$PWD/../nodd-software-layout/build/pyvenv/bin/python" \
  -Dpybind11_DIR="$nodd_ttbar_pybind_prefix/share/cmake/pybind11"
cmake --build build/strixel-ttbar-safe-fatras --parallel 2
ctest --test-dir build/strixel-ttbar-safe-fatras --output-on-failure
cmake -S software/source/ActsExamples/StrixelPileupSafeGbts \
  -B build/strixel-ttbar-safe-gbts -G Ninja \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DNODD_ACTS_SOURCE="$PWD/../nodd-software-layout/software/submodules/acts" \
  -DNODD_ACTS_BUILD="$PWD/../nodd-software-layout/build/acts" \
  -DPython_EXECUTABLE="$PWD/../nodd-software-layout/build/pyvenv/bin/python" \
  -Dpybind11_DIR="$nodd_ttbar_pybind_prefix/share/cmake/pybind11"
cmake --build build/strixel-ttbar-safe-gbts --parallel 2
ctest --test-dir build/strixel-ttbar-safe-gbts --output-on-failure
```

Matching ACTS source is
`355ea68493b326956756c9386d2fd9eaf9328568` in the runtime supplier, not the
separately modified development checkout. Defaults use sibling
`nodd-gen3-material-mapping` for existing detector/material/GBTS/SafeFatras
sidecars and `nodd-software-layout` for matching source/runtime. Override these
with `--supplier-root`, `--runtime-root`, `--native-dir` and
`--fatras-native-dir` and `--gbts-native-dir` if needed, keeping
the actual binding/runtime identities consistent.

Pythia retains its upstream scoped FPE-monitor disablement during generation.
Fatras and reconstruction monitoring remain active. The separate task-owned
Fatras component retains the existing zero-contribution exponential guard
and adds a conservative guard for an underflowing gamma power intermediate.
It changes an internal gamma value only where the downstream energy loss
already rounds exactly to zero; all random draws and the original path
elsewhere remain unchanged. Native and strict floating-point controls compare
energy loss, parent/photon state and RNG state, including the original
underflow-positive case. Compiled local/upstream/generated hashes bind the
actual component to its inputs. Shared/frozen helpers remain preserved.
Fatras retains pMin=0.5 GeV absolute momentum, interactions and propagation
limits. A separate audit copies failed-particle state before queue erasure,
without changing simulation output or random streams.

The first 100-event attempt under `build/strixel-ttbar-production/` is preserved
as failed: all event files were written, but final monitoring found the gamma
underflow. It is not an accepted reconstruction input. Corrected production
must rerun the same seed and compare every native particle/hit payload exactly.
Particle-level maximum-step failures remain reported and retained; generated
truth denominators are not filtered to hide transport losses.

The separate task-owned GBTS component uses uniquely named, hash-checked
copies of the required Core classes. It selects the scattering denominator
before division: one for barrel, squared slope for endcap. This preserves
selected arithmetic and avoids Clang O2 evaluation of a source-unselected
endcap divide at zero barrel slope. It introduces no rejection, epsilon,
floor, tuned cut or FPE mask. Exact native object flags/compiler, compiled
local/upstream/generated hashes, original/renamed/instrumented/guarded replay,
ordered seed IDs/quality bits and complete per-event numerical diagnostics
make the implementation explicit. Genuine selected-endcap/innovation failures
remain monitored. The frozen helper and shared ACTS build are preserved.

## Paired native execution

Commit/freeze executing sources before production. A distinct-seed smoke must
prove the selected transport input, interaction-origin mapping, complete native
particle/hit roundtrip, response variances and convergence first.

```sh
source software/env/truth_tracking.sh
python -B software/analysis/strixel_ttbar/campaign.py launch \
  --events 100 --seed 153042 --jobs 4 --output build/strixel-ttbar-repeat-01
python -B software/analysis/strixel_ttbar/campaign.py check \
  --events 100 --seed 153042 --jobs 4 --output build/strixel-ttbar-repeat-01
```

The campaign first generates/transports one sample, then reconstructs its four
lengths in fresh processes. Each process has one ACTS thread. `--jobs` bounds
concurrent reconstruction processes; default1. Generation has one hard-scatter
interaction followed by200pileup interactions, with vertex sigma
(0.0125,0.0125,55.5) mm and5ns. Generator selection is rho<=24mm, |z|<=1m,
|eta|<=3 and pT>=150MeV. Full preselection truth is retained separately.
Authoritative producer tags survive HepMC conversion; barcode numbering alone
is not used to infer hard scatter. Any ambiguous origin merger is an error.

Lossless per-event gzipJSON retains complete generated/selected/simulated
particle states, origin labels and hits. Each reconstruction reader restores
and exactly reserializes every native field before publishing inputs. This
avoids ROOT float32 precision and final-state omissions. Native audit includes
all generated events, initial positions/ct, measured inputs/associations,
pixel space points/seeds and every completed CKF/ambiguity candidate needed
for independent classification. Large raw outputs remain ignored and retained.

Choose a fresh output directory. `resume` requires the identical plan, revision,
sources and arguments; it verifies and skips only completed immutable cases.
Failed/interrupted/nonempty cases are preserved and refused, never silently
retried or overwritten. Disk guards fail explicitly rather than discarding
evidence. Small development runs can use --events1 --seed153043 in a separate
directory; they are not production performance evidence.

A completed immutable sample can be reused explicitly after a reconstruction
source change. Its original generation revision and full report hash remain
bound separately from the new reconstruction freeze. The campaign verifies
all sample outputs, seed and event count before reuse and after reconstruction;
it does not regenerate or relabel that sample. For the GBTS numerical remedy:

```sh
python -B software/analysis/strixel_ttbar/campaign.py launch \
  --events 100 --seed 153042 --jobs 4 \
  --sample build/strixel-ttbar-production-v2/sample \
  --output build/strixel-ttbar-production-v3
```

All four v2 loops processed100events but their final sequencer audits failed
one speculative GBTS divide at event57. Those outputs remain failed and are
preserved. The valid corrected Fatras sample is reused by the fresh v3
reconstruction; its generation revision remains250a211.

`resume` and the CLI `check` require the exact executing Git revision. After
committing evidence or journal updates without changing executing sources,
the retained plan can be checked read-only by its recorded source hashes:

```sh
python3 -B - <<'PY'
import json
from pathlib import Path
import sys
sys.path.insert(0, 'software/analysis/strixel_ttbar')
import campaign
directory = Path('build/strixel-ttbar-production-v3').resolve()
expected = json.loads((directory / 'campaign-plan.json').read_text())
assert campaign.source_identity() == expected['source_sha256'], 'Use the recorded executing sources'
print(json.dumps(campaign.verify(directory, expected), indent=2))
PY
```

For the numerical correction regression, the v2 plan was initialized with the
same `campaign.plan`/`write_json` functions and only generation was launched
first. The recorded
`logs/codex/SESSION-2026-10-31-strixel-ttbar-pu200/verify-numerical-replay.py`
rehashes all original/corrected event payloads and checks the completed report,
failure identities and affected-event truth inventories. Only after that gate
passed was the unchanged plan resumed for reconstruction. The first failed
attempt remains preserved; future ordinary campaigns can use `launch`.

## Metrics and uncertainties

Headline efficiency uses charged generated particles with pT>=1GeV, |eta|<=3,
rho<=24mm and |z|<=1m, before hit/track requirements. Report inclusive,
hard-scatter and pileup scopes. Conditional denominators >=9associated
measurements and >=6sensors/3physical pixel groups remain separate.

Match unique inlier measurements with purity>=0.5 and completeness>=0.5.
Choose ties by overlap then barcode, representatives by most inliers, lowest
chi2/ndf then stable index. Quality uses >=7unique inliers, reference and finite
positive fit covariance. Rejected raw candidates remain counted. An otherwise
accepted unique/native measurement-count mismatch is an error as in the frozen
classifier; raw rejected mismatches are retained as diagnostics.

Unmatched candidates are fakes. Matches to out-of-fiducial generated truth or
simulation secondaries are separate. Additional matches per truth particle are
duplicates, not fakes. Both CKF and ambiguity stages are retained. A separate
guide-like analysis selection requires reconstructed pT>=1GeV, |eta|<=3,
|loc0|<=4mm and <=2holes/outliers. This is applied after the frozen chain; it
does not reproduce the guide's different native reconstruction configuration.

Use2,000 deterministic jointly paired event-block bootstrap resamples for
ratio-of-sums efficiencies, candidate fractions and cross-length differences.
Particles/tracks within pileup events are not independent binomial trials.
Fake-event incidence additionally has Wilson intervals and, for zero observed
fake events, an exact one-sided95% upper bound (2.9513% at100events). That is
not a candidate-fake bound. Flag degenerate intervals and retain denominators;
all intervals are pointwise statistical statements, not equivalence claims.

The original GBTS graph limit remains2,000,000edges; the wider-window pilot
reaches it. This comparison probes the chain under that resource limit. Each reconstruction
retains `native-sequencer.log` and a complete event-indexed `graph_audit` in its
native report, with edge/link counts, cap-warning consistency and incidence.
Debug logging changes no algorithm or random-stream position. The separate
`capped_seeds` output statistic does not diagnose this graph limit. Report
graph-cap incidence alongside efficiency; the result is not unconstrained
seeder or detector performance.

Offline analysis uses the existing pinned NumPy/uproot/unrooted environment at
`../nodd-gen3-material-mapping/build/truth-tracking-baseline/analysis-venv/bin/python`.
Per-event numeric NPZ matching inputs allow independent classification replay
without ACTS or raw native files. No package installation is needed.

```sh
nodd_ttbar_analysis_python="$PWD/../nodd-gen3-material-mapping/build/truth-tracking-baseline/analysis-venv/bin/python"
for nodd_ttbar_pitch in 0.5 1 1.5 2; do
  "$nodd_ttbar_analysis_python" -B software/analysis/strixel_ttbar/analyze.py retain \
    "build/strixel-ttbar-production-v3/pitch$nodd_ttbar_pitch" \
    --events 100 --output "docs/validation/DES-042/ttbar-pu200/pitch$nodd_ttbar_pitch"
done
"$nodd_ttbar_analysis_python" -B software/analysis/strixel_ttbar/analyze.py statistics \
  --data docs/validation/DES-042/ttbar-pu200 \
  --output docs/validation/DES-042/ttbar-pu200 --replicates 2000
"$nodd_ttbar_analysis_python" -B software/analysis/strixel_ttbar/analyze.py statistics \
  --data docs/validation/DES-042/ttbar-pu200 \
  --output docs/validation/DES-042/ttbar-pu200 --replicates 2000 --verify
"$nodd_ttbar_analysis_python" -B software/analysis/strixel_ttbar/plot.py \
  --data docs/validation/DES-042/ttbar-pu200/profiles.json.gz \
  --output docs/validation/DES-042/ttbar-pu200/figures
"$nodd_ttbar_analysis_python" -B -m unittest discover \
  -s software/analysis/strixel_ttbar -p 'test_*.py' -v
```

For a repeat, use fresh native/evidence/figure directories. Retention refuses
existing output, verifies native hashes and validates every measurement variance,
pixel transform, hypothesis and candidate before saving portable inputs.
`replay <retained-case-directory>` independently rebuilds its classifications
and all sufficient counts. `statistics --verify` checks all four classifications,
paired controls, all 2,000 bootstrap results and generated Markdown exactly.
The raw sample/output hashes and sanitized native reports remain in retained
case summaries. Figure manifests bind source/data and each PNG/PDF; a fresh
rerender can be compared byte-for-byte without ACTS.


## Published artifacts and local data

The 2026-10-31 human instruction excludes raw/portable data from the PR.
`pitch*/`, `profiles.json.gz` and all native build outputs remain local and
ignored; plots, compact reports/provenance and rerun code are published.
The source/review revisions refer to the original local snapshots preserved
at the archive ref in `docs/validation/DES-042/local-artifacts.json`.
A fresh clone must generate/retain a dataset before full offline replay.
CI runs the synthetic tests and verifies published figure/source hashes.

```sh
python3 -B software/analysis/strixel_reconstruction/verify_plots.py
```
