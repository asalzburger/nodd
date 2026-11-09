# nODD geometry and silicon digitization comparison

Date: 2026-11-09. **PROTOTYPE; execution in progress, no detector acceptance.**
Requested in [PR118 comment6744059438](https://github.com/asalzburger/nodd/pull/118#issuecomment-6744059438).
The [frozen protocol](nodd-digitization-protocol.md) and
[pre-analysis clarifications](nodd-digitization-analysis-notes.md) govern this
extension. The earlier [fielded ODD digitizer study](digitization-results.md)
and [isolated positive-endcap tiling/control study](tiling-response.md) retain
their separate configurations and numerical evidence.

## Actual scope and current checks

This study uses the maintained **LAYOUT-001 tracker plus Si–W ECAL stage**:
beam pipe/tracker systems0–7, full DES031 barrel8 and both DES030 tiled endcaps9.
Local hardware and all sectors/layers remain. The baseline has no solenoid,
magnetic field, HCAL, FCAL or muon system. It is not a complete fielded detector.

The newly exported native union passes construction, exact ten-system root
mapping and a complete ROOT overlap/extrusion scan at **1e-5 mm (10 nm)**:
13,506,030 physical nodes, 650,387 volume UIDs, zero reported overlaps/extrusions.
The scan considered16,946,408 candidate pairs. Point preparation took1372.71s;
the24-thread candidate check took35.734s. Normal cleanup and process exit0 were
verified. This geometric software check grants no engineering sign-off.
The [compact native proof](previews/nodd-geometry-validation.json) retains the
source, exported geometry/material/factory identities, original report/log
hashes, aggregate counts and runtime registration fingerprints.

The matched control uses ODD
`d70556f33b1c36abdf101a07ad8cf57eb56fbdf1`, with its original component scope
and a task-owned root-copy wrapper removing only the field block. Both transports
use an explicitly audited5-mm charged-particle maximum step in sensitive ECAL
silicon,0.7-mm production range cut and FTFP_BERT. Other geometry/material scope
differences remain intentional; this does not isolate a tiling-only effect.

The excluded two-block technical pilot verified actual initialized G4 field0,
both ECAL detector identities, effective region cuts0.7mm, silicon Birks0,
charged StepLimiter processes/maxstep5mm, and independent reset RNG states.
Four pilot muons have exact origin0, ordered run/event identities and momentum
residual at most3.6e-15GeV. They never enter response denominators.

All **9,500 transport events** and **48 native digitization jobs** now close
normally. Four transport receipts bind the full frozen inventory, actual
initialized field/cuts/step settings, source/configuration/library hashes and
independent RNG states. Every population passes truth, ordered header, count,
unique-cell and raw-hash checks. The [compact transport/native execution
record](previews/nodd-transport-validation.json) retains all 48 population
identities, aggregate counts, seeds and hashes, without event payloads.
The nODD shower and muon groups take 12,389.345 s and 7,215.299 s respectively.
Slow DDG4 path mapping and repeated Geant4 material/cut-couple scans are retained;
no runtime, factory or geometry is modified to bypass them.

Both actual cell-position audits and the closed six-muon analysis pass. A
separate PhysVal agent reproduces its counts, spectra, uncertainty calculations
and all central fits before author conclusions. Full shower statistics and the first four response figures now close and pass
separate scientific assessment. The original/native nODD framework comparison
is still running; the earlier ODD-only pass remains separate evidence.

## Frozen samples and interpretation

The main matrix is e−/γ at5/20/50GeV/c andη0/1/2,200events per point per geometry.
A bounded e−20GeV/c,η−2 control adds200events per geometry. Detailed10GeV/c
muons have250events at eachη0/2/−2 per geometry. Four independent zero-field
ODD electron references have100events at20GeV/c,η0/1/2/−2.
Total:4550nODD validation events plus4950ODD events = **9500new transport events**.
The negative control is not a full negative-η energy/species scan.

The native Geant4 gun receives the requested momentum directly. Denominators
use persisted generated **total energy**. The origin, PDG, momentum/direction,
monoenergetic total energy, run/event order, counts and every raw hash are checked.
The shared fixed response is148.75keV/MIP, strict>0.6MIP threshold,2500MIP
pre-noise range,3.6eV pair energy and0.13MIP electronics RMS. D disables both
random coefficients; PN enables both. These remain unsigned comparator settings.

One independent ODD-reference calibration perη is shared across both geometries,
species, energies and stages. Unscaled visible fractions remain primary, so a
separate nODD calibration cannot hide geometry effects. Raw/D/PN are paired on
the same event within a geometry; the two geometry transports are independent.
The5000-replicate whole-event/reference bootstrap retains their shared-scale
and paired-stage covariance. Distribution SD/mean is not reconstructed resolution.

Muon spectra use primary-qualified single-cell crossings, actual native normals
and immediate constructed neighbouring planes. Missing deposits remain unknown
transported crossings. Nominal opportunity yield and conditional identified
crossing yield are separate; straight-ray active-mask predictions are explicitly
approximate. The fixed Landau–Gaussian model/1000-event bootstrap can remain
unavailable or flagged; the MIP scale and fit range are never retuned.

## Electron/photon response and geometry comparison

Across all 19 matched gun points, the nODD/ODD mean **raw silicon visible-energy
ratio is 0.48801–0.62934**; after PN digitization it is 0.48593–0.62823.
The substantial difference already exists in transport. These geometries differ
in tracker, ECAL sampling construction, inactive material and overall scope;
this study cannot isolate its cause or assign it to tiling alone. It provides
no area-averaged tiling loss or detector acceptance. The earlier isolated
[tiled/continuous-silicon control](tiling-response.md) addresses a narrower
question and retains its own input geometry.

Representative 20 GeV/c mean ratios are below (± whole-event bootstrap SE).
The negative-η electron point is a bounded control, not a complete signed scan.

| Particle, η | Raw nODD / ODD | PN nODD / ODD |
| --- | --- | --- |
| e-, +0 | 0.62219 ± 0.00244 | 0.62113 ± 0.00247 |
| e-, +1 | 0.57006 ± 0.00247 | 0.56892 ± 0.00249 |
| e-, +2 | 0.51654 ± 0.00299 | 0.51468 ± 0.00301 |
| gamma, +0 | 0.61688 ± 0.00278 | 0.61580 ± 0.00281 |
| gamma, +1 | 0.57191 ± 0.00239 | 0.57092 ± 0.00240 |
| gamma, +2 | 0.53747 ± 0.00349 | 0.53574 ± 0.00351 |
| e-, -2 | 0.51551 ± 0.00292 | 0.51380 ± 0.00292 |

PN reduces mean silicon signal relative to raw by **0.664–1.214% in nODD** and
**0.486–0.793% in ODD**, using paired events. These modest digitizer changes do
not explain the much larger geometry response difference. Across this matrix,
PN SD/mean spans 3.06–14.26% (nODD) and 1.90–7.20% (ODD). These are all-event
visible-response spreads, not Gaussian-core fits or reconstructed resolutions.
No shower population has a zero-energy event, histogram underflow or overflow.

The independent ODD D-reference calibration factors at η=0/1/2/−2 are
37.97949 ± 0.13751 / 37.22087 ± 0.13951 / 38.11792 ± 0.12742 /
38.18039 ± 0.12908 (bootstrap SE). No nODD factor is fitted. All 3,800 nODD
shower events satisfy the frozen low-response diagnostic `Cη·S_PN/Etrue < 0.8`,
compared with 3/3,800 ODD events. The common ODD scale makes this geometry
response difference visible; this tail is not a measured electronic inefficiency.

The [compact response](previews/nodd-digitized-response.json) contains all 38
population moments, paired changes, histograms/flow counts, observed
region/side/layer means and errors, 19 geometry comparisons, and full shared
114-axis response/width/tail covariance matrices from 5,000 replicates.
The [descriptive quantile attachment](previews/nodd-response-quantiles.json)
adds exact unbinned quantiles, including zero totals, to the unchanged closed
response. The frozen producer omitted this protocol requirement; the separate
source-identified attachment reproduces every closed mean/SD/zero count before
export. Its probability grid and linear-interpolation convention were specified
after execution as descriptive summaries; they introduce no acceptance gate.
Per-layer sums are checked against event totals; late-layer signal is not a
measurement of escaping-energy leakage.

## Muon response and geometric opportunities

Each entry below uses 250 independent 10 GeV/c muons at fixed φ=0.123 rad.
The opportunity denominator is 250 × 48 nominal depths = 12,000. The
path-normalized PN fit reports the **underlying Landau MPV**, rather than the
mode of its Gaussian convolution; uncertainties are whole-event bootstrap SE.
SNR divides that MPV by the signed model-pedestal RMS, 0.130119 MIP.

| Geometry, η | PN Landau MPV ± SE (MIP) | Model SNR | Identified depths / 12,000 | PN >0.6 MIP / 12,000 | PN yield among identified depths |
| --- | --- | --- | --- | --- | --- |
| nODD, 0 | 0.95767 ± 0.00304 | 7.360 | 10,513 | 10,474 (87.283%) | 99.629% |
| nODD, +2 | 0.96670 ± 0.00305 | 7.429 | 10,704 | 10,658 (88.817%) | 99.570% |
| nODD, −2 | 0.96187 ± 0.00304 | 7.392 | 10,698 | 10,657 (88.808%) | 99.617% |
| ODD, 0 | 0.96118 ± 0.00280 | 7.387 | 12,000 | 11,964 (99.700%) | 99.700% |
| ODD, +2 | 0.95871 ± 0.00257 | 7.368 | 12,000 | 11,972 (99.767%) | 99.767% |
| ODD, −2 | 0.96188 ± 0.00266 | 7.392 | 12,000 | 11,969 (99.742%) | 99.742% |

nODD has 1,487 / 1,296 / 1,302 missing deposits at η=0/+2/−2. Their transported
crossing status is **unknown**. These nominal-layer yields cannot be interpreted
as measured electronics inefficiency, acceptance or hardware performance.
Actual native cell-position checks find 2,304 constructed plane groups in each
geometry and maximum reference residuals 0.000195313 / 0.000097656 mm (nODD/ODD),
below the fixed 0.002-mm tolerance, with no encoded plane collisions.
Initial straight native rays intersect 42/43/43 nODD depths versus 48/48/48 ODD
depths; these are approximate geometric diagnostics, not transported truth.
Layer-to-layer chords and the single-cell/primary selection also limit the
interpretation of the normalized MIP peak.

All 18 central fits and 18,000/18,000 fixed bootstrap fits converge, without
boundary or diagnostic flags. Independent checks reproduce all 18 central fits,
all 1,500 muon frames/74,767 hit references and the full 1,000-fit nODD central
PN bootstrap. Rare split categories retain undefined uncertainty replicas and
null errors where appropriate; no failed or undefined replicas are discarded.
The 200,000-draw signed pedestal is reused only after exact backend, request,
output and receipt identity checks. It tests the configured Gaussian model;
empty detector channels and real detector occupancy are outside this study.

## Response figures

The following figures use only the committed compact response, fixed component
colors and the unchanged source-identified renderer. All four are visually
checked by CaloTech and the coordinator; the MIP image reproduces the earlier
closed-subset preview byte for byte.

![Electron raw and digitized response](previews/nodd-digitized-electron.png)

![Photon raw and digitized response](previews/nodd-digitized-photon.png)

![Digitized muon spectra, model SNR and threshold yields](previews/nodd-digitized-mip.png)

![Geometry response ratios and paired digitization changes](previews/nodd-digitized-comparison.png)

## Source and execution provenance

Transport/protocol freeze:`5afb019eac6e152608639d02223dda73098a197f`.
Native geometry/factory source bytes are unchanged from the input baseline;
the fresh native report and every binary/XML/material/configuration identity
are bound before nODD events. Analysis correction
`855ccf7886bfb78718d16887b2b39145af5c6293` closes separately reproduced module16,
empty-population and configuration/input-binding defects before new digitization.
All42focused controls pass, including a native DD4hep encoder check and rejection
of outer geometry/population labels inconsistent with the bound sample.

ODD physically numbers modules1–16, while the actual four-bit readout encoder
maps physical16 to encoded0. The analysis retains all physical/decoded fields
in a local crosswalk and rejects collisions. It changes no detector ID.

The original G4 launch lacked tracker plugin registrations. Building the five
`Components_*` targets fixed discovery; all six factory binaries remained
byte-identical to the native PASS. Five files from the failed pre-event attempt
were retained byte-identically with relocation metadata. No failed output enters
the sample inventory. Registration hashes are retained separately.

Node preflight warned of changed setup/lock fingerprints. Actual DD4hep1.38,
Geant411.4.3, ROOT6.40.04, DD4hep/DDG4 imports and all12dataset paths were
reverified. Existing Key4hep/Gaudi imports passed. No shared install changed.
Raw ROOT/JSONL samples, RNG states and detailed logs stay local and ignored;
only compact binwise/statistical evidence, plots and exact recipes will be kept.

## Reproduction boundary

Use the recorded source revision, fresh task-owned directories and reverified
node environment. Build all required tracker **Components_*** registration
targets as well as their libraries; the calo target is
`Components_nODDCalorimeterPrototype`. Run the complete baseline native audit
before nODD transport. The executed generation entry point is
`software/analysis/calorimeter_digitization/nodd_generate.py` with stages
`prepare`, four geometry/population `run` calls, then `index`. The prepared
manifest fixes48populations, source/configuration/library/SDK fingerprints,
all seed pairs, compacts and the source/native-PASS binding.

Native diagnostics/common-scale analysis use `nodd_response.py`; original full
Key4hep comparison uses `nodd_reference_validation.py`. The plotter
`plot_nodd_digitization.py` reads compact summaries without ROOT or event files.
Exact completed commands, compact-result links and figures will be added after
their actual execution. No unexecuted command is a validation pass.

## Export, build and transport recipe

The following uses the executed task-owned directory layout and macOS library
suffixes. Choose fresh directories for a new execution; completed manifests and
raw files are immutable. Use the pinned clean ODD checkout and the reverified
Spack runtime described above. Build the native response executables and the
original Key4hep reference with the existing [implementation recipe](../../../software/source/ActsExamples/Calorimeter/README.md)
and [PR123 installation recipe](pr123-framework-install.md); no shared packages
are installed by this study.

```sh
python3 /Users/salzburg/.codex/skills/acts-spack/scripts/preflight.py
software/env/run.sh python3 software/env/doctor.py

task_work=build/issue117/nodd
odd_source=../nodd-software-layout/software/submodules/OpenDataDetector
python3 -B tools/calorimeter_baselines/export.py \
  --layout LAYOUT-001 --output "$task_work/geometry/nodd"
software/env/run.sh cmake -S . -B "$task_work/factories/tracker" \
  -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
software/env/run.sh cmake --build "$task_work/factories/tracker" --parallel 3 \
  --target Components_nODDPixelBarrel Components_nODDBeamPipe \
  Components_nODDShortStripBarrel Components_nODDShortStripEndcap Components_nODDLongStrip
software/env/run.sh cmake -S prototypes/calorimeter -B "$task_work/factories/calo" \
  -G Ninja -DCMAKE_BUILD_TYPE=Release
software/env/run.sh cmake --build "$task_work/factories/calo" --parallel 3 \
  --target Components_nODDCalorimeterPrototype

nodd_libraries=(
  --library "$task_work/factories/tracker/detector/libnODDPixelBarrel.dylib"
  --library "$task_work/factories/tracker/detector/libnODDBeamPipe.dylib"
  --library "$task_work/factories/tracker/detector/libnODDShortStripBarrel.dylib"
  --library "$task_work/factories/tracker/detector/libnODDShortStripEndcap.dylib"
  --library "$task_work/factories/tracker/detector/libnODDLongStrip.dylib"
  --library "$task_work/factories/calo/libnODDCalorimeterPrototype.dylib"
)
software/env/run.sh python3 -B tools/calorimeter_baselines/native.py \
  --directory "$task_work/geometry/nodd" "${nodd_libraries[@]}" \
  --output "$task_work/geometry/nodd-native.json"
software/env/run.sh python3 -B software/analysis/calorimeter_digitization/nodd_generate.py prepare \
  --work "$task_work" --nodd-directory "$task_work/geometry/nodd" \
  --native-report "$task_work/geometry/nodd-native.json" "${nodd_libraries[@]}" \
  --odd-source "$odd_source" --odd-library build/odd/factory/libOpenDataDetector.dylib
```

The six library paths must identify the binaries used by the native PASS. Build
ODD at its pinned source with the earlier recipe if its task-owned library is
absent. The native scan can take tens of minutes. DDG4 path-map initialization
for the integrated nODD geometry is substantially slower than ODD; a successful
conversion message alone is not evidence that any event has run.

Run these four independent groups, retaining each controller output. They may
run in separate processes, subject to available memory. Every group must close
normally and pass postflight checks before indexing:

```sh
software/env/run.sh python3 -B software/analysis/calorimeter_digitization/nodd_generate.py run \
  --work "$task_work" --geometry nodd --population showers
software/env/run.sh python3 -B software/analysis/calorimeter_digitization/nodd_generate.py run \
  --work "$task_work" --geometry nodd --population muons
software/env/run.sh python3 -B software/analysis/calorimeter_digitization/nodd_generate.py run \
  --work "$task_work" --geometry odd-zero --population showers
software/env/run.sh python3 -B software/analysis/calorimeter_digitization/nodd_generate.py run \
  --work "$task_work" --geometry odd-zero --population muons
```

Indexing, original-framework processing, response execution and actual-data
plotting remain pending at this report revision. Their final commands and
closed execution identities will be recorded with the results. The generation
manifest freezes the exact 48 populations and 9,500-event total; technical probes
and failed pre-event attempts are excluded.
