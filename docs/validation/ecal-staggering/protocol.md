# Calibration and physical module staggering — prospective protocol

Status: **PROTOTYPE**, authorized by the human on 2026-11-12. This implements
the bounded tests proposed in PR135. No production integration, sector-interface
redesign, engineering sign-off or predicted resolution improvement is implied.
Keep the original tiled and continuous samples unchanged and local.

## Geometry intervention and transport

Use independent four-layer tangential/axial board phases (0,0), (48,0), (0,48),
(48,48) mm, in addition to inherited −96/+96 mm slab-joint staggering. A physical
narrow barrel family uses 46×94 mm PCB, 42×90 mm silicon, 40×88 mm active area,
1 mm guards, 2 mm PCB margins and two complete ASIC/thermal stacks. Replacing
one full board by two narrow boards preserves the row envelope and ASIC capacity,
while changing silicon/guard/PCB area; record those changes. Full-slab axial rows
shift 48 mm away from their service bay. Short slabs use a declared 24 mm
quarter-pitch shift to preserve all rows and positive clearance. This adaptation
is chosen from packing constraints before response inspection, not from a fit.

Endcaps use four actual packing/sensor/PCB/electrode families with radial and
tangential half-phases, including the inner partial row. Preserve the aperture,
common absorber/skins/frames/cooling and carrier envelopes/sector transforms.
All guards, electronics, identifiers and partial-electrode references must follow
their physical modules. Existing full-depth sector seams remain.

Gate transport on native construction, overlaps at 1e-5 mm, counts, valid unique
physical IDs, mask/readout references, material accounting and dense geometric
coverage screening. Coverage does not predict energy resolution. Run a 24-event
12-worker pilot, then the **same retained 10,000 primary bytes** with 12 workers,
seed133812341/per-event seeding, FTFP_BERT, 0.7 mm cuts, 5 mm charged steps in
sensitive silicon and zero field. Disk planning uses twice pilot bytes/event plus
30 GiB reserve; reduce only if necessary, never delete retained data. Repeat
the existing full saved-primary/hit/native-worker audit.

## Reconstructed features and calibration

Infer features from persisted hit energy, position and cell layer only. An
energy-weighted hit centroid defines an axis from the known origin. No primary
truth energy, direction, geometry-pair response or true impact enters inference.
Use the actual candidate's sensitive polygons, including signed-end transforms.

Ten predeclared features per reconstructed barrel/endcap region are: absolute
reconstructed eta; three physical-mask exposure probes; longest central-ray
missing-layer streak/48; a sector-seam proximity transform; first16- and last16-
layer energy fractions; energy fraction in the other ECAL section; and lateral
width. The region is the section with the larger measured silicon signal.

The exposure probes convolve each layer mask with a 5×5 Gaussian sample pattern
at transverse scales 5.5, 11 and 22 mm, then average using a fixed Gaussian layer
probe centred at layer16 with width8 layers. Mix section exposures by measured
section energy fractions. Seam proximity uses a Gaussian of the distance to the
sector boundary with width22 mm. Lateral width is expressed in units22 mm.
These are **analysis test probes**, derived from pad-pitch multiples or declared
layer-basis choices, not measured shower-shape or engineering parameters.

Freeze five event-ID outer folds with permutation seed1337000 and three
independent inner folds with seed1337001; use identical assignments for both
geometries. Never split duplicate IDs across folds. Every calibrated prediction
excludes its original ID from training and hyperparameter selection.

Within each training region derive R0=weighted mean(S/Etrue), centring/scales
and ridge coefficients for y=(S/Etrue)/R0. Use an unpenalized intercept and
objective weighted mean squared error + lambda*sum(beta²), with fixed
lambda={0.01,1,100}, selected on the inner folds only. Break exact ties in favour
of stronger regularization. No absolute S/logS/energy-proxy feature is included
in the primary model. Apply Ecal=(S/R0)/clip(yhat,1/3,2); relative gains are
bounded at0.5–3. These bounds are regularization choices. Record clipping.

Invalid axes use a declared training-global scale-only fallback. Every generated
event remains in evaluation, and S=0 remains Ecal=0. Training includes all valid-axis
training events in its region; global fallback normalization includes zeros.
Freeze a secondary prior sensitivity using 1/Etrue training weights, keeping
test IDs and inference features identical. Truth supplies training weights/labels
and evaluation denominators only. Do not promote the secondary after inspecting
held-out results. Ten thousand events establish a demonstrator, not a fine-grained
production calibration or an independent fixed-energy certification.

## Comparisons and uncertainty

Report baseline/raw, baseline/calibrated, staggered/raw and staggered/calibrated.
Each geometry fits its own calibration with the same algorithm/folds. Raw angular
width uses the original S/Etrue populations unchanged. Calibrated width uses
Ecal/Etrue. Retain the same ten |eta| and signed folded-phi bins (22.5° period);
layer phasing never changes the plotting fold. The continuous curve remains a
separate diagnostic reference.

Include means, sample SD/mean, central q16–q84 width, zero/invalid-axis/clipping
fractions, signed-eta/end/sector summaries and fourteen 5 GeV true-energy slices.
For calibrated tails report Pr(Ecal/Etrue<0.5). The raw tail comparator must use
the cross-fit training-only scale S/R0, rather than unscaled silicon deposits.
Keep inclusive denominators. Inspect energy-dependent bias and prior sensitivity;
do not select a model by inclusive width alone.

Use 1,000 common whole-event bootstrap resamples, seed1338000. Keep original
ID folds and refit all preprocessing, inner selection and outer models in every
replicate. Use common multiplicities across geometries and raw/calibrated outputs.
Retain pointwise approximate95% percentile intervals, undefined counts and joint
angular-width/contrast covariance. This includes training uncertainty; bootstrapping
only frozen predictions does not. Model parameters/compact bin summaries may be
public; event features/predictions/full ROOT remain ignored and local. Export all
final scientific plots as PNG/PDF/SVG and retain original evidence unchanged.
