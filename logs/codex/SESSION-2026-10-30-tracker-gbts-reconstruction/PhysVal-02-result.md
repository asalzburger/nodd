# RECO-PhysVal-02 — independent implementation assessment

Reviewed d166334b93ec19692e0c433cf03dd343d648f135; read-only, no native jobs.
Confirmed measured SP→CoreGBTS→hit parameter estimate→all-measurement CKF→ambiguity
flow, no truth initialization,3T and muon hypothesis. Identified internal CKF
selector hiding quality rejects; native ct time units; lost ordered seed links;
unguarded state reference surface; configurable group denominator ignored;
unfair setup-inclusive runtime tie-break; missing output/input/runtime hash
closure. Main removed internal selection, retained raw completed outputs, fixed
ordered links/state guard/denominator, separated sequencer time, enforced all
fingerprints, and added full fitted-covariance LLT/finite-chi2/positive-ndf quality.
Independent smoke checks: all4pinned metric controls PASS; all10event stage counts
and5primary matches reproduced; all67SPs exactly equal float32(measured local to
global), all146measurement identities/output hashes checked. Precast SP difference
max9.765625e-5mm. Execution launchHEADff672a4 differs from source-content pin d166;
recorded hashes establish the executed source. No final performance acceptance.
