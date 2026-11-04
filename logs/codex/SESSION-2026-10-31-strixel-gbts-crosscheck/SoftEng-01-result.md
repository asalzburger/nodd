# STRIXEL-GBTS-SoftEng-01 — isolated native runner

Child `/root/strixel_gbts_softeng`, explicit SoftEng mandate fallback at full
input revision `4ea4af17727020bac2ba8f5e2f6172378711c15a`.
Implemented four owned new files: runtime.py, campaign.py, test_runtime.py and
README.md in software/analysis/strixel_reconstruction. No frozen helper edits,
commits, shared dependency modifications, further delegation or publication.

Nine focused tests passed: matrix/template/profile identity, local-v-only
scaling, all-four baseline gates, geometry-only tolerance, appended writer RNG
order, all-event/strict ambiguity gates, two-process launch, verified resume and
no overwrites, source/data sensitivity and actual frozen timing schedule.

Eight2-event native smokes at10GeV completed: four Fatrasmuon pitches plus
0.5/2mm guarded Fatras electron and Geant4 electron. Outputs remain ignored at
/private/tmp/nodd-strixel-gbts/smoke-v2. Every case passed four baseline-equivalence
and source/native/prepared-input immutability gates. Muon/electron Fatras startup
about33s, Geant4 electron about100s. Geant4 maps46250/46250 sensors with no duplicate
or unmatched volumes, processes exactly2events and reports version11.4.3.
Runtime Python3.14.5, ROOT6.40.04. Registry fingerprint preflight warning persists;
no attempt to repair shared environment. Session validator passed217records.

Mandatory hits.root appended at end of sequencer preserves existing random
algorithm slots. It persists float32 hit position/ct/momentum/delta and integer
identities, not native float64 bits. Full events.jsonl.gz keeps native audit.
Independent physical pairing/response/scoring checks belong to retention.
Optional --write-root adds existing measurement/track summaries. The campaign
uses fresh one-thread subprocesses, repeatable jobs3 concurrency and longest-cost
first scheduling from20 hashed frozen reference timings. Geant4electron100GeV
can take about20min/1000events before contention, based on old actual timings.

Final native source hashes: runtime.py
`346e0fe6631e777f271642b5aaa25af7dc7bd271c8bd7961ac9e309d3d7c7ce7`;
campaign.py `5b167712c0a171849e60c42b0f9626e1bead0ac12c7a5ea134509dc119d1d319`.
No native physics source changed after smoke; the final campaign change only
adds deterministic scheduling and its hashed timing references. Final parent
source freeze precedes the production campaign.

Actual selected seeds appear in top-level report and strixel_crosscheck metadata.
Fatrasmuon uses common converged species schema from electron_campaign.json,
with particle=muon and actual seed123042; inherited sample_seeds remains frozen
historical source metadata. No cut, selected profile or hypothesis was retuned.
Original1000iteration ambiguity budget is proved nonlimiting only for cases
whose all-event raw candidate maximum<=1000; production/bridge must establish
scope, not extrapolate the2-event smoke to all historical5000events.

Client per-turn exact token counters unavailable; no estimate entered.
