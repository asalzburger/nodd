// This file is part of the ACTS project.
//
// Copyright (C) 2016 CERN for the benefit of the ACTS project
//
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at https://mozilla.org/MPL/2.0/.

#include "ActsExamples/Calorimeter/CalorimeterDigitizationAlgorithm.hpp"

#include <stdexcept>

namespace ActsExamples {

CalorimeterDigitizationAlgorithm::CalorimeterDigitizationAlgorithm(
    const Config& config, Acts::Logging::Level level)
    : IAlgorithm(
          "CalorimeterDigitizationAlgorithm",
          Acts::getDefaultLogger("CalorimeterDigitizationAlgorithm", level)),
      m_config(config) {
  if (config.inputSimHits.empty() || config.outputHits.empty() ||
      config.inputSimHits == config.outputHits) {
    throw std::invalid_argument(
        "Calorimeter input/output names must be distinct and nonempty");
  }
  m_input.initialize(config.inputSimHits);
  m_output.initialize(config.outputHits);
}

ProcessCode CalorimeterDigitizationAlgorithm::execute(
    const AlgorithmContext& /*context*/) const {
  throw std::logic_error(
      "CalorimeterDigitizationAlgorithm: no physical implementation configured "
      "(issue #114)");
}

}  // namespace ActsExamples
