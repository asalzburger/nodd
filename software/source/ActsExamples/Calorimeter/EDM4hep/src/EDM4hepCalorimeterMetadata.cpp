// This file is part of the ACTS project.
//
// Copyright (C) 2016 CERN for the benefit of the ACTS project
//
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at https://mozilla.org/MPL/2.0/.

#include "ActsExamples/Calorimeter/EDM4hepCalorimeterMetadata.hpp"

#include <algorithm>
#include <cmath>
#include <set>
#include <stdexcept>
#include <utility>

#include "Acts/Definitions/Units.hpp"

namespace ActsExamples {
EDM4hepCalorimeterMetadata::EDM4hepCalorimeterMetadata(
    const Config& config, Acts::Logging::Level level)
    : IAlgorithm("EDM4hepCalorimeterMetadata",
                 Acts::getDefaultLogger("EDM4hepCalorimeterMetadata", level)) {
  if (config.inputFrame.empty() || config.outputFrame.empty() ||
      config.inputFrame == config.outputFrame ||
      config.geometryIdentifier.empty() ||
      config.input.inputFrame != config.inputFrame ||
      config.response.inputSimHits != config.input.outputDeposits ||
      config.response.outputHits != config.clustering.inputHits ||
      config.response.outputHits != config.hitOutput.inputHits ||
      config.input.outputDeposits != config.hitOutput.inputDeposits ||
      config.input.outputSources != config.hitOutput.inputSources ||
      config.clustering.inputHits != config.clusterOutput.inputHits ||
      config.clustering.outputClusters != config.clusterOutput.inputClusters ||
      config.hitOutput.outputHits != config.clusterOutput.inputEdmHits) {
    throw std::invalid_argument(
        "Inconsistent calorimeter metadata configuration");
  }
  // Validate declared I/O boundaries without executing either skeleton.
  (void)EDM4hepCalorimeterInputConverter{config.input};
  (void)CalorimeterDigitizationAlgorithm{config.response};
  (void)CalorimeterClusteringAlgorithm{config.clustering};
  (void)EDM4hepCalorimeterOutputConverter{config.hitOutput};
  (void)EDM4hepCalorimeterClusterOutputConverter{config.clusterOutput};
  auto& strings = m_parameters.strings;
  auto& numbers = m_parameters.numbers;
  strings["acts.calo.geometry"] = {config.geometryIdentifier};
  strings["acts.calo.units"] = {"energy=GeV", "length=mm", "time=ns"};
  strings["acts.calo.response.status"] = {"unimplemented skeleton"};
  strings["acts.calo.clustering.status"] = {"unimplemented skeleton"};
  strings["acts.calo.cluster.unmeasured"] = {"intrinsic direction",
                                             "covariance", "shower shapes"};
  strings["acts.calo.links.weight"] = {
      "accepted deposited energy fraction per calibrated cell"};
  strings["acts.calo.input.simHits"] = {config.input.inputSimHits};
  strings["acts.calo.native.deposits"] = {config.input.outputDeposits};
  strings["acts.calo.native.sources"] = {config.input.outputSources};
  strings["acts.calo.native.hits"] = {config.response.outputHits};
  strings["acts.calo.native.clusters"] = {config.clustering.outputClusters};
  strings["acts.calo.output.hits"] = {config.hitOutput.outputHits};
  strings["acts.calo.output.truthLinks"] = {config.hitOutput.outputLinks};
  strings["acts.calo.output.clusters"] = {config.clusterOutput.outputClusters};
  strings["acts.calo.output.clusterTimes"] = {config.clusterOutput.outputTimes};
  strings["acts.calo.output.clusterSeedCellIds"] = {
      config.clusterOutput.outputSeedCellIds};
  strings["acts.calo.cluster.sidecars"] = {
      "same index as output cluster; time in ns; seed ID uint64"};
  // Version 2 explicitly removes the retired physics configuration.
  numbers["acts.calo.schemaVersion"] = {2};
  std::set<std::string> keys;
  for (const auto& [key, values] : strings) {
    keys.insert(key);
  }
  for (const auto& [key, values] : numbers) {
    keys.insert(key);
  }
  for (const auto& [key, values] : config.additional.strings) {
    if (!key.starts_with("acts.calo.") || !keys.insert(key).second) {
      throw std::invalid_argument(
          "Duplicate or invalid calorimeter metadata key");
    }
    strings.emplace(key, values);
  }
  for (const auto& [key, values] : config.additional.numbers) {
    if (!key.starts_with("acts.calo.") || !keys.insert(key).second ||
        std::ranges::any_of(
            values, [](double value) { return !std::isfinite(value); })) {
      throw std::invalid_argument(
          "Duplicate or invalid calorimeter metadata value");
    }
    numbers.emplace(key, values);
  }
  m_input.initialize(config.inputFrame);
  m_output.initialize(config.outputFrame);
}
ProcessCode EDM4hepCalorimeterMetadata::execute(
    const AlgorithmContext& context) const {
  auto frame = m_input(context);
  auto rejectExisting = [](const auto& keys) {
    if (std::ranges::any_of(keys, [](const auto& key) {
          return key.starts_with("acts.calo.");
        })) {
      throw std::invalid_argument(
          "Input frame already has calorimeter metadata");
    }
  };
  rejectExisting(frame.getParameterKeys<int>());
  rejectExisting(frame.getParameterKeys<float>());
  rejectExisting(frame.getParameterKeys<double>());
  rejectExisting(frame.getParameterKeys<std::string>());
  for (const auto& [key, values] : m_parameters.strings) {
    frame.putParameter(key, values);
  }
  for (const auto& [key, values] : m_parameters.numbers) {
    frame.putParameter(key, values);
  }
  m_output(context, std::move(frame));
  return ProcessCode::SUCCESS;
}
}  // namespace ActsExamples
