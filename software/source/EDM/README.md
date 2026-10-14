# nODD transient event data

`include/ActsCalorimeter/EventData` owns the migrated SimCalorimeterHit,
CalorimeterHit, CalorimeterCluster and CalorimeterJet types. They retain their
existing readout identity, native ACTS units and source-relation contracts.
The `nODD::EDM` interface target supplies these headers to local reconstruction.

Persistent storage remains external EDM4hep/podio from Spack. Its local
ActsExamples converters live under `../ActsExamples/Calorimeter/EDM4hep`.
Imported MPL-2.0 notices and provenance are recorded in `../NOTICE.md`.
