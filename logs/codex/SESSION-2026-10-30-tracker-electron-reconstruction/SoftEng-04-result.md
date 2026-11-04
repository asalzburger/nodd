# SPECIES-SoftEng-04 — tiny-argument and native-build correction

Input b8b8697ed4ec7e538b8ca2fedb6e7c468cdf791a. Only five owned SafeFatras
files changed. No native simulations or shared/active Geant4 source changes.
Ownership returned to coordinator.

Exact +0 branch for0<=u<2^-54 complements exact -1 foru>40. Native object's
-O2 -g -DNDEBUG -std=gnu++20 -fPIC -D_GNU_SOURCE and ROOT macros are imported
from checked build.ninja; pybind LTO extras disabled. No production FENV pragma,
FPE mask, random draw, collection alias, algorithm name or physics default change.

Production-mode and strict-mode tests both pass, each:1,572,432 bitwise loss
comparisons;6,000 exact parent/photon/RNG comparisons;127,229 exponent-stratified
guarded hardware/native FPE checks. Positive controls reproduce libm underflow
at1e-300 and800. Build/import/ABI/export checks pass; only Python initializer is
exported. AppleClang21.0.0.21000334 matches native; CMake4.4.4 versus native4.4.3,
Python3.14.5, pybind3.0.4/ABI11. Unsuppressed Boost CMP0144 warning remains.

Module SHA256 a87e8b3337ddff4e2b9a5b386738d6fe30449e809f3493c2e07c7f492c1b5dfd.
Native object-block SHA256 2fff648bc18aa084b4a53ce56fa03cd57ea388450cb9915580c0b8e78cc8f933.
First module preserved in ignored diagnostics. Same-seed full-event equality
remains a coordinator integration gate; no human acceptance is implied.
