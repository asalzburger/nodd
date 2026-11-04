// This file is part of the ACTS project.
//
// Copyright (C) 2016 CERN for the benefit of the ACTS project
//
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at https://mozilla.org/MPL/2.0/.

#include <podio/ROOTReader.h>
#include <podio/ROOTWriter.h>

#include <cmath>
#include <filesystem>
#include <iostream>
#include <memory>
#include <stdexcept>

#include "Acts/Definitions/Units.hpp"
#include "ActsExamples/Framework/Sequencer.hpp"
#include "ActsExamples/Io/Podio/PodioReader.hpp"
#include "ActsExamples/Io/Podio/PodioWriter.hpp"
#include "ReconstructionFixture.hpp"

namespace {
using namespace ActsExamples;
namespace Fixture = CalorimeterFixture;
/// Supplies fixed synthetic test values; deliberately bypasses both skeletons.
/// This is a persistence fixture, not a calorimeter simulation.
class FixtureProvider final : public IAlgorithm {
 public:
  FixtureProvider()
      : IAlgorithm("CalorimeterFixtureProvider",
                   Acts::getDefaultLogger("CalorimeterFixtureProvider",
                                          Acts::Logging::INFO)) {
    m_hits.initialize("calo_hits");
    m_clusters.initialize("calo_clusters");
  }
  ProcessCode execute(const AlgorithmContext& context) const override {
    m_hits(context, Fixture::preparedHits());
    m_clusters(context, Fixture::preparedClusters());
    return ProcessCode::SUCCESS;
  }

 private:
  WriteDataHandle<ActsCalorimeter::CalorimeterHitContainer> m_hits{this,
                                                                   "Hits"};
  WriteDataHandle<ActsCalorimeter::CalorimeterClusterContainer> m_clusters{
      this, "Clusters"};
};

void require(bool condition, const char* message) {
  if (!condition) {
    throw std::runtime_error(message);
  }
}
void checkOutput(const std::filesystem::path& path) {
  podio::ROOTReader reader;
  reader.openFile(path.string());
  require(reader.getEntries("events") == 3,
          "Unexpected calorimeter event count");
  for (unsigned int event = 0; event < 3; ++event) {
    podio::Frame frame = reader.readEntry("events", event);
    const auto& hits = frame.get<edm4hep::CalorimeterHitCollection>("CaloHits");
    const auto& links =
        frame.get<edm4hep::CaloHitSimCaloHitLinkCollection>("CaloLinks");
    const auto& simHits =
        frame.get<edm4hep::SimCalorimeterHitCollection>("SimCaloHits");
    const auto& clusters =
        frame.get<edm4hep::ClusterCollection>("CaloClusters");
    const auto& times =
        frame.get<podio::UserDataCollection<double>>("CaloClusterTimes");
    const auto& seeds = frame.get<podio::UserDataCollection<std::uint64_t>>(
        "CaloClusterSeedCellIds");
    require(hits.size() == 4 && links.size() == 5 && simHits.size() == 5 &&
                clusters.size() == 3 && times.size() == 3 && seeds.size() == 3,
            "Unexpected persistent collection size");
    require(hits[0].getCellID() == 7 && hits[1].getCellID() == 42 &&
                hits[2].getCellID() == Fixture::highCellId &&
                hits[3].getCellID() == Fixture::highCellId + 1 &&
                std::abs(hits[2].getEnergy() - 0.08) < 1e-7 &&
                std::abs(hits[2].getTime() - 4) < 1e-6 &&
                hits[2].getPosition().x == 1500,
            "Unexpected supplied persistent hit values");
    double weightSum = 0;
    for (const auto& link : links) {
      require(link.getFrom().isAvailable() && link.getTo().isAvailable() &&
                  link.getFrom().getCellID() == link.getTo().getCellID(),
              "Broken truth relation");
      if (link.getFrom().getCellID() == Fixture::highCellId) {
        weightSum += link.getWeight();
        const double expected =
            link.getTo().getObjectID().index == 0 ? 0.75 : 0.25;
        require(std::abs(link.getWeight() - expected) < 1e-6,
                "Unexpected truth weight");
      }
      for (const auto& contribution : link.getTo().getContributions()) {
        require(contribution.isAvailable() &&
                    contribution.getParticle().isAvailable() &&
                    contribution.getParticle().getPDG() == 211,
                "Broken contribution/particle relation");
      }
    }
    require(std::abs(weightSum - 1) < 1e-6, "Truth weights do not sum to one");
    require(std::abs(clusters[0].getEnergy() - 0.06) < 1e-7 &&
                std::abs(clusters[1].getEnergy() - 0.04) < 1e-7 &&
                std::abs(clusters[2].getEnergy() - 0.12) < 1e-7 &&
                clusters[0].getHits(0) == hits[0] &&
                clusters[1].getHits(0) == hits[1] &&
                clusters[2].hits_size() == 2 &&
                clusters[2].getHits(0) == hits[2] &&
                clusters[2].getHits(1) == hits[3],
            "Broken cluster energy/hit relations");
    require(
        seeds[0] == 7 && seeds[1] == 42 && seeds[2] == Fixture::highCellId &&
            std::abs(times[0] - 6) < 1e-6 && std::abs(times[1] - 2) < 1e-6 &&
            std::abs(times[2] - 10. / 3) < 1e-6 &&
            std::abs(clusters[2].getPosition().y - 40. / 3) < 1e-5,
        "Broken cluster sidecars or centre");
    require(
        frame.getParameter<std::string>("generator.tag") == "synthetic" &&
            frame.getParameter<double>("acts.calo.schemaVersion") == 2 &&
            frame.getParameter<std::string>("acts.calo.response.status") ==
                "unimplemented skeleton" &&
            frame.getParameter<std::string>("acts.calo.clustering.status") ==
                "unimplemented skeleton" &&
            frame.getParameter<std::string>("acts.calo.output.clusterTimes") ==
                "CaloClusterTimes",
        "Missing or incorrect reconstruction metadata");
  }
}
}  // namespace

int main(int argc, char* argv[]) {
  if (argc != 2) {
    std::cerr << "Usage: " << argv[0] << " OUTPUT_DIRECTORY\n";
    return 1;
  }
  const std::filesystem::path directory(argv[1]);
  std::filesystem::create_directories(directory);
  const auto inputPath = directory / "calorimeter-input.root";
  const auto outputPath = directory / "calorimeter-output.root";
  {
    podio::ROOTWriter writer(inputPath.string());
    for (int event = 0; event < 3; ++event) {
      auto frame = Fixture::makeFrame(true);
      frame.putParameter("generator.tag", std::string("synthetic"));
      writer.writeFrame(frame, "events");
    }
    writer.finish();
  }
  Sequencer::Config sequence;
  sequence.events = 3;
  sequence.numThreads = 1;
  sequence.outputDir = directory.string();
  Sequencer sequencer(sequence);
  PodioReader::Config reader;
  reader.inputPath = inputPath;
  sequencer.addReader(
      std::make_shared<PodioReader>(reader, Acts::Logging::INFO));
  auto metadata = Fixture::metadataConfig();
  sequencer.addAlgorithm(
      std::make_shared<EDM4hepCalorimeterInputConverter>(metadata.input));
  sequencer.addAlgorithm(std::make_shared<FixtureProvider>());
  auto hitConverter =
      std::make_shared<EDM4hepCalorimeterOutputConverter>(metadata.hitOutput);
  auto clusterConverter =
      std::make_shared<EDM4hepCalorimeterClusterOutputConverter>(
          metadata.clusterOutput);
  sequencer.addAlgorithm(hitConverter);
  sequencer.addAlgorithm(clusterConverter);
  auto collections = hitConverter->collections();
  const auto clusterCollections = clusterConverter->collections();
  collections.insert(collections.end(), clusterCollections.begin(),
                     clusterCollections.end());

  sequencer.addAlgorithm(
      std::make_shared<EDM4hepCalorimeterMetadata>(metadata));
  PodioWriter::Config writer;
  writer.inputFrame = metadata.outputFrame;
  writer.outputPath = outputPath.string();
  writer.category = "events";
  writer.collections = collections;
  sequencer.addWriter(
      std::make_shared<PodioWriter>(writer, Acts::Logging::INFO));
  const auto result = sequencer.run();
  if (result != 0) {
    return result;
  }
  checkOutput(outputPath);
  std::cout
      << "Calorimeter I/O fixture ROOT round trip passed for three events\n";
  return 0;
}
