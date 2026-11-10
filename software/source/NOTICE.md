# Calorimeter software provenance

The restored hit/cluster event data and EDM4hep converters originated in
`asalzburger/acts` revision `8adca5eec180515a23d58d132a1e17e317a59e67`,
then migrated in nODD PR #80 at
`530080cfe16c7513228bf60238b99d4b9938538a`. Source copyright notices and the
Mozilla Public License 2.0 are retained in [LICENSE-ACTS-MPL-2.0](LICENSE-ACTS-MPL-2.0).
This notice concerns these imported files, not unrelated repository sources.

Issue #114 restores only the hit/cluster EDM, input/output converters,
metadata and persistence fixtures. The two processing adapters retain only
collection-name configuration and fail explicitly when executed. The former
threshold response, connected-component implementation, jets and ACTS build
injection are excluded. CMake, fixtures, tests and metadata were adapted to
this limited restoration; the restored tree is not claimed byte-identical to
PR #80. The source revision remains visible in Git and this notice.

External ACTS is pinned to `355ea68493b326956756c9386d2fd9eaf9328568`;
EDM4hep and podio remain separate existing dependencies under their own licenses.

## Issue #117 isolated MarlinReco silicon backend

The optional standalone executable under
`ActsExamples/Calorimeter/upstream/marlin/` reuses external
`iLCSoft/MarlinReco@255967eb855ebbc8f75ebaac190b268b63332e8b` sources:
`CaloDigi/Realistic/src/RealisticCaloDigiSilicon.cc` (whole unchanged translation
unit) and `RealisticCaloDigi.cc` (whole unchanged `EnergyDigi` method extracted
at configure time). The upstream comments attribute the calorimeter digitizer
to D. Jeans (2016), with timing extensions by R. Ete (2020); the latter timing
methods are not part of this subset. MarlinReco's `LICENCE` supplies GPL version
3, retained as [the backend license](ActsExamples/Calorimeter/upstream/marlin/LICENSE).

The nODD-written framework registration adapter, backend main and preparation
script are supplied for this isolated executable. Backend C++ adapter files use
GPL-3.0-only notices. The original external source is not redistributed in this
repository; preparation verifies complete upstream file hashes and records
them alongside the generated files, including the upstream license. The helper
links CLHEP and nlohmann/json under their own licenses, without ACTS or the MPL
nODD libraries. The MPL framework adapter exchanges JSON requests/responses
with the helper through a separate process. No GPL method is copied into or
linked with the MPL library. Retain upstream source and all license notices
when distributing this optional backend.

The reused energy subset excludes upstream timing integration, gain and
dead-cell configuration. Empty-channel electronics noise is an explicit adapter
extension that bypasses the positive-energy pair division. Its existence is not
evidence of full original-framework equivalence or detector-performance acceptance.
