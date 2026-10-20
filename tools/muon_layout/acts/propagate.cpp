// Isolated DES040 vacuum geometry PROTOTYPE. No detector response or material.
#include "Acts/Definitions/Units.hpp"
#include "Acts/ActsVersion.hpp"
#include "Acts/EventData/BoundTrackParameters.hpp"
#include "Acts/EventData/ParticleHypothesis.hpp"
#include "Acts/Geometry/CylinderVolumeBounds.hpp"
#include "Acts/Geometry/GenericCuboidVolumeBounds.hpp"
#include "Acts/Geometry/GeometryContext.hpp"
#include "Acts/Geometry/Polyhedron.hpp"
#include "Acts/Geometry/Portal.hpp"
#include "Acts/Geometry/PortalLinkBase.hpp"
#include "Acts/Geometry/TrackingGeometry.hpp"
#include "Acts/Geometry/TrackingGeometryVisitor.hpp"
#include "Acts/Geometry/TrackingVolume.hpp"
#include "Acts/MagneticField/MagneticFieldProvider.hpp"
#include "Acts/MagneticField/MagneticFieldError.hpp"
#include "Acts/Navigation/INavigationPolicy.hpp"
#include "Acts/Navigation/NavigationStream.hpp"
#include "Acts/Propagator/ActorList.hpp"
#include "Acts/Propagator/EigenStepper.hpp"
#include "Acts/Propagator/Navigator.hpp"
#include "Acts/Propagator/Propagator.hpp"
#include "Acts/Propagator/PropagatorError.hpp"
#include "Acts/Propagator/PropagatorState.hpp"
#include "Acts/Propagator/StandardAborters.hpp"
#include "Acts/Surfaces/Surface.hpp"
#include "Acts/Surfaces/CylinderSurface.hpp"
#include "Acts/Surfaces/CylinderBounds.hpp"
#include "Acts/Surfaces/DiscSurface.hpp"
#include "Acts/Surfaces/RadialBounds.hpp"
#include "Acts/Utilities/Logger.hpp"
#include <algorithm>
#include <array>
#include <bit>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <map>
#include <numbers>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace {
using V3 = Acts::Vector3;
namespace U = Acts::UnitConstants;
constexpr double worldRadiusM = 9.1, worldHalfZM = 11.5;
struct Options {
  std::string geometry, map, tracks, output, query, field="map", policy="indexed", mode="surface-audit";
  double bz=0., step=.05, tolerance=1e-8, rkTolerance=1e-11, pathLimit=100.;
  unsigned maxSteps=20000;
  bool inspect=false,rootAudit=false;
};
std::string jsonString(const std::string& s) {
  std::ostringstream o; o << '"';
  for (unsigned char c : s) {
    if (c=='"' || c=='\\') o << '\\' << c;
    else if (c=='\n') o << "\\n";
    else if (c=='\r') o << "\\r";
    else if (c=='\t') o << "\\t";
    else if (c<32) o << "\\u" << std::hex << std::setw(4) << std::setfill('0') << int(c) << std::dec;
    else o << c;
  }
  o << '"'; return o.str();
}
bool compatibleVersions(const Acts::VersionInfo& a,const Acts::VersionInfo& b) {
  return a.withoutCommit()==b.withoutCommit() && (!a.commitHash || !b.commitHash || a.commitHash==b.commitHash);
}
std::string csv(const std::string& s) {
  std::string out="\""; for(char c:s) { if(c=='"') out+='"'; out+=c; } return out+'"';
}
Options arguments(int argc,char** argv) {
  Options o;
  for(int i=1;i<argc;++i) {
    std::string k=argv[i];
    auto value=[&](){ if(++i>=argc) throw std::runtime_error("missing value: "+k); return std::string(argv[i]); };
    if(k=="--geometry") o.geometry=value(); else if(k=="--map") o.map=value();
    else if(k=="--tracks") o.tracks=value(); else if(k=="--output-dir") o.output=value();
    else if(k=="--query-field") o.query=value(); else if(k=="--field") o.field=value();
    else if(k=="--policy") o.policy=value(); else if(k=="--bz") o.bz=std::stod(value());
    else if(k=="--mode") o.mode=value();
    else if(k=="--boundary-mode") {o.mode=value();if(o.mode=="support-plane")o.mode="surface-audit";}
    else if(k=="--max-step-m") o.step=std::stod(value());
    else if(k=="--tolerance-m") o.tolerance=std::stod(value());
    else if(k=="--rk-tolerance-m") o.rkTolerance=std::stod(value());
    else if(k=="--path-limit-m") o.pathLimit=std::stod(value());
    else if(k=="--max-steps") o.maxSteps=std::stoul(value());
    else if(k=="--inspect-only") o.inspect=true;
    else if(k=="--audit-roots") o.rootAudit=true;
    else if(k=="--help") { std::cout << "--geometry TEXT --map BINARY --tracks TEXT --output-dir DIR\n"
      "[--field map|zero|constant --bz TESLA] [--policy indexed|exhaustive|unbounded]\n"
      "[--mode surface-audit|finite-portals]\n"
      "[--max-step-m .05 --tolerance-m 1e-8 --rk-tolerance-m 1e-11 --max-steps 20000 --path-limit-m 100]\n"
      "[--inspect-only] [--query-field POINTS]\n"; std::exit(0); }
    else throw std::runtime_error("unknown argument: "+k);
  }
  if(o.output.empty() || (o.query.empty() && o.geometry.empty())) throw std::runtime_error("output and geometry/query inputs required");
  if(o.field!="map" && o.field!="zero" && o.field!="constant") throw std::runtime_error("unknown field mode");
  if(o.policy!="indexed" && o.policy!="exhaustive" && o.policy!="unbounded") throw std::runtime_error("unknown policy");
  if(o.mode!="surface-audit" && o.mode!="finite-portals") throw std::runtime_error("unknown boundary mode");
  if(o.field=="map" && o.map.empty()) throw std::runtime_error("map mode requires --map");
  if(!(o.step>0 && o.tolerance>0 && o.rkTolerance>0 && o.pathLimit>0 && o.maxSteps>0) ||
     !std::isfinite(o.step+o.tolerance+o.rkTolerance+o.pathLimit+o.bz)) throw std::runtime_error("invalid numerical setting");
  return o;
}
double readReal(std::istream& input) {
  std::string token;if(!(input>>token))throw std::runtime_error("truncated numeric input");
  try {std::size_t used=0;double value=std::stod(token,&used);return used==token.size()?value:std::numeric_limits<double>::quiet_NaN();}
  catch(const std::exception&){return std::numeric_limits<double>::quiet_NaN();}
}
struct FaceInfo { std::size_t panel; unsigned face; bool large; std::uint64_t id; };
struct Hit { FaceInfo owner; V3 position,direction; double path; };
struct RootAudit {std::uint64_t id;V3 position;double path;std::size_t matched;};
struct StepAudit {std::uint64_t target,current;V3 position;double path,remaining;};
struct Capture {
  std::string id, fieldFailure;
  V3 position=V3::Zero(), direction=V3::Zero(), failedPosition=V3::Zero();
  double path=0.; std::size_t steps=0,fieldQueries=0,navQueries=0,navCandidates=0;
  std::size_t nativeRoots=0,finiteChecks=0,outsideRoots=0;
  std::size_t nativeCorrections=0,guardCaps=0,guardChecks=0;
  double curvaturePerM=0.,minGuardM=std::numeric_limits<double>::infinity();
  bool preserveTarget=false;
  std::unordered_set<std::uint64_t> parallelAmbiguities;
  bool exited=false, returned=false;
  std::vector<Hit> hits;
  std::vector<RootAudit> roots;
  std::vector<StepAudit> stepAudit;
};
struct FieldGrid {
  std::vector<double> r,z,phi; std::vector<float> b; std::vector<std::uint8_t> valid;
  std::size_t nr=0,nz=0,np=0;
  double maxNormT=0.;
  template<class T> static void read(std::ifstream& f,T* p,std::size_t n) {
    if(!f.read(reinterpret_cast<char*>(p),static_cast<std::streamsize>(n*sizeof(T)))) throw std::runtime_error("truncated field map");
  }
  explicit FieldGrid(const std::string& filename) {
    if constexpr(std::endian::native!=std::endian::little) throw std::runtime_error("little-endian map reader required");
    std::ifstream f(filename,std::ios::binary); if(!f) throw std::runtime_error("cannot read map: "+filename);
    char magic[8]; read(f,magic,8); if(std::string(magic,8)!="NODDMAP1") throw std::runtime_error("wrong map magic");
    std::array<std::uint64_t,3> n{}; read(f,n.data(),3);
    if(n[0]<2 || n[1]<2 || n[2]<2 || n[0]>10000 || n[1]>10000 || n[2]>10000 ||
       n[0]*n[1]*n[2]>100000000) throw std::runtime_error("invalid map dimensions");
    nr=n[0];nz=n[1];np=n[2];r.resize(nr);z.resize(nz);phi.resize(np);
    read(f,r.data(),nr);read(f,z.data(),nz);read(f,phi.data(),np);
    for(const auto* a:{&r,&z,&phi}) for(std::size_t j=0;j<a->size();++j)
      if(!std::isfinite((*a)[j]) || (j && (*a)[j]<=(*a)[j-1])) throw std::runtime_error("invalid field axis");
    if(std::abs(phi.front())>1e-12 || std::abs(phi.back()-30)>1e-12) throw std::runtime_error("map must cover phi0..30 degrees");
    b.resize(nr*nz*np*3);valid.resize(nr*nz*np);read(f,b.data(),b.size());read(f,valid.data(),valid.size());
    for(std::size_t j=0;j<valid.size();++j)if(valid[j]) {
      const double norm=std::hypot(double(b[3*j]),double(b[3*j+1]),double(b[3*j+2]));
      if(!std::isfinite(norm))throw std::runtime_error("nonfinite valid field node");
      maxNormT=std::max(maxNormT,norm);
    }
    // Trilinear weights are nonnegative and sum to1. Inflate a few ulps to
    // retain the norm bound under floating arithmetic, without changing fields.
    maxNormT*=1+32*std::numeric_limits<double>::epsilon();
    char extra; if(f.read(&extra,1)) throw std::runtime_error("unexpected map trailing bytes");
  }
  bool interpolate(const V3& p,V3& result,std::string& error) const {
    if(!p.allFinite()) {error="nonfinite_field_position";return false;}
    const double angle=std::atan2(p.y(),p.x()); double ph=std::fmod(angle*180/std::numbers::pi,30.);if(ph<0)ph+=30.;
    const std::array<double,3> q{std::hypot(p.x(),p.y()),p.z(),ph};
    const std::array<const std::vector<double>*,3> axes{&r,&z,&phi};
    std::array<std::size_t,3> index{};std::array<double,3> frac{};
    for(unsigned j=0;j<3;++j) {
      const auto& a=*axes[j]; if(q[j]<a.front() || q[j]>a.back()) {error="outside_map";return false;}
      auto k=std::upper_bound(a.begin(),a.end(),q[j])-a.begin();
      index[j]=std::clamp<std::size_t>(k?std::size_t(k-1):0,0,a.size()-2);
      frac[j]=(q[j]-a[index[j]])/(a[index[j]+1]-a[index[j]]);
    }
    V3 cylindrical=V3::Zero();
    for(unsigned i=0;i<2;++i)for(unsigned j=0;j<2;++j)for(unsigned k=0;k<2;++k) {
      std::size_t cell=((index[0]+i)*nz+index[1]+j)*np+index[2]+k;
      if(!valid[cell]) {error="field_masked";return false;}
      double weight=(i?frac[0]:1-frac[0])*(j?frac[1]:1-frac[1])*(k?frac[2]:1-frac[2]);
      for(unsigned c=0;c<3;++c) {
        if(!std::isfinite(b[cell*3+c])) {error="nonfinite_map_node";return false;}
        cylindrical[c]+=weight*double(b[cell*3+c]);
      }
    }
    double c=std::cos(angle),s=std::sin(angle);
    result={c*cylindrical[0]-s*cylindrical[1],s*cylindrical[0]+c*cylindrical[1],cylindrical[2]};return true;
  }
};
class Field final:public Acts::MagneticFieldProvider {
  struct Empty {};
  std::unique_ptr<FieldGrid> grid;
  std::string mode; double bz;
 public:
  mutable Capture* active=nullptr;
  double maxNormT=0.;
  explicit Field(const Options& o):mode(o.field),bz(o.bz) {if(mode=="map"){grid=std::make_unique<FieldGrid>(o.map);maxNormT=grid->maxNormT;}else if(mode=="constant")maxNormT=std::abs(bz);}
  Cache makeCache(const Acts::MagneticFieldContext&) const override {return Cache(std::in_place_type<Empty>);}
  Acts::Result<V3> getField(const V3& position,Cache&) const override {
    if(active)++active->fieldQueries;
    V3 b=V3::Zero();std::string error;
    if(!position.allFinite()) {
      if(active && active->fieldFailure.empty()){active->fieldFailure="nonfinite_field_position";active->failedPosition=position/U::m;}
      return Acts::Result<V3>::failure(Acts::make_error_code(Acts::MagneticFieldError::OutOfBounds));
    }
    if(mode=="constant")b.z()=bz;
    if(mode=="map" && !grid->interpolate(position/U::m,b,error)) {
      if(active && active->fieldFailure.empty()) {active->fieldFailure=error;active->failedPosition=position/U::m;}
      return Acts::Result<V3>::failure(Acts::make_error_code(Acts::MagneticFieldError::OutOfBounds));
    }
    return Acts::Result<V3>::success(V3(b*U::T));
  }
};
struct Panel {
  std::string id; int station; double depth;
  Acts::Transform3 transform; std::array<V3,8> vertices;
  V3 low,high,normal;
  std::vector<std::shared_ptr<Acts::Portal>> portals;
};
std::vector<Panel> readPanels(const std::string& filename) {
  std::ifstream f(filename);std::size_t n;if(!(f>>n) || !n || n>Acts::GeometryIdentifier::getMaxLayer()) throw std::runtime_error("invalid panel count");
  std::vector<Panel> panels;panels.reserve(n);std::set<std::string> ids;
  for(std::size_t i=0;i<n;++i) {
    Panel p;V3 origin;Acts::RotationMatrix3 rotation;std::array<Acts::Vector2,4> vertices;
    if(!(f>>p.id>>p.station>>p.depth>>origin.x()>>origin.y()>>origin.z()))throw std::runtime_error("truncated panel row");
    for(unsigned a=0;a<3;++a)for(unsigned b=0;b<3;++b)f>>rotation(a,b);
    for(auto& v:vertices)f>>v.x()>>v.y();
    if(!f || p.station<1 || p.station>3 || !(p.depth>0) || !std::isfinite(p.depth) || !origin.allFinite() ||
       !rotation.allFinite() || !(rotation.transpose()*rotation).isApprox(Acts::RotationMatrix3::Identity(),1e-10) || rotation.determinant()<.999999 || !ids.insert(p.id).second)
      throw std::runtime_error("invalid panel transform/identity");
    double area=0.;for(unsigned j=0;j<4;++j) {if(!vertices[j].allFinite())throw std::runtime_error("invalid panel vertex");auto& a=vertices[j];auto& b=vertices[(j+1)%4];area+=a.x()*b.y()-a.y()*b.x();}
    if(area<=0)throw std::runtime_error("panel footprint must be counterclockwise");
    p.transform=Acts::Transform3::Identity();p.transform.linear()=rotation;p.transform.translation()=origin*U::m;p.normal=rotation.col(2);
    p.low=V3::Constant(std::numeric_limits<double>::infinity());p.high=-p.low;
    for(unsigned j=0;j<8;++j) {
      p.vertices[j]=V3(vertices[j%4].x(),vertices[j%4].y(),(j<4?-.5:.5)*p.depth)*U::m;
      V3 g=p.transform*p.vertices[j];p.low=p.low.cwiseMin(g);p.high=p.high.cwiseMax(g);
      if(std::hypot(g.x(),g.y())>worldRadiusM*U::m || std::abs(g.z())>worldHalfZM*U::m)throw std::runtime_error("panel outside world");
    }
    panels.push_back(std::move(p));
  }
  std::string extra;if(f>>extra)throw std::runtime_error("unexpected geometry trailing text");return panels;
}
struct Cell {int x,y,z;bool operator==(const Cell&)const=default;};
struct CellHash {std::size_t operator()(const Cell& a)const noexcept {return std::size_t(a.x*73856093LL)^std::size_t(a.y*19349663LL)^std::size_t(a.z*83492791LL);}};
struct Scene {
  std::vector<Panel> panels;
  std::shared_ptr<Acts::TrackingVolume> world;
  std::shared_ptr<const Acts::TrackingGeometry> geometry;
  std::unordered_map<const Acts::Surface*,FaceInfo> faces;
  std::unordered_map<Cell,std::vector<std::size_t>,CellHash> cells;
  std::vector<std::shared_ptr<Acts::Portal>> outer;
  std::vector<std::shared_ptr<Acts::Surface>> entrance;
  std::unordered_map<const Acts::Surface*,double> entranceSign;
  std::unordered_map<const Acts::Surface*,double> outerSign;
  double cellSize=U::m, searchRadius,maxStepM;
  bool indexed,bounded,audit;
  mutable Capture* active=nullptr;
  std::size_t visitedVolumes=0,largeFaces=0;
  static int cell(double x,double size){return int(std::floor(x/size));}
  Scene(const Options& o):panels(readPanels(o.geometry)),searchRadius((2*o.step+2*o.tolerance)*U::m),maxStepM(o.step),indexed(o.policy=="indexed"),bounded(o.policy!="unbounded"),audit(o.mode=="surface-audit"){}
  std::vector<std::size_t> nearby(const V3& position) const {
    V3 lo=position-V3::Constant(searchRadius),hi=position+V3::Constant(searchRadius);
    std::vector<std::size_t> candidate;
    if(!indexed) {
      candidate.reserve(panels.size());for(std::size_t i=0;i<panels.size();++i)candidate.push_back(i);
      if(!bounded)return candidate;
    } else for(int x=cell(lo.x(),cellSize);x<=cell(hi.x(),cellSize);++x)
      for(int y=cell(lo.y(),cellSize);y<=cell(hi.y(),cellSize);++y)
        for(int z=cell(lo.z(),cellSize);z<=cell(hi.z(),cellSize);++z) {
          auto found=cells.find({x,y,z});if(found!=cells.end())candidate.insert(candidate.end(),found->second.begin(),found->second.end());
        }
    std::sort(candidate.begin(),candidate.end());candidate.erase(std::unique(candidate.begin(),candidate.end()),candidate.end());
    candidate.erase(std::remove_if(candidate.begin(),candidate.end(),[&](auto i) {
      V3 delta=(panels[i].low-position).cwiseMax(V3::Zero())+(position-panels[i].high).cwiseMax(V3::Zero());
      return delta.squaredNorm()>searchRadius*searchRadius;
    }),candidate.end());return candidate;
  }
};
class RefreshPolicy final:public Acts::INavigationPolicy {
  struct State {V3 position=V3::Zero(),direction=V3::Zero();bool ready=false;};
  const Acts::TrackingVolume& volume;const Scene& scene;bool world;
 public:
  RefreshPolicy(const Acts::TrackingVolume& v,const Scene& s,bool w):volume(v),scene(s),world(w){}
  void createState(const Acts::GeometryContext&,const Acts::NavigationArguments&,Acts::NavigationPolicyStateManager& m,const Acts::Logger&)const override {m.pushState<State>();}
  bool isValid(const Acts::GeometryContext&,const Acts::NavigationArguments& a,Acts::NavigationPolicyState& s,const Acts::Logger&)const override {
    // The native RKN target may need a negative correction after overshooting
    // its support. Refreshing here would discard that target as behind us.
    if(scene.audit && scene.active && scene.active->preserveTarget)return true;
    const auto& p=s.as<State>();return p.ready && (a.position-p.position).squaredNorm()<=1e-20 && (a.direction-p.direction).squaredNorm()<=1e-24;
  }
  void initializeCandidates(const Acts::GeometryContext&,const Acts::NavigationArguments& a,Acts::NavigationPolicyState& s,Acts::AppendOnlyNavigationStream& stream,const Acts::Logger&)const {
    auto& p=s.as<State>();p.position=a.position;p.direction=a.direction;p.ready=true;std::size_t count=0;
    if(scene.audit) {
      // All roots remain ACTS roots of the actual native surfaces. Infinite
      // candidate bounds discover curved edge entries; Recorder applies the
      // unchanged finite bounds at the native root, including coplanar owners.
      for(const auto& surface:scene.entrance){stream.addSurfaceCandidate(*surface,Acts::BoundaryTolerance::Infinite());++count;}
      for(const auto& portal:scene.outer){stream.addSurfaceCandidate(portal->surface(),Acts::BoundaryTolerance::Infinite());++count;}
      auto addPanel=[&](std::size_t i){for(const auto& portal:scene.panels[i].portals){stream.addSurfaceCandidate(portal->surface(),Acts::BoundaryTolerance::Infinite());++count;}};
      for(auto i:scene.nearby(a.position))addPanel(i);
    } else {
      if(world)for(const auto& surface:scene.entrance){stream.addSurfaceCandidate(*surface,Acts::BoundaryTolerance::None());++count;}
      if(world && scene.indexed) {
      for(const auto& portal:scene.outer){stream.addPortalCandidate(*portal);++count;}
      for(auto i:scene.nearby(a.position))for(const auto& portal:scene.panels[i].portals){stream.addPortalCandidate(*portal);++count;}
      } else for(const auto& portal:volume.portals()){stream.addPortalCandidate(portal);++count;}
    }
    if(scene.active){++scene.active->navQueries;scene.active->navCandidates+=count;}
  }
  void connect(Acts::NavigationDelegate& d)const override {connectDefault<RefreshPolicy>(d);}
};
void build(Scene& s,const Acts::GeometryContext& context,const Acts::Logger& logger) {
  s.world=std::make_shared<Acts::TrackingVolume>(Acts::Transform3::Identity(),std::make_shared<Acts::CylinderVolumeBounds>(0.,worldRadiusM*U::m,worldHalfZM*U::m),"world");
  s.world->assignGeometryId(Acts::GeometryIdentifier{}.withVolume(1));unsigned face=0;
  for(auto& os:s.world->volumeBounds().orientedSurfaces(Acts::Transform3::Identity())) {
    os.surface->assignGeometryId(s.world->geometryId().withBoundary(++face));
    s.outerSign[os.surface.get()]=os.surface->center(context).z()<0?-1.:1.;
    auto portal=std::make_shared<Acts::Portal>(os.direction,os.surface,*s.world);s.outer.push_back(portal);s.world->addPortal(portal);
  }
  // Native virtual closed MS entrance: no material and never a muon hit.
  s.entrance.push_back(Acts::Surface::makeShared<Acts::CylinderSurface>(Acts::Transform3::Identity(),std::make_shared<Acts::CylinderBounds>(4.35*U::m,6.5*U::m)));
  for(double side:{-1.,1.}) {
    Acts::Transform3 transform=Acts::Transform3::Identity();transform.translation()=V3(0,0,side*6.5*U::m);
    s.entrance.push_back(Acts::Surface::makeShared<Acts::DiscSurface>(transform,std::make_shared<Acts::RadialBounds>(0.,4.35*U::m)));
  }
  for(std::size_t i=0;i<s.entrance.size();++i) {
    auto& surface=s.entrance[i];surface->assignGeometryId(s.world->geometryId().withSensitive(i+1));
    s.entranceSign[surface.get()]=(i==1?-1.:1.);s.world->addSurface(surface);
  }
  for(std::size_t i=0;i<s.panels.size();++i) {
    auto& p=s.panels[i];auto leaf=std::make_unique<Acts::TrackingVolume>(p.transform,std::make_shared<Acts::GenericCuboidVolumeBounds>(p.vertices),p.id);
    auto id=Acts::GeometryIdentifier{}.withVolume(2).withLayer(i+1);leaf->assignGeometryId(id);face=0;unsigned large=0;
    for(auto& os:leaf->volumeBounds().orientedSurfaces(p.transform)) {
      auto fid=id.withBoundary(face+1);os.surface->assignGeometryId(fid);V3 c=os.surface->center(context);V3 n=os.surface->normal(context,c);
      bool isLarge=std::abs(n.dot(p.normal))>1-1e-10;large+=isLarge;
      s.faces[os.surface.get()]={i,face,isLarge,fid.value()};
      auto portal=std::make_shared<Acts::Portal>(os.direction,os.surface,*leaf);portal->fill(*s.world);leaf->addPortal(portal);s.world->addPortal(portal);p.portals.push_back(portal);++face;
    }
    if(face!=6 || large!=2)throw std::runtime_error("wrong native face classification");s.largeFaces+=large;
    leaf->setNavigationPolicy(std::make_unique<RefreshPolicy>(*leaf,s,false));leaf->navigationPolicy()->initializeStatelessCache(context,logger);s.world->addVolume(std::move(leaf));
    for(int x=Scene::cell(p.low.x(),s.cellSize);x<=Scene::cell(p.high.x(),s.cellSize);++x)
      for(int y=Scene::cell(p.low.y(),s.cellSize);y<=Scene::cell(p.high.y(),s.cellSize);++y)
        for(int z=Scene::cell(p.low.z(),s.cellSize);z<=Scene::cell(p.high.z(),s.cellSize);++z)s.cells[{x,y,z}].push_back(i);
  }
  s.world->setNavigationPolicy(std::make_unique<RefreshPolicy>(*s.world,s,true));s.world->navigationPolicy()->initializeStatelessCache(context,logger);
  s.geometry=std::make_shared<Acts::TrackingGeometry>(s.world,nullptr,Acts::GeometryIdentifierHook{},logger,false);
  struct Audit:Acts::TrackingGeometryVisitor {
    std::size_t volumes=0;std::set<std::uint64_t> ids;std::unordered_set<const Acts::Surface*> surfaces;
    void visitVolume(const Acts::TrackingVolume& v)override {++volumes;if(!ids.insert(v.geometryId().value()).second)throw std::runtime_error("duplicate native volume ID");}
    void visitPortal(const Acts::Portal& p)override {if(surfaces.insert(&p.surface()).second && !ids.insert(p.surface().geometryId().value()).second)throw std::runtime_error("duplicate native portal ID");}
  }audit;
  s.geometry->apply(audit);s.visitedVolumes=audit.volumes;
  if(audit.volumes!=s.panels.size()+1 || audit.surfaces.size()!=s.faces.size()+s.outer.size() || s.geometry->geometryVersion()!=Acts::TrackingGeometry::GeometryVersion::Gen3)throw std::runtime_error("native geometry audit count/version failed");
}
void exportGeometry(const Scene& s,const Acts::GeometryContext& context,const std::filesystem::path& output) {
  std::ofstream f(output/"geometry.csv"),corners(output/"geometry-corners.csv");f<<std::setprecision(17);corners<<std::setprecision(17);
  f<<"panel_index,face_index,is_large,geometry_id,cx_m,cy_m,cz_m,nx,ny,nz\n";
  corners<<"panel_index,face_index,vertex_index,x_m,y_m,z_m\n";
  for(const auto& p:s.panels)for(const auto& portal:p.portals) {
    auto& sf=portal->surface();auto info=s.faces.at(&sf);V3 c=sf.center(context)/U::m,n=sf.normal(context,sf.center(context));
    f<<info.panel<<','<<info.face<<','<<info.large<<','<<info.id<<','<<c.x()<<','<<c.y()<<','<<c.z()<<','<<n.x()<<','<<n.y()<<','<<n.z()<<'\n';
    auto poly=sf.polyhedronRepresentation(context,1);unsigned j=0;for(const auto& v:poly.vertices){auto q=(v/U::m).eval();corners<<info.panel<<','<<info.face<<','<<j++<<','<<q.x()<<','<<q.y()<<','<<q.z()<<'\n';}
  }
}
struct Recorder {
  const Scene* scene=nullptr;std::shared_ptr<Capture> capture;bool auditRoots=false;
  struct result_type {};
  template<class State,class Stepper,class Navigator>
  void guard(State& state,const Stepper& stepper,const Navigator& nav)const {
    auto& c=*capture;
    if(!scene->audit || c.preserveTarget || !(c.curvaturePerM>0))return;
    const auto& gctx=state.options.geoContext.get();
    const V3 position=stepper.position(state.stepping);
    const double tolerance=state.options.surfaceTolerance/U::m;
    double limit=scene->maxStepM;
    auto consider=[&](const Acts::Surface& sf) {
      if(sf.type()!=Acts::Surface::Plane && sf.type()!=Acts::Surface::Disc)return;
      ++c.guardChecks;
      const V3 normal=sf.normal(gctx,position,c.direction);
      const double g=normal.dot(position-sf.center(gctx))/U::m;
      const double vn=normal.dot(c.direction),gap=std::abs(g);
      if(g*vn<0)return; // A forward tangent root is native Navigator's task.
      // Before a first crossing, signed distance is bounded below by
      // gap+|vn|s-kappa*s^2/2. If this is positive through maxStep, no guard
      // is needed. This also avoids tiny caps immediately after normal exits.
      if(gap+std::abs(vn)*scene->maxStepM>.5*c.curvaturePerM*scene->maxStepM*scene->maxStepM)return;
      if(gap<=tolerance) {
        if(nav.currentSurface(state.navigation)==nullptr)c.parallelAmbiguities.insert(sf.geometryId().value());
        return; // No invented hit or artificial zero-length step at a graze.
      }
      const double safe=2*gap/(std::sqrt(vn*vn+2*c.curvaturePerM*gap)+std::abs(vn));
      limit=std::min(limit,.8*safe);
    };
    auto panel=[&](std::size_t i){for(const auto& portal:scene->panels[i].portals)consider(portal->surface());};
    for(auto i:scene->nearby(position))panel(i);
    for(const auto& surface:scene->entrance)consider(*surface);
    for(const auto& portal:scene->outer)consider(portal->surface());
    if(limit<scene->maxStepM) {
      stepper.updateStepSize(state.stepping,limit*U::m,Acts::ConstrainedStep::Type::Actor);
      ++c.guardCaps;c.minGuardM=std::min(c.minGuardM,limit);
    }
  }
  template<class State,class Stepper,class Navigator>
  Acts::Result<void> act(State& state,const Stepper& stepper,const Navigator& nav,result_type&,const Acts::Logger&)const {
    auto& c=*capture;c.position=stepper.position(state.stepping)/U::m;c.direction=stepper.direction(state.stepping);c.path=state.stepping.pathAccumulated/U::m;c.steps=state.stepping.nSteps;c.exited=c.exited||nav.endOfWorldReached(state.navigation);
    if(state.stage==Acts::PropagatorStage::postStep) {
      c.preserveTarget=scene->audit && nav.currentSurface(state.navigation)==nullptr && stepper.getStepSize(state.stepping,Acts::ConstrainedStep::Type::Navigator)<0;
      if(c.preserveTarget)++c.nativeCorrections;
      if(auditRoots)c.stepAudit.push_back({state.navigation.stream.isValid()?state.navigation.navCandidate().surface().geometryId().value():0,nav.currentSurface(state.navigation)?nav.currentSurface(state.navigation)->geometryId().value():0,c.position,c.path,stepper.getStepSize(state.stepping,Acts::ConstrainedStep::Type::Navigator)/U::m});
    }
    if(state.stage==Acts::PropagatorStage::prePropagation || state.stage==Acts::PropagatorStage::postStep)guard(state,stepper,nav);
    if(state.stage!=Acts::PropagatorStage::postStep)return {};
    const auto* surface=nav.currentSurface(state.navigation);if(!surface)return {};
    ++c.nativeRoots;
    const auto& gctx=state.options.geoContext.get();const V3 position=stepper.position(state.stepping);const double tolerance=state.options.surfaceTolerance;
    auto onFinite=[&](const Acts::Surface& sf){++c.finiteChecks;return sf.isOnSurface(gctx,position,c.direction,Acts::BoundaryTolerance::None(),tolerance);};
    if(scene->audit) {
      // A supporting root may lie outside the finite owning panel. Audit all
      // nearby finite faces at exactly this ACTS root, so coincident supports
      // cannot hide an owner. No trajectory segment or interpolated point is used.
      std::size_t matched=0;
      auto auditPanel=[&](std::size_t i){for(const auto& portal:scene->panels[i].portals)if(onFinite(portal->surface())){c.hits.push_back({scene->faces.at(&portal->surface()),c.position,c.direction,c.path});++matched;}};
      for(auto i:scene->nearby(position))auditPanel(i);
      if(scene->faces.contains(surface) && !matched)++c.outsideRoots;
      if(auditRoots)c.roots.push_back({surface->geometryId().value(),c.position,c.path,matched});
      for(const auto& sf:scene->entrance)if(onFinite(*sf)) {
        V3 normal=scene->entranceSign.at(sf.get())*sf->normal(gctx,position,c.direction);
        if(normal.dot(c.direction)<-1e-12)c.returned=true;
      }
      for(const auto& portal:scene->outer)if(onFinite(portal->surface())) {
        V3 normal=scene->outerSign.at(&portal->surface())*portal->surface().normal(gctx,position,c.direction);
        if(normal.dot(c.direction)>1e-12)c.exited=true;
      }
      return {};
    }
    auto virtualFace=scene->entranceSign.find(surface);
    if(virtualFace!=scene->entranceSign.end()) {
      V3 normal=virtualFace->second*surface->normal(state.options.geoContext.get(),stepper.position(state.stepping),stepper.direction(state.stepping));
      if(normal.dot(c.direction)<-1e-12)c.returned=true;
    }
    auto found=scene->faces.find(surface);if(found!=scene->faces.end())c.hits.push_back({found->second,c.position,c.direction,c.path});return {};
  }
  template<class State,class Stepper,class Navigator>
  bool checkAbort(State&,const Stepper&,const Navigator&,result_type&,const Acts::Logger&)const {return capture->returned||capture->exited;}
};
struct Track {std::string id;double p,q;V3 position,direction;};
std::vector<Track> readTracks(const std::string& filename) {
  std::ifstream f(filename);std::size_t n;if(!(f>>n))throw std::runtime_error("invalid track file");std::vector<Track> out;out.reserve(n);
  for(std::size_t i=0;i<n;++i){Track t;if(!(f>>t.id))throw std::runtime_error("truncated track identity");t.p=readReal(f);t.q=readReal(f);for(unsigned j=0;j<3;++j)t.position[j]=readReal(f);for(unsigned j=0;j<3;++j)t.direction[j]=readReal(f);out.push_back(t);}
  std::string extra;if(f>>extra)throw std::runtime_error("unexpected tracks trailing text");return out;
}
struct RunTotals {std::size_t tracks=0,hits=0,queries=0,navQueries=0,navCandidates=0,nativeRoots=0,finiteChecks=0,outsideRoots=0,nativeCorrections=0,guardCaps=0,guardChecks=0,parallelAmbiguities=0;double maxFieldNormT=0.,maxCurvaturePerM=0.,minGuardM=std::numeric_limits<double>::infinity();std::map<std::string,std::size_t> statuses;};
RunTotals propagate(Scene& scene,const Options& o,const std::shared_ptr<Field>& field,const Acts::GeometryContext& gctx,const Acts::MagneticFieldContext& mctx,const std::filesystem::path& output) {
  std::ofstream hits(output/"hits.csv"),tracks(output/"tracks.csv");hits<<std::setprecision(17);tracks<<std::setprecision(17);
  std::ofstream roots;if(o.rootAudit){roots.open(output/"root-audit.csv");roots<<std::setprecision(17)<<"track_id,target_geometry_id,path_m,x_m,y_m,z_m,finite_matched_faces\n";}
  std::ofstream steps;if(o.rootAudit){steps.open(output/"step-audit.csv");steps<<std::setprecision(17)<<"track_id,target_geometry_id,current_geometry_id,path_m,x_m,y_m,z_m,native_remaining_step_m\n";}
  hits<<"track_id,sequence,panel_index,face_index,is_large,geometry_id,x_m,y_m,z_m,path_m,dx,dy,dz\n";
  tracks<<"track_id,status,error,path_m,steps,x_m,y_m,z_m,field_queries,native_corrections,guard_caps,parallel_ambiguities,min_guard_m\n";
  using Stepper=Acts::EigenStepper<>;using Propagator=Acts::Propagator<Stepper,Acts::Navigator>;
  Acts::Navigator::Config config;config.trackingGeometry=scene.geometry;config.resolveSensitive=false;config.resolveMaterial=false;config.resolvePassive=true;
  Propagator prop{Stepper(field),Acts::Navigator(config,Acts::getDefaultLogger("MuonNavigator",Acts::Logging::ERROR)),Acts::getDefaultLogger("MuonPropagator",Acts::Logging::ERROR)};
  RunTotals total;total.maxFieldNormT=field->maxNormT;auto inputs=readTracks(o.tracks);
  for(const auto& t:inputs) {
    auto c=std::make_shared<Capture>();c->id=t.id;c->position=t.position;c->direction=t.direction;field->active=c.get();scene.active=c.get();std::string status,error;
    try {
      if(!(t.p>0) || !std::isfinite(t.p+t.q) || std::abs(t.q)!=1 || !t.position.allFinite() || !t.direction.allFinite() || std::abs(t.direction.norm()-1)>1e-8)throw std::runtime_error("nonfinite or invalid track input");
      c->curvaturePerM=.299792458*std::abs(t.q)*field->maxNormT/t.p;
      V3 start=t.position*U::m;
      auto parameters=Acts::BoundTrackParameters::createCurvilinear(Acts::Vector4(start.x(),start.y(),start.z(),0),t.direction,t.q/(t.p*U::GeV),std::nullopt,Acts::ParticleHypothesis::muon());
      using Actors=Acts::ActorList<Recorder,Acts::EndOfWorldReached>;
      Propagator::Options<Actors> options(gctx,mctx);options.pathLimit=o.pathLimit*U::m;options.maxSteps=o.maxSteps;options.loopProtection=false;options.surfaceTolerance=o.tolerance*U::m;options.navigation.surfaceTolerance=o.tolerance*U::m;options.stepping.maxStepSize=o.step*U::m;options.stepping.initialStepSize=o.step*U::m;options.stepping.stepTolerance=o.rkTolerance*U::m;
      // Refresh all support targets rather than retaining old Infinite-bound
      // candidates. Exhaustive coplanar faces may require more than the native
      // default100 zero-distance target skips; fanout was already recorded at
      // the preceding root before ACTS skips these on-surface targets.
      options.navigation.keepUnreachedExternal=false;
      // Native nearLimit defaults100nm independently of surfaceTolerance.
      // A refreshed target only a few nm ahead still needs native convergence.
      options.navigation.nearLimit=0.;
      options.maxTargetSkipping=std::max<std::size_t>(100,scene.faces.size()+scene.outer.size()+scene.entrance.size()+10);
      auto& recorder=options.actorList.template get<Recorder>();recorder.scene=&scene;recorder.capture=c;recorder.auditRoots=o.rootAudit;
      auto result=prop.propagate(parameters,options);
      if(!c->fieldFailure.empty()){status=c->fieldFailure=="outside_map"?"outside_map":"field_masked";error=c->fieldFailure;}
      else if(!result.ok()) {error=result.error().message();status=result.error()==Acts::make_error_code(Acts::PropagatorError::StepCountLimitReached)?"step_limit":"navigation_error";}
      else if(c->returned)status="returned_to_entrance";
      else if(c->exited)status="completed";
      else if(std::abs(c->path)>=o.pathLimit-o.tolerance)status="path_limit";
      else {status="navigation_error";error="normal termination without world exit or configured path limit";}
    }catch(const std::exception& e){status="navigation_error";error=e.what();}
    if(!c->fieldFailure.empty()) {
      std::ostringstream e;e<<c->fieldFailure<<" at "<<std::setprecision(17)<<c->failedPosition.transpose();error=e.str();status=c->fieldFailure=="outside_map"?"outside_map":"field_masked";
    }
    std::size_t sequence=0;for(const auto& h:c->hits)hits<<csv(t.id)<<','<<sequence++<<','<<h.owner.panel<<','<<h.owner.face<<','<<h.owner.large<<','<<h.owner.id<<','<<h.position.x()<<','<<h.position.y()<<','<<h.position.z()<<','<<h.path<<','<<h.direction.x()<<','<<h.direction.y()<<','<<h.direction.z()<<'\n';
    for(const auto& r:c->roots)roots<<csv(t.id)<<','<<r.id<<','<<r.path<<','<<r.position.x()<<','<<r.position.y()<<','<<r.position.z()<<','<<r.matched<<'\n';
    for(const auto& r:c->stepAudit)steps<<csv(t.id)<<','<<r.target<<','<<r.current<<','<<r.path<<','<<r.position.x()<<','<<r.position.y()<<','<<r.position.z()<<','<<r.remaining<<'\n';
    tracks<<csv(t.id)<<','<<status<<','<<csv(error)<<','<<c->path<<','<<c->steps<<','<<c->position.x()<<','<<c->position.y()<<','<<c->position.z()<<','<<c->fieldQueries<<','<<c->nativeCorrections<<','<<c->guardCaps<<','<<c->parallelAmbiguities.size()<<',';if(std::isfinite(c->minGuardM))tracks<<c->minGuardM;tracks<<'\n';
    ++total.tracks;total.hits+=c->hits.size();total.queries+=c->fieldQueries;total.navQueries+=c->navQueries;total.navCandidates+=c->navCandidates;++total.statuses[status];
    total.nativeRoots+=c->nativeRoots;total.finiteChecks+=c->finiteChecks;total.outsideRoots+=c->outsideRoots;
    total.nativeCorrections+=c->nativeCorrections;total.guardCaps+=c->guardCaps;total.guardChecks+=c->guardChecks;total.parallelAmbiguities+=c->parallelAmbiguities.size();total.minGuardM=std::min(total.minGuardM,c->minGuardM);total.maxCurvaturePerM=std::max(total.maxCurvaturePerM,c->curvaturePerM);
    field->active=nullptr;scene.active=nullptr;
  }
  return total;
}
RunTotals fieldQueries(const Options& o,Field& field,const Acts::MagneticFieldContext& mctx,const std::filesystem::path& output) {
  std::ifstream f(o.query);std::size_t n;if(!(f>>n))throw std::runtime_error("invalid query input");std::ofstream out(output/"field.csv");out<<std::setprecision(17)<<"point_index,status,Bx_T,By_T,Bz_T\n";auto cache=field.makeCache(mctx);RunTotals total;
  for(std::size_t i=0;i<n;++i){V3 p;for(unsigned j=0;j<3;++j)p[j]=readReal(f);Capture c;field.active=&c;auto result=field.getField((p*U::m).eval(),cache);out<<i<<','<<(result.ok()?"valid":c.fieldFailure);if(result.ok()){V3 b=*result/U::T;out<<','<<b.x()<<','<<b.y()<<','<<b.z();}else out<<",nan,nan,nan";out<<'\n';total.queries+=c.fieldQueries;}field.active=nullptr;return total;
}
void metadata(const Options& o,const Scene* scene,const RunTotals& t,const std::filesystem::path& output,double elapsed,int argc,char** argv) {
  std::ofstream f(output/"metadata.json");f<<std::setprecision(17);
  f<<"{\n  \"status\": \"isolated vacuum ACTS chamber envelope PROTOTYPE\",\n  \"acts_library_commit\": "<<jsonString(std::string(Acts::VersionInfo::fromLibrary().commitHash.value_or("unknown")))<<",\n  \"field\": "<<jsonString(o.field)<<",\n  \"policy\": "<<jsonString(o.policy)<<",\n  \"world_radius_m\": "<<worldRadiusM<<",\n  \"world_half_z_m\": "<<worldHalfZM<<",\n  \"max_step_m\": "<<o.step<<",\n  \"surface_tolerance_m\": "<<o.tolerance<<",\n  \"rk_step_tolerance_internal_length\": "<<o.rkTolerance*U::m<<",\n  \"path_limit_m\": "<<o.pathLimit<<",\n  \"max_steps\": "<<o.maxSteps<<",\n  \"loop_protection\": false,\n  \"returned_to_entrance_abort\": true,\n  \"native_current_surface_actor_only\": "<<(o.mode=="finite-portals"?"true":"false")<<",\n  \"virtual_entrance_surfaces\": 3,\n  \"entrance_radius_m\": 4.35,\n  \"entrance_half_z_m\": 6.5,\n  \"refresh_after_each_position_or_direction_change\": "<<(o.mode=="finite-portals"?"true":"false")<<",\n  \"index_cell_m\": 1,\n  \"candidate_radius_m\": "<<(2*o.step+2*o.tolerance)<<",\n  \"geometry_id_unique\": true,\n  \"chambers\": "<<(scene?scene->panels.size():0)<<",\n  \"visited_native_volumes\": "<<(scene?scene->visitedVolumes:0)<<",\n  \"native_chamber_faces\": "<<(scene?scene->faces.size():0)<<",\n  \"native_large_faces\": "<<(scene?scene->largeFaces:0)<<",\n  \"tracks\": "<<t.tracks<<",\n  \"raw_native_hits\": "<<t.hits<<",\n  \"field_queries\": "<<t.queries<<",\n  \"navigation_refreshes\": "<<t.navQueries<<",\n  \"navigation_candidates\": "<<t.navCandidates<<",\n  \"elapsed_seconds\": "<<elapsed<<",\n  \"limitations\": [\"Native support-root audit requires analytic, curved-edge, finite-bounds and refinement controls; chamber portal transitions are not validated\",\"No material, scattering, energy loss, segment response, fitting or reconstructed efficiency\"],";
  f<<"\n  \"mode\": "<<jsonString(o.mode)<<",\n  \"governing_face_audit_amendment\": \"faa544a1fa424906c68b27bcf37db181d783b84e\",\n  \"native_root_positions_only\": true,\n  \"infinite_candidate_boundary_tolerance\": "<<(o.mode=="surface-audit"?"true":"false")<<",\n  \"native_finite_face_filter\": "<<(o.mode=="surface-audit"?"true":"false")<<",\n  \"coincident_owner_fanout\": "<<(o.mode=="surface-audit"?"true":"false")<<",\n  \"chamber_portal_transitions_validated\": false,\n  \"world_exit_native_surface_actor\": "<<(o.mode=="surface-audit"?"true":"false")<<",\n  \"keep_unreached_external\": false,\n  \"max_target_skipping\": "<<(scene?std::max<std::size_t>(100,scene->faces.size()+scene->outer.size()+scene->entrance.size()+10):0)<<",\n  \"native_root_events\": "<<t.nativeRoots<<",\n  \"native_finite_face_checks\": "<<t.finiteChecks<<",\n  \"outside_footprint_chamber_support_roots\": "<<t.outsideRoots<<",\n  \"navigation_semantics\": "<<jsonString(o.mode=="surface-audit"?"ACTS support roots of actual surfaces; strict native finite face predicate and coincident-owner audit; world/entrance finite direction aborts":"Legacy finite portal transitions, retained as adverse negative control")<<",\n";
  f<<"  \"governing_native_correction_guard_amendment\": \"008ae5b6ab673de5504fe9ea55ab6378312d4d0a\",\n  \"preserve_pending_native_negative_correction\": "<<(o.mode=="surface-audit"?"true":"false")<<",\n  \"native_negative_corrections_preserved\": "<<t.nativeCorrections<<",\n  \"curvature_guard_constraint\": \"ACTS ConstrainedStep::Type::Actor\",\n  \"curvature_guard_factor\": 0.8,\n  \"curvature_guard_formula\": \"0.8*2*abs(g)/(sqrt(vn*vn+2*kappa*abs(g))+abs(vn))\",\n  \"curvature_guard_possible_crossing_test\": \"abs(g)+abs(vn)*maxStep <= kappa*maxStep*maxStep/2\",\n  \"curvature_guard_caps\": "<<t.guardCaps<<",\n  \"curvature_guard_plane_checks\": "<<t.guardChecks<<",\n  \"near_tolerance_parallel_face_ambiguities\": "<<t.parallelAmbiguities<<",\n  \"field_norm_bound_T\": "<<t.maxFieldNormT<<",\n  \"max_track_curvature_bound_per_m\": "<<t.maxCurvaturePerM<<",\n  \"minimum_curvature_guard_step_m\": ";
  if(std::isfinite(t.minGuardM))f<<t.minGuardM;else f<<"null";
  f<<",\n";
  f<<"  \"navigation_near_limit_m\": 0,\n  \"optional_native_root_step_audit\": "<<(o.rootAudit?"true":"false")<<",\n";
  f<<"  \"governing_bounded_discovery_rk_amendment\": \"cbef091d19984e475efe3b59f148ea676de8e90b\",\n  \"rk_tolerance_m\": "<<o.rkTolerance<<",\n  \"native_rkn_error_acceptance_factor\": 4,\n  \"candidate_refresh_semantics\": \"Refresh after position/direction changes except pending native negative target correction\",\n  \"root_and_owner_semantics\": \"Positions are native currentSurface roots; matched IDs are all actual finite owning faces at that point\",\n  \"support_candidate_selection\": "<<jsonString(o.policy=="unbounded"?"Negative control: all infinite supports without finite reach bound":o.policy=="exhaustive"?"Bounded exhaustive: scan all finite AABBs and apply conservative distance filter":"Indexed: grid AABB enumeration followed by conservative distance filter")<<",\n";
  f<<"  \"track_status_counts\": {";
  auto header=Acts::VersionInfo::fromHeader(),library=Acts::VersionInfo::fromLibrary();
  bool first=true;for(const auto& [key,n]:t.statuses){if(!first)f<<',';f<<jsonString(key)<<':'<<n;first=false;}f<<"},\n  \"acts_header_commit\": "<<jsonString(std::string(header.commitHash.value_or("unknown")))<<",\n  \"acts_header_library_version_match\": "<<(header.withoutCommit()==library.withoutCommit()?"true":"false")<<",\n  \"acts_library_commit_available\": "<<(library.commitHash?"true":"false")<<",\n  \"acts_discovery\": "<<jsonString(NODD_ACTS_DISCOVERY)<<",\n  \"argv\": [";for(int i=0;i<argc;++i){if(i)f<<',';f<<jsonString(argv[i]);}f<<"]\n}\n";
}
} // namespace
int main(int argc,char** argv) {
  try {
    auto started=std::chrono::steady_clock::now();auto o=arguments(argc,argv);
    if(!compatibleVersions(Acts::VersionInfo::fromHeader(),Acts::VersionInfo::fromLibrary())) {std::ostringstream message;message<<"ACTS header/library version mismatch: header="<<Acts::VersionInfo::fromHeader()<<"; library="<<Acts::VersionInfo::fromLibrary()<<"; discovery="<<NODD_ACTS_DISCOVERY;throw std::runtime_error(message.str());}std::filesystem::path output=o.output;std::filesystem::create_directories(output);
    Acts::GeometryContext context=Acts::GeometryContext::dangerouslyDefaultConstruct();Acts::MagneticFieldContext mctx{};
    auto field=std::make_shared<Field>(o);RunTotals totals;std::unique_ptr<Scene> scene;
    if(!o.query.empty())totals=fieldQueries(o,*field,mctx,output);
    else {scene=std::make_unique<Scene>(o);auto logger=Acts::getDefaultLogger("MuonGeometry",Acts::Logging::ERROR);build(*scene,context,*logger);exportGeometry(*scene,context,output);if(!o.inspect){if(o.tracks.empty())throw std::runtime_error("--tracks required unless inspect/query");totals=propagate(*scene,o,field,context,mctx,output);}}
    totals.maxFieldNormT=field->maxNormT;double elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-started).count();metadata(o,scene.get(),totals,output,elapsed,argc,argv);
    std::cout<<"native engine complete: "<<totals.tracks<<" tracks, "<<totals.hits<<" surface events, "<<elapsed<<" s\n";return 0;
  }catch(const std::exception& e){std::cerr<<"native engine fatal: "<<e.what()<<'\n';return 2;}
}
