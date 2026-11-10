# PR #118 — frozen ODD silicon-digitization validation protocol

- Status: **PROTOTYPE software validation and response characterization; no design acceptance**
- Prepared: 2026-11-09, assignment `I118-Nov9-CaloTech`
- Source examined: `1b0e0c050882ec9f780bf31b10fefe13b568718c`
- Governing design / artifact policy: [DES-044](../../design/DES-044-calorimeter-digitization.md), [ADR-003](../../decisions/ADR-003-validation-and-artifact-policy.md)
- Review requests: [cell/MIP/shower checks](https://github.com/asalzburger/nodd/pull/118#issuecomment-6684090541), [resume after installation](https://github.com/asalzburger/nodd/pull/118#issuecomment-6686211776), [run missing cross-checks](https://github.com/asalzburger/nodd/pull/118#issuecomment-6686715251)
- Human direction: the current request resumes digitization checks after [PR #123](pr123-framework-install.md). The earlier runtime deferral is historical, not the current disposition.
- Freeze boundary: commit this protocol and the actual executable/configuration identities **before new reference/campaign execution**. Later deviations are dated amendments, retaining failed checks; no retrospective relaxation or detector approval.

## Scope, sources and study parameters

**FACT about source:** the pinned [validation plan](validation-plan.md),
[full-framework recipe](../../../software/analysis/calorimeter_digitization/reference.md)
and [historical review disposition](pr118-review-request.md) distinguish a real
Key4hep `DigitiserSiliconMip` execution from synthetic utilities and a reused
Marlin kernel. This protocol completes that sequence using unchanged ODD
`d70556f33b1c36abdf101a07ad8cf57eb56fbdf1` hits. It does not change the nODD
endcap, remove historical tiling evidence or substitute ODD response for nODD
physical-tiling validation.

Exact model sources remain Key4hep `k4RecCalorimeter`
`03b3676cecbdf85818f6de159ecf90ffe2482cec`,
`RecCaloDigi/src/{DigitiserSiliconMip,BaseDigitiser}.cc`, versus the nODD adapter's
MarlinReco `255967eb855ebbc8f75ebaac190b268b63332e8b`
`RealisticCaloDigiSilicon.cc` and `RealisticCaloDigi::EnergyDigi`. Source identities,
ancestry, licensing and operations are catalogued in DES044. The original
Key4hep processor uses ROOT random numbers; the reused Marlin kernel uses CLHEP.
Neither equal seeds nor equal source equations imply equal stochastic draws.

Additional nODD files inspected at the same source revision:
`software/analysis/calorimeter_digitization/{generate,calibrate}.py`,
`software/source/ActsExamples/Calorimeter/{src/SiliconDigitization.cpp,tests/SiliconDigitizationTests.cpp,EDM4hep/SiliconCampaign.cpp}`.
`calibrate.py` chooses the most populated 2.5 keV cell-energy bin of the first
250 central muon events. Its frozen scale is **0.00014875 GeV/MIP**; this is a
historical empirical bin convention, not a fitted or accepted detector constant.
Its 1.25 keV half-bin quantization and unmeasured path/systematic uncertainty
remain explicit. Do not retune this scale to move a held-out peak to one.

All settings below are **NODD DESIGN CHOICES for unsigned comparator studies**,
not selected production electronics. The 0.13 MIP noise and 0.6 MIP threshold
come from the CALICE comparison context documented in the validation plan;
CALICE geometry and operating conditions differ from ODD.

| Setting | Deterministic / noise-off D | Pair-only P | Pair plus electronics PN |
| --- | ---: | ---: | ---: |
| MIP deposit scale, GeV | 0.00014875 | same | same |
| Pair energy, eV | 0 | 3.6 | 3.6 |
| Electronics noise RMS, MIP | 0 | 0 | 0.13 |
| Strict accepted-cell threshold, MIP | 0.6 | 0.6 | 0.6 |
| Pre-noise dynamic range, MIP | 2500 | 2500 | 2500 |
| Gain variations / dead cells | disabled | disabled | disabled |
| Time integration | all contributions | same | same |

The reference Standard integration uses time bounds [-1e30,+1e30] ns,
propagation correction off and time smearing off; verify all input times lie
strictly inside. This matches energy aggregation only. Native deposited-energy-
weighted times and original earliest-contribution times are different contracts:
no timing-equivalence claim is attempted. Range clipping precedes electronics
noise in the source; do not add a post-noise clip or another ADC model.

## A. Input integrity and deterministic full-framework gate

Verify the installed original processor/build, imported source pin/patches and
runtime, then run both algorithms over the **same hashed files and ordered
EventHeaders**. Use both ECalBarrelCollection and ECalEndcapCollection, including
empty collections. The existing 18 shower samples comprise e-/gamma at
5/20/50 GeV and η=0/1/2, 200 events each; the two historical 10 GeV muon files
have 500 events each. Preserve their recorded fixed φ=0.123 rad, full ODD
geometry/field, FTFP_BERT and transport settings. Audit completeness and hashes
before reuse; do not regenerate an existing file or silently replace its source.

Run D first on these representative existing samples. The original output must
retain the unchanged SimHits, their contributions, MC relation endpoints and
single EventHeader so the existing comparator can verify identity. Require:

- exact event count/order and unique run/event identifiers;
- one SimHit per input cell, full 64-bit IDs and source collection identity;
- exact accepted-cell sets, including no-output/empty events;
- each matched cell's MIP energy within `1e-5 + 5e-6*abs(E_reference_MIP)`.

These are the preregistered numerical controls in `reference.md`, reflecting
float accumulation/persistence rather than physics acceptance. Keep every
selection mismatch visible, including threshold-near cells. A difference that
merely looks small does not pass exact-cell selection. Investigate a failed
gate before stochastic or new performance claims; document and freeze any
necessary technical correction before rerunning. An empty comparison cannot pass.

Executable boundary, already present at the examined revision:

```sh
software/env/run.sh /path/to/build/EDM4hep/nodd_silicon_reference \
  /path/to/original-ddsim.root /path/to/full-key4hep-digi.root \
  /path/to/frozen-comparison.json /path/to/new-summary.json \
  /path/to/build/nodd_marlin_silicon_backend
```

The original full Key4hep job uses the recipe/installed adapter, not this
comparator or an nODD helper as its reference producer. Preserve exact executed
commands/config hashes in the result manifest. Synthetic smoke tests remain
separately labelled.

## B. Stochastic original/native comparison

Freeze two replay inputs before processing their stochastic outputs:

1. full real ODD event at zero-based index 250 of `mu-_E10_eta0`;
2. full real ODD event at zero-based index 0 of `gamma_E20_eta2`.

Each input repeats its selected complete source event **1000 times**, changing
only EventHeader run/event identifiers to unique ordered identities. Retain all
SimHit/contribution/MC data and relation endpoints unchanged and verify that
round trip. Each framework reads exactly the same hashed replay file. The source
file hash, selected origin and replay/header mapping stay in the ignored local
manifest; no repeated event payload or individual event-ID list is committed.
This is a controlled conditional model experiment, not 1000 independent showers.

Run P and PN for each replay input. Choose independent ROOT and CLHEP seed
streams; recorded initial choices are original `119200 + 2*fixture + mode`
and native `119300 + 2*fixture + mode`, with fixture=0/1, mode=0 for P and 1 for
PN. Keep processor names and unique-ID seeding service identity fixed. Confirm
per-event reseeding actually produces changing stochastic outputs.

Compare **event total accepted MIP energy** and **accepted cell multiplicity**
(zeros retained). Plot their distributions and cell-amplitude distributions;
only events, not correlated cells, are resampling/exchange units. For all four
fixture/mode combinations, freeze these software compatibility gates:

- Mean difference in each event observable must be within five combined standard
  errors, `5*sqrt(s_original²/1000 + s_native²/1000)`. If both variances vanish,
  require matching constants (integer equality for counts, the deterministic
  numerical energy tolerance for energy).
- For both observables use a two-sample empirical-CDF maximum-distance statistic
  with **10,000 event-label permutations**. Compute
  `p=(1+#permuted_statistic>=observed)/(10001)` and require `p>=0.001`.
  Permutation handles discrete-count ties; do not use a continuous-distribution
  KS calibration on tied counts. The eight declared CDF tests have a union-bound
  false-rejection probability at most 0.008 under their nulls.
- For positive event-energy standard deviations, a **95% independent-event
  bootstrap interval for s_native/s_original must lie inside [0.85,1.15]**.
  Use 10,000 bootstrap replicates. A zero energy variance in either framework
  on these positive-energy replay inputs is investigated, not excused as a
  degenerate pass. Count-width ratios are not required when the count is constant.

Use analysis seeds `119400 + 2*fixture + mode`, explicitly naming permutation
and bootstrap substreams. Record statistics, p values, intervals and failures.
The width margin is an explicit modest-sample software discrimination choice;
it is not a calorimeter performance tolerance. Nonrejection alone is not proof
of physical equivalence. Do not retry seeds until a stochastic comparison passes.

## C. Muon provenance, MIP peak, signal/noise and efficiency

### Input correction and held-out policy

The initial plan to reuse historical raw muons is limited by their persistence:
inspection found contribution PDG values zero and only generator MCParticles,
so those files cannot identify primary-muon deposits. Retain the first 250
central events' historical MIP scale and its provenance, and the remaining
historical halves as exploratory controls; do not label them primary-qualified.

**NODD DESIGN CHOICE — corrected validation input:** generate **250 new 10 GeV
mu- events at each η=0 and 2**, same ODD geometry/full configured field and
φ=0.123, using the verified DDSim `--enableDetailedShowerMode` option to retain
particle/step information. Initial transport seeds are 119000 and 119001.
All 500 new events are held out from MIP-scale determination. Verify, rather
than assume, that detailed output contains usable PDG=13 contributions and
unambiguous primary/ancestor relations. If that persistence is still absent,
report the primary-qualified measurements unavailable.

### Trial inventory and path approximation

Freeze the event/physical-layer crossing inventory **before digitization or
threshold selection**, using native ODD geometry and truth trajectory information.
Keep all generated events and report the 48*N nominal layer-opportunity count,
qualified geometric crossings, ambiguous trajectories, split-cell crossings,
missing/zero deposits and identified secondary/decay cases separately. A retained
hit list cannot by itself supply the zero-signal denominator.

Qualify primary muon contributions through PDG=13 and the unique intended
primary ancestry, with relation endpoints actually verified. Group by physical
sensitive sensor/layer. A threshold-independent cell set comes from primary
contribution positions plus the geometry/readout map; known predicted crossed
cells without a deposit are zero-signal trials. Missing truth or an unresolved
cell/geometry mapping is **unknown**, not a fabricated zero crossing. Retain
nominal-opportunity diagnostics when actual crossing qualification is incomplete;
label that denominator accurately and do not call it complete MIP efficiency.

The full ODD field bends charged muons. Determine actual slab normals from the
pinned geometry and estimate local direction from coherent adjacent-layer primary
contribution centres (or directly persisted primary step directions if available).
The initial straight IP ray is a cross-check, not an exact transported trajectory.
For the chord estimate define `ell_approx=0.5 mm/abs(n dot u_local)`. Contribution
positions are not step endpoints or recorded path lengths. Report the accepted
angle/path range, straight-versus-chord change and any hard-scatter/secondary
ambiguity. Preserve rejection reasons independently of measured pulse amplitude.
Do not claim step-accurate path qualification from this approximation.

For MIP spectra, use the documented well-contained, single-primary-cell crossing
category; keep split/ambiguous/secondary populations in separate diagnostics.
For efficiency, include all qualified crossings including split cells and known
zero-response trials. Define a crossing as passing a per-cell threshold if **any
of its identified primary-crossed cells** has the full simulated cell signal
above that threshold; do not sum split-cell pulses before applying a per-cell
threshold. Report split and single-cell efficiencies separately. Secondary energy
sharing a primary-crossed cell is recorded contamination, not silently replaced
by a primary-only pulse. Unknown empty-cell inventory does not create noise-only
channels in the original sparse processor.

### MIP spectra and fit

Store raw, noise-off and PN prethreshold amplitudes as well as the actual
thresholded output spectrum at 0.6 MIP. Use MIP units from the frozen 148.75 keV
scale and deposited GeV. Show the held-out peak at its measured value, without
shifting or refitting the scale to enforce one MIP.

The fit at η=0 is a Landau convolved with a Gaussian on the path-normalized
amplitude `E_cell*(0.5 mm/ell_approx)/mip_energy_GeV`. Freeze 0.025-MIP bins and
fit range [0.25,2.5] MIP for raw/prethreshold spectra. Integrate the normalized
model over bins; include the finite fit range in the likelihood normalization.
Record optimizer, initial/bound settings, convergence, goodness-of-fit diagnostic
and whether the Landau parameter denotes a location or its actual mode. Report
both the Landau-component MPV and the numerical mode of the convolved curve,
with their uncertainty; they are not interchangeable. A post-threshold fit must
include that truncation explicitly, not fit an untruncated model to selected hits.

Use **1000 whole-event bootstrap replicates** (seed 119401) for peak uncertainty,
resampling all eligible sensor trials from each selected event together. Record
fit failures; require at least 95% usable replicates before quoting a bootstrap
peak interval. Do not treat all cells as independent. Retain the fit/Hessian
error as a conditional numerical diagnostic, not the only statistical error.
If the fixed fit does not describe the held-out spectrum, report its failure and
the empirical mode/quantiles; do not change the range after viewing the peak.
η=2 supplies a separately reported path/response control, not an independently
retuned calibration.

### Signed pedestal, SNR and threshold curves

Measure **prethreshold signed** electronics-only noise through the backend/audit
boundary, using 200,000 zero-input channel trials with pairEnergy=0, noise=0.13
MIP, no threshold or positive clipping, seed 119402. Preserve negative values.
This is a configured-model pedestal experiment, not measured hardware noise or
whole-detector occupancy. Compare mean/RMS and strict >2σ tail to the five-sigma
analytic Gaussian criteria already specified in the validation plan. Reuse the
existing unit fixture as a regression, but record this comparator-setting audit
separately; accepted hits cannot estimate the unthresholded pedestal RMS.

Define `SNR = fitted prethreshold MIP signal peak / measured signed pedestal RMS`,
using the same MIP units and explicit peak/path convention. Propagate peak and
pedestal uncertainties. Quote the 0.13 MIP setting and historical scale/quantization
separately from statistical errors; no electronics measurement is inferred.

Scan fixed strict per-cell thresholds
`[0,0.2,0.4,0.6,0.8,1.0,1.2,1.5,2.0] MIP` on the **same prethreshold D/PN
amplitudes**, without generating new noise for each threshold. Thresholds apply
to the uncorrected pulse units; path normalization is only for the displayed MIP
fit. Include every qualified crossing in each denominator, including threshold-
rejected and known zero-signal crossings. Report passed/total, conditional 95%
Wilson intervals and whole-event bootstrap uncertainty/covariance across
thresholds (1000 replicates, seed 119403). Multiple layer trials share an event;
Wilson intervals alone do not remove that correlation. Report the model's
pedestal false-hit probability on its known fixture inventory separately. Do
not multiply a sparse occupied-cell result into a full-detector noise occupancy.

## D. Electron/photon raw, noise-off and noise-on response

Reuse the 18 complete existing ODD samples (200 events per species/energy/η,
3600 shower events). At each event retain raw summed ECal silicon deposits,
D digitization and PN digitization **on that same event**, summed over barrel
and endcap collections. Separate species, η and energy. Count all events,
including exactly zero raw/digitized response. Reject incomplete files, not
zero-response events. No signal-based shower/event selection is introduced.

**NODD DESIGN CHOICE — independent shower calibration:** generate 100 additional
20 GeV **electrons** at each η=0,1,2, initial seeds 119100–119102, using the same
fixed φ and transport settings. Their 300 events are independent of all plotted
validation populations. Run D on each reference sample and freeze one scalar
factor per η,

`C_eta = mean(E_generated, calibration) / mean(S_D, calibration)`.

Record the numerical factor and calibration uncertainty/hash before evaluating
validation response. Apply the **same C_eta to raw, D and PN**, to electrons
and photons, and to all 5/20/50 GeV energies. No separate photon factor, per-energy
factor, fitted offset or retuning is permitted. The same factor across stages
keeps threshold/noise shifts visible. State the actual gun/MC energy convention
(total versus kinetic) and verify the truth energy used in the denominator.
These factors are empirical ODD study calibrations, not production constants.

For every population plot and retain:

- raw/deposit-equivalent totals and `f_visible=S_raw/E_generated`, all-event
  means/errors, zero counts and distributions. Silicon-only `f_visible` is not
  active/(active+passive) physical sampling fraction;
- calibrated `E_cal=C_eta*S_stage` distributions and response
  `R=mean(E_cal/E_generated)` with linearity residual R-1;
- raw and digitized sample RMS/mean, with **whole-event paired bootstrap**
  standard errors and percentile intervals; distinguish this distribution spread
  from a Gaussian core fit or reconstructed calorimeter resolution;
- paired changes PN-D, D-raw and their response/spread changes, longitudinal
  deposits if available, and zero-response/tail fractions with explicitly frozen
  definitions. No tail cut is optimized after looking at the population.

Use 5000 bootstrap replicates (analysis seed 119404), resampling the same event
indices jointly for raw/D/PN in each population. Independently resample each
reference electron calibration and reuse that η's resampled C_eta for **all**
its species/energy/stage populations in a replicate. Retain the resulting shared-
calibration covariance and paired-stage covariance with axis labels. A common
scalar calibration cancels from a population's RMS/mean; do not inflate or erase
uncertainties by treating correlated copies as independent. This protocol sets
no detector-performance pass/fail bound; compare measured trends and scales
with the published Si-W context and its geometry/selection caveats.

## Execution record, retained evidence and completion boundary

The existing generation script supports the independent electron reference
without changing detector geometry, for example:

```sh
software/env/run.sh python3 software/analysis/calorimeter_digitization/generate.py \
  --odd-source /path/to/pinned/ODD --odd-library /path/to/ODD/library \
  --output build/issue117/nov9/electron-calibration --events 100 \
  --energies 20 --etas 0 1 2 --particles e- --seed 119100
```

The detailed-muon flag and new replay/paired-analysis runner must appear in their
actual frozen source/configuration/command manifest. Do not represent a planning
command or a synthetic utility as an executed original-framework result. Runtime
preflight and actual package/import checks follow the repository's Spack workflow;
installation availability is reverified, not assumed from PR #123's merge.

Retain plots, compact binwise counts/edges/units/normalization, sufficient moments,
fit outputs/intervals and bootstrap/covariance summaries in Git. Preserve
all-event/trial denominators, under/overflow and unknown/rejected categories.
Keep full SimHit/replay/digitized ROOT files, event/cell IDs and detailed logs
local and ignored with size/hash/recipe. State which checks need those local
files and which can be repeated from compact summaries alone.

Report A, B, C and D individually as passed software gate, failed, characterized,
or unavailable, with actual evidence. A deterministic/stochastic agreement does
not prove timing, pulse/ADC, empty-detector occupancy, irradiated response,
pileup, nODD tiling performance or production acceptance. The comparator study
keeps DES044 DRAFT; only identified humans may grant sign-off or acceptance.

## Dated analysis clarification before C/D outputs — 2026-11-09

Separate PhysVal protocol assessment at `baf36920` found A/B coherent and requested
three analysis choices be made explicit before C/D scientific outputs. The
following are frozen while new raw samples are being generated and before their
response analysis. No observed performance or failing gate motivated them.

1. The MIP spectrum category is **single-cell, near-normal primary muon**, not a
   certified Geant4 path-length or wafer-edge containment category. Require one
   generator-status-1 PDG13 primary; select contributions with PDG13 and that
   exact MC relation endpoint. At a layer require exactly one such cell and no
   contributions of another particle in that cell. Require primary contribution
   centroids in both immediately adjacent layers. Their energy-weighted centroid
   chord defines local direction; require `abs(n dot u)>=0.9` using the native
   slab normal. Layers 1 and 48 consequently cannot enter the fitted spectrum.
   There is no pulse-height selection. Split cells, contamination, unavailable
   chords and missing primary layers are counted separately. Efficiencies use
   the unnormalized full cell pulse and retain split layers; all 48 nominal
   opportunities/event remain a separate denominator. Known positive crossings
   and unknown/missing truth are explicitly distinguished. No claim of complete
   crossing efficiency is made when zero-signal geometry inventory is unresolved.
2. SNR uses the **underlying Landau-component MPV** of the path-normalized PN
   prethreshold fit divided by the signed pedestal RMS. The numerical convolved
   mode and its event-bootstrap uncertainty are reported separately. This is a
   normal-incidence-equivalent study convention; no hardware SNR is inferred.
3. Shower low-response tail means **`C_eta*S_stage/E_generated < 0.8`**, for all
   stages/species/energies. Retain conditional binomial intervals and joint
   whole-event/reference-bootstrap uncertainty/covariance. The same independently
   calibrated factor is used in the tail cut; no per-population cut or tuning.

Native diagnostic digitization streams start at seed119117, adding100 times the
manifest row index and then the barrel/endcap collection index. The same stream
convention applies across D/PN; their random draws are not claimed paired. The
paired bootstrap pairs the underlying event and its raw/D/PN outcomes.
