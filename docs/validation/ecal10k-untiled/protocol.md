# Continuous silicon control — prospective protocol

Status: **PROTOTYPE**, a deliberately unbuildable counterfactual requested by
the human on 2026-11-12. Governing physical references are the current isolated
DES-030/DES-031 ECAL prototypes and the retained PR134 sample. This control does
not amend either engineering design or the production detector.

**NODD DESIGN CHOICE, authorized for this control only:** replace the tiled
sensitive/guard silicon by continuous 0.5 mm sensitive silicon across each
sector's complete layer face. Preserve the beam aperture, sector count, layer
planes, pitch, absorber and all other passive material except intersections
with the new silicon plane, which must be explicitly subtracted and recorded.
Document actual bounds and changed material volumes before transport. This
fills module gaps, guards and available service margins together; it cannot
separate their individual contributions. Existing absorber/support cracks and
barrel/endcap transitions remain unless explicitly identified otherwise.

The complete **existing carrier** face retains its inherited 1 mm half-seam:
barrel sheets have radial x = 1702.5 + 10.9·l mm, |z| ≤ 3900 mm and
|y| ≤ x·tan(pi/16) − 1 mm through their 0.5 mm thickness. Endcap sheets
span 100 ≤ x ≤ 2223.2 mm, |y| ≤ x·tan(pi/16) − 1 mm, at local
z = 2.5 + 10.9·l mm. Preserve the signed-end transforms. These are inherited
prototype dimensions, not newly optimized values. Independent analytic targets
for full sensitive silicon are 2,327,867,693.009 mm³ in the barrel and
750,268,701.311 mm³ in both endcaps. Added wafer silicon totals
1,062,963,764.106 mm³; existing guards also become sensitive. Structural
subtractions are restricted to intersections with these silicon sheets.

Use the **identical retained 10,000 primary records**, verified by SHA-256,
rather than regenerating statistically equivalent inputs: uniform total energy
10–80 GeV, eta −3 to 3, full phi. Keep the original native geometry/audit
libraries where possible. Retain 12 DDSim workers, transport seed 133812341,
per-event seeding, FTFP_BERT, 0.7 mm cuts, 5 mm charged steps in sensitive
silicon, zero field and raw hit sums. A 24-event pilot precedes production.
Use the same disk guard: twice pilot bytes/event plus a 30 GiB reserve; retain
all 10k when it fits. Never remove the original sample.

Repeat the original saved-event/native-worker audits. Compare only after all
10,000 IDs, primary energies/directions and worker totals pass. Preserve both
original and new run/geometry/input/library identities. Geometry changes alter
random-number consumption; matching seeds do not make the two transported
showers identical.

Define R = total raw sensitive-silicon energy / true primary total energy.
Use sample SD(R), ddof=1, divided by mean(R), retaining every physical zero.
Keep the original ten |eta| bins and ten signed sector-folded phi bins
(period 22.5°, range [−11.25,+11.25)°). No cuts, angular calibration or
Gaussian-core fits. The result is a spectrum-averaged raw response width,
including leakage and within-bin variation, rather than fixed-energy
reconstructed calorimeter resolution.

Use 5,000 joint **paired whole-event** bootstrap replicas, seed 1335000:
resample event IDs once per replica and use the same indices for both
geometries and both projections. Retain 95% percentile intervals for each
width and the direct difference w_tiled − w_continuous. Store the joint
40-width covariance and 20-difference covariance in compact binwise evidence.
Do not subtract widths or variances in quadrature to claim a separate tiling
term; altered mean response and correlated geometric losses prevent that
interpretation without a model.

Overlay the two width curves, mean-response controls, zero counts and the
underlying response histograms with shared response bins. State the measured
counterfactual reduction with uncertainties and the changed material/coverage;
do not infer that the remaining width is an intrinsic stochastic term.

Only scripts, figures, provenance and compact binwise statistics go in Git.
Raw ROOT, primary/event ledgers and bulky transport logs remain local/ignored.
