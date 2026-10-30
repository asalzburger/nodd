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
#include <nlohmann/json.hpp>
#include <pybind11/pybind11.h>
#include <fstream>
#include <mutex>
#include <set>
#include <cmath>
using namespace ActsExamples;
using Json=nlohmann::json;
namespace py=pybind11;
static_assert(PYBIND11_INTERNALS_VERSION == NODD_EXPECTED_PYBIND11_INTERNALS_VERSION);

class ReconstructionAudit final: public IAlgorithm {
 public:
  explicit ReconstructionAudit(const std::string& path): IAlgorithm("ReconstructionAudit",Acts::getDefaultLogger("ReconstructionAudit",Acts::Logging::WARNING)), file(path) {
    if(!file) throw std::runtime_error("Cannot open all-event reconstruction audit");
    generated.initialize("particles_generated"); simulated.initialize("particles_simulated");
    hits.initialize("simhits"); measurements.initialize("measurements"); associations.initialize("measurement_particles_map");
    points.initialize("spacepoints"); seeds.initialize("seeds"); estimated.initialize("estimatedseeds");
    ckf.initialize("ckf_tracks"); ambi.initialize("ambi_tracks");
  }
  static Json seedData(const Acts::SeedContainer& container,const Acts::SpacePointContainer& sp) {
    auto result=Json::array();
    for(const auto& seed:container) {
      std::set<std::size_t> indices;
      for(const auto i:seed.spacePointIndices()) for(const auto& sl:sp.at(i).sourceLinks()) indices.insert(sl.get<IndexSourceLink>().index());
      result.push_back({{"measurements",indices},{"quality",seed.quality()}});
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
        states.push_back({{"geometry_id",state.referenceSurface().geometryId().value()},
                          {"measurement",sl ? Json(sl->index()) : Json()},
                          {"inlier",flags.isMeasurement()},
                          {"outlier",flags.isOutlier()},
                          {"hole",flags.isHole()}});
      }
      std::vector<double> parameters,variance;
      if(track.hasReferenceSurface()) for(int i=0;i<6;++i) {parameters.push_back(track.parameters()[i]);variance.push_back(track.covariance()(i,i));}
      result.push_back({{"index",track.index()},{"measurements",indices},{"states",states},
        {"nMeasurements",track.nMeasurements()},{"nHoles",track.nHoles()},{"nOutliers",track.nOutliers()},
        {"chi2",track.chi2()},{"ndf",track.nDoF()},{"reference",track.hasReferenceSurface()},
        {"parameters",parameters},{"variance",variance}});
    }
    return result;
  }
  ProcessCode execute(const AlgorithmContext& ctx) const override {
    Json row={{"event",ctx.eventNumber},{"simhits",hits(ctx).size()}};
    row["generated"]=Json::array();
    for(const auto& p:generated(ctx)) row["generated"].push_back({{"id",p.particleId().asArray()},
      {"charge",p.charge()},{"pt",p.transverseMomentum()},{"eta",std::asinh(p.direction().z()/std::hypot(p.direction().x(),p.direction().y()))},
      {"truth",{0.,0.,p.phi(),p.theta(),p.qOverP(),p.time()}}});
    row["simulated_ids"]=Json::array();
    for(const auto& p:simulated(ctx)) row["simulated_ids"].push_back(p.particleId().asArray());
    row["measurements"]=Json::array();
    const auto& ms=measurements(ctx);const auto& mp=associations(ctx);
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
  ReadDataHandle<MeasurementParticlesMap> associations{this,"Associations"};
  ReadDataHandle<Acts::SpacePointContainer> points{this,"MeasuredSpacePoints"};
  ReadDataHandle<Acts::SeedContainer> seeds{this,"GbtsSeeds"},estimated{this,"EstimatedSeeds"};
  ReadDataHandle<ConstTrackContainer> ckf{this,"Ckf"},ambi{this,"Ambiguity"};
  mutable std::mutex mutex;mutable std::ofstream file;
};
PYBIND11_MODULE(nodd_reconstruction,m) {
  py::class_<ReconstructionAudit,IAlgorithm,std::shared_ptr<ReconstructionAudit>>(m,"ReconstructionAudit").def(py::init<const std::string&>());
}
