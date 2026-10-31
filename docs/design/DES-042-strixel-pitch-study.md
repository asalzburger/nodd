# DES-042 — Longitudinal strixel pitch sensitivity

- Status: DRAFT; isolated **PROTOTYPE** study, not a baseline change.
- Date: 2026-10-31.
- Human request: truth tracking at 1, 1.5 and 2 mm longitudinal short-strip
  segmentation, and estimates of power and cable-space savings.
- Source baseline: `1dff0452ed1e7ac24d7b746fccc02ee15df5258d`, containing the
  PR104 balanced working tracker and PR107 reconstruction infrastructure.

## Scope and provenance

**FACT (repository baseline):** DES-007 specifies 48 × 96 mm² strixel sensors
with 75 µm × 0.5 mm cells. DES-020/021 contain 8,064 barrel and 4,320 endcap
sensors. The endcap count includes both ends. Baseline tracker layouts,
materials, pixel segmentation and the long-strip one-coordinate measurements
remain fixed throughout this study.

**NODD DESIGN CHOICE (study cases, human requested):** vary the strixel local-v
pitch through 0.5, 1, 1.5 and 2 mm, retaining 75 µm in local-u. Local-v is z in
the barrel and radial in the endcaps; it is not global z in the endcaps. These
cases do not authorize integration of a coarser baseline.

**INFERENCE:** integral grids have 192, 96, 64 and 48 bins along 96 mm.
Channels scale inversely with pitch. Single-cell uniform binary errors are
pitch/√12; this relation does not predict track-resolution degradation.

## Truth-associated tracking

Use the maintained PR104 balanced DD4hep → ACTS geometry, its existing
role-transported effective material map, and a constant 3 T axial field. Use
one origin muon per event, random charge, uniform eta in [-4,4], full phi, and
fixed pT 1, 10 and 100 GeV. Target 20,000 events for each of twelve cases.

Use the existing native geometric digitizer and truth-associated Kalman fit.
Change measured positions and native pitch-derived clustered covariance together.
The single-cell limit is pitch²/12; multi-cell centroids have the native weighted
cell covariance. Apply the same uncalibrated prescription to all cases rather than
reusing the old independently calibrated 0.5 mm widths. This defines a native
geometric response sensitivity; pulls diagnose that assumed model. The digital
configuration passes through the merged-cell path-weighted centroid/covariance
calculation described below. It does not
claim calibrated sensor response, occupancy performance or pattern recognition.

Retain the common random seed and verify generated truth and primary simulated
hits event by event. Report all-generated fit and native-match fractions,
uncut residual distributions, central 68.27% half-widths, biases, SD/RMS,
wrong-charge fraction and covariance validity versus eta and pT. Use a paired
event bootstrap for changes relative to 0.5 mm and a common-success control
for survivor effects. Bins with fewer than 30 finite entries remain undefined.
Statistical intervals omit detector-model and material-map systematics.

### Independent response control

The completed native digital scan has a narrower central z0/theta core at
100 GeV with coarser cells, while its pull widths do not close to one.
This observation does not establish improved physical sensor performance.

**FACT (inspected software, SRC-ACTS-REPO):** at ACTS source revision
`355ea68493b326956756c9386d2fd9eaf9328568`,
`Examples/Algorithms/Digitization/src/ModuleClusters.cpp` lines 249–325
recomputes both coordinate variances from the same two-dimensional cell
weights: `V_i = (p_i²/12) sum(w²)/(sum(w))²`. With merging enabled,
changing the coarse grid can therefore change fine-coordinate covariance.
Exact source hashes and the observed pilot check are retained in the response
diagnostic. This establishes a coupling, not the full cause of the fit effect.

**NODD DESIGN CHOICE (diagnostic added after observing that result):** run a
separate four-pitch, 5,000-event/case control at 100 GeV with independent Gaussian
hit errors `sigma = pitch/sqrt(12)` in every measured sensor coordinate, no
measurement merging, and one-coordinate long strips. Pixel and long-strip
pitches remain 50 and 80 µm, and strixel fine pitch remains 75 µm. Geometry,
material, field, generator and seed stay fixed. Record it separately from the
twelve-case digital campaign. It tests sensitivity to the overall response
model; replacing all measured-coordinate responses does not isolate one
covariance mechanism or calibrate a physical detector.

## Power and space model

**FACT (existing model, not qualified hardware):** DES-020/021 use 7.8 W/module
as a CMS PS service comparator and 7.8 × 122,880/30,208 W/module as a deliberately
crude channel-density proxy. They separately allocate 2 W/module sensor
leakage and 5 W per half-stave/petal board. Two 12 × 0.20 mm² Cu rails carry
12 V LV; HV leakage must not be added to their current. Public-source locators
are retained in `docs/design/inputs/DES-010-strip-services.md` (SS-F04/F10–12)
and `reference/manifest.yaml`; no new experimental fact is introduced here.

**NODD DESIGN CHOICE (sensitivity, not measured electronics):** scan a
channel-dependent fraction f of 0, 0.5 and 1 of each existing comparator load:

`P(p) = P(0.5) [(1-f) + f (0.5 mm / p)]`.

Keep leakage and board loads fixed; recompute existing local bus losses from
the discrete tap positions. External distribution/converter losses are unknown.
Neither comparator nor the f scan supplies physical bounds on a real ASIC.
Longer cells change capacitance and do not ensure equal power per channel.

**FACT (existing geometry):** downstream cable envelopes are 13.4 mm power
and 3.6 mm fibre, grouped separately inside each half-stave/petal; cooling
and trays have fixed topology. The 13.4 mm public comparator carries separate
LV/HV circuits for up to twelve modules, not a qualified aggregate-current
capacity for nODD. Merely changing pitch saves zero implemented service space.

**NODD DESIGN CHOICE (conditional redesign):** additionally estimate a power-only
reaggregation with unchanged benchmark cable OD and a relative load allowance
of twelve baseline module loads per harness. Round up within each network,
including its board power. Keep data fibres, cooling pipes, local buses,
electronics footprint and tray walls fixed. New fanout/conductor/connector and
HV/control topology would be required; these calculations do not establish
that such a harness can be built or installed. Preserve baseline cable lengths
from the existing collector, fan and cumulative trunk exports.

Report gross cable-envelope litres (including cable-internal void), material
litres separately, final cross-section per end, and area-equivalent annular
width at r=710 mm using the inherited 75% azimuth / 50% packing assumptions.
Width is a capacity-equivalent screen, not a cleared installation envelope.
Do not infer smaller cooling pipe diameter from reduced heat alone, or fewer
data links from fewer addresses at unchanged particle hit flux.

## Validation and open decisions

- Check balanced native sensor counts and identical geometry/material hashes.
- Check pitch grids, measurement dimensionality and paired generated/transport
  samples; preserve failures and all generated-event denominators.
- Replay compact statistics and plots; test service rounding, fixed-load
  limits, volume units, and conservation of unchanged fibres/cooling.
- Obtain separate PhysVal and SysArch assessments under the repository workflow.
- Select a future baseline only after reviewing track-performance tradeoffs,
  occupancy, ASIC power/capacitance, cooling and actual harness connectivity.

Software and numerical evidence: `software/analysis/strixel_pitch_study/` and
`docs/validation/DES-042/`. Exact commands, revisions and observed checks belong
to `logs/codex/SESSION-2026-10-31-strixel-pitch-study`.


## PROTOTYPE GBTS reconstruction cross-check (2026-10-31)

**NODD DESIGN CHOICE (user-requested isolated study):** extend the truth-fit
study with the DES-041 pixel-only GBTS seeder and full-sensor CKF, preserving
geometry, material, 3 T constant field, selected `pt4-nominal-triplet` profile,
track cuts and species hypotheses. Change no production configuration.
Use all five established transport/species populations: Fatras muons and
electrons, and Geant4 muons, electrons and charged pions, each at pT = 1, 5,
10 and 100 GeV and each longitudinal strixel pitch = 0.5, 1, 1.5 and 2 mm.
The cross-check uses 1,000 generated events per case (80 cases), with the
established random-charge, origin, uniform eta in [-4, 4] and full-phi gun.
This sample plan supplies a complete comparative scan; the retained DES-041
5,000-event baseline remains separate. Report finite-sample uncertainties,
including upper limits where no failures are observed, and undefined low-count
eta bins. These are repeat samples with the established frozen seeds, not a
new tuning or held-out validation campaign. The seeds are 123042 for Fatras
muons, 133042 for guarded Fatras electrons and 143042 for Geant4 populations.

**NODD DESIGN CHOICE (response sensitivity):** preserve the calibrated pooled
Gaussian response of DES-041 at 0.5 mm and scale only the local-v standard
deviation of systems 4 and 5 by `pitch / 0.5 mm`. Fine-coordinate errors,
pixels and long strips remain fixed; measurement merging remains disabled.
This tests the longitudinal-response dependence of the frozen reconstruction.
It is not an independently calibrated coarse sensor model and is separate
from the earlier all-coordinate nominal `pitch/sqrt(12)` truth-fit control.
Use the converged ambiguity-iteration budget from the species extension;
verify that the baseline muon budget was nonlimiting. Do not retune the seeder,
CKF or quality/matching definitions for any pitch.

Retain all generated-event denominators and uncut per-event audit records.
Reuse the independent DES-041 classifier for reconstructability, seed coverage,
accepted primary efficiency, fake/secondary/duplicate candidates, wrong charge,
invalid covariance, residuals and pulls. Compare efficiencies with paired
intervals, residual central-68.27% half-widths with paired event bootstrap and
common-success controls, plus biases, RMS and tails. Preserve truth-minus-fit
sign convention of this reconstruction analyzer. Truth is used for simulation
and scoring only; GBTS consumes measured pixel space points.

Verify geometry/material/native helper and GBTS configuration identities;
verify identical generated and transported particle records across lengths.
Compare measured pixel inputs, seed outputs and measurement losses explicitly:
bounded Gaussian rejection near sensor boundaries may consume different random
draws, so equal seeds alone do not establish bitwise paired measurement noise.
Report any such effect rather than attributing every observed change uniquely
to the longitudinal covariance. Preserve frozen helper sources and prior
reference evidence. Implement by isolated composition in
`software/analysis/strixel_reconstruction/`; retain evidence in
`docs/validation/DES-042/gbts/`. Separate PhysVal assesses the protocol and exact
final evidence revision. No numerical result grants design or production approval.
# Fatras ttbar plus 200 pileup extension (2026-10-31)

**PROTOTYPE — NODD DESIGN CHOICE (explicit human request):** reconstruct
100 events per strixel length (0.5, 1, 1.5 and 2 mm), with one Pythia8 ttbar
hard scatter plus exactly 200 minimum-bias pileup interactions per event,
using Fatras only. Compare efficiency, fake and duplicate rates. Keep the
existing scaled Gaussian response, fixed geometry/material/constant 3 T and
`pt4-nominal-triplet` GBTS with the common ttbar vertex-window adaptation below,
otherwise frozen CKF and converged ambiguity settings.
No tuning on this sample and no detector acceptance is implied.

**FACT (local ACTS guide):** the user-named guide is
`Examples/Scripts/Python/full_chain_odd.py` at installed matching ACTS revision
`355ea68493b326956756c9386d2fd9eaf9328568`. Its ttbar path uses
`Top:qqbar2ttbar=on`, 14 TeV proton beams, `SoftQCD:all=on` pileup with fixed
multiplicity, Gaussian vertex sigma (0.0125, 0.0125, 55.5) mm and 5 ns, and
generator selection rho <=24 mm, |z| <=1 m, |eta| <=3 and pT >=150 MeV.
Record explicit effective values rather than relying on defaults. The stock
ODD 2 T field, volume IDs and cuts are guidance, not nODD geometry inputs.

**NODD DESIGN CHOICE (pre-execution protocol):** production seed153042;
development smoke seed153043. Use the same generated and transported events
at all four lengths, proving full particle/hit identity rather than assuming
it from equal seeds. Prefer a once-generated, once-transported retained sample
replayed into the four reconstruction variants where this preserves native
semantics; otherwise verify every event's exact persisted particle/hit payload.
Retain all 100 events, including zero-track events and failures. Fatras keeps
its 0.5 GeV absolute-momentum threshold and interactions, using the already
validated numerical guard for mixed samples containing electrons. Keep the
muon reconstruction hypothesis as in the guide for this inclusive sample;
no truth species chooses a seed or fit hypothesis.

Efficiency denominator: charged generated particles satisfying pT >=1 GeV,
|eta| <=3, rho <=24 mm and |z| <=1 m, before hit/reconstruction requirements.
Report hard-scatter and pileup separately, plus inclusive. Also report the
guide-like conditional denominator with >=9 distinct associated measurements,
and the existing >=6 sensor/3 pixel-group reconstructability control.
The first generator vertex is hard scatter; verify the actual barcode/vertex
semantics before assigning this label. Do not group descendants into ancestors.

Match every quality-accepted track to generated or simulated truth with the
existing unique-inlier purity >=0.5 and completeness >=0.5 rule, deterministic
winner/representative ties and >=7 measurements plus valid reference/fit
covariance. Keep matched out-of-fiducial particles and simulation secondaries
separate from unmatched fakes. Duplicate tracks are additional matches beyond
one per truth particle, not fakes. Retain raw CKF, ambiguity, quality rejection,
wrong-charge and candidate counts. Report the frozen quality selection and
separately a guide-like track selection: reconstructed pT >=1 GeV, |eta| <=3,
|loc0| <=4 mm, at most2 holes and2 outliers. No truth input filters CKF hits.

Use 2,000 deterministic paired event-block bootstrap resamples for efficiency
(ratio of sums), candidate fake/duplicate fractions and cross-length differences;
particles/tracks in one pileup event are not independent binomial trials.
Report fake-event incidence with Wilson intervals and the exact one-sided95%
upper bound for zero fake events. Degenerate resampling is flagged, not treated
as equivalence. Include pT/eta profiles with denominators and uncertainty.
Preserve event-level sufficient counts and matching identities for independent
recomputation. Audit all ambiguity survivors before selection for convergence.

Validate native generation, sample pairing, response variance, all-system CKF
inputs and independent classifications with small distinct-seed smoke samples
before the frozen 100-event production. Record source/runtime/configuration,
Pythia settings/version, native numerical guard, RNG seeds and retained hashes.
An absent shared Pythia binding may be supplied by a task-owned sidecar against
the existing installed dependency; shared dependencies/runtime remain unchanged.
Independent PhysVal assessment must cover protocol and final committed evidence.

**Implementation qualification:** task-owned lossless per-event gzipJSON replay
is used because ROOT particle/hit writers reduce precision and omit some final
state metadata. The native reader restores and byte-compares the complete
reserialized particle/hit payload, including signed zero, before reconstruction.
Producer interaction tags establish hard-scatter origin through conversion.
The unchanged upstream Pythia generator temporarily disables its own FPE monitor
around generation; Fatras/reconstruction monitoring stays active. This scoped
upstream behavior is recorded, not represented as an entirely unmasked chain.

**NODD DESIGN CHOICE (before production):** widen the common GBTS z0 range
from the single-particle origin control's ±15 mm to ±1 m, matching the guide's
selected vertex-z region. Update geometry/ROI range, graph minZ0/maxZ0 and
tracking-filter maxZ0 consistently. The guide's 55.5 mm vertex-z sigma is much
larger than the origin control's acceptance. This is a physics-based scenario
adaptation, with the same range at every pitch; it is not a scan or optimization
on the untouched100-event sample. Keep all other seeder, CKF, matching and
quality settings. The earlier narrow-window smokes remain development controls.
The generated-particle denominator still includes displaced tracks whose
perigee z0 or d0 can lie outside reconstruction acceptance.

**FACT (development pilot and pinned ACTS implementation):** the common±1m
window reaches the existing2,000,000graph-edge cap. Preserve this default
through the comparison and record per-event edge/link counts and cap-warning
incidence using observational native logging with single-thread event IDs.
Require complete diagnostic coverage and count/warning consistency. This is
separate from an output-seed cap. Report efficiency as that of the current
resource-limited chain; do not claim unconstrained seeding/detector performance.

**FACT (first 100-event attempt):** all event payloads were written, but final
sequencer validation rejected the sample for one unmasked underflow in the
gamma sampler's power intermediate. The existing combined-product logarithmic
guard does not protect that intermediate. Six independent particle propagation
step-limit failures were retained. The matching multi-particle implementation
also copies a failed-particle reference after erasing its queued element, so
logged identities alone cannot establish which particles were lost. The failed
attempt remains preserved and is not a valid reconstruction input.

**NODD DESIGN CHOICE (numerical implementation correction):** use a distinct,
task-owned Fatras component with the same compiler/flags, algorithm position,
random draws, settings and collections. A conservative guard may replace an
internal gamma value only where the downstream binary64 energy-loss fraction
is provably already zero. Do not claim internal gamma-value equality. Keep
the original computation elsewhere, active exception monitoring and all four
angular draws. Capture failed-particle state before erasure in a separate
observational audit; do not change propagation limits or remove failed events.
Require native/strict floating-point positive controls, exact energy/parent/
photon/RNG comparisons, separate PhysVal assessment and same-seed replay of
all 100 native particle/hit payloads before corrected production is used.
This repairs numerical evaluation and diagnostics; it does not tune physics
or reconstruction parameters on the performance sample. Missing transport
outputs remain a qualification for efficiency, occupancy and fake rates.

**FACT (first four-length reconstruction and actual compiler evidence):** all
four loops processed100events, but final monitoring rejected one GBTS FLTDIV
at event57. Clang O2 evaluates the endcap `(1+tau²)/tau²` before selecting the
barrel result. The captured barrel slope is negative zero; the source-selected
barrel expression is valid. Shared, renamed and instrumented implementations
match all100 original ordered seed IDs and quality bits. Actual machine-code
and state-level evidence are retained in the separate validation report.
The failed reconstruction reports remain failed.

**NODD DESIGN CHOICE (numerical evaluation correction):** use a separate,
task-owned GBTS component with uniquely named, hash-checked copies of the
required Core classes. Select the denominator first (`1` for barrel, `tau²`
for endcap), then divide. Preserve selected arithmetic, algorithm name/slot,
random streams, graph limit, settings and collections. Do not reject candidates,
insert epsilon/floor values, mask exceptions or relax cuts. Require native and
strict floating-point controls retaining genuine selected singularities,
actual machine-code confirmation, all100 ordered seed/quality comparisons,
complete per-event numerical diagnostics, separate PhysVal review and a fresh
full reconstruction audit at all four lengths. Reuse the unchanged validated
Fatras sample with its original generation revision/report hash; freeze the
new reconstruction revision independently. This repairs compiler evaluation
without tuning physics or reconstruction parameters on performance results.


Completed prototype execution and independent evidence assessment are retained in
[the ttbar plus 200 pileup report](../validation/DES-042/ttbar-pu200/README.md).
This result grants no detector design acceptance or baseline change.
