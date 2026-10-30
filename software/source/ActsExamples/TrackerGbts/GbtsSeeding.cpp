// nODD DES-041 PROTOTYPE adapter for native ACTS Core GBTS.
//
// Scheduling/space-point plumbing adapted from ACTS355ea684
// Examples/Algorithms/TrackFinding/src/GraphBasedSeedingAlgorithm.cpp.
// Copyright (C) 2016 CERN for the benefit of the ACTS project.
// This Source Code Form is subject to the Mozilla Public License, v. 2.0.
// See https://mozilla.org/MPL/2.0/.
// GBTS graph building, cellular automaton, filtering and seed extraction remain
// in the linked ACTS Core implementation; no seeding algorithm is copied here.
#include "Acts/Definitions/Units.hpp"
#include "Acts/EventData/SeedContainer.hpp"
#include "Acts/EventData/SpacePointContainer.hpp"
#include "Acts/Seeding/GbtsGeometry.hpp"
#include "Acts/Seeding/GbtsTrackingFilter.hpp"
#include "Acts/Seeding/GraphBasedTrackSeeder.hpp"
#include "ActsExamples/EventData/IndexSourceLink.hpp"
#include "ActsExamples/Framework/AlgorithmContext.hpp"
#include "ActsExamples/Framework/DataHandle.hpp"
#include "ActsExamples/Framework/IAlgorithm.hpp"
#include <nlohmann/json.hpp>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <algorithm>
#include <array>
#include <fstream>
#include <map>
#include <mutex>
#include <numeric>
#include <sstream>
#include <stdexcept>
#include <string>

namespace py=pybind11;
using namespace ActsExamples;
namespace GB=Acts::Experimental;
using Json=nlohmann::json;
static_assert(PYBIND11_INTERNALS_VERSION == NODD_EXPECTED_PYBIND11_INTERNALS_VERSION);
namespace {
Json readJson(const std::string& path) {
  std::ifstream in(path); if(!in) throw std::runtime_error("Cannot open GBTS config "+path);
  return Json::parse(in);
}
template<class F> void readCsv(const std::string& path, F callback) {
  std::ifstream in(path); if(!in) throw std::runtime_error("Cannot open GBTS input "+path);
  std::string line;
  while(std::getline(in,line)) {
    std::replace(line.begin(),line.end(),',',' '); std::istringstream row(line);
    callback(row);
    if(!row || row.peek()!=std::char_traits<char>::eof()) throw std::runtime_error("Malformed GBTS CSV "+path);
  }
}
GB::GraphBasedTrackSeeder::Config seedConfig(const Json& cfg) {
  GB::GraphBasedTrackSeeder::Config c;
  for(const auto& [key,value]:cfg.items()) {
#define FIELD(name) if(key==#name) { value.get_to(c.name); continue; }
    FIELD(beamSpotCorrection) FIELD(useStripConnections) FIELD(useClusterWidthCuts)
    FIELD(matchBeforeCreate) FIELD(validateTriplets) FIELD(useAdaptiveCuts) FIELD(addTriplets)
    FIELD(tauRatioCut) FIELD(tauRatioPrecut) FIELD(tauRatioCorr) FIELD(tauRatioCorrStrip)
    FIELD(maxAbsEtaAddTriplets) FIELD(nMaxPhiSlice) FIELD(minPt) FIELD(tripletPtFraction)
    FIELD(useEtaBinning) FIELD(doubletFilterRZ) FIELD(nMaxEdges) FIELD(minDeltaRadius)
    FIELD(maxAbsTau) FIELD(d0Max) FIELD(cutDPhiMax) FIELD(cutDCurvMax) FIELD(minZ0) FIELD(maxZ0)
    FIELD(tuningPt) FIELD(maxCurvatureHighEta) FIELD(maxCurvatureLowEta) FIELD(curvatureSplitAbsTau)
    FIELD(phiWindowSplitDeltaRadius) FIELD(phiWindowNearOffset) FIELD(phiWindowNearSlope)
    FIELD(phiWindowFarOffset) FIELD(phiWindowFarSlope) FIELD(matchBeforeCreateMaxEdges)
    FIELD(z0HistogramMaxBarrelOrder) FIELD(matchBeforeCreateMaxBarrelOrder) FIELD(z0Resolution)
    FIELD(maxOuterRadius) FIELD(calibrateStrips) FIELD(maxStripLengthFraction) FIELD(ccaMaxIterations)
    FIELD(minSeedLevel) FIELD(minSplitSeedSize) FIELD(maxSplitSeedSize) FIELD(edgeMaskMinEta)
    FIELD(hitShareThreshold) FIELD(maxSeedSplitEta) FIELD(maxInvRadDiff) FIELD(maxEndcapClusterWidth)
    FIELD(moduleHalfLengthY) FIELD(moduleEdgeTolerance) FIELD(tauLutBinWidth) FIELD(phiIndexMargin)
    FIELD(phiSortBuckets)
#undef FIELD
    throw std::invalid_argument("Unknown GBTS seed finder field "+key);
  }
  if(c.useClusterWidthCuts || c.useStripConnections) throw std::invalid_argument("Gaussian pixel GBTS forbids cluster/strip cuts");
  return c;
}
GB::GbtsTrackingFilter::Config filterConfig(const Json& cfg) {
  GB::GbtsTrackingFilter::Config c;
  for(const auto& [key,value]:cfg.items()) {
#define FIELD(name) if(key==#name) { value.get_to(c.name); continue; }
    FIELD(sigmaMS) FIELD(radLen) FIELD(sigmaX) FIELD(sigmaY) FIELD(sigmaXStrip)
    FIELD(weightX) FIELD(weightY) FIELD(maxDChi2X) FIELD(maxDChi2Y) FIELD(addHit)
    FIELD(maxCurvature) FIELD(maxZ0) FIELD(initialVarianceX) FIELD(initialVarianceY)
#undef FIELD
    throw std::invalid_argument("Unknown GBTS filter field "+key);
  }
  return c;
}
Json seedValues(const GB::GraphBasedTrackSeeder::Config& c) {
  Json out;
  out["addTriplets"]=c.addTriplets;
  out["beamSpotCorrection"]=c.beamSpotCorrection;
  out["calibrateStrips"]=c.calibrateStrips;
  out["ccaMaxIterations"]=c.ccaMaxIterations;
  out["curvatureSplitAbsTau"]=c.curvatureSplitAbsTau;
  out["cutDCurvMax"]=c.cutDCurvMax;
  out["cutDPhiMax"]=c.cutDPhiMax;
  out["d0Max"]=c.d0Max;
  out["doubletFilterRZ"]=c.doubletFilterRZ;
  out["edgeMaskMinEta"]=c.edgeMaskMinEta;
  out["hitShareThreshold"]=c.hitShareThreshold;
  out["matchBeforeCreate"]=c.matchBeforeCreate;
  out["matchBeforeCreateMaxBarrelOrder"]=c.matchBeforeCreateMaxBarrelOrder;
  out["matchBeforeCreateMaxEdges"]=c.matchBeforeCreateMaxEdges;
  out["maxAbsEtaAddTriplets"]=c.maxAbsEtaAddTriplets;
  out["maxAbsTau"]=c.maxAbsTau;
  out["maxCurvatureHighEta"]=c.maxCurvatureHighEta;
  out["maxCurvatureLowEta"]=c.maxCurvatureLowEta;
  out["maxEndcapClusterWidth"]=c.maxEndcapClusterWidth;
  out["maxInvRadDiff"]=c.maxInvRadDiff;
  out["maxOuterRadius"]=c.maxOuterRadius;
  out["maxSeedSplitEta"]=c.maxSeedSplitEta;
  out["maxSplitSeedSize"]=c.maxSplitSeedSize;
  out["maxStripLengthFraction"]=c.maxStripLengthFraction;
  out["maxZ0"]=c.maxZ0;
  out["minDeltaRadius"]=c.minDeltaRadius;
  out["minPt"]=c.minPt;
  out["minSeedLevel"]=c.minSeedLevel;
  out["minSplitSeedSize"]=c.minSplitSeedSize;
  out["minZ0"]=c.minZ0;
  out["moduleEdgeTolerance"]=c.moduleEdgeTolerance;
  out["moduleHalfLengthY"]=c.moduleHalfLengthY;
  out["nMaxEdges"]=c.nMaxEdges;
  out["nMaxPhiSlice"]=c.nMaxPhiSlice;
  out["phiIndexMargin"]=c.phiIndexMargin;
  out["phiSortBuckets"]=c.phiSortBuckets;
  out["phiWindowFarOffset"]=c.phiWindowFarOffset;
  out["phiWindowFarSlope"]=c.phiWindowFarSlope;
  out["phiWindowNearOffset"]=c.phiWindowNearOffset;
  out["phiWindowNearSlope"]=c.phiWindowNearSlope;
  out["phiWindowSplitDeltaRadius"]=c.phiWindowSplitDeltaRadius;
  out["tauLutBinWidth"]=c.tauLutBinWidth;
  out["tauRatioCorr"]=c.tauRatioCorr;
  out["tauRatioCorrStrip"]=c.tauRatioCorrStrip;
  out["tauRatioCut"]=c.tauRatioCut;
  out["tauRatioPrecut"]=c.tauRatioPrecut;
  out["tripletPtFraction"]=c.tripletPtFraction;
  out["tuningPt"]=c.tuningPt;
  out["useAdaptiveCuts"]=c.useAdaptiveCuts;
  out["useClusterWidthCuts"]=c.useClusterWidthCuts;
  out["useEtaBinning"]=c.useEtaBinning;
  out["useStripConnections"]=c.useStripConnections;
  out["validateTriplets"]=c.validateTriplets;
  out["z0HistogramMaxBarrelOrder"]=c.z0HistogramMaxBarrelOrder;
  out["z0Resolution"]=c.z0Resolution;
  return out;
}

Json filterValues(const GB::GbtsTrackingFilter::Config& c) {
  Json out;
  out["addHit"]=c.addHit;
  out["initialVarianceX"]=c.initialVarianceX;
  out["initialVarianceY"]=c.initialVarianceY;
  out["maxCurvature"]=c.maxCurvature;
  out["maxDChi2X"]=c.maxDChi2X;
  out["maxDChi2Y"]=c.maxDChi2Y;
  out["maxZ0"]=c.maxZ0;
  out["radLen"]=c.radLen;
  out["sigmaMS"]=c.sigmaMS;
  out["sigmaX"]=c.sigmaX;
  out["sigmaXStrip"]=c.sigmaXStrip;
  out["sigmaY"]=c.sigmaY;
  out["weightX"]=c.weightX;
  out["weightY"]=c.weightY;
  return out;
}

}

class GbtsSeeding final:public IAlgorithm {
 public:
  GbtsSeeding(const std::string& directory, Acts::Logging::Level level)
   :IAlgorithm("NoddNativeGbts",Acts::getDefaultLogger("NoddNativeGbts",level)) {
    const auto cfg=readJson(directory+"/config.json");
    input.initialize(cfg.at("input_spacepoints").get<std::string>());
    output.initialize(cfg.at("output_seeds").get<std::string>());
    std::vector<GB::GbtsLayerDescription> layers;
    readCsv(directory+"/layers.csv",[&](auto& row) {
      GB::GbtsLayerDescription l;unsigned type;
      row>>l.id>>type>>l.refCoord>>l.layerThickness>>l.minBound>>l.maxBound;
      if(type>1) throw std::invalid_argument("Invalid GBTS layer type");
      l.type=static_cast<GB::GbtsLayerType>(type);l.technology=GB::GbtsLayerTechnology::Pixel;
      layers.push_back(l);
    });
    std::vector<GB::GbtsLayerConnection> links;
    readCsv(directory+"/connections.csv",[&](auto& row) {
      GB::GbtsLayerConnection link;row>>link.src>>link.dst;links.push_back(link);
    });
    const auto zrange=cfg.at("z0_range_mm").get<std::array<float,2>>();
    geometry=std::make_shared<GB::GbtsGeometry>(layers,links,cfg.at("eta_bin_width").get<float>(),GB::GbtsZ0Range{zrange[0],zrange[1]},logger());
    readCsv(directory+"/mapping.csv",[&](auto& row) {
      std::uint64_t id;GB::GbtsExperimentLayerId layer;row>>id>>layer;
      const auto index=geometry->layerIndex(layer);
      if(!index || !mapping.emplace(id,*index).second) throw std::invalid_argument("Invalid/duplicate GBTS sensor mapping");
    });
    auto seedCfg=seedConfig(cfg.at("seed_finder"));
    auto filterCfg=filterConfig(cfg.at("tracking_filter"));
    effectiveConfiguration=cfg;effectiveConfiguration["seed_finder"]=seedValues(seedCfg);
    effectiveConfiguration["tracking_filter"]=filterValues(filterCfg);
    finder=std::make_unique<GB::GraphBasedTrackSeeder>(GB::GraphBasedTrackSeeder::DerivedConfig(seedCfg),geometry,logger().cloneWithSuffix("Finder"));
    filter=std::make_unique<GB::GbtsTrackingFilter>(filterCfg,geometry,logger().cloneWithSuffix("Filter"));
    const auto etarange=cfg.at("eta_range").get<std::array<double,2>>();
    roi=std::make_unique<GB::GbtsRoiDescriptor>(etarange[0],etarange[1],zrange[0],zrange[1]);
    bField=cfg.at("b_field_T").get<float>()*Acts::UnitConstants::T;
    seedCap=cfg.at("max_seeds_per_event").get<unsigned>();
    layerNodes.assign(geometry->numLayers(),0);
    nBinGroups=geometry->binGroups().size();
  }
  ProcessCode execute(const AlgorithmContext& ctx) const override {
    const auto& points=input(ctx);auto storage=finder->makeNodeStorage();
    std::vector<unsigned long long> nodes(geometry->numLayers(),0);
    for(const auto& point:points) {
      const auto& links=point.sourceLinks();
      if(links.size()!=1) throw std::runtime_error("Pixel GBTS expects exactly one source link per measured point");
      const auto& link=links.front().get<IndexSourceLink>();
      const auto found=mapping.find(link.geometryId().value());
      if(found==mapping.end()) throw std::runtime_error("Measured space point has no Gen3 pixel GBTS mapping");
      storage.insert(point.index(),point.x(),point.y(),point.z(),found->second);++nodes.at(found->second);
    }
    storage.finalize();
    Acts::SeedContainer seeds;seeds.assignSpacePointContainer(points);
    finder->createSeeds(storage,*roi,*filter,GB::GraphBasedTrackSeeder::Options{.bFieldInZ=bField},seeds);
    const auto produced=seeds.size();
    if(seedCap && seeds.size()>seedCap) {
      std::vector<std::uint32_t> order(seeds.size());std::iota(order.begin(),order.end(),0);
      std::stable_sort(order.begin(),order.end(),[&](auto a,auto b){return seeds.at(a).quality()>seeds.at(b).quality();});
      Acts::SeedContainer retained;retained.assignSpacePointContainer(points);
      for(unsigned i=0;i<seedCap;++i) {
        const auto original=seeds.at(order[i]);auto kept=retained.createSeed();
        kept.assignSpacePointIndices(original.spacePointIndices());kept.quality()=original.quality();
      }
      seeds=std::move(retained);
    }
    {std::lock_guard lock(mutex);++events;inputPoints+=points.size();producedSeeds+=produced;retainedSeeds+=seeds.size();
      for(std::size_t i=0;i<nodes.size();++i) layerNodes[i]+=nodes[i];}
    output(ctx,std::move(seeds));return ProcessCode::SUCCESS;
  }
  std::string effectiveConfigurationJson() const { return effectiveConfiguration.dump(); }
  py::dict statistics() const {
    std::lock_guard lock(mutex);py::dict d;
    d["events"]=events;d["input_spacepoints"]=inputPoints;d["mapped_spacepoints"]=inputPoints;
    d["produced_seeds"]=producedSeeds;d["retained_seeds"]=retainedSeeds;d["capped_seeds"]=producedSeeds-retainedSeeds;
    d["mapped_sensors"]=mapping.size();d["logical_pixel_layers"]=geometry->numLayers();d["eta_bins"]=geometry->numBins();
    d["compatible_eta_bin_groups"]=nBinGroups;d["spacepoints_by_layer_index"]=layerNodes;return d;
  }
  // Native-core helper for explicitly synthetic unit fixtures only. Pipeline
  // input remains the framework's measured SpacePointContainer above.
  std::vector<std::vector<std::uint32_t>> testPoints(const std::vector<std::array<double,4>>& positions) const {
    Acts::SpacePointContainer points(Acts::SpacePointColumns::X|Acts::SpacePointColumns::Y|Acts::SpacePointColumns::Z);auto storage=finder->makeNodeStorage();
    for(const auto& p:positions) {
      const auto index=geometry->layerIndex(static_cast<GB::GbtsExperimentLayerId>(p[3]));
      if(!index) throw std::invalid_argument("Unknown fixture physical layer");
      auto point=points.createSpacePoint();point.x()=p[0];point.y()=p[1];point.z()=p[2];
      storage.insert(point.index(),p[0],p[1],p[2],*index);
    }
    storage.finalize();Acts::SeedContainer seeds;seeds.assignSpacePointContainer(points);
    finder->createSeeds(storage,*roi,*filter,GB::GraphBasedTrackSeeder::Options{.bFieldInZ=bField},seeds);
    std::vector<std::vector<std::uint32_t>> result;
    for(const auto& seed:seeds) {const auto indices=seed.spacePointIndices();result.emplace_back(indices.begin(),indices.end());}
    return result;
  }
 private:
  ReadDataHandle<Acts::SpacePointContainer> input{this,"MeasuredPixelSpacePoints"};
  WriteDataHandle<Acts::SeedContainer> output{this,"NativeGbtsSeeds"};
  std::shared_ptr<GB::GbtsGeometry> geometry;
  std::map<std::uint64_t,GB::GbtsLayerIndex> mapping;
  std::unique_ptr<GB::GraphBasedTrackSeeder> finder;
  std::unique_ptr<GB::GbtsTrackingFilter> filter;
  std::unique_ptr<GB::GbtsRoiDescriptor> roi;
  Json effectiveConfiguration;
  float bField{};unsigned seedCap{};std::size_t nBinGroups{};
  mutable std::mutex mutex;
  mutable unsigned long long events=0,inputPoints=0,producedSeeds=0,retainedSeeds=0;
  mutable std::vector<unsigned long long> layerNodes;
};
PYBIND11_MODULE(nodd_gbts,m) {
  py::class_<GbtsSeeding,IAlgorithm,std::shared_ptr<GbtsSeeding>>(m,"GbtsSeeding")
    .def(py::init<const std::string&,Acts::Logging::Level>())
    .def("statistics",&GbtsSeeding::statistics)
    .def("effective_configuration_json",&GbtsSeeding::effectiveConfigurationJson)
    .def("_test_points",&GbtsSeeding::testPoints);
  m.attr("acts_source_revision")="355ea68493b326956756c9386d2fd9eaf9328568";
  m.attr("pybind11_internals_version")=PYBIND11_INTERNALS_VERSION;
  m.attr("pybind11_version")=std::to_string(PYBIND11_VERSION_MAJOR)+"."+std::to_string(PYBIND11_VERSION_MINOR)+"."+std::to_string(PYBIND11_VERSION_MICRO);
}
