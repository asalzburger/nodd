# Prospective compact LAr controls

2026-11-18, PROTOTYPE. Freeze [design](../../design/inputs/DES-032-compact-hadron-prototype.md)
and [contract](contract.json) before the new10k production or response analysis.
Reference is the complete audited PR140 LAr10k transport; preserve its event/input
bytes, hashes and event IDs. Candidate geometry changes are physical and therefore
the shower histories differ even at equal event seeds.

Use10,000 origin electrons with the original10–80GeV/flatη−3…3/fullφ illumination,
12workers,133812341 event seeds,FTFP_BERT,0.7mm cuts,5mm active charged-step cap,
ECAL-only B=0. Keep every event, zero and low tail. Retain native-context count,
canonical hit/primary readback, source/library stability and worker audits.
Serial/MT24-event controls compare every saved canonical cell, energy and position;
100-event native-limit/5mm pilots are diagnostics, not a convergence proof.

Primary comparison is paired ΔCV = CV(candidate)−CV(reference), where
R=active deposited energy/primary energy and CV=sample SD(R)/mean(R). Report
inclusive and10|η|/10legacySiW-fold bins, fullφ/signedη,14energy slices and
energy slices within fixed broad |η| regions0–1.2/1.2–1.5/1.5–3. Keep old
populations3999/999/5002. Show means, low tails, quantiles and underlying response
distributions; null CV is retained for all-zero/undefined bins.

Use1000 shared whole-primary bootstrap multiplicities, seed13001000, preserving
cross-model/angular covariance. Intervals are pointwise conditional95% bounds,
not simultaneous guarantees. No noninferiority margin or acceptance threshold is
invented; a nonsignificant difference cannot prove no precision loss. In particular,
transition improvement must not conceal worse core-barrel energy-slice precision.

Separately classify old/new envelope path classes and their migration on common
primaries, including the union of old/new partial-depth directions. Preserve
native sampling/upstream/downstream material scans. The25X0 sampling screen is
for specified fully traversed interior ray grids; wheel supports and transitions
remain explicit exceptions requiring their own depth/response plots. It is not
a universal acceptance or TeV containment proof. A10–80GeV study cannot certify
multi-TeV lepton/photon tails, hadron/jet, radiation or pileup performance.

No old calibration is applied or silently refitted. Any later calibration must
bind to this geometry and use separate training and held-out validation.
