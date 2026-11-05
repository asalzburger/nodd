// Copyright (C) 2026 CERN for the benefit of the ACTS project
// SPDX-License-Identifier: MPL-2.0
#include <boost/test/unit_test.hpp>

#include <algorithm>
#include <cmath>
#include <limits>
#include <numeric>
#include <stdexcept>

#include "Acts/Definitions/Units.hpp"
#include "ActsExamples/Calorimeter/CalorimeterDigitizationAlgorithm.hpp"
#include "ActsExamples/Calorimeter/SiliconDigitization.hpp"
#include "ActsTests/CommonHelpers/WhiteBoardUtilities.hpp"

using namespace ActsExamples;
using namespace ActsCalorimeter;

namespace {
SiliconDigitizationConfig fixtureConfig() {
  SiliconDigitizationConfig config;
  config.executable = NODD_SILICON_BACKEND;
  // Numerical test scale, not an ODD MIP calibration measurement.
  config.mipEnergy = 1e-4 * Acts::UnitConstants::GeV;
  config.pairEnergyEv = 0;
  return config;
}
const CalorimeterHitContainer &readHits(WhiteBoard &board) {
  static ActsTests::DummySequenceElement source;
  static ReadDataHandle<CalorimeterHitContainer> handle(&source, "ReadHits");
  static const bool initialized = [] {
    handle.initialize("hits");
    return true;
  }();
  (void)initialized;
  AlgorithmContext context{0, 0, board, 0};
  return handle(context);
}
} // namespace

BOOST_AUTO_TEST_CASE(RejectInvalidSiliconConfigurationsAndEnergies) {
  for (const double value :
       {0., -1., std::numeric_limits<double>::infinity()}) {
    auto config = fixtureConfig();
    config.mipEnergy = value;
    BOOST_CHECK_THROW(validateSiliconDigitization(config),
                      std::invalid_argument);
  }
  auto config = fixtureConfig();
  config.thresholdMip = -1;
  BOOST_CHECK_THROW(validateSiliconDigitization(config), std::invalid_argument);
  config = fixtureConfig();
  BOOST_CHECK_THROW(runMarlinSilicon(config, {-1}, 0), std::invalid_argument);
  BOOST_CHECK_THROW(
      runMarlinSilicon(config, {std::numeric_limits<double>::infinity()}, 0),
      std::invalid_argument);
  config.executable = "/usr/bin/false";
  BOOST_CHECK_THROW(runMarlinSilicon(config, {1}, 0), std::runtime_error);
  config = fixtureConfig();
  config.pairEnergyEv = 3.6;
  BOOST_CHECK_THROW(
      runMarlinSilicon(config, {1e12 * Acts::UnitConstants::GeV}, 0),
      std::invalid_argument);
}

BOOST_AUTO_TEST_CASE(OriginalKernelZeroNoiseMipAndDynamicRangeControls) {
  const auto config = fixtureConfig();
  const std::vector<double> mipInputs{0, .25, .5, 1, 12, 2501};
  std::vector<double> energy;
  for (const auto mip : mipInputs) {
    energy.push_back(mip * config.mipEnergy);
  }
  const auto response = runMarlinSilicon(config, energy, 0);
  BOOST_REQUIRE_EQUAL(response.size(), mipInputs.size());
  for (std::size_t index = 0; index < response.size(); ++index) {
    const auto expected = std::min(mipInputs[index], config.dynamicRangeMip);
    BOOST_CHECK_SMALL(response[index] - expected, 3e-4);
  }
}

BOOST_AUTO_TEST_CASE(NoiseOnlyUnsuppressedRmsAndThresholdRate) {
  auto config = fixtureConfig();
  config.noiseMip = .2; // Test-only electronics setting.
  constexpr std::size_t count = 200000;
  const auto response =
      runMarlinSilicon(config, std::vector<double>(count, 0), 13);
  const double mean =
      std::accumulate(response.begin(), response.end(), 0.) / count;
  double sum2 = 0;
  std::size_t accepted = 0;
  constexpr double threshold = .4; // 2 sigma, one-sided Gaussian tail.
  for (const auto value : response) {
    sum2 += (value - mean) * (value - mean);
    accepted += value > threshold;
  }
  const double rms = std::sqrt(sum2 / (count - 1));
  const double probability =
      .5 * std::erfc(threshold / config.noiseMip / std::sqrt(2.));
  const double expected = count * probability;
  const double countSigma = std::sqrt(count * probability * (1 - probability));
  // Six statistical standard deviations; numerical tests, not detector
  // acceptance.
  BOOST_CHECK_SMALL(mean, 5 * config.noiseMip / std::sqrt(count));
  BOOST_CHECK_SMALL(rms - config.noiseMip,
                    5 * config.noiseMip / std::sqrt(2. * (count - 1)));
  BOOST_CHECK_SMALL(static_cast<double>(accepted) - expected, 5 * countSigma);
  BOOST_TEST_MESSAGE("Noise-only fixture N="
                     << count << " mean=" << mean << " rms=" << rms
                     << " threshold accepted=" << accepted
                     << " expected=" << expected);
  BOOST_CHECK(runMarlinSilicon(config, std::vector<double>(100, 0), 13) ==
              std::vector<double>(response.begin(), response.begin() + 100));
  BOOST_CHECK(runMarlinSilicon(config, std::vector<double>(100, 0), 14) !=
              std::vector<double>(response.begin(), response.begin() + 100));
}

BOOST_AUTO_TEST_CASE(OriginalSiliconPairStatisticsControl) {
  auto config = fixtureConfig();
  config.pairEnergyEv = 3.6;
  constexpr std::size_t count = 30000;
  const auto response = runMarlinSilicon(
      config, std::vector<double>(count, config.mipEnergy), 27);
  const double mean =
      std::accumulate(response.begin(), response.end(), 0.) / count;
  double sum2 = 0;
  for (const auto value : response) {
    sum2 += (value - mean) * (value - mean);
  }
  const double expectedRms =
      std::sqrt(config.pairEnergyEv /
                (1e9 * config.mipEnergy / Acts::UnitConstants::GeV));
  const double rms = std::sqrt(sum2 / (count - 1));
  BOOST_CHECK_SMALL(mean - 1, 6 * expectedRms / std::sqrt(count));
  BOOST_CHECK_SMALL(rms - expectedRms,
                    6 * expectedRms / std::sqrt(2. * (count - 1)));
}

BOOST_AUTO_TEST_CASE(
    AlgorithmSumsCellsAppliesStrictThresholdAndPreservesTruth) {
  auto silicon = fixtureConfig();
  silicon.thresholdMip = .5;
  WhiteBoard board;
  AlgorithmContext context{0, 31, board, 0};
  const Acts::Vector3 position{10, 20, 30};
  const std::uint64_t highId = 0xfedcba9876543210ULL;
  ActsTests::addToWhiteBoard(
      "deposits",
      SimCalorimeterHitContainer{{highId, position, .25 * silicon.mipEnergy, 1},
                                 {highId, position, .75 * silicon.mipEnergy, 3},
                                 {42, position, .5 * silicon.mipEnergy, 5}},
      board);
  CalorimeterDigitizationAlgorithm::Config config{"deposits", "hits"};
  config.silicon = silicon;
  BOOST_CHECK(CalorimeterDigitizationAlgorithm(config).execute(context) ==
              ProcessCode::SUCCESS);
  const auto &hits = readHits(board);
  BOOST_REQUIRE_EQUAL(hits.size(), 1);
  BOOST_CHECK_EQUAL(hits[0].cellId, highId);
  BOOST_CHECK_CLOSE(hits[0].energy / silicon.mipEnergy, 1, 1e-4);
  BOOST_CHECK_CLOSE(hits[0].time, 2.5, 1e-10);
  BOOST_CHECK(hits[0].sourceIndices == std::vector<std::size_t>({0, 1}));
}

BOOST_AUTO_TEST_CASE(ExplicitChannelInventoryGeneratesNoiseWithoutDeposits) {
  auto silicon = fixtureConfig();
  silicon.noiseMip = 1;
  silicon.thresholdMip = 0;
  CalorimeterDigitizationAlgorithm::Config config{"deposits", "hits"};
  config.silicon = silicon;
  for (std::uint64_t index = 0; index < 1000; ++index) {
    config.channels.push_back(
        {index, Acts::Vector3{static_cast<double>(index), 0, 0}});
  }
  WhiteBoard board;
  AlgorithmContext context{0, 7, board, 0};
  ActsTests::addToWhiteBoard("deposits", SimCalorimeterHitContainer{}, board);
  BOOST_CHECK(CalorimeterDigitizationAlgorithm(config).execute(context) ==
              ProcessCode::SUCCESS);
  const auto &hits = readHits(board);
  BOOST_CHECK_GT(hits.size(), 400);
  BOOST_CHECK_LT(hits.size(), 600);
  for (const auto &hit : hits) {
    BOOST_CHECK(hit.sourceIndices.empty());
    BOOST_CHECK_EQUAL(hit.time, 0);
    BOOST_CHECK_GT(hit.energy, 0);
  }
  config.channels.push_back(config.channels.front());
  BOOST_CHECK_THROW(CalorimeterDigitizationAlgorithm{config},
                    std::invalid_argument);
}

BOOST_AUTO_TEST_CASE(StrictThresholdUsesUpstreamFloatPrecision) {
  auto silicon = fixtureConfig();
  silicon.thresholdMip = .6;
  WhiteBoard board;
  AlgorithmContext context{0, 0, board, 0};
  ActsTests::addToWhiteBoard(
      "deposits",
      SimCalorimeterHitContainer{
          {42, Acts::Vector3::Zero(), .6 * silicon.mipEnergy, 0}},
      board);
  CalorimeterDigitizationAlgorithm::Config config{"deposits", "hits"};
  config.silicon = silicon;
  BOOST_CHECK(CalorimeterDigitizationAlgorithm(config).execute(context) ==
              ProcessCode::SUCCESS);
  BOOST_CHECK(readHits(board).empty());
}

BOOST_AUTO_TEST_CASE(UnknownChannelAndInconsistentPositionFailWithoutOutput) {
  auto silicon = fixtureConfig();
  CalorimeterDigitizationAlgorithm::Config config{"deposits", "hits"};
  config.silicon = silicon;
  config.channels.push_back({42, Acts::Vector3::Zero()});
  for (const auto id : {std::uint64_t{7}, std::uint64_t{42}}) {
    WhiteBoard board;
    AlgorithmContext context{0, 0, board, 0};
    ActsTests::addToWhiteBoard(
        "deposits",
        SimCalorimeterHitContainer{
            {id, Acts::Vector3{1, 0, 0}, silicon.mipEnergy, 0}},
        board);
    BOOST_CHECK_THROW(CalorimeterDigitizationAlgorithm(config).execute(context),
                      std::invalid_argument);
    BOOST_CHECK(!board.exists("hits"));
  }
}
