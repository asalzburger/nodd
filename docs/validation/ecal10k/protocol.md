# ECAL10K — Angular visible-response study

Status: **PROTOTYPE**, characterization of the retained PR133 ECAL geometry;
no design sign-off, calibration or reconstructed-resolution claim.

The human requests 10,000 electrons, E approximately 10–80 GeV, full uniform phi,
eta -3 to 3, 12 DDSim threads, disk-space gating and two ten-bin sigma(E)/E
projections. This protocol fixes the interpretation before the production run.

## Inputs and transport

Use the exact retained PR133 ECAL-only compact and materials, generated at
`3dab2346c4a08fd24898a7842906601884708a7d`; check both hashes against its receipt.
The governing unsigned prototypes are DES-030/DES-031. Omit tracker, beam pipe
and field, as in PR133. Retain FTFP_BERT, 0.7 mm production range cuts,
5 mm maximum charged-particle steps in sensitive silicon, raw EDM4hep cell hits
and default particle-truth persistence. Do not change geometry or sensitivity.

Generate independent uniform total energy E in [10,80] GeV, eta in [-3,3] and
phi in [-pi,pi), one electron per event at the origin. Input seed 13310000 uses
Python's standard-library Random. Export exact momentum components to 17
significant digits in uppercase `.HEPEvt` short format and retain a local input
ledger. Momentum is sqrt(E²-m_e²), with m_e=0.00051099895 GeV as the beam-input
mass parameter; verify actual saved mass/energy consistency on readback.

Use DDSim 1.38 / Geant4 11.4.3, 12 workers, random seed 133812341 and
`random.enableEventSeed=true`. The shared file reader serializes input and
assigns event identities; per-event seeding occurs after that assignment.
Use a single fixed output filename per invocation. Input/output event ordering
is not assumed. Native per-worker begin/end-run audits must establish all
12 initialized workers, both sensitive detector roles, zero field, cuts, step
policy and worker event counts. A serial control of a small identical pilot
provides an additional per-event response/reproducibility check.

## Disk policy

Initial available space is about 408 GiB. Reserve at least 30 GiB at all times.
After a 12-thread pilot, project storage at twice its observed bytes/event.
Keep 10,000 events when this fits; otherwise reduce only the total count to
the largest prefix fitting that conservative budget and report the reduction.
Never delete existing datasets to make room. Retain raw samples locally and
ignored; publish only recipes, compact bin summaries, provenance and figures.

## Observable, binning and uncertainties

For every valid primary, including valid no-hit events, sum all raw deposits in
`BARRELHits` and `EDGEHits`: S=sum(E_dep). Define R=S/E_primary using the
persisted total energy. In every angular bin compute sample SD(R), ddof=1,
divided by mean(R). This is the requested fractional width after removing the
trivial incident-energy spread. An overall multiplicative calibration cancels.
Do **not** compute SD(S)/mean(S) across the broad beam spectrum.

Label the plotted quantity `sigma(R)/mean(R), R=E_Si/E_true` and describe it as
the **fractional raw visible-response width for flat 10–80 GeV electrons**.
It includes shower fluctuations, gaps, leakage and unresolved response variation
inside each angular bin. It is not intrinsic reconstructed calorimeter energy
resolution. Keep all zero and transition responses; no post-hoc response cuts,
eta-dependent calibration or Gaussian-core fitting are permitted here.

Use ten equal |eta| bins from 0 to 3 (width 0.3). Both prototypes have sixteen
azimuthal replicas, with sector centres at phi=sector*2*pi/16. Set P=pi/8 and
phi_fold=((phi+P/2) modulo P)-P/2. Use ten equal signed bins from -11.25 to
+11.25 degrees (width 2.25 degrees); zero is the sector centre and endpoints
are seams. Do not additionally mirror the folded coordinate. Final |eta| upper
edge is inclusive, folded upper edge is excluded by modulo.

For each bin retain event count, energy mean/range, mean R, sample SD, width,
q16/q50/q84, valid zero-response count and 95% whole-event bootstrap percentile
intervals. Use 5,000 whole-event bootstrap replicates with seed 1335000.
Undefined bins/replicates remain null, with their counts reported. Retain joint
20-bin width covariance from the common event bootstrap when finite; this
preserves correlations between the two projections. Include signed eta and
sector counts/mean response as controls. No-hit events are physical zeros;
missing collections, invalid identities or nonfinite deposits are audit failures.

## Required readback and result checks

Require all expected unique EventHeader identities, exactly one status-1 PDG11
primary per event, origin vertex, matching input momentum/energy/direction,
in-range truth, finite positive stored cell energies and unique IDs per
collection. Confirm every system ID, complete worker audits and total worker
event count. Audit the actual ROOT event count/compression and file hash.
Store an ignored event-summary ledger for reanalysis; public data remain binwise.
Verify all projected-bin counts sum to the verified event total. Record actual
tools, source/recipe/library hashes, commands, seeds, wall/CPU time, child peak
RSS, disk size and bootstrap method. State deviations before interpreting them.

Prospective independent input: assignment ECAL10K-PHYSVAL at
`7ba71eeedc00c497bd4dc4168a9272039b300d8b`, source locators DES-030/031,
`barrel_export.py`, `edge_export.py`, `barrel_layout.py`, and the existing
issue117 raw-response/bootstrap conventions. This is an agent technical review,
not human approval.
