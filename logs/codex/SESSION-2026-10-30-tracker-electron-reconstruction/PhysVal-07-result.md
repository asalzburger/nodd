# SPECIES-PhysVal-07 — completed 14-case assessment

Separate read-only PhysVal assessment at17a4b2e8831081ddfdfb625c3eee15c52862befa.
Agent `/root/reco_species_physval`, thread01a18c6e-900f-71a0-a297-68e56d22a87b.
No modifications, native simulations or rebuilds. Both100GeV electron cases and
final canonical retention/report are excluded.

Independent scoring, without calling the author classifier, reclassified all
70,000events in14completedcases. Both CKF/ambiguity classifications, accepted and
rejected counts, fixed matching/quality, deterministic representatives and fitted
parameters/variance arrays agree exactly. Generated and both conditional
denominators, all16signed-eta bins, Wilson68/95 intervals, wrongcharge and full
uncut residual/pull arrays agree. Candidate bootstrap logic was reviewed; its
2,000resamplings were not independently rerun. Full LLT was not repeated; recorded
native covariance-positive-definiteness audits were used.

| Population | Matched at1/5/10/100GeV (each denominator5000) |
|---|---|
| Fatras electrons |2586/4185/4309/excluded|
| Geant4 muons |4805/4939/4953/4938|
| Geant4 electrons |2652/3942/4088/excluded|
| Geant4 pions |4033/4324/4351/4479|

All native survivors have at most2sharedmeasurements beforequality. Actual PDGs,
masses, charges, hypotheses, full simulated/parent IDs, secondary processes,
primary outcomes and final ct/positions pass. No unknown truth IDs or missing G4
parent identities. Source189revision-pinned files/runtime87fingerprints agree;
actual GBTS, baseline map/response and seeding/audit modules are stable. Every G4
case has46250unique sensor mappings/all7systems/5000native events/12datasetrecords.
Report-function replay agrees for sixparameter tails, quantiles, central68 widths,
hitcoverage and signed-eta outcomes.

Execution pins: Fatras e1/5/10 b9fc3aa4917027098f8a1739f1cf346f23d77288;
Geant4muons ande1/5/10 e71ecd03d1c54ccd84bcefaa3b7ef04f1fb01a50;
pion1 f5d4c26243078a204e9251f8f30de24062995d7e;
pion5/10/100 b8b8697ed4ec7e538b8ca2fedb6e7c468cdf791a.
Native and reduction hashes were inspected directly in the recorded build paths.

Findings: G4pion100 retains141/4479wrongcharges,476relative-pT errors>50%,
147q/p pulls>5sigma and maximumabsolute129.90. Wrongcharges extend to|eta|~0.20;
never describe them as exclusively farforward. G4electron1/5/10 timekills40/8/6,
with1/1/0reconstructed. Poststep terminal times reach~26.52ns. Without an uncut
control, timecut causal inefficiency/unbiasedness are unmeasured. Mixed candidates
can satisfy frozen>=50%purity; saydaughter-only tracks do notcountasprimaries.
Fatras e5events3047/4270 failmaximumpropagationsteps and lackfinalprimaryrecords;
all remain in5000denominator. Alive is not proof ofoutertracker survival.

At the reviewedpin the report omits SafeFatras numerical provenance and unmerged
Gaussian shower-response limitation. Coordinator added both guarded regimes,
unchangedRNG/physics/FPE,15kexact native/ROOT replay and retainedfailures afterthis
pin, plus all above scientific qualifications. Those later sourcebytes require
followup assessment. One-way electron vs two-waymu/pi, detailed vs effectivematerial,
prior-dominatedtime, header-version identity and G4internalFPE scope are explicit.

Disposition: no completed-case numerical mismatch. Distinct populations are not
pooled. Technical evidence assessment does not grant human signoff or acceptance;
final2cases/fullcanonicalreport remain to review.
