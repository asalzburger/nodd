# Staggered ECAL higher-statistics calibration — prospective protocol

**PROTOTYPE**, user-authorized 2026-11-12; staggered geometry only. The original
10k and all previous geometry/control results remain unchanged. No production
geometry, material, field, readout or sign-off change.

Use unchanged XML d78ecea5c5aa5173af54a4ce392994491eede936a7f4edb87d55bc72e69a0c2b,
original native geometry/audit libraries and transport settings:12 DDSim workers,
FTFP_BERT,0.7mm range cuts,5mm charged steps in sensitive Si,zero field.
Generate100k new training electrons and20k fresh independent validation electrons,
independent uniform total E10–80GeV,eta−3..3,phi−pi..pi,origin. Disjoint seeds and
campaign IDs,12serial10k batches; no old10k reuse. Maintain uniform sampling in
this primary test; extra gap sampling is deferred rather than changing the
training prior. Disk planning uses2×120k×measuredbytes/event +30GiB reserve;
keep a live guard and retain every earlier artifact. About375GiB is available.

## Existing-sample learning curve

Use the frozen original10-feature calibration with its unchanged5outer and3inner
ID folds, training preprocessing,lambda grid and0.5–3relativegain bounds.
For each outer fold select deterministic nested1000/2000/4000/8000event subsets
of its8000training IDs, with3prospective permutation seeds. Predict the same
2000held-out IDs; combine all five folds. Keep zeros and all inclusive counts.
Report individual seed metrics and their mean. Use200common whole-event
bootstrap multiplicities, seed13395100, refitting all subset models; fixed folds
and subset membership. This is exploratory because these10k already informed
model design. It measures statistics dependence of the frozen architecture,
not a fresh independent assessment of a revised model.

## Revised calibration and blinded validation

Prospectively split new100k into70kfit,15ktuning and15kclosure, using fixed random
ID permutation seed13395200. The fresh20k may undergo mandatory saved-primary/hit
and native-worker audits but its response performance is not inspected until
all final model settings, coefficients and closure factors are frozen in Git.

Primary response model: region-specific linear-response ridge regression of
(S/Etrue)/R0, with measured-feature additive piecewise-linear splines and fixed
physical interactions. R0, knots, clipping ranges, centring and scales derive
from response-fit data only. Use10existing reconstructed features; no truth
position, energy or absolute-signal proxy enters primary inference. Select3or7
interior quantile knots andlambda{0.0001,0.01,1} on15ktuning response-MSE only.
Predeclared interactions: |eta|×exposure22,exposure5.5×exposure22,
exposure22×missingstreak,exposure22×seam,exposure22×early,
exposure22×late,exposure22×lateralwidth,|eta|×othersectionfraction.
Keep prediction floor1/3 and ceiling2, so relative gains remain0.5–3.
Linear response targets conditional mean response; no log-response epsilon or
lognormal retransformation assumption is introduced.

After selection refit on85kfit+tuning, then estimate one global closure constant
C=1/mean(Epre/Etrue) from the untouched15kclosure events, including zeros.
Inference Ecal=C×Epre uses measured observables only. Global closure changes scale
and leaves SD/mean exactly unchanged; report pre/post closure separately.
Invalid axes use training-global scale fallback; physical zeros stay zero.
Do not refit response coefficients on the closure subset afterward.

Comparator: retrain the original10-feature architecture on the same70/15/refit85k
budgets, selectinglambda{0.01,1,100} with tuning-only response-MSE; same closure
subset and bounds. Distinguish this from the historical10k-trained coefficients.
The historical five-fold models may be ensembled as a separately labelled frozen
reference. No secondary model is promoted after seeing fresh20k outcomes.

## Evaluation and uncertainty

Report raw, historical reference, retrained original, revised pre-closure and
post-closure. Include inclusive means, sampleSD/mean,quantiles,zeros,clipping,
low-side tails,10|eta| and10signedfoldphi bins with unchanged22.5°period,
14five-GeV true-energy slices and signed-direction/sector controls.
These are broad-spectrum response widths, not fixed-energy resolution.

Use1000paired validation whole-event bootstrap replicas for conditional-on-frozen-
calibration intervals. Separately use200common resamples of the100k training
population with fixedstage memberships, repeating model selection,85krefit and
15kclosure, together with paired validation resampling, to include training
uncertainty. Keep the two uncertainty definitions explicit. Fixed stage/ID
assignments retain bootstrap duplicates. Freeze parameters before validation
unblinding; retain adverse results, energy-dependent bias and unresolved seams.

All scientific figures export PNG/PDF/vectorSVG; compact bin/model/covariance
records and reproducible recipes are public. ROOT,exact primary/event ledgers,
features,predictions and bulky audits remain local and ignored. Separate PhysVal
source/results assessment precedes closeout and a draft review PR.
