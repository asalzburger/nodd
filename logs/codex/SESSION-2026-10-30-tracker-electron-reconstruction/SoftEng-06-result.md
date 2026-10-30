# SPECIES-SoftEng-06 — retained-pipeline integrity

Read-only source assessment at228edf1a2503897b68f04f17bfd9acffe179c465.
Agent `/root/reco_species_softeng`, thread01a18c71-68a7-70e0-bd48-4f5e3e7a9ccf.
Author/reviewer overlap: this agent authored initial transport, plot/report and
SafeFatras corrections; this is not independent review of those implementations.
No source/native/canonical/job modifications; ownership returned.

Two P2 gaps reproduced in temporary synthetic ROOT fixtures:
1. audit_root.py34–38 accepts ROOT event IDs[0,0] against analysis[0,1] when
both events contain zero tracks. Rowcounts and matched-only joins miss the hole.
Require unique full event-ID coverage including unmatched/zero-trackevents.
2. audit_root.py23–28 accepts one measurement involume999 with variance99,
checked_variance_marginals0. Require known volumes and complete expected
coordinate-marginal coverage. Declared-volume wrongvariance is correctly rejected;
validfixture correctly passes. These gaps do not demonstrate native corruption.

All26pinned tests passed in isolated source snapshot; Python sources parse.
The other reviewed contracts are coherent: explicit16case completeness and exact
0…4999events, source/runtime/report/ROOThash identities, frozenconfigs, ambiguity
convergence, uncut residual/pull and wrongcharge retention, reference labels and
CI replay. Finaldataset claims remain separatePhysVal responsibility.

Coordinator remediation at9e6a2bf921656b6c389bf51c6391758996a25487 requires
complete unique ROOTeventIDs and declaredmeasurementvolumes/allcoordinates,
binds newgates in speciesverify, and adds valid/negativeROOTcontrols. All29tests
pass. Final16case actualROOTaudit will use correctedsource; no gate weakened.
