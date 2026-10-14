# Imported software provenance

The nODD adapter and calorimeter extensions originated in the user's ACTS fork.
Their source notices and MPL-2.0 license are retained in LICENSE-ACTS-MPL-2.0.
These files are now nODD-owned extensions, compiled against a pristine ACTS
submodule. This does not change the licenses of the other repository files.

The Nodd adapter was copied from acts-nodd HEAD
555c66e71d0639665c2fa3d5574a0fe7f3f62cde and the relevant inspected uncommitted
tracker/Gen3 changes present on 2026-10-14. The original checkout is preserved.
The later calorimeter migration records its source revision separately.
DD4hep factories and configuration were moved within nODD without changing
scientific inputs, material definitions or source contents.

Calorimeter source provenance: asalzburger/acts revision
8adca5eec180515a23d58d132a1e17e317a59e67. Core reconstruction lives in Calorimeter,
ActsExamples algorithms/converters in ActsExamples/Calorimeter, and transient
hit/cluster/jet data in EDM. Existing C++ controls are retained under Calorimeter/
tests. Source code is relocated with unchanged contents; build path declarations
are adjusted. Persistent data remains the external Spack EDM4hep/podio model.
