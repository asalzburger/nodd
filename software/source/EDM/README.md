# Additional event data

nODD-owned hit and cluster structs live under
`include/ActsCalorimeter/EventData`. Their fields retain the PR #80 transient
schema: 64-bit cell IDs, global positions, energies and times in ACTS native
units, and event-local provenance indices. The identifier encoding and
cell-centre lookup belong to the detector. These structs supply no cell-ID
service, response or clustering implementation.

Persistency adapters and the standalone build entry point are under
[../ActsExamples/Calorimeter](../ActsExamples/Calorimeter/README.md).
The converters preserve the existing supplied-cluster contract (sum energy,
energy-weighted position/time and highest-energy seed, smaller cell ID on a
tie); they validate supplied values rather than constructing clusters.
EDM4hep and podio remain external Spack dependencies. See
[imported-source attribution](../NOTICE.md).
