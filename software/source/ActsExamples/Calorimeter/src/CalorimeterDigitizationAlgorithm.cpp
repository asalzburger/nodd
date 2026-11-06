// This file is part of the ACTS project.
//
// Copyright (C) 2016 CERN for the benefit of the ACTS project
//
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at https://mozilla.org/MPL/2.0/.

#include "ActsExamples/Calorimeter/CalorimeterDigitizationAlgorithm.hpp"

#include <stdexcept>
#include <cmath>
#include <limits>
#include <map>

#include "Acts/Definitions/Units.hpp"

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
  if (config.silicon) {
    validateSiliconDigitization(*config.silicon);
  } else if (!config.channels.empty()) {
    throw std::invalid_argument("Channel inventory needs a silicon response");
  }
  std::map<std::uint64_t, Acts::Vector3> uniqueCells;
  for (const auto& cell : config.channels) {
    if (!cell.position.allFinite() ||
        !uniqueCells.emplace(cell.cellId, cell.position).second) {
      throw std::invalid_argument("Invalid silicon channel inventory");
    }
  }
}

ProcessCode CalorimeterDigitizationAlgorithm::execute(
    const AlgorithmContext& context) const {
  if (!m_config.silicon) {
    throw std::logic_error(
      "CalorimeterDigitizationAlgorithm: no physical implementation configured "
      "(issue #117 requires explicit PROTOTYPE silicon configuration)");
  }
  struct Cell {
    Acts::Vector3 position;
    double energy = 0;
    double energyTime = 0;
    std::vector<std::size_t> indices;
  };
  std::map<std::uint64_t, Cell> cells;
  for (const auto& channel : m_config.channels) {
    cells.emplace(channel.cellId, Cell{channel.position});
  }
  const auto& deposits = m_input(context);
  for (std::size_t index = 0; index < deposits.size(); ++index) {
    const auto& deposit = deposits[index];
    if (!deposit.position.allFinite() ||
        !std::isfinite(deposit.depositedEnergy) ||
        deposit.depositedEnergy < 0 || !std::isfinite(deposit.time)) {
      throw std::invalid_argument("Invalid silicon simulated deposit");
    }
    if (!m_config.channels.empty() && !cells.contains(deposit.cellId)) {
      throw std::invalid_argument("Simulated deposit absent from channel inventory");
    }
    auto [found, inserted] =
        cells.try_emplace(deposit.cellId, Cell{deposit.position});
    auto& cell = found->second;
    if (cell.position != deposit.position) {
      throw std::invalid_argument("Inconsistent silicon cell-centre positions");
    }
    cell.energy += deposit.depositedEnergy;
    cell.energyTime += deposit.depositedEnergy * deposit.time;
    if (deposit.depositedEnergy > 0) {
      cell.indices.push_back(index);
    }
    if (!std::isfinite(cell.energy) || !std::isfinite(cell.energyTime)) {
      throw std::overflow_error("Silicon cell accumulation overflow");
    }
  }
  std::vector<double> energies;
  energies.reserve(cells.size());
  for (const auto& [id, cell] : cells) {
    energies.push_back(cell.energy);
  }
  const auto& config = *m_config.silicon;
  const auto responses = runMarlinSilicon(config, energies, context.eventNumber);
  ActsCalorimeter::CalorimeterHitContainer hits;
  std::size_t index = 0;
  for (const auto& [id, cell] : cells) {
    const auto mip = responses[index++];
    // Upstream stores the threshold as float; preserve its strict comparison
    // at decimal thresholds that are not exactly representable (e.g. 0.6).
    if (mip > static_cast<float>(config.thresholdMip)) {
      const auto energy = mip * config.mipEnergy;
      if (!std::isfinite(energy)) {
        throw std::overflow_error("Silicon calibrated energy overflow");
      }
      // Native event data defines energy-weighted deposit time. Empty channels
      // have no measured time: use the documented zero placeholder, no links.
      hits.push_back({id, cell.position, energy,
                      cell.energy > 0 ? cell.energyTime / cell.energy : 0,
                      cell.indices});
    }
  }
  m_output(context, std::move(hits));
  return ProcessCode::SUCCESS;
}

}  // namespace ActsExamples
