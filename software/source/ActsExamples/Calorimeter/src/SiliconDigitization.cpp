// Copyright (C) 2026 CERN for the benefit of the ACTS project
// SPDX-License-Identifier: MPL-2.0
#include "ActsExamples/Calorimeter/SiliconDigitization.hpp"

#include <cerrno>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <limits>
#include <spawn.h>
#include <stdexcept>
#include <sys/wait.h>
#include <unistd.h>

#include <nlohmann/json.hpp>

#include "Acts/Definitions/Units.hpp"

extern char **environ;

namespace ActsExamples {
namespace {
struct TemporaryDirectory {
  std::filesystem::path path;
  TemporaryDirectory() {
    std::string pattern =
        (std::filesystem::temp_directory_path() / "nodd-silicon-XXXXXX")
            .string();
    if (const auto created = ::mkdtemp(pattern.data()); created != nullptr) {
      path = created;
    } else {
      throw std::runtime_error(
          "Cannot create silicon backend working directory");
    }
  }
  ~TemporaryDirectory() {
    std::error_code error;
    std::filesystem::remove_all(path, error);
  }
};

bool representableFloat(double value) {
  return std::isfinite(value) &&
         std::abs(value) <= std::numeric_limits<float>::max();
}
} // namespace

void validateSiliconDigitization(const SiliconDigitizationConfig &config) {
  if (config.executable.empty() || !representableFloat(config.mipEnergy) ||
      config.mipEnergy / Acts::UnitConstants::GeV <
          std::numeric_limits<float>::min() ||
      !representableFloat(config.pairEnergyEv) || config.pairEnergyEv < 0 ||
      !representableFloat(config.noiseMip) || config.noiseMip < 0 ||
      !representableFloat(config.dynamicRangeMip) ||
      config.dynamicRangeMip < 0 || !representableFloat(config.thresholdMip) ||
      config.thresholdMip < 0) {
    throw std::invalid_argument(
        "Invalid PROTOTYPE silicon response configuration");
  }
}

std::vector<double>
runMarlinSilicon(const SiliconDigitizationConfig &config,
                 const std::vector<double> &depositedEnergies,
                 std::uint64_t eventNumber) {
  validateSiliconDigitization(config);
  std::vector<double> energiesGeV;
  energiesGeV.reserve(depositedEnergies.size());
  for (const double energy : depositedEnergies) {
    const double gev = energy / Acts::UnitConstants::GeV;
    if (!representableFloat(gev) || gev < 0 ||
        (gev > 0 && static_cast<float>(gev) == 0)) {
      throw std::invalid_argument("Invalid silicon deposited energy");
    }
    if (config.pairEnergyEv > 0 && gev > 0 &&
        (!representableFloat(1e9 * gev / config.pairEnergyEv) ||
         static_cast<float>(1e9 * gev / config.pairEnergyEv) == 0)) {
      throw std::invalid_argument(
          "Silicon pair expectation exceeds float range");
    }
    energiesGeV.push_back(gev);
  }
  TemporaryDirectory work;
  const std::string input = (work.path / "input.json").string();
  const std::string output = (work.path / "output.json").string();
  const nlohmann::json request{
      {"schema", 1},
      {"event", eventNumber},
      {"seed", config.seed},
      {"mipGeV", config.mipEnergy / Acts::UnitConstants::GeV},
      {"pairEnergyEv", config.pairEnergyEv},
      {"noiseMip", config.noiseMip},
      {"dynamicRangeMip", config.dynamicRangeMip},
      {"energiesGeV", energiesGeV}};
  {
    std::ofstream stream(input);
    stream << request;
    if (!stream) {
      throw std::runtime_error("Cannot write silicon backend request");
    }
  }
  // argv is passed directly to posix_spawnp. Executable/file paths are never
  // interpreted by a shell, including paths with spaces or metacharacters.
  std::vector<std::string> arguments{config.executable, input, output};
  std::vector<char *> argv;
  for (auto &argument : arguments) {
    argv.push_back(argument.data());
  }
  argv.push_back(nullptr);
  pid_t child;
  const int spawnResult =
      ::posix_spawnp(&child, argv[0], nullptr, nullptr, argv.data(), environ);
  if (spawnResult != 0) {
    throw std::runtime_error("Cannot start external silicon response backend");
  }
  int status = 0;
  pid_t waited;
  do {
    waited = ::waitpid(child, &status, 0);
  } while (waited < 0 && errno == EINTR);
  if (waited < 0 || !WIFEXITED(status) || WEXITSTATUS(status) != 0) {
    throw std::runtime_error("External silicon response backend failed");
  }
  std::ifstream stream(output);
  nlohmann::json response;
  stream >> response;
  if (!stream || response.at("schema") != 1 ||
      response.at("upstream") !=
          "iLCSoft/MarlinReco@255967eb855ebbc8f75ebaac190b268b63332e8b") {
    throw std::runtime_error("Invalid silicon backend response provenance");
  }
  auto values = response.at("mip").get<std::vector<double>>();
  if (values.size() != depositedEnergies.size()) {
    throw std::runtime_error("Silicon backend response size mismatch");
  }
  for (const auto value : values) {
    if (!std::isfinite(value)) {
      throw std::runtime_error("Nonfinite silicon backend response");
    }
  }
  return values;
}
} // namespace ActsExamples
