// This file is part of the ACTS project.
//
// Copyright (C) 2016 CERN for the benefit of the ACTS project
//
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at https://mozilla.org/MPL/2.0/.

#pragma once

#include <string>
#include <optional>
#include <vector>

#include "ActsCalorimeter/EventData/CalorimeterHit.hpp"
#include "ActsExamples/Framework/DataHandle.hpp"
#include "ActsExamples/Framework/IAlgorithm.hpp"
#include "ActsExamples/Calorimeter/SiliconDigitization.hpp"

namespace ActsExamples {

/// Framework adapter for an explicitly opted-in, unsigned Si-W PROTOTYPE.
/// Without silicon configuration execute() retains the unimplemented failure.
class CalorimeterDigitizationAlgorithm final : public IAlgorithm {
 public:
  struct Config {
    std::string inputSimHits;
    std::string outputHits;
    std::optional<SiliconDigitizationConfig> silicon;
    /// A complete declared channel inventory is required for empty-channel
    /// noise. Empty means sparse input-hit mode; it does not measure detector
    /// noise occupancy. Inventory entries must be unique and finite.
    std::vector<SiliconDigitizationCell> channels;
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
