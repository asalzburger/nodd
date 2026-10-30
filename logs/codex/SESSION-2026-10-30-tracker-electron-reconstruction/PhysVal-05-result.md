# SPECIES-PhysVal-05 — independent SafeFatras assessment

Exact reviewed pin `f5d4c26243078a204e9251f8f30de24062995d7e`. Seven assigned
source hashes verified. Read-only; no rebuild, simulation or writes by reviewer.
No source-level numerical blocker found.

For u>40, exp(-u)<2^-54. Binary64 spacing immediately above -1 is2^-53,
so exp(-u)-1 rounds exactly to -1 under round-to-nearest. The branch preserves
multiplication order, gamma/four-angle draws, native photon generation and
parent updates. Scheduling checks rounding without changing it or FPE controls.

Independently ran the existing numerical executable:1,572,360 bitwise loss
comparisons and6,000 exact parent/photon/RNG comparisons pass, including the
original underflow positive control and guarded hardware/native FPE checks.
Six upstream hashes and all configure-time transformations were independently
replayed; generated header/source bytes exactly match. Hidden module exports
only PyInit_nodd_safe_fatras. Module hash95e83263...7035bb; test executable
03f12163...1428. Initial pT1/5/10 failures each wrote5,000events, seed133042,
and only11/5/12underflows; retained diagnostic hashes match.

Correction: ACTS seeds streams by configuredseed,eventnumber,algorithmnumber,
not logger/algorithm name. Preserve one simulation algorithm in the same slot.
The b8b8697 replay launcher explicitly replaces that dependency one-for-one;
full same-seed event comparison is still required before accepting reruns.
Compare generated/simulated identities, secondaries, measurements, seeds,
complete states/parameters/covariances and matching, not just operator-level loss.
Require full events, successful FPE gate and exact source/runtime provenance.
Original failures/interrupted100GeV remain excluded diagnostics. No model-cut
change, human acceptance or full-results assessment is implied.
