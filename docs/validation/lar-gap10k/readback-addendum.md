# Logical and physical volume identity in observer readback

2026-11-14. **PROTOTYPE / postprocessing correction; transport unchanged.**
The [observer protocol](observer-protocol.md) and all runtime producer files
remain frozen during the two full replays.

Completed failure records expose an identity-schema mismatch in the first
observer reader. The C++ observer records `G4LogicalVolume::GetName()`, for
example `w1_gap1`. DD4hep's error message reports the pre-step physical volume,
for example `w1_gap1_7`. The original reader compares those different names
literally. That correspondence check will reject valid failure records, even
though native energy accumulation, event identity and raw volume ID are intact.

**NODD DESIGN CHOICE — separate corrected readback:** preserve the original
runtime code, receipts, ROOT/observer files and first readback outputs. Add a
separately versioned auditor and analysis entry point. Resolve logical-to-physical
name aliases from the exact hash-bound native placement ledger: sensitive
placement `volume` is the logical name and its path's final node is the physical
name. Reject missing or unsupported aliases. Keep exact raw volume-ID matching,
the original coordinate comparison at its documented print precision, full
failure-count correspondence, all energy/identity/precision checks, and every
source/library/map/hash guard. No regular-expression-only name forgiveness and
no physical or numerical tolerance changes.

The corrected auditor must independently repeat successful-cell and A/S/U/H
closure from the original observer records and saved ROOT. It writes fresh
derived ledgers/proofs into its own output directory, with its own source
revision/hash and reused-helper/native-ledger bindings. It must not overwrite
or relabel original producer/auditor hashes. The corrected analysis uses the
unchanged frozen statistical functions and tail threshold, identifying its
own entry point and the corrected proof dependencies explicitly.

This is a postprocessing identity correction. It does not change Geant4,
geometry, sampling, segmentation, midpoint policy, guard, contributions, RNG,
or any already recorded energy. Repeating transport is unnecessary when exact
producer and artifact bindings establish that those runtime inputs are unchanged.
Full-population replay equality and deposited-energy completeness still require
the actual corrected audit; this addendum itself claims neither result.
