# SPECIES-PhysVal-06 — independent full native numerical regression

Exact reviewed pin b9fc3aa4917027098f8a1739f1cf346f23d77288. Seven assigned
hashes verified. Read-only; no simulations, rebuilds or writes by reviewer.
No blocking defect found in the two-sided numerical repair.

Independently streamed all15,000 original/replay audit events. Every byte matches:
5,000each at1/5/10GeV, with186,998,556 /608,815,566 /820,470,218uncompressed
bytes. This includes generated/simulated identities and secondaries, measurements,
seeds, every candidate/state and recorded parameter/variance. SHA256s match the
initial failure manifest and coordinator's canonical regression artifact.

All9 persisted ROOT files also match bitwise in every tree branch form, length,
dtype, shape and underlying buffer:322,624measurement rows with42branches/tree;
both5,000event summary trees per momentum have99branches, including covariance.
ROOT headers/UUIDs are not asserted identical.

The exact+0 rounding proof for0<=u<2^-54 and exact-1 proof foru>40 are valid.
Native O2/NDEBUG flags/macros/compiler identity are checked; optional pybind LTO
is disabled. No production FENV pragma, mask, clearing or rounding modification.
The task-owned transport dependency replaces one simulation algorithm in the
same sequencer position, retaining aliases and algorithm-number-based streams.

Both existing production and strict executables independently pass; each has
1,572,432bitwise loss,6,000parent/photon/RNG and127,229guarded hardware/native
FPE checks, including tiny/large underflow positive controls. Three reports pin
b9fc3aa, seed133042, selected profile,5,000events and completed after unchanged
FPE gate. Modulea87e8b33...1b5dfd,47common source/binary fingerprints, runtime
fingerprints and prepared geometry/material/response match originals. Campaign
differences are only declared guard metadata; exports remain Python initializer.

This is a numerical correction with unchanged recorded physics, not retuning
on validation performance. Preserve all failed attempts. Running100GeV Fatras
and the Geant4 matrix were not inspected/accepted. Full performance assessment
and human acceptance remain separate.
