# GEANTINO-PhysVal-02 — correction assessment

Reviewed 7c0012184a6bb033eb4366d48db4f8699b22f8d5. Both prior findings are resolved
within the bounded correction scope.

P3 fixed: separate lower/upper half-neighbor spacings and signed grid offsets
resolve excessive cell extent at positive and negative powers of two.
P2 fixed: native-rerun-4008abf.json preserves the separately identified prior run,
with exact reviewed classifier/launcher hashes. Header include path and header
hash recording support correction provenance.

Actual checks: read all five exact committed inputs and verify hashes; compile
exact committed regression with clang++ -std=c++17 -Wall -Wextra -Werror and
assertions enabled, then run successfully. Covers asymmetric widths at +/-128,
symmetric widths at127.5, subnormal half-widths atzero, grid containment and
infinity rejection. Temporary sources/executable stayed under /private/tmp.

No finding remains in scope. Corrected whole-scan rerun is coordinator-owned and
not claimed passed by this assessment. Finite-grid and original geometry/seed
limits persist. No repository edits, native simulation, install, activation,
external access or delegation. Technical assessment, not human sign-off.
