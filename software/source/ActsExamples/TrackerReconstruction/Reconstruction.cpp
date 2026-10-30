// DES041 PROTOTYPE observation only; no truth data feed reconstruction.
#include "ActsExamples/Framework/IAlgorithm.hpp"
#include "ActsExamples/Framework/AlgorithmContext.hpp"
#include "ActsExamples/Framework/DataHandle.hpp"
#include "ActsExamples/EventData/SimParticle.hpp"
#include "ActsExamples/EventData/SimHit.hpp"
#include "ActsExamples/EventData/Measurement.hpp"
#include "ActsExamples/EventData/TruthMatching.hpp"
#include "ActsExamples/EventData/Track.hpp"
#include "ActsExamples/EventData/IndexSourceLink.hpp"
#include "Acts/EventData/SeedContainer.hpp"
#include "Acts/EventData/SpacePointContainer.hpp"
#include "ActsExamples/Geant4/SensitiveSurfaceMapper.hpp"
#include "ActsExamples/DetectorCommons/Detector.hpp"
#include "ActsExamples/DD4hepDetector/DD4hepDetector.hpp"
#include <DD4hep/Detector.h>
#include <DD4hep/DetElement.h>
#include <DD4hep/Volumes.h>
#include <G4VUserDetectorConstruction.hh>
#include <G4TransportationManager.hh>
#include <G4Navigator.hh>
#include <G4VPhysicalVolume.hh>
#include <G4LogicalVolume.hh>
#include <G4Material.hh>
#include <G4ProductionCutsTable.hh>
#include <G4MaterialCutsCouple.hh>
#include <G4ProductionCuts.hh>
#include <G4RunManager.hh>
#include <G4Run.hh>
#include <G4VUserPhysicsList.hh>
#include <G4Version.hh>
#include <nlohmann/json.hpp>
#include <pybind11/pybind11.h>
#include <fstream>
#include <mutex>
#include <set>
#include <cmath>
#include <Eigen/Cholesky>
using namespace ActsExamples;
using Json=nlohmann::json;
namespace py=pybind11;
static_assert(PYBIND11_INTERNALS_VERSION == NODD_EXPECTED_PYBIND11_INTERNALS_VERSION);

// The generic ACTS substring mapper cannot distinguish a strip face named F0
// from its F0_* passive components. Tag the exact DD4hep-sensitive logical
// volumes during conversion. Names change; solids, materials, placements and
// native DD4hep/G4 volume identifiers are untouched.
class SensitiveConstruction final: public G4VUserDetectorConstruction {
 public:
  SensitiveConstruction(std::unique_ptr<G4VUserDetectorConstruction> inner,std::set<std::string> names): original(std::move(inner)),activeNames(std::move(names)) {}
  G4VPhysicalVolume* Construct() override {
    auto* world=original->Construct();std::set<G4LogicalVolume*> seen;
    const auto visit=[&](auto&& self,G4VPhysicalVolume* physical)->void {
      auto* logical=physical->GetLogicalVolume();
      if(seen.insert(logical).second) {
        const std::string name=logical->GetName();
        if(activeNames.contains(name)) logical->SetName("nodd_active::"+name);
        for(int i=0;i<logical->GetNoDaughters();++i) self(self,logical->GetDaughter(i));
      }
    };visit(visit,world);return world;
  }
  void ConstructSDandField() override {original->ConstructSDandField();}
 private:
  std::unique_ptr<G4VUserDetectorConstruction> original;std::set<std::string> activeNames;
};

class SensitiveDetector final: public Detector {
 public:
  explicit SensitiveDetector(std::shared_ptr<Detector> detector):Detector(Acts::getDefaultLogger("SensitiveDetector",Acts::Logging::WARNING)),original(std::move(detector)) {
    const auto visit=[&](auto&& self,const dd4hep::DetElement& element)->void {
      if(element.placement().isValid() && element.volume().isSensitive()) activeNames.insert(element.volume().name());
      for(const auto& [name,child]:element.children()) self(self,child);
    };
    const auto* dd=dynamic_cast<DD4hepDetectorBase*>(original.get());
    if(!dd) throw std::runtime_error("Sensitivity wrapper requires the actual DD4hep detector instance");
    visit(visit,dd->dd4hepDetector().world());
    if(activeNames.empty()) throw std::runtime_error("No canonical DD4hep-sensitive volume names");
  }
  const Acts::GeometryContext& nominalGeometryContext() const override {return original->nominalGeometryContext();}
  std::shared_ptr<const Acts::TrackingGeometry> trackingGeometry() const override {return original->trackingGeometry();}
  std::vector<std::shared_ptr<IContextDecorator>> contextDecorators() const override {return original->contextDecorators();}
  std::unique_ptr<G4VUserDetectorConstruction> buildGeant4DetectorConstruction(const Geant4ConstructionOptions& options) const override {
    return std::make_unique<SensitiveConstruction>(original->buildGeant4DetectorConstruction(options),activeNames);
  }
 private:
  std::shared_ptr<Detector> original;std::set<std::string> activeNames;
};

// Repeat the same deterministic native mapper to expose its coverage. This
// observation does not replace the live stepping-action mapping or filter hits.
std::string geant4Mapping(const std::shared_ptr<const Acts::TrackingGeometry>& geometry) {
  using namespace ActsExamples::Geant4;
  auto* world=G4TransportationManager::GetTransportationManager()->GetNavigatorForTracking()->GetWorldVolume();
  if(!world) throw std::runtime_error("No initialized Geant4 world for mapping audit");
  SensitiveSurfaceMapper::Config config;
  config.volumeMappings={"nodd_active::"};
  config.candidateSurfaces=std::make_shared<SensitiveCandidates>(geometry,Acts::getDefaultLogger("MappingAuditCandidates",Acts::Logging::WARNING));
  SensitiveSurfaceMapper mapper(config,Acts::getDefaultLogger("MappingAudit",Acts::Logging::WARNING));
  SensitiveSurfaceMapper::State state;
  const auto context=Acts::GeometryContext::dangerouslyDefaultConstruct();
  mapper.remapSensitiveNames(state,context,world,Acts::Transform3::Identity());
  Json result={{"scope","independent deterministic replay of configured native mapper; live stepping map is not replaced"},
               {"all_sensitive_surfaces_mapped",mapper.checkMapping(state,context,false,false)}};
  std::map<std::uint64_t,std::size_t> counts;
  for(const auto& [volume,surfaces]:state.g4VolumeToSurfaces)
    for(const auto& [position,surface]:surfaces) ++counts[surface->geometryId().value()];
  result["mapped_geometry_ids"]=Json::array();result["duplicate_geometry_ids"]=Json::array();
  for(const auto& [id,count]:counts) {result["mapped_geometry_ids"].push_back(id);if(count!=1) result["duplicate_geometry_ids"].push_back({{"id",id},{"count",count}});}
  result["expected_geometry_ids"]=Json::array();
  for(const auto* surface:config.candidateSurfaces->queryAll()) result["expected_geometry_ids"].push_back(surface->geometryId().value());
  result["unmatched_g4_volumes"]=Json::array();
  for(const auto& [volume,transform]:state.missingVolumes) result["unmatched_g4_volumes"].push_back({
    {"name",volume->GetLogicalVolume()->GetName()},{"material",volume->GetLogicalVolume()->GetMaterial()->GetName()},
    {"sensitive_detector",volume->GetLogicalVolume()->GetSensitiveDetector()!=nullptr},
    {"position_mm",{transform.translation().x(),transform.translation().y(),transform.translation().z()}}});
  result["production_cuts"]=Json::array();auto* cuts=G4ProductionCutsTable::GetProductionCutsTable();
  for(std::size_t i=0;i<cuts->GetTableSize();++i) {const auto* couple=cuts->GetMaterialCutsCouple(i);std::vector<double> ranges;
    for(int j=0;j<4;++j) ranges.push_back(couple->GetProductionCuts()->GetProductionCut(j));
    result["production_cuts"].push_back({{"material",couple->GetMaterial()->GetName()},{"range_mm_gamma_electron_positron_proton",ranges}});
  }
  return result.dump();
}

class ReconstructionAudit final: public IAlgorithm {
 public:
  explicit ReconstructionAudit(const std::string& path): IAlgorithm("ReconstructionAudit",Acts::getDefaultLogger("ReconstructionAudit",Acts::Logging::WARNING)), file(path) {
    if(!file) throw std::runtime_error("Cannot open all-event reconstruction audit");
    generated.initialize("particles_generated"); simulated.initialize("particles_simulated");
    hits.initialize("simhits"); measurements.initialize("measurements"); associations.initialize("measurement_particles_map");
    subset.initialize("measurement_subset");
    points.initialize("spacepoints"); seeds.initialize("seeds"); estimated.initialize("estimatedseeds");
    initialParameters.initialize("estimatedparameters");
    ckf.initialize("ckf_tracks"); ambi.initialize("ambi_tracks");
  }
  static Json seedData(const Acts::SeedContainer& container,const Acts::SpacePointContainer& sp) {
    auto result=Json::array();
    for(const auto& seed:container) {
      std::set<std::size_t> indices;
      std::vector<std::size_t> pointIndices,orderedMeasurements;
      for(const auto i:seed.spacePointIndices()) {pointIndices.push_back(i);
        for(const auto& sl:sp.at(i).sourceLinks()) {const auto m=sl.get<IndexSourceLink>().index();indices.insert(m);orderedMeasurements.push_back(m);}}
      result.push_back({{"measurements",indices},{"spacepoint_indices",pointIndices},
                        {"ordered_measurements",orderedMeasurements},{"quality",seed.quality()}});
    }
    return result;
  }
  static Json trackData(const ConstTrackContainer& container) {
    auto result=Json::array();
    for(const auto track:container) {
      std::set<std::size_t> indices; auto states=Json::array();
      for(const auto& state:track.trackStatesReversed()) {
        const auto sl=state.hasUncalibratedSourceLink() ? state.getUncalibratedSourceLink().getPtr<IndexSourceLink>() : nullptr;
        const auto flags=state.typeFlags();
        if(sl && flags.isMeasurement() && !flags.isOutlier()) indices.insert(sl->index());
        Json saved={{"geometry_id",state.hasReferenceSurface() ? Json(state.referenceSurface().geometryId().value()) : Json()},
                          {"measurement",sl ? Json(sl->index()) : Json()},
                          {"inlier",flags.isMeasurement()},
                          {"outlier",flags.isOutlier()},
                          {"hole",flags.isHole()}};
        const auto storeParameters=[&](const char* label,const auto& values,const auto& covariance) {
          std::vector<double> parameters,variance;
          for(int i=0;i<6;++i) {parameters.push_back(values[i]);variance.push_back(covariance(i,i));}
          saved[label]={{"parameters",parameters},{"variance",variance}};
        };
        if(state.hasPredicted()) storeParameters("predicted",state.predicted(),state.predictedCovariance());
        if(state.hasFiltered()) storeParameters("filtered",state.filtered(),state.filteredCovariance());
        if(state.hasSmoothed()) storeParameters("smoothed",state.smoothed(),state.smoothedCovariance());
        states.push_back(std::move(saved));
      }
      std::vector<double> parameters,variance;bool covariancePositiveDefinite=false;
      if(track.hasReferenceSurface()) for(int i=0;i<6;++i) {parameters.push_back(track.parameters()[i]);variance.push_back(track.covariance()(i,i));}
      if(track.hasReferenceSurface() && track.covariance().allFinite()) {
        const Acts::BoundMatrix covariance=track.covariance();
        covariancePositiveDefinite=covariance.isApprox(covariance.transpose(),1.e-10)
          && Eigen::LLT<Acts::BoundMatrix>(covariance).info()==Eigen::Success;
      }
      result.push_back({{"index",track.index()},{"measurements",indices},{"states",states},
        {"hypothesis",{{"absolute_pdg",static_cast<int>(track.particleHypothesis().absolutePdg())},{"mass_GeV",track.particleHypothesis().mass()}}},
        {"nMeasurements",track.nMeasurements()},{"nHoles",track.nHoles()},{"nOutliers",track.nOutliers()},
        {"chi2",track.chi2()},{"ndf",track.nDoF()},{"reference",track.hasReferenceSurface()},
        {"parameters",parameters},{"variance",variance},{"covariance_positive_definite",covariancePositiveDefinite}});
    }
    return result;
  }
  ProcessCode execute(const AlgorithmContext& ctx) const override {
    Json row={{"event",ctx.eventNumber},{"simhits",hits(ctx).size()}};
    row["generated"]=Json::array();
    for(const auto& p:generated(ctx)) row["generated"].push_back({{"id",p.particleId().asArray()},
      {"pdg",static_cast<int>(p.pdg())},{"mass_GeV",p.mass()},
      {"charge",p.charge()},{"pt",p.transverseMomentum()},{"eta",std::asinh(p.direction().z()/std::hypot(p.direction().x(),p.direction().y()))},
      {"truth",{0.,0.,p.phi(),p.theta(),p.qOverP(),p.time()}}});
    row["simulated_ids"]=Json::array();
    for(const auto& p:simulated(ctx)) row["simulated_ids"].push_back(p.particleId().asArray());
    row["simulated_particles"]=Json::array();
    for(const auto& p:simulated(ctx)) row["simulated_particles"].push_back({
      {"id",p.particleId().asArray()},{"parent_id",p.parentParticleId().asArray()},
      {"pdg",static_cast<int>(p.pdg())},{"mass_GeV",p.mass()},{"charge",p.charge()},
      {"process",static_cast<int>(p.process())},{"outcome",static_cast<int>(p.outcome())},
      {"final_position_mm",{p.finalState().position().x(),p.finalState().position().y(),p.finalState().position().z()}},
      {"final_ct_mm",p.finalState().time()},{"path_X0",p.pathInX0()},{"path_L0",p.pathInL0()},
      {"p_initial_GeV",p.initialState().absoluteMomentum()},{"p_final_GeV",p.finalState().absoluteMomentum()}});
    row["estimated_hypotheses"]=Json::array();
    for(const auto& p:initialParameters(ctx)) row["estimated_hypotheses"].push_back({
      {"absolute_pdg",static_cast<int>(p.particleHypothesis().absolutePdg())},
      {"mass_GeV",p.particleHypothesis().mass()}});
    row["measurements"]=Json::array();
    const auto& ms=measurements(ctx);const auto& mp=associations(ctx);
    const auto& selected=subset(ctx);
    std::set<std::size_t> allIndices;
    for(const auto& sl:selected.orderedIndices()) allIndices.insert(sl.index());
    if(allIndices.size()!=ms.size() || (!allIndices.empty() && (*allIndices.begin()!=0 || *allIndices.rbegin()!=ms.size()-1)))
      throw std::runtime_error("CKF measurement subset does not contain every original measurement");
    row["ckf_input_measurements"]=allIndices.size();
    for(std::size_t i=0;i<ms.size();++i) {
      const auto m=ms.getMeasurement(i);std::set<std::array<std::uint32_t,5>> particles;
      const auto [first,last]=mp.equal_range(i);for(auto it=first;it!=last;++it) particles.insert(it->second.asArray());
      std::vector<double> values,variance;
      for(std::size_t j=0;j<m.size();++j) {values.push_back(m.parameters()[j]);variance.push_back(m.covariance()(j,j));}
      row["measurements"].push_back({{"index",i},{"geometry_id",m.geometryId().value()},
        {"dimension",m.size()},{"particles",particles},{"values",values},{"variance",variance}});
    }
    row["spacepoints"]=Json::array();
    for(const auto& p:points(ctx)) {auto links=Json::array();for(const auto& sl:p.sourceLinks()) links.push_back(sl.get<IndexSourceLink>().index());
      row["spacepoints"].push_back({{"index",p.index()},{"position",{p.x(),p.y(),p.z()}},{"measurements",links}});}
    row["seeds"]=seedData(seeds(ctx),points(ctx));row["estimated_seeds"]=seedData(estimated(ctx),points(ctx));
    row["ckf"]=trackData(ckf(ctx));row["ambi"]=trackData(ambi(ctx));
    std::lock_guard lock(mutex);file<<row.dump()<<'\n';file.flush();
    if(!file) throw std::runtime_error("Failed to write reconstruction audit");
    return ProcessCode::SUCCESS;
  }
 private:
  ReadDataHandle<SimParticleContainer> generated{this,"Generated"},simulated{this,"Simulated"};
  ReadDataHandle<SimHitContainer> hits{this,"Hits"};
  ReadDataHandle<MeasurementContainer> measurements{this,"Measurements"};
  ReadDataHandle<MeasurementSubset> subset{this,"CompleteMeasurementSubset"};
  ReadDataHandle<MeasurementParticlesMap> associations{this,"Associations"};
  ReadDataHandle<Acts::SpacePointContainer> points{this,"MeasuredSpacePoints"};
  ReadDataHandle<Acts::SeedContainer> seeds{this,"GbtsSeeds"},estimated{this,"EstimatedSeeds"};
  ReadDataHandle<TrackParametersContainer> initialParameters{this,"EstimatedParameters"};
  ReadDataHandle<ConstTrackContainer> ckf{this,"Ckf"},ambi{this,"Ambiguity"};
  mutable std::mutex mutex;mutable std::ofstream file;
};
PYBIND11_MODULE(nodd_reconstruction,m) {
  py::class_<SensitiveDetector,Detector,std::shared_ptr<SensitiveDetector>>(m,"SensitiveDetector").def(py::init<std::shared_ptr<Detector>>());
  m.def("geant4_mapping_json",&geant4Mapping);
  m.def("geant4_event_count",[]() {const auto* manager=G4RunManager::GetRunManager();
    const auto* run=manager ? manager->GetCurrentRun() : nullptr;
    return run ? run->GetNumberOfEvent() : -1;});
  m.def("geant4_runtime_json",[]() {Json result={{"loaded_Geant4_version",G4Version},{"production_cuts",Json::array()}};
    const auto* manager=G4RunManager::GetRunManager();
    if(manager && manager->GetUserPhysicsList()) result["default_range_cut_mm"]=manager->GetUserPhysicsList()->GetDefaultCutValue();
    auto* table=G4ProductionCutsTable::GetProductionCutsTable();
    for(std::size_t i=0;i<table->GetTableSize();++i) {const auto* couple=table->GetMaterialCutsCouple(i);std::vector<double> ranges;
      for(int j=0;j<4;++j) ranges.push_back(couple->GetProductionCuts()->GetProductionCut(j));
      result["production_cuts"].push_back({{"material",couple->GetMaterial()->GetName()},{"range_mm_gamma_electron_positron_proton",ranges}});}
    return result.dump();});
  py::class_<ReconstructionAudit,IAlgorithm,std::shared_ptr<ReconstructionAudit>>(m,"ReconstructionAudit").def(py::init<const std::string&>());
}
