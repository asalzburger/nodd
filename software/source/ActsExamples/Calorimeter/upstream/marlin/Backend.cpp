// Copyright (C) 2026 CERN
// SPDX-License-Identifier: GPL-3.0-only
// Isolated executable wrapper; never linked to the MPL nODD libraries.
#include "RealisticCaloDigiSilicon.h"

#include <CLHEP/Random/JamesRandom.h>
#include <CLHEP/Random/Random.h>

#include <cmath>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <nlohmann/json.hpp>
#include <stdexcept>
#include <vector>

namespace {
// Event-local deterministic seed; independent of framework scheduling.
std::uint64_t mix(std::uint64_t value) {
  value += 0x9e3779b97f4a7c15ULL;
  value = (value ^ (value >> 30)) * 0xbf58476d1ce4e5b9ULL;
  value = (value ^ (value >> 27)) * 0x94d049bb133111ebULL;
  return value ^ (value >> 31);
}
float finiteFloat(const nlohmann::json &value) {
  const double number = value.get<double>();
  if (!std::isfinite(number) || number < 0 ||
      number > std::numeric_limits<float>::max()) {
    throw std::invalid_argument("Backend parameter outside float range");
  }
  return static_cast<float>(number);
}
} // namespace

int main(int argc, char **argv) {
  try {
    if (argc != 3) {
      throw std::invalid_argument(
          "usage: nodd_marlin_silicon_backend input.json output.json");
    }
    std::ifstream input(argv[1]);
    nlohmann::json request;
    input >> request;
    if (!input || request.at("schema") != 1) {
      throw std::invalid_argument("Invalid backend request");
    }
    const auto seed = request.at("seed").get<std::uint64_t>();
    const auto event = request.at("event").get<std::uint64_t>();
    const long engineSeed = 1 + mix(seed ^ mix(event)) % 900000000ULL;
    CLHEP::HepJamesRandom engine(engineSeed);
    CLHEP::HepRandom::setTheEngine(&engine);
    RealisticCaloDigiSilicon model;
    model._calib_mip = finiteFloat(request.at("mipGeV"));
    model._ehEnergy = finiteFloat(request.at("pairEnergyEv"));
    model._elec_noiseMip = finiteFloat(request.at("noiseMip"));
    model._elec_rangeMip = finiteFloat(request.at("dynamicRangeMip"));
    if (model._calib_mip <= 0) {
      throw std::invalid_argument("MIP energy must be positive");
    }
    const float pairEnergy = model._ehEnergy;
    std::vector<double> values;
    for (const auto &entry : request.at("energiesGeV")) {
      const float energy = finiteFloat(entry);
      // The upstream silicon method divides by its positive pair expectation.
      // For empty channels only, disable that step before calling unchanged
      // EnergyDigi so electronics noise can be evaluated. Not upstream sparse
      // event behavior and never represented as original-framework equivalence.
      model._ehEnergy = energy == 0 ? 0 : pairEnergy;
      const float value = model.EnergyDigi(energy, 0, 0);
      if (!std::isfinite(value)) {
        throw std::runtime_error("Nonfinite upstream response");
      }
      values.push_back(value);
    }
    const nlohmann::json response{
        {"schema", 1},
        {"upstream",
         "iLCSoft/MarlinReco@255967eb855ebbc8f75ebaac190b268b63332e8b"},
        {"mip", values}};
    std::ofstream output(argv[2]);
    output << response;
    if (!output) {
      throw std::runtime_error("Cannot write backend output");
    }
    return 0;
  } catch (const std::exception &error) {
    std::cerr << "Silicon backend: " << error.what() << '\n';
    return 1;
  }
}
