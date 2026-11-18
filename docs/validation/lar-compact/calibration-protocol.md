# Secondary held-out η-only calibration diagnostic

2026-11-18. **Exploratory PROTOTYPE**, specified after the primary raw10k result
and before any calibrated predictions. It does not replace or alter the frozen
raw study. Raw global width is52.57% versus17.84%;95.34% of candidate variance
is between the three fixed broad-region means. A position-gain diagnostic is
needed before interpreting this mixture as energy precision.

Use the same saved10k events, exact primary pair and physical/metadata gates.
No new transport or geometry changes. Fit each model separately with identical
fixed algorithm:60 equal |η| bins of width0.05 over0–3; within each training bin,
mean R=S/Etrue is the forward gain. Application is Ehat=S/gain(|η|), with no true
energy input, energy regression, prior shrinkage, response clipping or tail cuts.
Truth η supplies an ideal track-direction control, not a measured cluster model.
All zero signals remain zero; missing/nonpositive trained gains fail explicitly.

Use five fixed folds from a seeded permutation of primary IDs (seed14865017),
shared across both geometries. Every primary's gain excludes its own entire
fold. Keep all10000 held-out predictions; save per-fold training counts/gains.
No bin-width/fold/feature search or hyperparameter tuning is performed.

For1000 shared whole-primary bootstrap replicates (seed14865018), refit training
bin means under the replicate multiplicities separately for every fold/model,
then evaluate held-out predictions and weighted statistics. Fixed fold labels
preserve hold-out identity even when a primary is resampled. Refit uncertainty
and cross-model/projection covariance remain explicit. Intervals are pointwise,
conditional on these models, illumination and fixed calibration family; no
noninferiority margin or engineering acceptance is invented.

Report calibrated SD(Ehat/Etrue)/mean, mean closure, zeros/tails, energy-conditioned
widths in the original broad regions,10|η|/10legacyfoldedφ bins and underlying
histograms. Compare core barrel separately; improved transition cannot conceal
poorer core precision. Mean closure versus energy is required, because this
η-only model cannot remove nonlinearity. No digitization/noise/pileup or multi-TeV
claim follows. A full10k-fit gain table may be recorded for later reuse, clearly
separate from the five cross-validation models actually evaluated; its deployment
requires fresh validation and matching geometry/material/source provenance.

PhysVal prospective clarifications: no recentering/normalization with held-out
labels. Histograms show Y=Ehat/Etrue around absolute unity. Mean closure versus
energy **and energy×broad region** accompanies widths. The η-family choice
followed inspection of the full raw sample: cross-fitting prevents gain-fit
leakage but does not erase this selection reuse. These are **exploratory
cross-validated** results, with bootstrap conditional on that selected family;
they are not independent validation and cannot reverse the primary raw result.
