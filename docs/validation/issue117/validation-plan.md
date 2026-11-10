# Issue #117 — Si-W prototype validation plan

- Status: DRAFT; proposed checks, with no execution or physics-acceptance claim.
- Date: 2026-11-05.
- Assignment: `I117-PhysVal`, separate PhysVal agent context.
- Examined nODD input: `96dbf57d0da7f3027e59109c1846d992d68d4d44`.
- Scope: the opt-in digitization PROTOTYPE requested in [issue #117](https://github.com/asalzburger/nodd/issues/117), [DES-044](../../design/DES-044-calorimeter-digitization.md), and the artifact rules in [ADR-003](../../decisions/ADR-003-validation-and-artifact-policy.md).
- This document authors a validation proposal; it does not independently review a later implementation revision. That review must name the exact code commit.

## Inputs and primary evidence

**FACT — ODD source:** the nODD input pins OpenDataDetector at
`d70556f33b1c36abdf101a07ad8cf57eb56fbdf1`. Its
[CalorimeterECal.xml](https://github.com/OpenDataDetector/OpenDataDetector/blob/d70556f33b1c36abdf101a07ad8cf57eb56fbdf1/xml/detectors/CalorimeterECal.xml),
`ECal_cell_size` and both detector `layer` blocks, define 5.1 mm cells and
48 repetitions of 1.90 mm tungsten alloy and 0.50 mm sensitive silicon plus
passive support/electronics slices. The two named readouts are
`ECalBarrelCollection` and `ECalEndcapCollection`. Its
[calorimeter CI](https://github.com/OpenDataDetector/OpenDataDetector/blob/d70556f33b1c36abdf101a07ad8cf57eb56fbdf1/ci/calorimeter.yml),
`simulate-ecal-*`, provides an existing `ddsim` photon-gun recipe. Neither source
establishes realistic digitization or nODD response acceptance.

**FACT — published Si-W context:** `SRC-CALICE-SIW-ELECTRONS-2008`,
[CALICE electron-response paper, arXiv:0811.2354v1](https://arxiv.org/pdf/0811.2354v1),
§§3–4 (PDF pp. 4–6), uses muon Landau convolved with Gaussian calibration,
0.13 MIP typical channel noise and a 0.6 MIP analysis threshold. Its detector
has 30 layers with three tungsten thicknesses and 525 μm silicon. §6.2,
Figs. 14–16 (PDF pp. 16–18), reports approximately 1% linearity and
`16.6%/sqrt(E/GeV) ⊕ 1.1%` resolution over 6–45 GeV. These are facts about
that test-beam configuration. **INFERENCE:** they provide a comparison scale;
they are unsuitable as equality tolerances for ODD, whose geometry, sampling,
upstream material, event selection and noise configuration differ. Do not copy
the CALICE layer weights or fit a noise parameter to force this agreement.

## Required checks

The matrix defines proposed software checks and measurements. Human review of
quantitative detector-acceptance criteria remains pending. Fixture values must
be named as test values; they do not select nODD electronics parameters.

| Check | Required input and method | Observable and proposed software criterion | Limitation |
| --- | --- | --- | --- |
| Configuration and provenance | Explicit prototype opt-in; pinned original silicon model, build and configuration; native and upstream units recorded. | Reject missing model/calibration, invalid thresholds/noise, wrong collection, duplicate or inconsistent cell metadata and nonfinite values before producing output. | Successful parsing does not select physical operating parameters. |
| Empty and noise-only events | A test inventory of known cells, including cells without simulated deposits; empty SimHit input; independent event seeds. | Count all channel trials, not just retained hits. With Gaussian noise enabled, verify the prethreshold mean and RMS against configured parameters and threshold occupancy against the model's one-sided tail probability. | A fixture inventory validates the algorithm. Full-detector false-hit occupancy requires the actual channel inventory, masks and channel-dependent noise. |
| Noise statistics | For an explicitly Gaussian test configuration, use independent channel-event draws and thresholds with a measurable tail, such as `T/σ = 2`; retain the exact seed and draw count. | Proposed unit criterion: mean within `5σ/sqrt(N)` of its configured value, RMS within five of its Gaussian standard errors, and tail count within five binomial standard deviations of `N p`, where `p = erfc(T/(sqrt(2)σ))/2`. Choose `N` before running so `N p` is adequate. Also test strict/inclusive threshold equality deterministically. | Upstream clipping, ADC rounding and saturation can alter the analytic expectation. Test at the same stage as the prediction. A production high threshold with zero observed hits gives an upper bound, not an RMS measurement. |
| Deterministic response | Zero-noise, fixed-gain same-cell and multiple-cell deposits; time-window edges, upper dynamic-range edges, threshold edges; IDs above 32 bits. | Verify accumulation order, energy conversion, thresholding, times, output IDs and truth mapping against the original implementation. Test input permutations and event-order/thread reproducibility. | A formula independently rewritten in a test is a unit oracle; it is not an execution of the original implementation. |
| Original-model comparison | Feed identical ODD `ddsim` hits, selected collections, time cuts, calibration and channel map to the original MarlinReco implementation and the nODD adapter. Record immutable model source, steering, input SHA-256 and event IDs. | In the deterministic limit compare accepted cell IDs and per-cell energies with a documented floating-point/float-persistence tolerance. For stochastic comparisons use shared draws only if both implementations really share an engine and draw order; otherwise compare distributions and uncertainties over independent replications. | A silicon-kernel-only comparison validates that kernel. The issue's end-to-end same-hit reference gate also needs the original framework's cell aggregation, thresholds, gain/dead-cell and timing behavior. A copied equation or shared helper on both sides cannot establish this gate. |
| Muon MIP | Independent `ddsim` muons; identified primary crossings, known silicon path lengths, noise off/on and threshold off/on. Fit deposit spectra with a Landau convolved with a Gaussian, record range/binning and fit uncertainty. | Report MPV in deposited GeV, configured MIP units and digitized units. Compare against the documented expected MPV for the actual thickness/path and original-model output. Separate calibration and held-out closure samples. | Injecting a value defined to be one MIP checks a conversion only. A mean stopping-power estimate is not the Landau MPV. Summing all shower/secondary deposits is not a single-crossing MIP measurement. |
| Electron/photon response | Several fixed generated energies and signed η values; exact gun, material, field, cuts and physics list; frozen calibration. Include all generated events. | Retain distributions and count denominators; report visible response, linearity residuals, `σ/mean` resolution with uncertainty, longitudinal response and leakage proxies. Keep species and η separate. Compare raw deposits, noise-free digitization and full configured digitization on the same events. | This is characterization until acceptance bounds are reviewed. Applying independent calibrations at every energy makes a linearity test circular. A sparse handful of events cannot establish a resolution curve. |

For zero-mean Gaussian noise, clipping negative values to zero or applying a
threshold changes both the mean and RMS. Measure the raw stage or use the
correct truncated distribution; the retained hit energies cannot directly
reproduce the configured Gaussian RMS. Correlated/common-mode terms require
their covariance model rather than treating all channels as independent.

## Modest first campaign

**NODD DESIGN CHOICE — proposed characterization grid, approval pending:**
use `e-` and `gamma` at 5, 20 and 50 GeV and η = 0, 1 and 2, initially
200 independent events per point: 3,600 shower events. This covers two barrel
directions and one endcap direction without claiming transition coverage.
Use a fixed φ away from a verified module boundary, recorded in the recipe;
add seam/transition and negative-η controls separately. For a narrow Gaussian
sample, 200 events give roughly 5% relative statistical uncertainty on its
width; increase to 1,000 per point for roughly 2% when a stable pilot warrants
it. These are sample-size planning estimates, not observed precision.

Add a 10 GeV `mu-` pilot at η = 0 and 2, 500 events each, keeping the per-layer
path-length categories distinct. A 50/50 calibration/closure split is an
explicit proposal only if a new MIP calibration is necessary. Prefer an
independently documented original calibration when available. Report
insufficient fit statistics rather than silently pooling different paths.

An example generation command, to be checked against the verified local
`ddsim --help`, is:

```sh
ddsim --enableGun --numberOfEvents 200 --random.seed 117001 \
  --gun.energy '20*GeV' --gun.particle gamma \
  --gun.thetaMin 1.5707963267948966 --gun.thetaMax 1.5707963267948966 \
  --gun.distribution uniform --compactFile /path/to/pinned/ODD/xml/OpenDataDetector.xml \
  --outputFile /path/to/ignored/run/gamma-20GeV-eta0.edm4hep.root
```

This command uses the ODD CI gun pattern and fixes θ for η = 0; its default φ
distribution must be recorded or explicitly replaced by the campaign steering.
For other η use `θ = 2 atan(exp(-η))`, always a polar angle in `[0,π]`.
Assign a distinct recorded seed to every sample, with an independent control
seed. The executed report must provide the final complete generation,
digitization, reference and plotting commands; no unimplemented command is
presented here as an existing tool.

Define `f_visible = sum(E_Si deposited)/E_generated` if only sensitive hits
are available. A physical deposited-energy sampling fraction is
`f_sampling = E_active/(E_active + E_passive)` under a stated volume set and
event selection. It additionally requires active and passive deposition
scoring; the sensitive-hit sum alone cannot determine its denominator.
Report escape/leakage and upstream losses separately. Do not label
`f_visible` as a directly measured physical sampling fraction.

## Minimal remaining inputs and interpretation

1. A verified ODD detector installation plus `ddsim`/DD4hep/Geant4 with the
   pinned compact, materials, physics list and random-seed controls, or existing
   EDM4hep samples accompanied by those identities, event truth and hashes.
   Hit positions may be used as cell centres only when the producer's contract
   guarantees that meaning; contribution/step positions have another meaning.
2. A working original MarlinReco/LCIO runtime for the selected model, or an
   authorized equivalent remote execution environment, with source, steering
   and a traceable same-hit EDM4hep-to-original-input conversion. An isolated
   original kernel can unblock kernel tests while leaving the framework gate
   visibly open.
3. A full active-channel inventory for whole-detector noise occupancy and
   masks. Use an explicitly bounded fixture inventory for unit tests. Real
   irradiation/temperature/noise inputs, pulse response and pileup overlays
   remain required before 14 TeV, μ = 200 claims; this single-particle campaign
   does not provide them.
4. The physical calibration and operating assumptions for the prototype, with
   their source or explicit unsigned study status. Unit-test noise/MIP values
   and published test-beam parameters must not silently become detector defaults.

## Retained evidence and closeout

Retain only resulting plots, compact binwise summaries and reproduction/provenance
records in Git. Histogram summaries need edges, units, under/overflow, counts,
selection and generated-event denominators. Means and widths additionally need
sufficient moments or documented fit outputs/uncertainties; same-event paired
comparisons need retained covariance statistics. Record zero-signal and failed
events. Do not retain event-level samples disguised as binwise data.

Keep full ROOT events and detailed logs local and ignored, with size and SHA-256
in the recipe. Record nODD/ODD/original-model full revisions, dirty patches,
executed source hashes, compiler/library versions, input/configuration hashes,
seeds, event counts, timestamps, commands and exit codes. Distinguish checks
reproducible from the compact retained summaries from those needing the full
same-hit samples. An executed results report must mark each matrix row as
passed, failed, characterization-only or unavailable with its actual evidence.
