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
