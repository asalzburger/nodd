// This file is part of the ACTS project.
//
// Copyright (C) 2016 CERN for the benefit of the ACTS project
//
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at https://mozilla.org/MPL/2.0/.

#pragma once

#include "ActsExamples/Calorimeter/EDM4hepCalorimeterMetadata.hpp"
#include "ExampleFixture.hpp"

namespace ActsExamples::CalorimeterFixture {
inline EDM4hepCalorimeterInputConverter::Config inputConfig() {
  return {"events", "SimCaloHits", "calo_deposits", "calo_sources", cellCentre};
}
inline CalorimeterDigitizationAlgorithm::Config responseConfig() {
  return {"calo_deposits", "calo_hits"};
}
inline CalorimeterClusteringAlgorithm::Config clusteringConfig() {
  return {"calo_hits", "calo_clusters"};
}
inline EDM4hepCalorimeterOutputConverter::Config hitOutputConfig() {
  return {"calo_hits", "calo_deposits", "calo_sources", "CaloHits",
          "CaloLinks"};
}
inline EDM4hepCalorimeterClusterOutputConverter::Config clusterOutputConfig() {
  return {"calo_clusters", "calo_hits",        "CaloHits",
          "CaloClusters",  "CaloClusterTimes", "CaloClusterSeedCellIds"};
}
inline EDM4hepCalorimeterMetadata::Config metadataConfig() {
  EDM4hepCalorimeterMetadata::Config config;
  config.outputFrame = "calo_events";
  config.geometryIdentifier =
      "synthetic calorimeter IO fixture v3; global cell centres in mm";
  config.input = inputConfig();
  config.response = responseConfig();
  config.clustering = clusteringConfig();
  config.hitOutput = hitOutputConfig();
  config.clusterOutput = clusterOutputConfig();
  return config;
}

/// Fixed test data supplied by a fixture, never computed from deposits.
/// The values exercise persistence/provenance contracts, not physical response.
inline ActsCalorimeter::CalorimeterHitContainer preparedHits() {
  using ActsCalorimeter::CalorimeterHit;
  return {CalorimeterHit{7,
                         cellCentre(7),
                         0.06 * Acts::UnitConstants::GeV,
                         6 * Acts::UnitConstants::ns,
                         {6}},
          CalorimeterHit{42,
                         cellCentre(42),
                         0.04 * Acts::UnitConstants::GeV,
                         2 * Acts::UnitConstants::ns,
                         {4}},
          CalorimeterHit{highCellId,
                         cellCentre(highCellId),
                         0.08 * Acts::UnitConstants::GeV,
                         4 * Acts::UnitConstants::ns,
                         {0, 1, 3}},
          CalorimeterHit{highCellId + 1,
                         cellCentre(highCellId + 1),
                         0.04 * Acts::UnitConstants::GeV,
                         2 * Acts::UnitConstants::ns,
                         {5}}};
}
inline ActsCalorimeter::CalorimeterClusterContainer preparedClusters() {
  using ActsCalorimeter::CalorimeterCluster;
  return {CalorimeterCluster{0.06 * Acts::UnitConstants::GeV,
                             cellCentre(7),
                             6 * Acts::UnitConstants::ns,
                             7,
                             {0}},
          CalorimeterCluster{0.04 * Acts::UnitConstants::GeV,
                             cellCentre(42),
                             2 * Acts::UnitConstants::ns,
                             42,
                             {1}},
          CalorimeterCluster{
              0.12 * Acts::UnitConstants::GeV,
              Acts::Vector3{1500, 40. / 3, 5} * Acts::UnitConstants::mm,
              10. / 3 * Acts::UnitConstants::ns,
              highCellId,
              {2, 3}}};
}
}  // namespace ActsExamples::CalorimeterFixture
