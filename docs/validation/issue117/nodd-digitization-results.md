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

The complete zero-field ODD control has generated and verified **4950events**:
4550test/muon events and400independent electron references. Fresh nODD transport
is still initializing its Geant4 volume/path mapping. Original/native nODD
agreement, new response fits and scientific figures are **not yet executed**;
the earlier ODD-only pass must not be relabelled as an nODD pass.

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

## Source and execution provenance

Transport/protocol freeze:`5afb019eac6e152608639d02223dda73098a197f`.
Native geometry/factory source bytes are unchanged from the input baseline;
the fresh native report and every binary/XML/material/configuration identity
are bound before nODD events. Analysis correction
`855ccf7886bfb78718d16887b2b39145af5c6293` closes separately reproduced module16,
empty-population and configuration/input-binding defects before new digitization.
All36focused controls pass, including a native DD4hep encoder check and rejection
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
