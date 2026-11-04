# RECO-SPECIES-PhysVal-03 — implementation assessment

Exact inputcaa5487c4315557604797be5c9152606867e0c28. Read-only source review.
BlockingP1 atthatpin: sensitivity wrapper uses global DD4hep singleton instead
of the owned DD4hepDetectorBase instance; coordinator reports native invalid
world-handle failure before transport. Requires checked owned accessor, newpin
and full mapping/event smoke. Conceptually correct sensitivity attribution is
not runtime validation atcaa. P3 recommends selected-profile launch/effective
settings guard; matrix verifier and launch policy must enforce actual GBTS.

Species identity/mass/sign and native hypotheses are consistent; no truth input
leakage; frozen all-generated matching and secondary identities preserved.
One-way electrons are justified before-validation compatibility change: reviewer
inspected26FLTDIV+26FLTINV reverseTrackStates diagnostic. Cross-species fit-policy
difference remains explicit. Exact sensitivity tags preserve geometry/material/
placement/IDs and matching; requires one-to-one46250sensor/nativeevent evidence.

Independent checks: all eight pinned input hashes;35muon first100arrays exactly
equal; native muon/electronpT1 smoke identity and complete-subset audit100/100
each, both signs and separate e/photon secondaries. Prior five-muon lifecycle
comparison had no differing particle/hit/measurement/summary/audit branches.
Unchanged persistent helper source SHA7fd68501444ee04e0e18abee70778c47cc7ac4a7d94ce9749a39016fa3f35c6f.
Historical lifecycle evidence supports the method, not current new-species
geometry/mapping. No new native runs/install/writes or final performance claim.
