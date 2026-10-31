// DES042 actual generated-filter controls; fixture values are not physics cuts.
#include "nodd/gbts/NoddRenamedGbtsTrackingFilter.hpp"
#include "nodd/gbts/NoddRenamedGbtsGeometry.hpp"
#include "nodd/gbts/NoddGuardedGbtsTrackingFilter.hpp"
#include "nodd/gbts/NoddGuardedGbtsGeometry.hpp"
#include "ActsPlugins/FpeMonitoring/FpeMonitor.hpp"
#include "DivisionAudit.hpp"
#include <array>
#include <bit>
#include <cfenv>
#include <iostream>
#include <limits>
#include <stdexcept>

namespace Acts::Experimental {
struct NoddGbtsNumericFixture {
  template<class Filter,class State> static bool update(const Filter& filter,
      const detail::GbtsNodeView& view,const detail::GbtsEdge& edge,State& state) {
    return filter.update(view,edge,state);
  }
};
}
namespace GB=Acts::Experimental;
using Monitor=ActsPlugins::FpeMonitor;
using Json=nlohmann::json;
void require(bool test,const char* message) {if(!test) throw std::runtime_error(message);}

// The two selected expressions are copied literally from the pinned source and
// correction. noinline keeps dynamic layer choice visible to the compiler.
__attribute__((noinline)) float originalLength(float tau2,bool barrel) {
  const float invSin2=1+tau2;
  return barrel?invSin2:invSin2/tau2;
}
__attribute__((noinline)) float correctedLength(float tau2,bool barrel) {
  const float invSin2=1+tau2;
  const float denominator=barrel?1.f:tau2;
  return invSin2/denominator;
}
struct Result {bool accepted;Json state;Monitor::Result fpes;};
template<class Filter,class Geometry,class State,class ZRange>
Result fixture(float tau,GB::GbtsLayerType type,int singularInnovation=0) {
  GB::GbtsLayerDescription layer{};layer.id=1;layer.type=type;
  layer.technology=GB::GbtsLayerTechnology::Pixel;
  layer.refCoord=type==GB::GbtsLayerType::Barrel?1.f:10.f;
  layer.minBound=type==GB::GbtsLayerType::Barrel?-1000.f:1.f;
  layer.maxBound=type==GB::GbtsLayerType::Barrel?1000.f:20.f;
  layer.layerThickness=1.f;
  layer.barrelOrder=type==GB::GbtsLayerType::Barrel?0:-1;
  const std::array layers{layer};const std::array<GB::GbtsLayerConnection,0> connections{};
  auto geometry=std::make_shared<Geometry>(layers,connections,.2f,ZRange{-1000.f,1000.f});
  typename Filter::Config config{};config.maxZ0=1000.f;
  if(singularInnovation) config.radLen=0.f;
  // Exact binary square: native FMA must also see a genuinely zero sum.
  // The production sigmaX is unchanged; this is only an adverse fixture.
  if(singularInnovation==1) config.sigmaX=.125f;
  Filter filter(config,geometry,Acts::getDefaultLogger("Fixture",Acts::Logging::FATAL));
  const std::array<std::array<float,4>,2> positions{{{1.f,0.f,0.f,1.f},{2.f,0.f,0.f,2.f}}};
  const std::array<GB::GbtsLayerIndex,2> layerIndices{0,0};
  const GB::detail::GbtsNodeView view{positions,layerIndices,{}, {}};
  GB::detail::GbtsEdge edge{};edge.n1=0;edge.n2=1;
  State state{};state.initialized=true;state.c=1.f;state.s=0.f;state.refX=1.f;state.refY=1.f;
  state.y={0.f,tau};state.cx[0][0]=.25f;state.cx[1][1]=.001f;state.cx[2][2]=.001f;
  state.cy[0][0]=1.5f;state.cy[1][1]=.001f;
  if(singularInnovation==1) state.cx[0][0]=-config.sigmaX*config.sigmaX;
  if(singularInnovation==2) state.cy[0][0]=-config.sigmaY*config.sigmaY;
  nodd::gbts::resetAudit(0);
  bool accepted;Monitor::Result fpes;
  {
    Monitor monitor;accepted=GB::NoddGbtsNumericFixture::update(filter,view,edge,state);
    fpes=monitor.result();
  }
  Json out={{"x",nodd::gbts::bits(state.x)},{"y",nodd::gbts::bits(state.y)},
    {"cx",nodd::gbts::bits(state.cx)},{"cy",nodd::gbts::bits(state.cy)},
    {"score",nodd::gbts::bits(state.j)},
    {"ref",{nodd::gbts::bits(state.refX),nodd::gbts::bits(state.refY),nodd::gbts::bits(state.c),nodd::gbts::bits(state.s)}}};
  return {accepted,std::move(out),std::move(fpes)};
}
Result originalFixture(float tau,GB::GbtsLayerType type,int singular=0) {
  return fixture<GB::NoddRenamedGbtsTrackingFilter,GB::NoddRenamedGbtsGeometry,
    GB::detail::NoddRenamedGbtsEdgeState,GB::NoddRenamedGbtsZ0Range>(tau,type,singular);
}
Result correctedFixture(float tau,GB::GbtsLayerType type,int singular=0) {
  return fixture<GB::NoddGuardedGbtsTrackingFilter,GB::NoddGuardedGbtsGeometry,
    GB::detail::NoddGuardedGbtsEdgeState,GB::NoddGuardedGbtsZ0Range>(tau,type,singular);
}
bool div(const Result& r) {return r.fpes.encountered(ActsPlugins::FpeType::FLTDIV);}
int main() {
  require(Monitor::isSupported(),"Native FPE monitor unavailable");
  require(std::fegetround()==FE_TONEAREST,"Rounding mode differs from native round-to-nearest");
  std::size_t expressionComparisons=0,filterComparisons=0;
  // Binary32 exponent-stratified and deterministic mantissa fixtures. Integer
  // bit construction is independent of all campaign RNG engines.
  std::vector<std::uint32_t> values{0U,0x80000000U,1U,0x80000001U,0x007fffffU,0x00800000U,0x7f7fffffU};
  std::uint32_t state=0x95a711U;
  for(unsigned e=0;e<255;++e) for(unsigned j=0;j<1024;++j) {
    state=1664525U*state+1013904223U;values.push_back((e<<23)|(state&0x007fffffU));
  }
  for(const auto bits:values) {
    const float tau2=std::bit_cast<float>(bits);
    for(bool barrel:{false,true}) {
      float expected,observed;
      {Monitor mon;expected=originalLength(tau2,barrel);}
      {Monitor mon;observed=correctedLength(tau2,barrel);
        if(barrel) require(!mon.result().hasStackTraces(),"Corrected barrel expression raised FPE");}
      require(std::bit_cast<std::uint32_t>(expected)==std::bit_cast<std::uint32_t>(observed),"Selected expression bits changed");
      ++expressionComparisons;
    }
  }
  const std::array taus{0.f,-0.f,std::numeric_limits<float>::denorm_min(),-std::numeric_limits<float>::denorm_min(),
    std::numeric_limits<float>::min(),-std::numeric_limits<float>::min(),.001f,-.001f,1.f,-1.f,20.f,-20.f,
    0x1p-60f,0x1p60f,std::numeric_limits<float>::infinity(),-std::numeric_limits<float>::infinity(),
    std::numeric_limits<float>::quiet_NaN()};
  for(float tau:taus) for(auto type:{GB::GbtsLayerType::Barrel,GB::GbtsLayerType::Endcap}) {
    const auto a=originalFixture(tau,type),b=correctedFixture(tau,type);
    require(a.accepted==b.accepted && a.state==b.state,"Actual filter selected state changed");++filterComparisons;
    if(tau==0.f) {
      if(type==GB::GbtsLayerType::Barrel) {
#ifdef NODD_STRICT_FIXTURE
        require(!div(a),"Strict original unexpectedly speculated barrel divide");
#else
        require(div(a),"Original speculative barrel FLTDIV positive control absent");
#endif
        require(!b.fpes.hasStackTraces(),"Corrected actual barrel-zero filter raised FPE");
      } else require(div(a)&&div(b),"Genuine endcap-zero FLTDIV was suppressed");
    }
  }
  for(int singular:{1,2}) {
    const auto a=originalFixture(1.f,GB::GbtsLayerType::Barrel,singular),b=correctedFixture(1.f,GB::GbtsLayerType::Barrel,singular);
    require(div(a)&&div(b),"Genuine innovation-zero FLTDIV was suppressed");
    require(a.accepted==b.accepted && a.state==b.state,"Innovation control state changed");++filterComparisons;
  }
  std::cout<<Json{{"status","PASS"},{"expression_bit_comparisons",expressionComparisons},
    {"actual_filter_bit_comparisons",filterComparisons},{"barrel_signed_zero",true},
    {"endcap_and_innovation_exceptions_retained",true},
#ifdef NODD_STRICT_FIXTURE
    {"fp_mode","strict"},{"original_speculation_expected",false}
#else
    {"fp_mode","native"},{"original_speculation_positive_control",true}
#endif
  }.dump()<<'\n';
}
