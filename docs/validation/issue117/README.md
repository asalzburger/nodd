# Issue #117 — existing-model Si–W digitization prototype

Date: 2026-11-05. **PROTOTYPE**, governed by [DES-044](../../design/DES-044-calorimeter-digitization.md).
The model survey and opt-in implementation are available. Native software tests
pass. The Marlin study and original-framework comparison are **DEFERRED BY HUMAN
DIRECTION** on 2026-11-05 until appropriate software is installed. Neither full
reconstruction runtime is installed in the verified local environment. Existing
prototype code and exploratory results remain isolated; no additional Marlin
study is run after that direction. No design sign-off or physics acceptance is
recorded.

## Implementation and reference identity

Starting nODD main: `96dbf57d0da7f3027e59109c1846d992d68d4d44`.
The implementation uses MarlinReco
`255967eb855ebbc8f75ebaac190b268b63332e8b`:
the unchanged `RealisticCaloDigiSilicon.cc` translation unit and complete unchanged
`RealisticCaloDigi::EnergyDigi` method. SHA-256 checks reject changed upstream
bytes. A separate GPL executable compiles those methods with real CLHEP and
small framework-registration adapters; it exchanges event batches with the MPL
ACTS algorithm through files and `posix_spawnp`, without a shell or linked GPL
code. Full upstream sources remain external. [Notices](../../../software/source/NOTICE.md)
and the [implementation guide](../../../software/source/ActsExamples/Calorimeter/README.md)
describe the boundary, source retrieval and disabled operations.

The subset includes Poisson charge generation, conversion to MIP units, range
clipping before Gaussian noise and a strict float-precision threshold. It merges
all deposits by cell and preserves native deposited-energy-weighted time. It
does not reproduce upstream Standard/ROC timing integration, gain/dead-cell
effects, ADC/ToA, pulse shapes, ageing or pileup. The cell-position converter is
explicitly opt-in for producer-defined cell positions. Empty-channel enumeration
is an adapter extension; noise-only output has no invented truth link.

Compiling original methods proves source reuse. Analytic controls of those
methods are **kernel tests**, and cannot establish agreement with the complete
original event processor on the same `ddsim` hits.

## Verified local environment

- Node: `acts-mac-studio-01.cern.ch`, Darwin arm64; AppleClang 21.0.0.21000334.
- Existing pristine ACTS source/build: sibling
  `nodd-software-layout/software/submodules/acts` and `nodd-software-layout/build/acts`,
  source `355ea68493b326956756c9386d2fd9eaf9328568`.
- DD4hep 1.38 `/3yd4hz3`, Geant4 11.4.3 `/wfg55xi`, EDM4hep 1.1.1 `/bsgcccc`,
  podio 1.8 `/hg64alv`, ROOT 6.40.04 `/szgev3e`; Python 3.14.5.
- Setup SHA-256 `53ed8ad1854b592a01f6b9f9d3b8b49dbbb8a06bddb6677805d4099af2432a97`;
  Spack lock SHA-256 `d51753ae83a710850d06413f3dc0a6bf6ad18554d3911108774c48671dda2cde`.

The registry preflight returned exit 2 because recorded fingerprints changed.
The user was warned before dependent work. Actual `software/env/run.sh python3
software/env/doctor.py` passed DD4hep/DDG4 imports and all twelve Geant4 dataset
presence checks, followed by successful compilation, native tests and `ddsim`.
Sandbox `sysctl`/`ps` and CMake policy warnings were retained. No shared dependency
installation or ACTS build was changed. Marlin, `k4run` and `gaudirun.py` were
not found. A separate SciPy availability probe failed; the retained analysis
uses no SciPy and makes no fitted-MIP claim.

## Native tests

Six CTest suites pass, including eight silicon cases, converter validation and
the existing three-event synthetic ROOT I/O round trip. The latter supplies
fixed fixture hits; it is not a digitized shower reference. The sixth suite
checks the same-hit comparison utility using synthetic files, including corruption
rejection; it executes no original framework.

The signed noise fixture uses 200,000 draws with configured RMS 0.2 MIP and
threshold 0.4 MIP: mean `0.0004413758` MIP, measured RMS `0.200103546` MIP,
and 4,518 accepted draws versus Gaussian expectation 4,550.026. Mean, RMS and
tail checks use the plan's five-standard-error criteria. These are software-test
settings and a declared test-cell inventory, not measured ODD/nODD noise.
Other tests cover Poisson variance, deterministic MIP/range controls, strict
threshold equality, stable event replay, malformed/range-overflow input,
position modes, all-channel empty events and signal/noise truth semantics.

## Prepared reproduction recipe — Marlin phase deferred

The following recipe preserves the prepared workflow for future resumption.
The user deferred the Marlin study; do not treat these commands as completed
full-framework validation. First run the repository's Spack preflight and doctor. Build the native backend
using the implementation guide and an existing matching ACTS source/build.
The local execution used `/private/tmp/nodd-digitization117-build`; substitute
your task-owned build below. Build ODD at
`d70556f33b1c36abdf101a07ad8cf57eb56fbdf1`, preserving its tracked source.

```sh
software/env/run.sh cmake -S /path/to/pinned/OpenDataDetector -B build/odd -G Ninja -DCMAKE_BUILD_TYPE=Release
software/env/run.sh cmake --build build/odd --parallel 4
software/env/run.sh ctest --test-dir /path/to/calorimeter-build --output-on-failure
software/env/run.sh python3 software/analysis/calorimeter_digitization/generate.py \
  --odd-source /path/to/pinned/OpenDataDetector \
  --odd-library build/odd/factory/libOpenDataDetector.dylib \
  --output build/issue117/muons --events 500 --energies 10 --etas 0 2 --particles mu-
software/env/run.sh python3 software/analysis/calorimeter_digitization/generate.py \
  --odd-source /path/to/pinned/OpenDataDetector \
  --odd-library build/odd/factory/libOpenDataDetector.dylib \
  --output build/issue117/showers --events 200 --energies 5 20 50 --etas 0 1 2 --particles e- gamma
software/env/run.sh python3 software/analysis/calorimeter_digitization/calibrate.py \
  build/issue117/muons/mu-_E10_eta0/sim.edm4hep.root build/issue117/calibration.json
software/env/run.sh python3 software/analysis/calorimeter_digitization/analyze.py \
  --samples build/issue117/showers/samples.json build/issue117/muons/samples.json \
  --calibration build/issue117/calibration.json \
  --binary /path/to/calorimeter-build/EDM4hep/nodd_silicon_campaign \
  --backend /path/to/calorimeter-build/nodd_marlin_silicon_backend \
  --work build/issue117/analysis --output docs/validation/issue117/binwise.json
/path/to/matplotlib-python software/analysis/calorimeter_digitization/plot.py \
  docs/validation/issue117/binwise.json docs/validation/issue117
```

On Linux substitute the built `.so` ODD library. Generation invokes the active
Python interpreter on `ddsim`, avoiding the macOS executable-shebang environment
issue. `generate.py` records actual commands, full input hashes, library/script
hashes, seeds, exits and elapsed times in ignored local manifests. It refuses to
overwrite existing samples. An initial pilot attempt supplied an unsupported
boolean argument; this was corrected before the successful smoke and campaigns.
The gun has fixed φ=0.123 rad, `FTFP_BERT`, the full unchanged ODD detector and
its configured field; positive η points alone are not a signed-η/φ acceptance scan.

`calibrate.py` freezes the first 250 central muon events' most populated 2.5 keV
silicon-energy bin as one MIP, giving **148.75 keV**. The remaining 250 events
are held out. This is an empirical bin convention, with 1.25 keV half-bin
quantization; it supplies no Landau–Gaussian fit or systematic uncertainty.
Noise 0.13 MIP and threshold 0.6 MIP reproduce *comparator settings* from CALICE
arXiv:0811.2354v1, not approved nODD parameters. The 2,500-MIP pre-noise range
is the upstream default. Physics/response seeds and every sample input digest
are captured by the prepared binwise workflow; the transport manifests already
retain the completed input identities. Digitization uses all event deposits without
a time cut and sparse signal cells; empty detector cells are not simulated here.

The full ROOT events, intermediate summaries and run logs stay ignored under
`build/issue117/`. No full study results are committed in this preparation change. Exploratory
plots and binwise outputs remain local; retained study evidence will be added
after resumption. Replotting prepared summaries needs JSON and Matplotlib. Regeneration, the MIP split,
per-event correlated checks and a full original-framework comparison need the
local or regenerated event files and verified runtime.

## Remaining issue gates

| Issue deliverable | State / evidence |
| --- | --- |
| Draft recommendation per technology | Available: DES-044, six pinned source implementations and explicit pp/μ=200 gaps |
| Si–W implementation and unit tests | Available: opt-in prototype, five passing native suites |
| Original-framework same-hit comparison | **DEFERRED BY USER** until appropriate software is installed; [prepared recipe and comparator](../../../software/analysis/calorimeter_digitization/reference.md) |
| Muon expected MIP peak | Exploratory local binned characterization only; fitted/path-aware Marlin study deferred |
| Shower plots / linearity / resolution | Geant4 inputs and analysis recipe prepared; further digitized study deferred; no complete physics qualification |
| Remaining technology follow-ups | Three bounded issue drafts listed in DES-044 for maintainer triage |

The visible response is deposited silicon energy / generated energy.
Deposit-equivalent digitized energy has no incident-shower calibration.
Physical active-plus-passive sampling fraction, longitudinal leakage, a
noise-free paired shower control and signed-η coverage are not established by
these summaries. CALICE's 30-layer, graded-absorber geometry is distinct from
ODD's 48 layers; its published performance supplies scale context, not an
acceptance band for this geometry. Issue #117 stays open until its required
reference and physics gates are satisfied.

## User-directed deferral and retained preparation

The user stated: “Hold on for the Marlin study, we will add that when we the appropriate software is installed”.
The Docker inventory approval was interrupted; no inventory result or container
execution is claimed, and no installation was attempted. Six native software
suites passed before this direction. A partial electron-only exploratory analysis
and muon calibration were run before the deferral, not accepted as the completed
Marlin/physics study. The code, source survey, comparison utility and future
recipe are retained; full study plots/results are left for the later software
installation. Full Geant4 input-generation counts are recorded in the session
journal; these are independent transport inputs, not a Marlin validation pass.
