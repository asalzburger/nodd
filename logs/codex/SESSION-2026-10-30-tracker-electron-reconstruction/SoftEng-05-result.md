# SPECIES-SoftEng-05 — event-range feasibility

Read-only SoftEng assessment of `17a4b2e8831081ddfdfb625c3eee15c52862befa`.
Agent `/root/reco_species_softeng`, thread `01a18c71-68a7-70e0-bd48-4f5e3e7a9ccf`.
No files, processes or runtime settings changed.

Matching ACTS355ea Sequencer.cpp supports skip S and count M, giving absolute
event contexts [S,S+M). RandomNumbers.cpp seeds from configured seed, absolute
event number and numeric algorithm slot. Fatras range equivalence is plausible
but would require exact native event and ROOT branch replay, including the first
event in each fresh range. Geant4 reseeds per ACTS context but SimParticleTranslation
starts its private event counter at zero; the persistent helper has a separate
local processed-event counter. Skip advances neither. Fresh-process initialization
and other run-level state are not proven irrelevant to transport.

Source locators: matching ACTS Examples/Framework/src/Framework/Sequencer.cpp
223–282 and470–525; RandomNumbers.cpp23–25;
Examples/Algorithms/Geant4/src/Geant4Simulation.cpp126–147;
SimParticleTranslation.cpp42; project TruthTracking.cpp119–143.

Any future batching requires separate completed child reports, disjoint absolute
ranges whose union is exactly0…4999, actual local native event counts, identical
physics/sequence/runtime and full per-event numerical equivalence. Aggregate
metrics must be recomputed, never averaged or presented as one native process.
An unfinished prefix cannot pass final FPE/count/hash gates.

Coordinator decision: keep the original serial Geant4 case unchanged. No batching
implementation or speculative execution speedup is introduced. Fatras100GeV has
since completed natively with its existing strict gates. Human approval is not
inferred from this technical assessment.
