// Isolated PROTOTYPE observation only: native algorithms perform all physics.
#include "ActsExamples/Framework/IAlgorithm.hpp"
#include "ActsExamples/Framework/AlgorithmContext.hpp"
#include "ActsExamples/Framework/DataHandle.hpp"
#include "ActsExamples/EventData/SimParticle.hpp"
#include "ActsExamples/EventData/SimHit.hpp"
#include "ActsExamples/EventData/Measurement.hpp"
#include "ActsExamples/EventData/Cluster.hpp"
#include "ActsExamples/EventData/TruthMatching.hpp"
#include "ActsExamples/EventData/ProtoTrack.hpp"
#include "ActsExamples/EventData/Track.hpp"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <TFile.h>
#include <TTree.h>
#include <mutex>
#include <map>
#include <cmath>
#include <set>
#include <algorithm>
#include <iostream>
#include "ActsExamples/Geant4/Geant4Manager.hpp"
#include <G4RunManager.hh>
#include <G4VUserPhysicsList.hh>
namespace py=pybind11;
using namespace ActsExamples;
static_assert(PYBIND11_INTERNALS_VERSION == NODD_EXPECTED_PYBIND11_INTERNALS_VERSION);
// Adapted from ACTS355ea684 Examples/Algorithms/TruthTracking/.../TruthTrackFinder.cpp.
// Repair the redundant map.nth lookup; preserve native association/time ordering.
std::vector<Index> orderMeasurements(const std::vector<Index>& measurementIndices,
    const std::map<Index,Index>& association,const std::vector<double>& times) {
  std::vector<Index> indices;
  std::set<Index> seen;
  for(const auto index:measurementIndices) if(seen.insert(index).second) indices.push_back(index);
  std::stable_sort(indices.begin(),indices.end(),[&](Index a,Index b) {
    return times.at(association.at(a)) < times.at(association.at(b));
  });
  return indices;
}
class CorrectTruthProtoTracks final : public IAlgorithm {
 public:
  CorrectTruthProtoTracks(): IAlgorithm("CorrectTruthProtoTracks",Acts::getDefaultLogger("CorrectTruthProtoTracks",Acts::Logging::WARNING)) {
    particles.initialize("particles_digitized_selected");map.initialize("particle_measurements_map");
    simhits.initialize("simhits");associations.initialize("measurement_simhits_map");
    output.initialize("truth_particle_tracks_corrected");
  }
  ProcessCode execute(const AlgorithmContext& ctx) const override {
    const auto& pm=map(ctx);const auto& ms=associations(ctx);const auto& hs=simhits(ctx);
    std::vector<double> times;times.reserve(hs.size());
    for(const auto& hit:hs) times.push_back(hit.time());
    ProtoTrackContainer result;
    for(const auto& particle:particles(ctx)) {
      std::vector<Index> indices;std::map<Index,Index> lookup;
      auto [begin,end]=pm.equal_range(particle.particleId());
      for(auto it=begin;it!=end;++it) {
        const auto measurement=it->second;
        const auto source=ms.find(measurement);
        if(source==ms.end() || source->second>=hs.size()) throw std::runtime_error("Invalid direct measurement-simhit association");
        indices.push_back(measurement);lookup[measurement]=source->second;
      }
      const auto sorted=orderMeasurements(indices,lookup,times);
      result.emplace_back(sorted.begin(),sorted.end());
    }
    output(ctx,std::move(result));return ProcessCode::SUCCESS;
  }
 private:
  ReadDataHandle<SimParticleContainer> particles{this,"Particles"};
  ReadDataHandle<ParticleMeasurementsMap> map{this,"ParticleMeasurements"};
  ReadDataHandle<SimHitContainer> simhits{this,"Hits"};
  ReadDataHandle<MeasurementSimHitsMap> associations{this,"MeasurementSimHits"};
  WriteDataHandle<ProtoTrackContainer> output{this,"CorrectedProtoTracks"};
};
double clusterVariance(const std::vector<double>& rms,std::size_t size) {
  if(rms.empty() || size==0) throw std::invalid_argument("Empty RMS vector or zero cluster size");
  const double value=rms.at(std::min(size,rms.size())-1);
  if(!std::isfinite(value) || value<=0) throw std::invalid_argument("Invalid cluster RMS");
  return value*value;
}
class ClusterErrors final : public IAlgorithm {
 public:
  explicit ClusterErrors(const py::list& entries): IAlgorithm("ClusterErrors",Acts::getDefaultLogger("ClusterErrors",Acts::Logging::WARNING)) {
    input.initialize("measurements_raw");clusters.initialize("clusters");output.initialize("measurements_calibrated");
    for(auto object:entries) {
      auto item=py::cast<py::dict>(object);auto volume=py::cast<unsigned long>(item["volume"]);
      for(auto value:py::cast<py::list>(item["value"])) {
        auto entry=py::cast<py::dict>(value);
        auto index=py::cast<unsigned int>(entry["index"]);
        table[volume][index]=py::cast<std::vector<double>>(entry["rms"]);
      }
    }
  }
  ProcessCode execute(const AlgorithmContext& ctx) const override {
    const auto& source=input(ctx);const auto& cs=clusters(ctx);
    if(source.size()!=cs.size()) throw std::runtime_error("Cluster/measurement count mismatch");
    MeasurementContainer calibrated;calibrated.reserve(source.size());
    for(std::size_t i=0;i<source.size();++i) {
      const auto original=source.getMeasurement(i);auto target=calibrated.copyMeasurement(original);
      target.covariance().setZero();
      const auto& volume=table.at(original.geometryId().volume());
      for(std::size_t j=0;j<target.size();++j) {
        const auto boundIndex=target.subspaceIndexVector()[j];
        if(boundIndex>1) throw std::runtime_error("Only geometric local coordinates supported");
        const auto size=boundIndex==0?cs[i].sizeLoc0:cs[i].sizeLoc1;
        target.covariance()(j,j)=clusterVariance(volume.at(boundIndex),size);
      }
      if(target.geometryId()!=original.geometryId() || target.index()!=original.index()
          || !target.parameters().isApprox(original.parameters(),0)) throw std::runtime_error("Calibration changed measurement identity/position");
    }
    output(ctx,std::move(calibrated));return ProcessCode::SUCCESS;
  }
 private:
  std::map<unsigned long,std::map<unsigned int,std::vector<double>>> table;
  ReadDataHandle<MeasurementContainer> input{this,"RawMeasurements"};
  ReadDataHandle<ClusterContainer> clusters{this,"Clusters"};
  WriteDataHandle<MeasurementContainer> output{this,"CalibratedMeasurements"};
};
// Use the documented granular Geant4 event loop to avoid rebuilding unchanged
// production-cut tables for every ACTS event. Each ACTS event remains one G4 event.
class PersistentRunManager final : public G4RunManager {
 public:
  explicit PersistentRunManager(int events): expected(events) {
    if(events<=0) throw std::invalid_argument("Positive persistent event count required");
  }
  void BeamOn(G4int count,const char* macro=nullptr,G4int select=-1) override {
    if(count!=1 || macro!=nullptr || select!=-1 || finished) throw std::runtime_error("Persistent mode requires one standard event per call");
    if(!started) {
      if(!ConfirmBeamOnCondition()) throw std::runtime_error("Geant4 initialization condition failed");
      numberOfEventToBeProcessed=expected;
      RunInitialization();
      InitializeEventLoop(expected,nullptr,-1);
      started=true;
    }
    if(runAborted) throw std::runtime_error("Native Geant4 run aborted");
    ProcessOneEvent(processed);
    TerminateOneEvent();
    ++processed;
    if(processed==expected) finish();
  }
  void finish() {
    if(started && !finished) {TerminateEventLoop();RunTermination();finished=true;}
  }
 private:
  int expected,processed=0;bool started=false,finished=false;
};
std::shared_ptr<Geant4Handle> persistentHandle(int events) {
  auto& manager=Geant4Manager::instance();
  if(manager.currentHandle()) throw std::runtime_error("A Geant4 handle already exists");
  return std::make_shared<Geant4Handle>(std::make_unique<PersistentRunManager>(events),
      manager.createPhysicsList("FTFP_BERT"),"FTFP_BERT");
}
template<typename Label>
std::vector<std::pair<Index,Label>> uniquePairs(const std::vector<std::pair<Index,Label>>& input) {
  const std::set<std::pair<Index,Label>> unique(input.begin(),input.end());
  return {unique.begin(),unique.end()};
}
class UniqueAssociations final : public IAlgorithm {
 public:
  UniqueAssociations():IAlgorithm("UniqueAssociations",Acts::getDefaultLogger("UniqueAssociations",Acts::Logging::WARNING)) {
    input.initialize("measurement_particles_map_raw");
    outputMeasurements.initialize("measurement_particles_map");outputParticles.initialize("particle_measurements_map");
  }
  ProcessCode execute(const AlgorithmContext& ctx) const override {
    std::vector<std::pair<Index,SimBarcode>> pairs;
    for(const auto& association:input(ctx)) pairs.push_back(association);
    MeasurementParticlesMap unique;
    for(const auto& [index,barcode]:uniquePairs(pairs)) unique.emplace(index,barcode);
    auto inverse=invertIndexMultimap(unique);
    outputMeasurements(ctx,std::move(unique));outputParticles(ctx,std::move(inverse));
    return ProcessCode::SUCCESS;
  }
 private:
  ReadDataHandle<MeasurementParticlesMap> input{this,"RawAssociations"};
  WriteDataHandle<MeasurementParticlesMap> outputMeasurements{this,"UniqueMeasurementParticles"};
  WriteDataHandle<ParticleMeasurementsMap> outputParticles{this,"UniqueParticleMeasurements"};
};
class Audit final : public IAlgorithm {
 public:
  explicit Audit(const std::string& path) : IAlgorithm("TruthTrackingAudit", Acts::getDefaultLogger("TruthTrackingAudit",Acts::Logging::WARNING)), file(TFile::Open(path.c_str(),"RECREATE")), tree("audit","All-event native truth-tracking accounting") {
    if(!file || file->IsZombie()) throw std::runtime_error("Cannot open audit output");
    generated.initialize("particles_generated"); selected.initialize("particles_digitized_selected");
    hits.initialize("simhits"); measurements.initialize("measurements");
    map.initialize("particle_measurements_map"); rawMap.initialize("particle_measurements_map_raw"); proto.initialize("truth_particle_tracks_corrected"); tracks.initialize("kf_tracks");
    tree.SetDirectory(file.get());
    tree.Branch("event_nr",&event); tree.Branch("generated",&nGenerated);
    tree.Branch("simhits",&nHits); tree.Branch("measurements",&nMeasurements);
    tree.Branch("original_proto_reference_enabled",&referenceEnabled);
    tree.Branch("original_proto_measurements",&nOriginalProtoMeasurements);
    tree.Branch("corrected_proto_measurements",&nCorrectedProtoMeasurements);
    tree.Branch("selected",&nSelected); tree.Branch("fit_attempts",&nProto);
    tree.Branch("fit_tracks",&nTracks); tree.Branch("invalid_covariance",&nInvalid);
    tree.Branch("primary_measurements",&nPrimaryMeasurements);
    tree.Branch("primary_measurement_associations_raw",&nPrimaryRaw);
    tree.Branch("measurement_geometry_id",&geometryIds); tree.Branch("measurement_dimension",&dimensions);
  }
  ProcessCode execute(const AlgorithmContext& ctx) const override {
    std::lock_guard<std::mutex> lock(mutex);
    event=ctx.eventNumber; nGenerated=generated(ctx).size(); nHits=hits(ctx).size();
    const auto& ms=measurements(ctx); nMeasurements=ms.size(); nSelected=selected(ctx).size();
    nOriginalProtoMeasurements=0;nCorrectedProtoMeasurements=0;
    // The broken native reference finder is intentionally not executed.
    // Its count is an explicit disabled sentinel, not a comparison measurement.
    for(const auto& track:proto(ctx)) nCorrectedProtoMeasurements+=track.size();
    nProto=proto(ctx).size(); nTracks=tracks(ctx).size(); nInvalid=0; nPrimaryMeasurements=0;
    const auto& pm=map(ctx);
    nPrimaryRaw=0;
    for(const auto& p:generated(ctx)) {nPrimaryMeasurements+=pm.count(p.particleId());nPrimaryRaw+=rawMap(ctx).count(p.particleId());}
    geometryIds.clear(); dimensions.clear();
    for(std::size_t i=0;i<ms.size();++i) {const auto m=ms.getMeasurement(i); geometryIds.push_back(m.geometryId().value());dimensions.push_back(m.size());}
    for(const auto tr: tracks(ctx)) {
      if(!tr.hasReferenceSurface() || !tr.covariance().allFinite() || (tr.covariance().diagonal().array()<=0).any()) ++nInvalid;
    }
    tree.Fill();
    if(event%1000==0) std::cout << "TRUTH_AUDIT event=" << event << " measurements=" << nMeasurements << " fits=" << nTracks << std::endl;
    return ProcessCode::SUCCESS;
  }
  ProcessCode finalize() override { file->cd(); tree.Write(); tree.SetDirectory(nullptr); file->Close(); return ProcessCode::SUCCESS; }
 private:
  ReadDataHandle<SimParticleContainer> generated{this,"Generated"}, selected{this,"Selected"};
  ReadDataHandle<SimHitContainer> hits{this,"Hits"};
  ReadDataHandle<MeasurementContainer> measurements{this,"Measurements"};
  ReadDataHandle<ParticleMeasurementsMap> map{this,"ParticleMeasurements"},rawMap{this,"RawParticleMeasurements"};
  ReadDataHandle<ProtoTrackContainer> proto{this,"ProtoTracks"};
  ReadDataHandle<ConstTrackContainer> tracks{this,"Tracks"};
  std::unique_ptr<TFile> file; mutable TTree tree; mutable std::mutex mutex;
  mutable unsigned long long event=0,nGenerated=0,nHits=0,nMeasurements=0,nSelected=0,nProto=0,nTracks=0,nInvalid=0,nPrimaryMeasurements=0;
  mutable bool referenceEnabled=false;
  mutable unsigned long long nOriginalProtoMeasurements=0,nCorrectedProtoMeasurements=0,nPrimaryRaw=0;
  mutable std::vector<unsigned long long> geometryIds;
  mutable std::vector<unsigned int> dimensions;
};
PYBIND11_MODULE(nodd_truth_tracking,m) {
  py::class_<UniqueAssociations,IAlgorithm,std::shared_ptr<UniqueAssociations>>(m,"UniqueAssociations").def(py::init<>());
  m.def("unique_associations",&uniquePairs<unsigned long long>);
  m.def("persistent_handle",&persistentHandle);
  m.def("finish_persistent",[](Geant4Handle& handle) {
    auto* manager=dynamic_cast<PersistentRunManager*>(handle.runManager.get());
    if(!manager) throw std::invalid_argument("Not a persistent handle");manager->finish();
  });
  m.def("order_measurements",&orderMeasurements);
  m.def("cluster_variance",&clusterVariance);
  py::class_<ClusterErrors,IAlgorithm,std::shared_ptr<ClusterErrors>>(m,"ClusterErrors").def(py::init<const py::list&>());
  py::class_<CorrectTruthProtoTracks,IAlgorithm,std::shared_ptr<CorrectTruthProtoTracks>>(m,"CorrectTruthProtoTracks").def(py::init<>());py::class_<Audit,IAlgorithm,std::shared_ptr<Audit>>(m,"Audit").def(py::init<const std::string&>());m.attr("pybind11_version")="3.0.4";m.attr("pybind11_internals_version")=PYBIND11_INTERNALS_VERSION;}
