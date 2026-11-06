// This file is part of the ACTS project.
//
// Copyright (C) 2016 CERN for the benefit of the ACTS project
//
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at https://mozilla.org/MPL/2.0/.

#include <boost/test/unit_test.hpp>
#include <cmath>
#include <functional>
#include <limits>
#include <stdexcept>

#include "EDM4hepReconstructionTestHelpers.hpp"

namespace ActsTests {
namespace {
using namespace ActsExamples;
using namespace ActsCalorimeter;
namespace Fixture = ActsExamples::CalorimeterFixture;
}  // namespace
BOOST_AUTO_TEST_SUITE(CalorimeterEDM4hepReconstructionSuite)
BOOST_AUTO_TEST_CASE(ClusterRelationsTimesAndSeedIds) {
  CalorimeterIoEvent event;
  event.provideFixture();
  event.persistClusters();
  const auto& clusters =
      event.readPodio<edm4hep::ClusterCollection>("CaloClusters");
  const auto& times =
      event.readPodio<podio::UserDataCollection<double>>("CaloClusterTimes");
  const auto& seeds = event.readPodio<podio::UserDataCollection<std::uint64_t>>(
      "CaloClusterSeedCellIds");
  const auto& hits =
      event.readPodio<edm4hep::CalorimeterHitCollection>("CaloHits");
  BOOST_REQUIRE_EQUAL(clusters.size(), 3);
  BOOST_REQUIRE_EQUAL(times.size(), 3);
  BOOST_REQUIRE_EQUAL(seeds.size(), 3);
  BOOST_CHECK_CLOSE(clusters[2].getEnergy(), 0.12, 1e-4);
  BOOST_REQUIRE_EQUAL(clusters[2].hits_size(), 2);
  BOOST_CHECK(clusters[2].getHits(0) == hits[2]);
  BOOST_CHECK(clusters[2].getHits(1) == hits[3]);
  BOOST_CHECK_EQUAL(seeds[2], Fixture::highCellId);
  BOOST_CHECK_CLOSE(times[2], 10. / 3, 1e-4);
  BOOST_CHECK_CLOSE(clusters[2].getPosition().y, 40. / 3, 1e-4);
  BOOST_CHECK(event.board.exists("calo_hits") &&
              event.board.exists("calo_clusters"));
}
BOOST_AUTO_TEST_CASE(RejectMalformedClustersWithoutWritingPartialOutput) {
  const std::vector<std::function<void(CalorimeterClusterContainer&)>> changes{
      [](auto& clusters) { clusters[2].hitIndices.clear(); },
      [](auto& clusters) { clusters[2].hitIndices = {999}; },
      [](auto& clusters) { clusters[2].hitIndices = {2, 2}; },
      [](auto& clusters) { clusters[2].hitIndices = {0}; },
      [](auto& clusters) { clusters[2].energy *= 2; },
      [](auto& clusters) { clusters[2].seedCellId = 7; },
      [](auto& clusters) { clusters[2].time += 1; },
      [](auto& clusters) { clusters[2].position.x() += 1; },
      [](auto& clusters) {
        clusters[2].energy = std::numeric_limits<double>::infinity();
      },
      [](auto& clusters) {
        clusters[2].position.y() = std::numeric_limits<double>::quiet_NaN();
      }};
  for (const auto& change : changes) {
    CalorimeterIoEvent event;
    event.provideFixture();
    auto native = event.read<CalorimeterClusterContainer>("calo_clusters");
    change(native);
    event.write("changed_clusters", std::move(native));
    auto config = Fixture::clusterOutputConfig();
    config.inputClusters = "changed_clusters";
    BOOST_CHECK_THROW(
        EDM4hepCalorimeterClusterOutputConverter{config}.execute(event.context),
        std::invalid_argument);
    BOOST_CHECK(!event.board.exists("CaloClusters") &&
                !event.board.exists("CaloClusterTimes") &&
                !event.board.exists("CaloClusterSeedCellIds"));
  }
}
BOOST_AUTO_TEST_CASE(RejectClusterEnergyOverflowWithRepresentableHits) {
  CalorimeterIoEvent event;
  event.provideFixture(3e39);
  BOOST_CHECK_THROW(event.persistClusters(), std::overflow_error);
  BOOST_CHECK(!event.board.exists("CaloClusters"));
}

BOOST_AUTO_TEST_CASE(RejectWrongPersistentHitMapping) {
  for (bool empty : {false, true}) {
    CalorimeterIoEvent event;
    event.provideFixture();
    edm4hep::CalorimeterHitCollection changed;
    if (!empty) {
      const auto& original =
          event.readPodio<edm4hep::CalorimeterHitCollection>("CaloHits");
      for (std::size_t index = 0; index < original.size(); ++index) {
        const auto hit = original[(index + 1) % original.size()];
        auto copy = changed.create();
        copy.setCellID(hit.getCellID());
        copy.setEnergy(hit.getEnergy());
        copy.setTime(hit.getTime());
        copy.setPosition(hit.getPosition());
      }
    }
    event.writePodio("wrong_hits", std::move(changed));
    auto config = Fixture::clusterOutputConfig();
    config.inputEdmHits = "wrong_hits";
    BOOST_CHECK_THROW(
        EDM4hepCalorimeterClusterOutputConverter{config}.execute(event.context),
        std::invalid_argument);
  }
}
BOOST_AUTO_TEST_CASE(EmptyClusterCollectionsAndMetadata) {
  CalorimeterIoEvent event{emptyCalorimeterFrame()};
  event.provideFixture();
  event.persistClusters();
  BOOST_CHECK(
      event.readPodio<edm4hep::ClusterCollection>("CaloClusters").empty());
  BOOST_CHECK(
      event.readPodio<podio::UserDataCollection<double>>("CaloClusterTimes")
          .empty());
  EDM4hepCalorimeterMetadata{Fixture::metadataConfig()}.execute(event.context);
  const auto& frame = event.read<podio::Frame>("calo_events");
  BOOST_CHECK(frame.getParameter<double>("acts.calo.schemaVersion") == 2);
  BOOST_CHECK(!event.board.exists("events"));
}
BOOST_AUTO_TEST_CASE(MetadataPreservesFrameAndRecordsActualConfiguration) {
  auto frame = Fixture::makeFrame(true);
  frame.putParameter("generator.tag", std::string("existing value"));
  CalorimeterIoEvent event{std::move(frame)};
  event.provideFixture();
  event.persistClusters();
  auto config = Fixture::metadataConfig();
  BOOST_CHECK(EDM4hepCalorimeterMetadata{config}.execute(event.context) ==
              ProcessCode::SUCCESS);
  const auto& output = event.read<podio::Frame>("calo_events");
  BOOST_CHECK(output.getParameter<std::string>("generator.tag") ==
              "existing value");
  BOOST_CHECK_EQUAL(
      output.get<edm4hep::SimCalorimeterHitCollection>("SimCaloHits").size(),
      5);
  BOOST_CHECK(output.getParameter<std::string>("acts.calo.response.status") ==
              "unimplemented skeleton");
  BOOST_CHECK(output.getParameter<std::string>("acts.calo.clustering.status") ==
              "unimplemented skeleton");
  BOOST_CHECK(!output.getParameter<double>("acts.calo.response.energyScale"));
  BOOST_CHECK(
      output.getParameter<std::string>("acts.calo.output.clusterSeedCellIds") ==
      "CaloClusterSeedCellIds");
}
BOOST_AUTO_TEST_CASE(RejectMetadataCollisionsAcrossParameterTypes) {
  for (int type = 0; type < 4; ++type) {
    auto frame = Fixture::makeFrame();
    const std::string key = "acts.calo.old";
    if (type == 0) {
      frame.putParameter(key, 1);
    }
    if (type == 1) {
      frame.putParameter(key, 1.f);
    }
    if (type == 2) {
      frame.putParameter(key, 1.);
    }
    if (type == 3) {
      frame.putParameter(key, std::string("old"));
    }
    CalorimeterIoEvent event{std::move(frame)};
    BOOST_CHECK_THROW(
        EDM4hepCalorimeterMetadata{Fixture::metadataConfig()}.execute(
            event.context),
        std::invalid_argument);
    BOOST_CHECK(!event.board.exists("calo_events"));
  }
}
BOOST_AUTO_TEST_CASE(RejectInvalidOutputAndMetadataConfiguration) {
  auto cluster = Fixture::clusterOutputConfig();
  cluster.outputTimes = cluster.outputClusters;
  BOOST_CHECK_THROW(EDM4hepCalorimeterClusterOutputConverter{cluster},
                    std::invalid_argument);
  cluster = Fixture::clusterOutputConfig();
  cluster.inputEdmHits.clear();
  BOOST_CHECK_THROW(EDM4hepCalorimeterClusterOutputConverter{cluster},
                    std::invalid_argument);
  const std::vector<std::function<void(EDM4hepCalorimeterMetadata::Config&)>>
      changes{[](auto& config) { config.outputFrame = config.inputFrame; },
              [](auto& config) { config.geometryIdentifier.clear(); },
              [](auto& config) { config.clustering.inputHits = "wrong_hits"; },
              [](auto& config) { config.response.outputHits = "wrong_hits"; },
              [](auto& config) {
                config.additional.numbers["acts.calo.schemaVersion"] = {2};
              },
              [](auto& config) {
                config.additional.strings["other.key"] = {"value"};
              },
              [](auto& config) {
                config.additional.numbers["acts.calo.extra"] = {
                    std::numeric_limits<double>::infinity()};
              },
              [](auto& config) {
                config.additional.strings["acts.calo.extra"] = {"value"};
                config.additional.numbers["acts.calo.extra"] = {1};
              }};
  for (const auto& change : changes) {
    auto config = Fixture::metadataConfig();
    change(config);
    BOOST_CHECK_THROW(EDM4hepCalorimeterMetadata{config},
                      std::invalid_argument);
  }
}

BOOST_AUTO_TEST_CASE(ExplicitStoredCellCentreInputAndMalformedPositions) {
  for (int variant = 0; variant < 3; ++variant) {
    edm4hep::SimCalorimeterHitCollection hits;
    edm4hep::CaloHitContributionCollection contributions;
    auto hit = hits.create();
    hit.setCellID(42);
    hit.setEnergy(.1f);
    hit.setPosition({100.f, 20.f, variant == 1
        ? std::numeric_limits<float>::quiet_NaN() : 3.f});
    auto contribution = contributions.create();
    contribution.setEnergy(.1f);
    contribution.setTime(7);
    contribution.setStepPosition({999, 888, 777});
    hit.addToContributions(contribution);
    if (variant == 2) {
      auto repeated = hits.create();
      repeated.setCellID(42);
      repeated.setEnergy(0);
      repeated.setPosition({101, 20, 3});
    }
    podio::Frame frame;
    frame.put(std::move(contributions), "CaloContributions");
    frame.put(std::move(hits), "SimCaloHits");
    CalorimeterIoEvent event{std::move(frame)};
    auto config = Fixture::inputConfig();
    config.cellCentre = {};
    config.useHitPosition = true;
    if (variant == 0) {
      BOOST_CHECK(EDM4hepCalorimeterInputConverter{config}.execute(event.context) ==
                  ProcessCode::SUCCESS);
      const auto& deposits = event.read<SimCalorimeterHitContainer>("calo_deposits");
      BOOST_REQUIRE_EQUAL(deposits.size(), 1);
      BOOST_CHECK(deposits[0].position == Acts::Vector3(100, 20, 3) * Acts::UnitConstants::mm);
    } else {
      BOOST_CHECK_THROW(EDM4hepCalorimeterInputConverter{config}.execute(event.context),
                        std::invalid_argument);
      BOOST_CHECK(!event.board.exists("calo_deposits"));
    }
  }
  auto config = Fixture::inputConfig();
  config.useHitPosition = true;
  BOOST_CHECK_THROW(EDM4hepCalorimeterInputConverter{config}, std::invalid_argument);
}

BOOST_AUTO_TEST_CASE(ExplicitNoiseOnlyOutputHasNoSimulatedTruthLinks) {
  CalorimeterIoEvent event{emptyCalorimeterFrame()};
  EDM4hepCalorimeterInputConverter{Fixture::inputConfig()}.execute(event.context);
  event.write("calo_hits", CalorimeterHitContainer{
      {42, Acts::Vector3{100, 20, 3}, .1 * Acts::UnitConstants::GeV, 0, {}}});
  auto config = Fixture::hitOutputConfig();
  BOOST_CHECK_THROW(EDM4hepCalorimeterOutputConverter{config}.execute(event.context),
                    std::invalid_argument);
  config.allowNoiseOnlyHits = true;
  BOOST_CHECK(EDM4hepCalorimeterOutputConverter{config}.execute(event.context) ==
              ProcessCode::SUCCESS);
  BOOST_REQUIRE_EQUAL(event.readPodio<edm4hep::CalorimeterHitCollection>("CaloHits").size(), 1);
  BOOST_CHECK(event.readPodio<edm4hep::CaloHitSimCaloHitLinkCollection>("CaloLinks").empty());
}

BOOST_AUTO_TEST_CASE(PrototypeMetadataRetainsSourceConfigurationAndLimitations) {
  CalorimeterIoEvent event;
  event.provideFixture();
  event.persistClusters();
  auto config = Fixture::metadataConfig();
  SiliconDigitizationConfig silicon;
  silicon.executable = "test-fixture-backend-not-executed";
  silicon.mipEnergy = 1e-4 * Acts::UnitConstants::GeV;
  config.response.silicon = silicon;
  BOOST_CHECK(EDM4hepCalorimeterMetadata{config}.execute(event.context) == ProcessCode::SUCCESS);
  const auto& frame = event.read<podio::Frame>("calo_events");
  BOOST_CHECK(frame.getParameter<std::string>("acts.calo.response.status") ==
              "PROTOTYPE MarlinReco silicon energy subset");
  BOOST_CHECK(frame.getParameter<std::string>("acts.calo.response.coverage") ==
              "sparse input cells");
  BOOST_CHECK(frame.getParameter<double>("acts.calo.response.mipEnergyGeV") == 1e-4);
  BOOST_CHECK(frame.getParameter<std::string>("acts.calo.clustering.status") ==
              "unimplemented skeleton");
}
BOOST_AUTO_TEST_SUITE_END()
}  // namespace ActsTests
