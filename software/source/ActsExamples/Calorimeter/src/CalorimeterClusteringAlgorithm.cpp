// This file is part of the ACTS project.
//
// Copyright (C) 2016 CERN for the benefit of the ACTS project
//
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at https://mozilla.org/MPL/2.0/.

#include "ActsExamples/Calorimeter/CalorimeterClusteringAlgorithm.hpp"

#include <stdexcept>

namespace ActsExamples {

CalorimeterClusteringAlgorithm::CalorimeterClusteringAlgorithm(
    const Config& config, Acts::Logging::Level level)
    : IAlgorithm(
          "CalorimeterClusteringAlgorithm",
          Acts::getDefaultLogger("CalorimeterClusteringAlgorithm", level)),
      m_config(config) {
  if (config.inputHits.empty() || config.outputClusters.empty() ||
      config.inputHits == config.outputClusters) {
    throw std::invalid_argument(
        "Calorimeter input/output names must be distinct and nonempty");
  }
  m_input.initialize(config.inputHits);
  m_output.initialize(config.outputClusters);
}

ProcessCode CalorimeterClusteringAlgorithm::execute(
    const AlgorithmContext& /*context*/) const {
  throw std::logic_error(
      "CalorimeterClusteringAlgorithm: no physical implementation configured "
      "(issue #114)");
}

}  // namespace ActsExamples
