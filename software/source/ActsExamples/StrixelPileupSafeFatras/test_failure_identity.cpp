// Synthetic failure fixture; validates observation, queue, output and RNG identity.
#include "nodd/ttbar_safe_fatras/TtbarMultiParticleSimulation.hpp"
#include "FailureAudit.hpp"
#include <random>
#include <iostream>
#include <stdexcept>
#include <system_error>
using namespace ActsFatras;
static void require(bool c,const char* m){if(!c)throw std::runtime_error(m);}
struct All {bool operator()(const Particle&)const{return true;}};
struct FixtureSimulator {
  template<class Generator>
  Acts::Result<SingleParticleSimulationResult> simulate(const Acts::GeometryContext&,const Acts::MagneticFieldContext&,
                                                        Generator& rng,const Particle& p)const {
    (void)rng();
    if(p.particleId().particle()==1 || (p.particleId().generation()==1 && p.particleId().subParticle()==0))
      return std::make_error_code(std::errc::operation_canceled);
    SingleParticleSimulationResult r;r.particle=p;
    if(p.particleId().particle()==2 && p.particleId().generation()==0) {
      r.generatedParticles.push_back(p.withParticleId(p.particleId().withGeneration(1).withSubParticle(0)));
      r.generatedParticles.push_back(p.withParticleId(p.particleId().withGeneration(1).withSubParticle(1)));
    }
    return r;
  }
};
int main() {
  TtbarMultiParticleSimulation<All,FixtureSimulator,All,FixtureSimulator> simulation(FixtureSimulator{},FixtureSimulator{});
  std::vector<Particle> input;for(unsigned i=1;i<=3;++i) {Particle p(Barcode().withVertexPrimary(1).withParticle(i),Acts::PdgParticle::eMuon);p.setAbsoluteMomentum(2.+i).setDirection(.2,.3,1.);input.push_back(p);}
  std::vector<Particle> initial,final;std::vector<Hit> hits;std::mt19937_64 rng(8123),expectedRng(8123);
  auto result=simulation.simulate(Acts::GeometryContext::dangerouslyDefaultConstruct(),Acts::MagneticFieldContext{},rng,input,initial,final,hits);
  require(result.ok() && result->size()==2,"Unexpected failure inventory");
  require(result->at(0).particle.particleId()==input[0].particleId(),"Erased primary failure identity changed");
  require(result->at(1).particle.particleId()==input[1].particleId().withGeneration(1).withSubParticle(0),"Erased middle-queue failure identity changed");
  require(result->at(0).particle.absoluteMomentum()==3. && result->at(1).particle.absoluteMomentum()==4.,"Failed initial momentum changed");
  require(initial.size()==3 && final.size()==3 && hits.empty(),"Simulation output/container changes");
  require(initial[0].particleId()==input[1].particleId() && initial[1].particleId()==input[1].particleId().withGeneration(1).withSubParticle(1) && initial[2].particleId()==input[2].particleId(),"Queue order changed");
  for(unsigned i=0;i<5;++i)(void)expectedRng();require(rng==expectedRng,"Diagnostic changed random-state consumption");
  nodd::ttbar_safe_fatras::resetFailureAudit();nodd::ttbar_safe_fatras::recordFailures(8,result.value());
  const auto audit=nlohmann::json::parse(nodd::ttbar_safe_fatras::failureAuditJson());
  require(audit["events"][0]["failures"][0]["initial_state"]["id"]==result->at(0).particle.particleId().asArray(),"Failure audit identity mismatch");
  require(rng==expectedRng,"Failure serialization changed RNG");
  std::cout<<"PASS: primary/end and secondary/middle erase identities, full failure audit, unchanged queue/output/RNG\n";
}
