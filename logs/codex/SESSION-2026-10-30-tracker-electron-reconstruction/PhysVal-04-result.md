# SPECIES-PhysVal-04 — separate source assessment

Reviewed exact commit `72f9c8fb18077c9234546f1913800c1c902826ec`, all assigned
inputs, matching ACTS355ea source and completed diagnostic smokes at their own
pins. Read-only; no native simulations, installations or writes by reviewer.

- P2: the matrix verifier omitted case-label/report/summary/generated-pT identity.
  Coordinator added exact label/report/summary agreement and per-event tolerance
  rtol=1e-12 before final evidence verification. This is an audit correction.
- P3: G4Version is a static header string, not an independent runtime probe.
  Treat `loaded_Geant4_version` as historical field naming; interpret it as the
  observer header version alongside actual shared-library hashes and CLI version.
- Owned typed DD4hep construction, exact sensitivity tagging and live/replay
  mapper equivalence resolve the earlier singleton/cast defect.
- ACTS uses uint32 iteration budget; each nonterminal ambiguity step removes one
  track. Native termination is strict sharedCount<3. Five independent fixtures
  confirm the audit handles repeated state links and track sets correctly before
  quality selection. The computation-budget correction preserves physics cuts.
- Independently reproduced the old electron 100GeV event62:2,653 survivors,
  maximum13 shared measurements. Completed dabb1cc7 Geant4 muon2/electron20/pion20
  smoke cases have exact46,250 mappings, correct event counts and max shared0.
- All-generated scoring, full particle identities, secondary separation,
  hypothesis checks, complete measurement inputs, frozen material/response and
  persistent cleanup remain satisfactory at source level.

The running full matrix and converged-budget smoke were not reviewed. Existing
Fatras electron, Gaussian response, material representation and Geant4 time/FPE
limits remain. No human approval is inferred.
