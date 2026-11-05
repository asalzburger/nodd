// Copyright (C) 2026 CERN for the benefit of the ACTS project
// SPDX-License-Identifier: MPL-2.0
// Deterministic same-hit comparison; an external full-processor output is
// needed.
#include <edm4hep/CaloHitContributionCollection.h>
#include <edm4hep/CalorimeterHitCollection.h>
#include <edm4hep/EventHeaderCollection.h>
#include <edm4hep/SimCalorimeterHitCollection.h>
#include <nlohmann/json.hpp>
#include <podio/ROOTReader.h>
#include <podio/ROOTWriter.h>

#include <algorithm>
#include <array>
#include <cerrno>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <spawn.h>
#include <stdexcept>
#include <sys/wait.h>
#include <unistd.h>

#include "Acts/Definitions/Units.hpp"
#include "ActsExamples/Calorimeter/CalorimeterDigitizationAlgorithm.hpp"
#include "ActsExamples/Calorimeter/EDM4hepCalorimeterInputConverter.hpp"

extern char **environ;
using namespace ActsExamples;
using nlohmann::json;
namespace {
constexpr auto marlinPin = "255967eb855ebbc8f75ebaac190b268b63332e8b";
constexpr auto key4hepPin = "03b3676cecbdf85818f6de159ecf90ffe2482cec";

class Access final : public IAlgorithm {
public:
  Access()
      : IAlgorithm(
            "ReferenceAccess",
            Acts::getDefaultLogger("ReferenceAccess", Acts::Logging::WARNING)) {
    m_frame.initialize("events");
    m_hits.initialize("digitized");
  }
  ProcessCode execute(const AlgorithmContext &) const override {
    return ProcessCode::SUCCESS;
  }
  void frame(const AlgorithmContext &context, podio::Frame value) {
    m_frame(context, std::move(value));
  }
  const auto &hits(const AlgorithmContext &context) { return m_hits(context); }

private:
  WriteDataHandle<podio::Frame> m_frame{this, "Frame"};
  ReadDataHandle<ActsCalorimeter::CalorimeterHitContainer> m_hits{this, "Hits"};
};

bool isHash(const std::string &value) {
  return value.size() == 64 &&
         std::all_of(value.begin(), value.end(), [](char c) {
           return (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f');
         });
}

std::string sha256(const std::string &file, const std::string &tool) {
  std::string temporary =
      (std::filesystem::temp_directory_path() / "nodd-reference-hash-XXXXXX")
          .string();
  const int descriptor = ::mkstemp(temporary.data());
  if (descriptor < 0)
    throw std::runtime_error("Cannot create hash output");
  struct Cleanup {
    int descriptor;
    std::string path;
    ~Cleanup() {
      ::close(descriptor);
      std::error_code error;
      std::filesystem::remove(path, error);
    }
  } cleanup{descriptor, temporary};
  posix_spawn_file_actions_t actions;
  if (::posix_spawn_file_actions_init(&actions) != 0)
    throw std::runtime_error("Cannot initialize hash process");
  const int redirect =
      ::posix_spawn_file_actions_adddup2(&actions, descriptor, STDOUT_FILENO);
  std::vector<std::string> arguments{tool, "-a", "256", "--", file};
  std::vector<char *> argv;
  for (auto &argument : arguments)
    argv.push_back(argument.data());
  argv.push_back(nullptr);
  pid_t child;
  const int started = redirect == 0
                          ? ::posix_spawnp(&child, argv[0], &actions, nullptr,
                                           argv.data(), environ)
                          : redirect;
  ::posix_spawn_file_actions_destroy(&actions);
  if (started != 0)
    throw std::runtime_error("Cannot start shasum-compatible hash tool");
  int status = 0;
  pid_t waited;
  do {
    waited = ::waitpid(child, &status, 0);
  } while (waited < 0 && errno == EINTR);
  if (waited < 0 || !WIFEXITED(status) || WEXITSTATUS(status) != 0)
    throw std::runtime_error("Hash process failed");
  std::ifstream output(temporary);
  std::string value;
  output >> value;
  if (!isHash(value))
    throw std::runtime_error("Invalid SHA-256 output");
  return value;
}

void verifyHashes(const std::string &input, const std::string &reference,
                  const json &config) {
  const auto expectedInput = config.at("input_sha256").get<std::string>();
  const auto expectedReference =
      config.at("reference_sha256").get<std::string>();
  if (!isHash(expectedInput) || !isHash(expectedReference))
    throw std::invalid_argument("Malformed input/reference SHA-256 manifest");
  const auto tool = config.at("sha256_tool").get<std::string>();
  if (sha256(input, tool) != expectedInput ||
      sha256(reference, tool) != expectedReference)
    throw std::invalid_argument(
        "Input/reference SHA-256 differs from manifest");
}

SiliconDigitizationConfig responseConfig(const json &config,
                                         const std::string &backend) {
  if (config.at("pair_energy_eV") != 0 || config.at("noise_MIP") != 0 ||
      config.at("reference_energy_unit") != "MIP" ||
      config.at("input_position_contract") != "cell-centres" ||
      config.at("timing_mode") != "all contributions; energy comparison only") {
    throw std::invalid_argument("Comparator requires deterministic "
                                "zero-noise/all-contribution MIP control");
  }
  SiliconDigitizationConfig result;
  result.executable = backend;
  result.mipEnergy =
      config.at("mip_energy_GeV").get<double>() * Acts::UnitConstants::GeV;
  result.pairEnergyEv = 0;
  result.noiseMip = 0;
  result.thresholdMip = config.at("threshold_MIP");
  result.dynamicRangeMip = config.at("dynamic_range_MIP");
  result.seed = config.at("seed");
  validateSiliconDigitization(result);
  for (const auto key : {"absolute_tolerance_MIP", "relative_tolerance"}) {
    const double value = config.at(key);
    if (!std::isfinite(value) || value < 0)
      throw std::invalid_argument("Invalid comparison tolerance");
  }
  if (config.at("absolute_tolerance_MIP").get<double>() == 0 &&
      config.at("relative_tolerance").get<double>() == 0) {
    throw std::invalid_argument(
        "Declare a nonzero float-persistence tolerance");
  }
  const auto collectionNames =
      config.at("collections").get<std::vector<json>>();
  std::set<std::string> simNames, referenceNames;
  if (collectionNames.empty())
    throw std::invalid_argument("No comparison collections");
  for (const auto &names : collectionNames) {
    const auto sim = names.at("sim").get<std::string>();
    const auto reference = names.at("reference").get<std::string>();
    if (sim.empty() || reference.empty() || sim == reference ||
        !simNames.insert(sim).second ||
        !referenceNames.insert(reference).second) {
      throw std::invalid_argument("Invalid or repeated collection names");
    }
  }
  return result;
}

std::pair<int, int> eventId(const podio::Frame &frame,
                            const std::string &collection) {
  const auto &headers = frame.get<edm4hep::EventHeaderCollection>(collection);
  if (headers.size() != 1)
    throw std::invalid_argument("Each event needs exactly one EventHeader");
  return {headers[0].getRunNumber(), headers[0].getEventNumber()};
}

void sameSimHits(const edm4hep::SimCalorimeterHitCollection &input,
                 const edm4hep::SimCalorimeterHitCollection &retained) {
  if (input.size() != retained.size())
    throw std::invalid_argument(
        "Reference did not retain identical simulation-hit counts");
  std::map<std::uint64_t, edm4hep::SimCalorimeterHit> originals;
  for (const auto &hit : input) {
    if (!originals.emplace(hit.getCellID(), hit).second) {
      throw std::invalid_argument(
          "Deterministic reference control requires one SimHit per cell");
    }
  }
  std::set<std::uint64_t> seen;
  for (const auto &hit : retained) {
    const auto found = originals.find(hit.getCellID());
    if (found == originals.end() || !seen.insert(hit.getCellID()).second)
      throw std::invalid_argument("Reference simulation cell IDs changed");
    const auto &original = found->second;
    const auto a = original.getPosition(), b = hit.getPosition();
    if (original.getEnergy() != hit.getEnergy() || a.x != b.x || a.y != b.y ||
        a.z != b.z ||
        original.contributions_size() != hit.contributions_size()) {
      throw std::invalid_argument("Reference simulation hit values changed");
    }
    for (std::size_t index = 0; index < original.contributions_size();
         ++index) {
      const auto x = original.getContributions(index),
                 y = hit.getContributions(index);
      const auto p = x.getStepPosition(), q = y.getStepPosition();
      if (x.getEnergy() != y.getEnergy() || x.getTime() != y.getTime() ||
          p.x != q.x || p.y != q.y || p.z != q.z) {
        throw std::invalid_argument(
            "Reference simulation contributions changed");
      }
    }
  }
}

json compare(const std::string &inputPath, const std::string &referencePath,
             const json &config, const std::string &backend) {
  const auto response = responseConfig(config, backend);
  podio::ROOTReader inputReader, referenceReader;
  inputReader.openFile(inputPath);
  referenceReader.openFile(referencePath);
  const auto events = inputReader.getEntries("events");
  if (events == 0 || events != referenceReader.getEntries("events"))
    throw std::invalid_argument(
        "Reference event count differs or input is empty");
  std::set<std::pair<int, int>> eventIds;
  std::uint64_t inputCells = 0, nativeCells = 0, referenceCells = 0,
                matched = 0;
  std::uint64_t nativeOnly = 0, referenceOnly = 0, energyMismatch = 0,
                badEvents = 0;
  std::array<std::uint64_t, 80> residualBins{};
  std::uint64_t underflow = 0, overflow = 0;
  double maxDifference = 0;
  const double absolute = config.at("absolute_tolerance_MIP");
  const double relative = config.at("relative_tolerance");
  const auto header = config.at("header_collection").get<std::string>();
  for (std::size_t event = 0; event < events; ++event) {
    auto source = podio::Frame{inputReader.readEntry("events", event)};
    auto reference = podio::Frame{referenceReader.readEntry("events", event)};
    const auto identity = eventId(source, header);
    if (identity != eventId(reference, header) ||
        !eventIds.insert(identity).second)
      throw std::invalid_argument(
          "Mismatched or duplicate ordered run/event IDs");
    const auto before = nativeOnly + referenceOnly + energyMismatch;
    for (const auto &names : config.at("collections")) {
      const auto simName = names.at("sim").get<std::string>();
      const auto refName = names.at("reference").get<std::string>();
      const auto &sim =
          source.get<edm4hep::SimCalorimeterHitCollection>(simName);
      sameSimHits(sim,
                  reference.get<edm4hep::SimCalorimeterHitCollection>(simName));
      inputCells += sim.size();
      WhiteBoard board;
      AlgorithmContext context{0, event, board, 0};
      Access access;
      // Each collection gets a fresh read of the same event; the source frame
      // remains available above for the identity/unchanged-input checks.
      access.frame(context,
                   podio::Frame{inputReader.readEntry("events", event)});
      EDM4hepCalorimeterInputConverter::Config in;
      in.inputSimHits = simName;
      in.outputDeposits = "deposits";
      in.outputSources = "sources";
      in.useHitPosition = true;
      EDM4hepCalorimeterInputConverter(in, Acts::Logging::WARNING)
          .execute(context);
      CalorimeterDigitizationAlgorithm::Config digitization{"deposits",
                                                            "digitized"};
      digitization.silicon = response;
      CalorimeterDigitizationAlgorithm(digitization, Acts::Logging::WARNING)
          .execute(context);
      std::map<std::uint64_t, double> native, original;
      for (const auto &hit : access.hits(context))
        native.emplace(hit.cellId, hit.energy / response.mipEnergy);
      for (const auto &hit :
           reference.get<edm4hep::CalorimeterHitCollection>(refName)) {
        if (!std::isfinite(hit.getEnergy()) || hit.getEnergy() <= 0 ||
            !original.emplace(hit.getCellID(), hit.getEnergy()).second)
          throw std::invalid_argument(
              "Invalid reference energy or repeated cell ID");
      }
      nativeCells += native.size();
      referenceCells += original.size();
      for (const auto &[id, energy] : native) {
        const auto found = original.find(id);
        if (found == original.end()) {
          ++nativeOnly;
          continue;
        }
        ++matched;
        const double difference = energy - found->second;
        const double tolerance =
            absolute +
            relative * std::max(std::abs(energy), std::abs(found->second));
        maxDifference = std::max(maxDifference, std::abs(difference));
        energyMismatch += std::abs(difference) > tolerance;
        const double residual = difference / tolerance;
        if (residual < -2)
          ++underflow;
        else if (residual >= 2)
          ++overflow;
        else
          ++residualBins.at(static_cast<std::size_t>((residual + 2) / 4 *
                                                     residualBins.size()));
      }
      for (const auto &[id, energy] : original)
        referenceOnly += !native.contains(id);
    }
    badEvents += before != nativeOnly + referenceOnly + energyMismatch;
  }
  std::vector<double> edges;
  for (std::size_t i = 0; i <= residualBins.size(); ++i)
    edges.push_back(-2 + 4. * i / residualBins.size());
  return {
      {"passed", badEvents == 0 && matched > 0},
      {"configuration", config},
      {"events", events},
      {"unique_ordered_run_event_ids", eventIds.size()},
      {"input_sim_cells", inputCells},
      {"native_accepted_cells", nativeCells},
      {"reference_accepted_cells", referenceCells},
      {"matched_cells", matched},
      {"native_only_cells", nativeOnly},
      {"reference_only_cells", referenceOnly},
      {"energy_mismatch_cells", energyMismatch},
      {"mismatched_events", badEvents},
      {"max_absolute_difference_MIP", maxDifference},
      {"normalized_residual",
       {{"edges", edges},
        {"counts", residualBins},
        {"underflow", underflow},
        {"overflow", overflow},
        {"unit", "difference / declared tolerance"},
        {"normalization", "matched cell counts; all input events retained"}}},
      {"limitations",
       {"Energy/selection deterministic control only; timing and stochastic "
        "equivalence untested.",
        "Producer/source/runtime identity is supplied provenance, not "
        "authenticated by this comparator.",
        "Full event IDs and hit payloads remain in hashed local ROOT files, "
        "not this binwise summary."}}};
}

podio::Frame fixtureFrame(int event, bool reference, int fault) {
  edm4hep::EventHeaderCollection headers;
  auto header = headers.create();
  header.setRunNumber(7);
  header.setEventNumber(event + (fault == 2 ? 1 : 0));
  edm4hep::CaloHitContributionCollection contributions;
  edm4hep::SimCalorimeterHitCollection hits;
  edm4hep::CalorimeterHitCollection digitized;
  if (event == 0) {
    auto contribution = contributions.create();
    contribution.setEnergy(fault == 3 ? .0005f : .0004f);
    contribution.setTime(3);
    contribution.setStepPosition({20, 30, 40});
    auto hit = hits.create();
    hit.setCellID(0xfedcba9876543210ULL);
    hit.setEnergy(contribution.getEnergy());
    hit.setPosition({100, 20, 3});
    hit.addToContributions(contribution);
    auto output = digitized.create();
    output.setCellID(hit.getCellID());
    output.setEnergy(fault == 1 ? 5 : 4);
    output.setPosition(hit.getPosition());
    output.setTime(3);
  }
  podio::Frame frame;
  frame.put(std::move(headers), "EventHeader");
  frame.put(std::move(contributions), "Contributions");
  frame.put(std::move(hits), "SimHits");
  if (reference)
    frame.put(std::move(digitized), "OriginalHits");
  return frame;
}

void selfTest(const std::string &backend,
              const std::filesystem::path &directory) {
  std::filesystem::create_directories(directory);
  const auto input = (directory / "synthetic-input.root").string();
  const auto reference = (directory / "synthetic-reference.root").string();
  json config{
      {"mip_energy_GeV", 1e-4},
      {"pair_energy_eV", 0},
      {"noise_MIP", 0},
      {"threshold_MIP", .5},
      {"dynamic_range_MIP", 2500},
      {"seed", 117},
      {"reference_energy_unit", "MIP"},
      {"input_position_contract", "cell-centres"},
      {"timing_mode", "all contributions; energy comparison only"},
      {"absolute_tolerance_MIP", 1e-5},
      {"relative_tolerance", 5e-6},
      {"header_collection", "EventHeader"},
      {"collections", {{{"sim", "SimHits"}, {"reference", "OriginalHits"}}}}};
  {
    podio::ROOTWriter writer(input);
    for (int event = 0; event < 2; ++event)
      writer.writeFrame(fixtureFrame(event, false, 0), "events");
    writer.finish();
  }
  for (int fault = 0; fault < 4; ++fault) {
    {
      podio::ROOTWriter writer(reference);
      for (int event = 0; event < 2; ++event)
        writer.writeFrame(fixtureFrame(event, true, fault), "events");
      writer.finish();
    }
    bool rejected = false;
    try {
      const auto result = compare(input, reference, config, backend);
      rejected = !result.at("passed").get<bool>();
      if (fault == 0 &&
          (result.at("events") != 2 || result.at("matched_cells") != 1))
        throw std::runtime_error("Fixture denominator mismatch");
    } catch (const std::invalid_argument &) {
      rejected = true;
    }
    if (rejected != (fault != 0))
      throw std::runtime_error("Synthetic comparator corruption check failed");
  }
  config["sha256_tool"] = "/usr/bin/shasum";
  config["input_sha256"] = sha256(input, "/usr/bin/shasum");
  config["reference_sha256"] = sha256(reference, "/usr/bin/shasum");
  verifyHashes(input, reference, config);
  config["input_sha256"] = std::string(64, '0');
  bool badHashRejected = false;
  try {
    verifyHashes(input, reference, config);
  } catch (const std::invalid_argument &) {
    badHashRejected = true;
  }
  if (!badHashRejected)
    throw std::runtime_error("Hash mismatch was accepted");
  config["reference_energy_unit"] = "GeV";
  bool badUnitRejected = false;
  try {
    (void)responseConfig(config, backend);
  } catch (const std::invalid_argument &) {
    badUnitRejected = true;
  }
  if (!badUnitRejected)
    throw std::runtime_error("Wrong reference energy unit was accepted");
  std::cout << "Synthetic utility checks passed: baseline, energy mismatch, "
               "event-ID mismatch, contribution mismatch; no "
               "original-framework run.\n";
}
} // namespace

int main(int argc, char **argv) try {
  if (argc == 4 && std::string(argv[1]) == "--self-test") {
    selfTest(argv[2], argv[3]);
    return 0;
  }
  if (argc != 6)
    throw std::invalid_argument(
        "Usage: nodd_silicon_reference INPUT.root ORIGINAL.root CONFIG.json "
        "SUMMARY.json BACKEND; or --self-test BACKEND DIRECTORY");
  if (std::filesystem::exists(argv[4]))
    throw std::invalid_argument(
        "Comparison summary must use a new output path");
  json config;
  std::ifstream(argv[3]) >> config;
  const auto &producer = config.at("reference_producer");
  const auto repository = producer.at("repository").get<std::string>();
  const auto revision = producer.at("revision").get<std::string>();
  const auto processor = producer.at("processor").get<std::string>();
  if (producer.at("kind") != "original-framework" ||
      producer.at("runtime_identity").get<std::string>().empty() ||
      !isHash(producer.at("steering_sha256")) ||
      !((repository == "iLCSoft/MarlinReco" && revision == marlinPin &&
         processor == "RealisticCaloDigiSilicon") ||
        (repository == "key4hep/k4RecCalorimeter" && revision == key4hepPin &&
         processor == "DigitiserSiliconMip"))) {
    throw std::invalid_argument(
        "Missing or incompatible original-framework provenance");
  }
  if (std::filesystem::equivalent(argv[1], argv[2]))
    throw std::invalid_argument(
        "Input and original output must be distinct files");
  verifyHashes(argv[1], argv[2], config);
  const auto result = compare(argv[1], argv[2], config, argv[5]);
  std::ofstream output(argv[4]);
  output << result.dump(2) << '\n';
  if (!output)
    throw std::runtime_error("Cannot write comparison summary");
  return result.at("passed").get<bool>() ? 0 : 2;
} catch (const std::exception &error) {
  std::cerr << error.what() << '\n';
  return 1;
}
