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
