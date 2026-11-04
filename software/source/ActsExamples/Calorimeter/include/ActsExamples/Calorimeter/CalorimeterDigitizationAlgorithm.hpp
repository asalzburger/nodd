// This file is part of the ACTS project.
//
// Copyright (C) 2016 CERN for the benefit of the ACTS project
//
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at https://mozilla.org/MPL/2.0/.

#pragma once

#include <string>

#include "ActsCalorimeter/EventData/CalorimeterHit.hpp"
#include "ActsExamples/Framework/DataHandle.hpp"
#include "ActsExamples/Framework/IAlgorithm.hpp"

namespace ActsExamples {

/// Reserved framework I/O boundary. No physical algorithm is implemented.
/// execute() throws std::logic_error and never manufactures output collections.
class CalorimeterDigitizationAlgorithm final : public IAlgorithm {
 public:
  struct Config {
    std::string inputSimHits;
    std::string outputHits;
  };

  explicit CalorimeterDigitizationAlgorithm(
      const Config& config, Acts::Logging::Level level = Acts::Logging::INFO);
  ProcessCode execute(const AlgorithmContext& context) const override;
  const Config& config() const { return m_config; }

 private:
  Config m_config;
  ReadDataHandle<ActsCalorimeter::SimCalorimeterHitContainer> m_input{this,
                                                                      "Input"};
  WriteDataHandle<ActsCalorimeter::CalorimeterHitContainer> m_output{this,
                                                                     "Output"};
};

}  // namespace ActsExamples
