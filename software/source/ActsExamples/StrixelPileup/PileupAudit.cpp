// DES042 isolated lossless sample, replay checks and observation-only audits.
#include "ActsExamples/Framework/IAlgorithm.hpp"
#include "ActsExamples/Framework/IReader.hpp"
#include "ActsExamples/Framework/AlgorithmContext.hpp"
#include "ActsExamples/Framework/DataHandle.hpp"
#include "ActsExamples/EventData/SimParticle.hpp"
#include "ActsExamples/EventData/SimVertex.hpp"
#include "ActsExamples/EventData/SimHit.hpp"
#include "ActsExamples/EventData/Measurement.hpp"
#include "ActsExamples/EventData/TruthMatching.hpp"
#include "ActsExamples/EventData/Track.hpp"
#include "ActsExamples/EventData/IndexSourceLink.hpp"
#include "Acts/EventData/SeedContainer.hpp"
#include "Acts/EventData/SpacePointContainer.hpp"
#include "Acts/Geometry/TrackingGeometry.hpp"
#include <HepMC3/GenEvent.h>
#include <HepMC3/GenParticle.h>
#include <HepMC3/Attribute.h>
#include <nlohmann/json.hpp>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <Eigen/Cholesky>
#include <zlib.h>
#include <filesystem>
#include <fstream>
#include <set>
#include <mutex>
#include <iomanip>
#include <sstream>
using namespace ActsExamples;
using Json=nlohmann::json;
namespace py=pybind11;
namespace fs=std::filesystem;
static std::string eventPath(const std::string& dir,std::size_t event) {
  std::ostringstream s;s<<dir<<"/event"<<std::setw(6)<<std::setfill('0')<<event<<".json.gz";return s.str();
}
static void diskGuard(const std::string& path) {
  if(fs::space(fs::path(path).parent_path()).available<2ull*1024*1024*1024) throw std::runtime_error("Less than 2 GiB available; partial evidence retained");
}
static void gzWrite(const std::string& path,const std::string& value) {
  diskGuard(path);gzFile f=gzopen(path.c_str(),"wb3");if(!f) throw std::runtime_error("Cannot open gzip audit "+path);
  std::size_t offset=0;while(offset<value.size()) {const auto n=std::min<std::size_t>(value.size()-offset,1<<20);if(gzwrite(f,value.data()+offset,n)!=static_cast<int>(n)) {gzclose(f);throw std::runtime_error("Gzip audit write failure");}offset+=n;}
  if(gzclose(f)!=Z_OK) throw std::runtime_error("Gzip audit close failure");
}
static Json gzRead(const std::string& path) {
  gzFile f=gzopen(path.c_str(),"rb");if(!f) throw std::runtime_error("Cannot read sample "+path);
  std::string value;char buffer[65536];int n;while((n=gzread(f,buffer,sizeof(buffer)))>0) value.append(buffer,n);
  const auto status=gzclose(f);if(n<0 || status!=Z_OK) throw std::runtime_error("Corrupt gzip sample");return Json::parse(value);
}
static Json vector(const auto& v) {auto j=Json::array();for(int i=0;i<v.size();++i) j.push_back(v[i]);return j;}
static SimBarcode barcode(const Json& j) {return SimBarcode().withVertexPrimary(j.at(0)).withVertexSecondary(j.at(1)).withParticle(j.at(2)).withGeneration(j.at(3)).withSubParticle(j.at(4));}
static Acts::Vector4 four(const Json& j) {return Acts::Vector4(j.at(0),j.at(1),j.at(2),j.at(3));}
static Json stateJson(const SimParticleState& p) {
  return {{"id",p.particleId().asArray()},{"parent_id",p.parentParticleId().asArray()},{"pdg",static_cast<int>(p.pdg())},
    {"mass_GeV",p.mass()},{"charge",p.charge()},{"position4",vector(p.fourPosition())},{"direction",vector(p.direction())},
    {"p_GeV",p.absoluteMomentum()},{"process",static_cast<int>(p.process())},{"outcome",static_cast<int>(p.outcome())},
    {"proper_time",p.properTime()},{"path_X0",p.pathInX0()},{"path_L0",p.pathInL0()},{"n_hits",p.numberOfHits()},
    {"orig_particle_idx",p.origParticleIdx()},{"reference_geometry_id",p.hasReferenceSurface() ? Json(p.referenceSurface()->geometryId().value()):Json()}};
}
static SimParticleState restoreState(const Json& j,const Acts::TrackingGeometry& geometry) {
  SimParticleState p(barcode(j.at("id")),static_cast<Acts::PdgParticle>(j.at("pdg").get<int>()),j.at("charge"),j.at("mass_GeV"));
  p.setParentParticleId(barcode(j.at("parent_id")));p.setPosition4(four(j.at("position4")));
  const auto& d=j.at("direction");Acts::Vector3 direction(d.at(0),d.at(1),d.at(2));
  if(!direction.allFinite() || std::abs(direction.norm()-1.)>1.e-12) throw std::runtime_error("Invalid saved unit direction");
  p.setDirection(direction);
  // This fresh mutable object owns this vector. Its public setter renormalizes
  // already normalized native vectors, which can change one ulp. Restore the
  // validated stored vector exactly through the public reference; no shared or
  // const object is modified. The complete reserialization equality below gates it.
  const_cast<Acts::Vector3&>(p.direction())=direction;
  p.setAbsoluteMomentum(j.at("p_GeV"));p.setProcess(static_cast<ActsFatras::GenerationProcess>(j.at("process").get<int>()));
  p.setOutcome(static_cast<ActsFatras::SimulationOutcome>(j.at("outcome").get<int>()));p.setProperTime(j.at("proper_time"));
  p.setMaterialPassed(j.at("path_X0"),j.at("path_L0"));p.setNumberOfHits(j.at("n_hits"));p.setOrigParticleIdx(j.at("orig_particle_idx"));
  if(!j.at("reference_geometry_id").is_null()) {auto* s=geometry.findSurface(Acts::GeometryIdentifier(j.at("reference_geometry_id").get<std::uint64_t>()));if(!s)throw std::runtime_error("Saved particle surface is absent");p.setReferenceSurface(s);}
  if(stateJson(p).dump()!=j.dump()) throw std::runtime_error("Native particle-state roundtrip mismatch");return p;
}
static Json particlesJson(const SimParticleContainer& particles) {auto j=Json::array();for(const auto& p:particles) j.push_back({{"initial",stateJson(p.initialState())},{"final",stateJson(p.finalState())},{"heavy_flavour_origin",static_cast<int>(p.heavyFlavourOrigin())}});return j;}
static SimParticleContainer restoreParticles(const Json& j,const Acts::TrackingGeometry& geometry) {
  std::vector<SimParticle> data;data.reserve(j.size());for(const auto& item:j) {SimParticle p(restoreState(item.at("initial"),geometry),restoreState(item.at("final"),geometry));p.setHeavyFlavourOrigin(static_cast<HeavyFlavourOrigin>(item.at("heavy_flavour_origin").get<int>()));data.push_back(std::move(p));}
  SimParticleContainer result(data.begin(),data.end());if(particlesJson(result).dump()!=j.dump())throw std::runtime_error("Native particle container/order roundtrip mismatch");return result;
}
static Json hitsJson(const SimHitContainer& hits) {auto j=Json::array();for(const auto& h:hits) j.push_back({{"geometry_id",h.geometryId().value()},{"particle_id",h.particleId().asArray()},{"index",h.index()},{"position4",vector(h.fourPosition())},{"before4",vector(h.momentum4Before())},{"after4",vector(h.momentum4After())}});return j;}
static SimHitContainer restoreHits(const Json& j) {
  std::vector<SimHit> values;values.reserve(j.size());for(const auto& h:j)values.emplace_back(Acts::GeometryIdentifier(h.at("geometry_id").get<std::uint64_t>()),barcode(h.at("particle_id")),four(h.at("position4")),four(h.at("before4")),four(h.at("after4")),h.at("index"));
  SimHitContainer result(values.begin(),values.end());if(hitsJson(result).dump()!=j.dump())throw std::runtime_error("Native hit container/order roundtrip mismatch");return result;
}
static void requireConvertedOrigins(const std::set<int>& origins) {
  if(origins.size()!=201 || *origins.begin()!=0 || *origins.rbegin()!=200)
    throw std::runtime_error("Full unfiltered generated truth lacks one or more of the 201 generator origins");
}
class SampleWriter final: public IAlgorithm {
 public:
  explicit SampleWriter(std::string path):IAlgorithm("PileupSampleWriter",Acts::getDefaultLogger("PileupSampleWriter",Acts::Logging::WARNING)),directory(std::move(path)) {
    generated.initialize("particles_generated_all");selected.initialize("particles_generated");simulated.initialize("particles_simulated");hits.initialize("simhits");hepmc.initialize("pythia8-event");vertices.initialize("vertices_generated");fs::create_directories(directory);
  }
  ProcessCode execute(const AlgorithmContext& ctx) const override {
    const auto& event=*hepmc(ctx);std::map<int,int> origins;std::set<int> originSet;
    for(const auto& p:event.particles()) {const auto tag=p->attribute_as_string("nodd_interaction");if(tag.empty())throw std::runtime_error("Missing authoritative Pythia interaction tag");int origin=std::stoi(tag);origins[p->id()]=origin;originSet.insert(origin);}
    if(originSet.size()!=201 || *originSet.begin()!=0 || *originSet.rbegin()!=200)throw std::runtime_error("Pythia interaction origin inventory differs from 1+200");
    Json labels=Json::array();std::map<unsigned,int> primaryOrigin;std::set<int> convertedOrigins;
    for(const auto& p:generated(ctx)) {int origin=origins.at(p.origParticleIdx());convertedOrigins.insert(origin);auto [it,inserted]=primaryOrigin.emplace(p.particleId().vertexPrimary(),origin);if(!inserted && it->second!=origin)throw std::runtime_error("Merged primary barcode spans generator interactions");labels.push_back({{"id",p.particleId().asArray()},{"interaction",origin},{"hard_scatter",origin==0}});}
    requireConvertedOrigins(convertedOrigins);
    Json primaryVertices=Json::array();for(const auto& v:vertices(ctx))if(v.id.vertexSecondary()==0)primaryVertices.push_back({{"id",v.id.barcode().asArray()},{"position4",vector(v.position4)}});
    Json row={{"schema_version",1},{"event",ctx.eventNumber},{"generated",particlesJson(generated(ctx))},{"selected",particlesJson(selected(ctx))},{"simulated",particlesJson(simulated(ctx))},{"hits",hitsJson(hits(ctx))},{"labels",labels},{"interaction_origins",originSet},{"primary_vertices",primaryVertices},{"barcode_primary_origin",primaryOrigin}};
    gzWrite(eventPath(directory,ctx.eventNumber),row.dump());return ProcessCode::SUCCESS;
  }
 private: std::string directory;ReadDataHandle<SimParticleContainer> generated{this,"AllGenerated"},selected{this,"SelectedGenerated"},simulated{this,"Simulated"};ReadDataHandle<SimHitContainer> hits{this,"Hits"};ReadDataHandle<std::shared_ptr<HepMC3::GenEvent>> hepmc{this,"HepMC"};ReadDataHandle<SimVertexContainer> vertices{this,"Vertices"};
};
class SampleReader final: public IReader {
 public:
  SampleReader(std::string path,std::size_t count,std::shared_ptr<const Acts::TrackingGeometry> geometry):directory(std::move(path)),events(count),trackingGeometry(std::move(geometry)) {generated.initialize("particles_generated_all");selected.initialize("particles_generated");simulated.initialize("particles_simulated");hits.initialize("simhits");metadata.initialize("pileup_sample_metadata");}
  std::string name()const override{return "PileupSampleReader";}
  std::pair<std::size_t,std::size_t> availableEvents()const override{return {0,events};}
  ProcessCode read(const AlgorithmContext& ctx)override {
    auto j=gzRead(eventPath(directory,ctx.eventNumber));if(j.at("event")!=ctx.eventNumber || j.at("schema_version")!=1)throw std::runtime_error("Sample event/schema mismatch");
    std::set<int> convertedOrigins;for(const auto& label:j.at("labels"))convertedOrigins.insert(label.at("interaction").get<int>());requireConvertedOrigins(convertedOrigins);
    auto g=restoreParticles(j.at("generated"),*trackingGeometry);auto s=restoreParticles(j.at("selected"),*trackingGeometry);auto p=restoreParticles(j.at("simulated"),*trackingGeometry);auto h=restoreHits(j.at("hits"));
    generated(ctx,std::move(g));selected(ctx,std::move(s));simulated(ctx,std::move(p));hits(ctx,std::move(h));
    Json meta={{"labels",j.at("labels")},{"interaction_origins",j.at("interaction_origins")},{"primary_vertices",j.at("primary_vertices")},{"barcode_primary_origin",j.at("barcode_primary_origin")},{"roundtrip_all_native_particle_and_hit_fields",true}};
    metadata(ctx,std::move(meta));return ProcessCode::SUCCESS;
  }
 private: std::string directory;std::size_t events;std::shared_ptr<const Acts::TrackingGeometry> trackingGeometry;WriteDataHandle<SimParticleContainer> generated{this,"AllGenerated"},selected{this,"SelectedGenerated"},simulated{this,"Simulated"};WriteDataHandle<SimHitContainer> hits{this,"Hits"};WriteDataHandle<Json> metadata{this,"SampleMetadata"};
};
class PileupAudit final: public IAlgorithm {
 public:
  explicit PileupAudit(const std::string& path): IAlgorithm("PileupAudit",Acts::getDefaultLogger("PileupAudit",Acts::Logging::WARNING)), directory(path) {
    fs::create_directories(directory);
    generated.initialize("particles_generated_all"); selectedGenerated.initialize("particles_generated"); metadata.initialize("pileup_sample_metadata"); simulated.initialize("particles_simulated");
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
      std::set<std::size_t> indices; std::vector<std::size_t> sharedMeasurements;
      for(const auto& state:track.trackStatesReversed()) {
        const auto sl=state.hasUncalibratedSourceLink() ? state.getUncalibratedSourceLink().getPtr<IndexSourceLink>() : nullptr;
        const auto flags=state.typeFlags();
        if(sl && flags.isMeasurement()) sharedMeasurements.push_back(sl->index());
        if(sl && flags.isMeasurement() && !flags.isOutlier()) indices.insert(sl->index());
      }
      std::vector<double> parameters,variance;bool covariancePositiveDefinite=false;
      if(track.hasReferenceSurface()) for(int i=0;i<6;++i) {parameters.push_back(track.parameters()[i]);variance.push_back(track.covariance()(i,i));}
      if(track.hasReferenceSurface() && track.covariance().allFinite()) {
        const Acts::BoundMatrix covariance=track.covariance();
        covariancePositiveDefinite=covariance.isApprox(covariance.transpose(),1.e-10)
          && Eigen::LLT<Acts::BoundMatrix>(covariance).info()==Eigen::Success;
      }
      result.push_back({{"index",track.index()},{"measurements",indices},{"shared_measurements",sharedMeasurements},
        {"hypothesis",{{"absolute_pdg",static_cast<int>(track.particleHypothesis().absolutePdg())},{"mass_GeV",track.particleHypothesis().mass()}}},
        {"nMeasurements",track.nMeasurements()},{"nHoles",track.nHoles()},{"nOutliers",track.nOutliers()},
        {"chi2",track.chi2()},{"ndf",track.nDoF()},{"reference",track.hasReferenceSurface()},
        {"parameters",parameters},{"variance",variance},{"covariance_positive_definite",covariancePositiveDefinite}});
    }
    return result;
  }
  ProcessCode execute(const AlgorithmContext& ctx) const override {
    Json row={{"event",ctx.eventNumber},{"simhits",hits(ctx).size()}};
    row["sample_metadata"]=metadata(ctx);
    std::map<std::array<std::uint32_t,5>,int> labels;
    for(const auto& l:metadata(ctx).at("labels")) labels[l.at("id").get<std::array<std::uint32_t,5>>()]=l.at("interaction");
    row["selected_generated_ids"]=Json::array();
    for(const auto& p:selectedGenerated(ctx))row["selected_generated_ids"].push_back(p.particleId().asArray());
    row["generated"]=Json::array();
    for(const auto& p:generated(ctx)) row["generated"].push_back({{"id",p.particleId().asArray()},
      {"pdg",static_cast<int>(p.pdg())},{"mass_GeV",p.mass()},{"charge",p.charge()},{"pt",p.transverseMomentum()},
      {"eta",std::asinh(p.direction().z()/std::hypot(p.direction().x(),p.direction().y()))},
      {"position_mm",{p.position().x(),p.position().y(),p.position().z()}},{"ct_mm",p.time()},
      {"vertex_primary",p.particleId().vertexPrimary()},{"vertex_secondary",p.particleId().vertexSecondary()},
      {"interaction",labels.at(p.particleId().asArray())},{"hard_scatter",labels.at(p.particleId().asArray())==0},
      {"truth",{Json(),Json(),p.phi(),p.theta(),p.qOverP(),p.time()}}});
    row["simulated_ids"]=Json::array();
    for(const auto& p:simulated(ctx)) row["simulated_ids"].push_back(p.particleId().asArray());
    row["simulated_particles"]=Json::array();
    for(const auto& p:simulated(ctx)) row["simulated_particles"].push_back({
      {"id",p.particleId().asArray()},{"parent_id",p.parentParticleId().asArray()},
      {"pdg",static_cast<int>(p.pdg())},{"mass_GeV",p.mass()},{"charge",p.charge()},
      {"process",static_cast<int>(p.process())},{"outcome",static_cast<int>(p.outcome())},
      {"initial_position_mm",{p.position().x(),p.position().y(),p.position().z()}},
      {"initial_ct_mm",p.time()},{"initial_direction",vector(p.direction())},
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
    gzWrite(eventPath(directory,ctx.eventNumber),row.dump());
    return ProcessCode::SUCCESS;
  }
 private:
  ReadDataHandle<SimParticleContainer> generated{this,"Generated"},selectedGenerated{this,"SelectedGenerated"},simulated{this,"Simulated"};
  ReadDataHandle<Json> metadata{this,"SampleMetadata"};
  ReadDataHandle<SimHitContainer> hits{this,"Hits"};
  ReadDataHandle<MeasurementContainer> measurements{this,"Measurements"};
  ReadDataHandle<MeasurementSubset> subset{this,"CompleteMeasurementSubset"};
  ReadDataHandle<MeasurementParticlesMap> associations{this,"Associations"};
  ReadDataHandle<Acts::SpacePointContainer> points{this,"MeasuredSpacePoints"};
  ReadDataHandle<Acts::SeedContainer> seeds{this,"GbtsSeeds"},estimated{this,"EstimatedSeeds"};
  ReadDataHandle<TrackParametersContainer> initialParameters{this,"EstimatedParameters"};
  ReadDataHandle<ConstTrackContainer> ckf{this,"Ckf"},ambi{this,"Ambiguity"};
  std::string directory;
};
void bindPileupAudit(py::module_& m) {
  m.def("_check_converted_origins",[](const std::vector<int>& values){requireConvertedOrigins(std::set<int>(values.begin(),values.end()));});
  py::class_<SampleWriter,IAlgorithm,std::shared_ptr<SampleWriter>>(m,"SampleWriter").def(py::init<std::string>());
  py::class_<SampleReader,IReader,std::shared_ptr<SampleReader>>(m,"SampleReader").def(py::init<std::string,std::size_t,std::shared_ptr<const Acts::TrackingGeometry>>());
  py::class_<PileupAudit,IAlgorithm,std::shared_ptr<PileupAudit>>(m,"PileupAudit").def(py::init<const std::string&>());
}
