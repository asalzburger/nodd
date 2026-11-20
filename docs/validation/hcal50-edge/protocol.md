# HCAL edge coverage and fixed-direction pion response protocol

2026-11-20. **DRAFT / PROTOTYPE; prospective, before new showers.** PhysVal
assignment HCAL-EDGE-PHYS, input revision
`b91b1d7969b94cccb4e0516e1c84246f4d2e2cd0`. This protocol governs the new
edge-module study and its separate angular, calibration and validation samples;
it grants no engineering sign-off or detector acceptance.

**FACT about retained evidence:** [the first HCAL protocol](../hcal50/protocol.md)
and [its summary](../hcal50/summary.json) define the unchanged comparison sample.
Its raw coefficient of variation includes gaps and angular nonuniformity.
The [DES-045 model](../../design/DES-045-hcal-restored-ecal-pion50.md) has 60
steel/carrier sampling layers and explicit pointing cracks. Preserve that
geometry, sample and result as dated evidence. New edge hardware, depth and
packing require their own source-bound geometry validation.

All new sample sizes, scan/ranking rules, seeds and statistical/display choices
below are **NODD DESIGN CHOICES** for this bounded simulation study. They are
not measured device properties or detector acceptance requirements. Equations
and scale-invariance statements are **INFERENCE**, derived from the definitions.

## Shared transport and integrity contract

Use one pi-minus primary, PDG -211, at the origin with **total energy 50 GeV**
and input mass 0.13957039 GeV. Set momentum magnitude to
`sqrt(50^2 - 0.13957039^2)` GeV. The geometry contains the complete new HCAL
barrel/endcaps and represented local hardware only: omit ECAL, tracker, beam
pipe, FCAL, solenoid and magnetic field consistently in all new samples.

Retain FTFP_BERT, 0.7 mm range cuts, the 5 mm maximum charged step in active
PSHost, event seeding, and twelve production workers. Audit actual cuts,
StepLimiter processes, active material, zero Birks constant, zero field and
worker event totals. No optical statistics, SiPM response, saturation, noise,
threshold, time-window selection, digitization or shower compensation is added.

Before production, require deterministic exports, complete and unique carrier
and logical tile IDs, physical cell-centre checks, overlap checks, native
material/depth evidence and ROOT/converted-Geant4 finite-solid membership
checks appropriate to the new edge shapes. Independently close all positive
sensitive-step deposits to native cells, then saved cells within documented
persistence tolerances. A sum of saved hits alone does not prove completeness.
Run and audit serial/twelve-worker controls and a pilot before full samples.

Each sample has its own ID, input, geometry, producer/library hashes, seed,
receipt and saved-data readback. Event numbers may repeat between independent
samples; identify records by `(sample ID, event number)`. Require every expected
primary, finite saved truth, correct energy/direction/mass, permitted canonical
cell IDs and every saved physical cell centre. Missing collections or broken
identities are audit failures, while valid empty collections are zero response.
Retain all zeros, non-Gaussian tails and late hadronic deposits. No response
cuts, Gaussian-core fits, direction changes or geometry retuning after showers.

## Angular sample and comparison

Use exactly **10,000** independent origin primaries with uniform signed eta in
[-3, 3] and full phi in [-pi, pi), independent of each other. Reuse the retained
input-angle records, or regenerate them with standard-library Random input seed
20261120 and verify identical primary bytes/directions against the old sample.
Use transport seed 202650001. The common primaries support a matched illumination
comparison; different geometries can produce different shower histories despite
matching event seeds.

Define `S = sum(saved raw scintillator deposited energies)` in GeV and
`r = S/Etrue`. Plot sample `SD(r, ddof=1)/mean(r)` versus fifteen equal **signed
eta** bins from -3 to 3, and fifteen equal signed folded-phi bins over one
complete 22.5 degree barrel sector. The phase is
`u = 100 * (((phi + P/2) modulo P) - P/2) / P`, with `P = pi/8`.
Central bins span u=-50 to +50 percent. Display u=-65 to +65 by periodic
repetition of existing points and errors; these margins add no events, bins or
independent measurements. Do not reflect the phase. Lower bin edges are
inclusive, upper edges exclusive, except the final eta edge is included.

Keep full-phi controls in sixteen equal bins and signed eta controls. Label
folding as a barrel reference whenever endcap hardware lacks sixteenfold
symmetry. Every eta and complete folded-phi projection must contain all 10,000
primaries. Retain per-bin counts, mean S, SD(S), mean r, SD(r), SD(r)/mean(r),
quantiles, zeros and response distributions with histogram units, normalization,
edges/counts and any underflow/overflow. Separately show mean response so a width
change is not mistaken for uniform response or calibrated energy resolution.

Use 1000 whole-primary bootstrap replicates, seed 13001000, jointly across both
angular projections. For a comparison, resample matched primary IDs jointly in
old and new geometries. Publish pointwise 95% percentile intervals, paired width
differences and the labelled joint width covariance. Undefined bins/replicates
remain null with counts; do not silently drop them. No angular calibration is
trained from this evaluation sample.

## Prospectively chosen fixed barrel direction

Choose the fixed direction from **geometry only**, after the new geometry is
frozen and before inspecting any new calibration or validation showers. This
is a conditional central-barrel reference, not an optimization of shower width
or a global optimum over all possible directions.

Scan eta=-0.6 to +0.6 in steps of 0.02 and phi=-11.25 to +11.25 degrees in steps
of 0.25 degree in the reference sector. For each candidate, also trace the nine
combinations of tangential/axial front-face offsets (-5, 0, +5) mm. Define these
offsets at the sector's front face x=3130 mm: the central intersection is
`(3130, 3130*tan(phi), 3130*sinh(eta)/cos(phi))`; add the transverse and axial
offsets there and aim each neighbouring ray from the origin through that point.
Count an active layer only for strictly positive ray length in its actual
finite scintillator solids, with recesses and gaps respected.

Reject a candidate if any of its nine rays lacks the complete nominal steel
traversal for that ray direction. Rank the remaining candidates, in order, by:

1. Largest minimum active-layer count among the nine rays.
2. Largest mean active-layer count among the nine rays.
3. Largest minimum transverse core-edge clearance at the core reference plane
   among actual crossed cores in that nine-ray set; use zero if a crossed core
   has no interior reference-plane intersection. Treat clearances differing by
   less than 1e-6 mm as tied, avoiding a floating-point tie-break optimum.
4. Smallest absolute eta, then smallest absolute phi, then positive eta and
   positive phi for exact remaining sign ties.

The offsets make the selection robust over a declared sampled neighbourhood,
rather than selecting an isolated submillimetre path. They are not a proof over
the entire continuous neighbourhood. Analytic box-minus-recess intersections
and finite steel-trapezoid clipping may implement the full scan; independently
confirm the winner and all nine neighbouring rays with native ROOT navigation.
Require analytic/native material and active-layer agreement at declared
numerical tolerances. A discrepancy must be understood before showers.

Record candidate grid, exact ranking, winner eta/phi, all nine ray results,
geometry/selector hashes and commit in an immutable pre-shower direction
receipt. Do not choose another direction after seeing response. If no candidate
passes the geometric prerequisite, report that failure and amend the protocol
before transport, with a visible reason. The fixed sample uses exactly the
winning central ray, without angular smearing; the nine rays are a geometry
selection/control and do not alter its primary distribution.

## Independent calibration and fixed-direction validation

Generate **2000 calibration primaries** at the chosen fixed direction with
transport seed 202650102. Separately generate **10,000 validation primaries** at
that same direction with seed 202650103. All have 50 GeV total energy. Repeated
fixed input vectors need no angular random generator. Separate event-seed
sequences and sample identities provide independent shower samples; do not
reuse calibration events in the validation population.

Fit one scalar `fs = mean_cal(S/Etrue)` using every valid calibration primary,
including zeros and tails. Require finite positive fs and freeze it, its
uncertainty, calibration population and all source/readback hashes before
examining validation results. This is an **effective 50 GeV pi-minus response
factor at this direction**, including the represented sampling, geometric and
hadronic losses. It is not an independently measured intrinsic material
sampling fraction. Its transfer to other energies, directions, geometries or
digitized signals is unvalidated. Never refit fs to validation data or train a
separate correction per validation bin.

Use the following three distribution panels for the independent 10k validation:

| Panel | Event coordinate | Required scale and width |
| --- | --- | --- |
| Raw energy | `S` [GeV] | mean(S) and sample SD(S) [GeV] |
| Raw fractional response | `r = S/Etrue` | mean(r), SD(r) [dimensionless or %], and SD(r)/mean(r) |
| Sampling-corrected relative residual | `delta = S/(fs*Etrue) - 1` | mean(delta) bias and SD(delta) [dimensionless or %]; also SD(Ecorr)/mean(Ecorr), with `Ecorr=S/fs` |

All widths use ddof=1 and the full inclusive population. At fixed energy,
`SD(r)=SD(S)/50` and `SD(delta)=SD(S)/(fs*50)` are widths relative to the **true
energy**, whereas `SD(S)/mean(S)` is relative to the **measured mean**. Give
these denominators explicitly; the two meanings of “relative resolution” are
not interchangeable. Use the calibration fs, rather than forcing the validation
mean residual to zero. Display histograms and bias/quantiles/zero counts, not
only one width number.

A positive constant scale leaves
`SD(Ecorr)/mean(Ecorr) = SD(S)/mean(S) = SD(r)/mean(r)` exactly unchanged. A
sampling correction changes the energy scale and SD/Etrue; it cannot by itself
improve the coefficient of variation or remove tails, dead regions or leakage.

Use 1000 **two-sample** bootstrap replicates, with independent default_rng
generators seeded 13001001 for validation and 13001002 for calibration. In each
replicate, resample 10k validation primaries once and reuse that resample for all
three panels; independently resample 2000 calibration primaries and refit fs for
that replica. Report pointwise 95% percentile intervals for fs, validation bias,
each width and other claimed scalar statistics, preserving their covariance.
This propagates finite calibration statistics and validation fluctuations.
The point estimate always uses the original frozen fs. Record undefined
replicates explicitly. Report conditional-on-fs intervals separately only if
clearly labelled, not as a replacement for the two-sample result. Verify the
coefficient-of-variation identity in the point estimate and every replica.

## Depth, interpretation and retained evidence

For the angular and fixed samples, retain longitudinal profiles, terminal-six
activity, zeros and world-escaped kinetic energy separately. Recheck nominal
steel interaction lengths and seam/edge/transition material paths for the new
geometry. Small final-layer activity does not exclude side or transition escape;
world-escaped kinetic energy excludes rest mass and nuclear invisible energy
and is not a calorimetric balance. A good fixed-direction result does not
establish inclusive angular, jet, pileup, timing, radiation or high-energy
performance. Scalar response calibration is not compensation or reconstruction.

Freeze geometry and protocol before showers and preserve failed/adverse controls.
Keep full XML, ROOT, primary/event ledgers, scan payloads and bulky logs local
and ignored. Publish the source/command recipe, direction and calibration
receipts, compact binwise statistics/covariance and plots. Distinguish source
revisions, any dirty launch inputs, later auditing revisions and executed checks.
Sampling error intervals condition on this transport/material model and omit
physics-list, detector-engineering and response-model systematic uncertainties.
