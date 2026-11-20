// DES045 isolated physical HCAL, reused real carriers/layers/sectors.
#include <DD4hep/DetFactoryHelper.h>
#include <DD4hep/detail/SegmentationsInterna.h>
#include <DDSegmentation/Segmentation.h>
#include <TGeoBoolNode.h>
#include <TGeoCompositeShape.h>
#include <TGeoMatrix.h>
#include <mutex>
#include <sstream>
#include <iomanip>
#include <array>
#include <cmath>
#include <functional>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
namespace {
using namespace dd4hep;
using xml::Handle_t;
using dd4hep::DDSegmentation::BitFieldCoder;
using dd4hep::DDSegmentation::CellID;
using dd4hep::DDSegmentation::VolumeID;
using dd4hep::DDSegmentation::Vector3D;
class TileGrid : public dd4hep::DDSegmentation::Segmentation {
  std::vector<double> table;
  mutable std::once_flag initialized;
  mutable std::array<Vector3D,72> centers;
  void initialize() const {
    std::call_once(initialized,[this] {
      if(table.size()!=72*5)throw std::runtime_error("HCAL tile table requires72cells");
      std::set<int> seen;
      for(size_t i=0;i<table.size();i+=5) {
        int module=int(table[i]),sensor=int(table[i+1]);
        if(module<0||module>1||sensor<0||sensor>35||!seen.insert(module*36+sensor).second)throw std::runtime_error("HCAL invalid tile table ID");
        centers[module*36+sensor]=Vector3D(table[i+2]*mm,table[i+3]*mm,table[i+4]*mm);
        double ex=(module?186.:0.)+30.*(sensor%6),ey=30.*(sensor/6);
        if(std::abs(table[i+2]-ex)>1e-9||std::abs(table[i+3]-ey)>1e-9||std::abs(table[i+4])>1e-9)throw std::runtime_error("HCAL tile table differs from frozen physical module");
      }
    });
  }
 public:
  explicit TileGrid(const BitFieldCoder* decoder):dd4hep::DDSegmentation::Segmentation(decoder) {
    _type="nODDHCALTileGrid";_description="72exact physical recessed scintillator cells inside one compound sensitive carrier volume";
    registerParameter("tile_table_mm","module,sensor,active-volume-local center x,y,z in mm",table,std::vector<double>{});
  }
  Vector3D position(const CellID& id) const override {
    initialize();int module=int(_decoder->get(id,"module")),sensor=int(_decoder->get(id,"sensor"));
    if(module<0||module>1||sensor<0||sensor>35||_decoder->get(id,"x")||_decoder->get(id,"y"))throw std::runtime_error("HCAL invalid logical cell");
    return centers[module*36+sensor];
  }
  CellID cellID(const Vector3D& local,const Vector3D&,const VolumeID& raw) const override {
    initialize();int module=local.x()<168.*mm?0:1;
    int col=int(std::llround((local.x()/mm-(module?186.:0.))/30.));
    int row=int(std::llround((local.y()/mm)/30.));
    if(col<0||col>=6||row<0||row>=6) {
      std::ostringstream msg;msg<<std::setprecision(17)<<"HCAL hit outside physical tile field: active-local-mm="<<local.x()/mm<<","<<local.y()/mm<<","<<local.z()/mm<<" module="<<module<<" col="<<col<<" row="<<row<<" raw="<<raw;throw std::runtime_error(msg.str());
    }
    int sensor=row*6+col;auto center=centers[module*36+sensor];
    if(std::abs(local.x()-center.x())>14.85001*mm||std::abs(local.y()-center.y())>14.85001*mm||std::abs(local.z()-center.z())>1.50001*mm) {
      std::ostringstream msg;msg<<std::setprecision(17)<<"HCAL hit in a physical tile gap: active-local-mm="<<local.x()/mm<<","<<local.y()/mm<<","<<local.z()/mm<<" chosen-center-mm="<<center.x()/mm<<","<<center.y()/mm<<","<<center.z()/mm<<" module="<<module<<" sensor="<<sensor<<" raw="<<raw;throw std::runtime_error(msg.str());
    }
    CellID result=raw;_decoder->set(result,"module",module);_decoder->set(result,"sensor",sensor);_decoder->set(result,"x",0);_decoder->set(result,"y",0);return result;
  }
  VolumeID volumeID(const CellID& id) const override {
    position(id);VolumeID result=id;
    for(auto key:{"module","sensor","x","y"})_decoder->set(result,key,0);
    return result;
  }
  std::vector<double> cellDimensions(const CellID&) const override {return {29.7*mm,29.7*mm,3.*mm};}
};

double val(Handle_t h,const char* key) {
  const double x=h.attr<double>(key);
  if(!std::isfinite(x))throw std::runtime_error("HCAL nonfinite dimension");
  return x;
}
Transform3D pose(Handle_t h) {
  return Transform3D(Rotation3D(val(h,"a00"),val(h,"a01"),val(h,"a02"),val(h,"a10"),val(h,"a11"),val(h,"a12"),val(h,"a20"),val(h,"a21"),val(h,"a22")),Position(val(h,"x"),val(h,"y"),val(h,"z")));
}
Solid primitive(Handle_t h) {
  const auto kind=h.attr<std::string>("kind");
  if(kind=="box")return Box(val(h,"sx")/2,val(h,"sy")/2,val(h,"sz")/2);
  if(kind=="tube")return Tube(val(h,"rmin"),val(h,"rmax"),val(h,"length")/2);
  if(kind=="arb8") {
    std::vector<double> xy;
    for(xml::Collection_t v(h,"vertex");v;++v){xy.push_back(val(v,"x"));xy.push_back(val(v,"y"));}
    if(xy.size()!=16)throw std::runtime_error("HCAL arb8 requires eight vertices");
    return EightPointSolid(val(h,"half_z"),xy.data());
  }
  if(kind=="xtru") {
    std::vector<double>x,y;
    for(xml::Collection_t v(h,"vertex");v;++v){x.push_back(val(v,"x"));y.push_back(val(v,"y"));}
    double half=val(h,"depth")/2;
    return ExtrudedPolygon(x,y,{-half,half},{0,0},{0,0},{1,1});
  }
  if(kind=="ring") {
    int n=h.attr<int>("sides");std::vector<double>x,y,ix,iy;const double pi=std::acos(-1.);
    for(int i=0;i<n;++i) {
      double a=(2*i+1)*pi/n;
      x.push_back(val(h,"outer")/std::cos(pi/n)*std::cos(a));y.push_back(val(h,"outer")/std::cos(pi/n)*std::sin(a));
      ix.push_back(val(h,"inner")/std::cos(pi/n)*std::cos(a));iy.push_back(val(h,"inner")/std::cos(pi/n)*std::sin(a));
    }
    double half=val(h,"depth")/2;
    return SubtractionSolid(ExtrudedPolygon(x,y,{-half,half},{0,0},{0,0},{1,1}),ExtrudedPolygon(ix,iy,{-half,half},{0,0},{0,0},{1,1}));
  }
  throw std::runtime_error("HCAL unsupported shape: "+kind);
}
Solid shape(Handle_t h) {
  Solid result=primitive(h);
  for(xml::Collection_t cut(h,"cut");cut;++cut)result=SubtractionSolid(result,primitive(cut),pose(cut));
  return result;
}
Ref_t createHCAL(Detector& detector,Handle_t h,SensitiveDetector sd) {
  const std::string name=h.attr<std::string>("name");const int system=h.attr<int>("id");
  if(system!=13&&system!=14)throw std::runtime_error("HCAL system mapping");
  DetElement result(name,system);sd.setType("calorimeter");
  std::map<std::string,Handle_t> definitions;
  std::map<std::string,Volume> volumes;
  std::set<std::string> building;
  for(xml::Collection_t t(h,"template");t;++t) {
    const auto key=t.attr<std::string>("name");
    if(!definitions.emplace(key,t).second)throw std::runtime_error("HCAL duplicate template");
  }
  std::function<Volume(const std::string&)> make=[&](const std::string& key)->Volume {
    auto ready=volumes.find(key);if(ready!=volumes.end())return ready->second;
    auto found=definitions.find(key);if(found==definitions.end()||!building.insert(key).second)throw std::runtime_error("HCAL missing/cyclic template "+key);
    Handle_t t=found->second;Handle_t sh=t.child(_U(shape));
    Volume volume;
    if(sh.attr<std::string>("kind")=="assembly")volume=Assembly(name+key);
    else volume=Volume(name+key,shape(sh),detector.material(t.attr<std::string>("material")));
    std::set<int> tileIds;
    std::vector<std::pair<Solid,Position>> sensitiveLeaves;
    for(xml::Collection_t p(t,"piece");p;++p) {
      const auto pn=p.attr<std::string>("name");
      bool sensitive=p.hasAttr("sensor");
      Solid solid=shape(p.child(_U(shape)));
      if(sensitive) {
        if(p.attr<std::string>("material")!="PSHost")throw std::runtime_error("HCAL compound requires identical PSHost material");
        for(int i=0;i<3;++i)for(int j=0;j<3;++j) {
          std::string k="a"+std::to_string(i)+std::to_string(j);
          if(std::abs(val(p,k.c_str())-(i==j?1.:0.))>1e-12)throw std::runtime_error("HCAL compound tile frame changed");
        }
        sensitiveLeaves.emplace_back(solid,Position(val(p,"x"),val(p,"y"),val(p,"z")));
      } else {
        Volume pv(name+key+pn,solid,detector.material(p.attr<std::string>("material")));
        volume.placeVolume(pv,pose(p));
      }
      if(sensitive) {
        int module=p.attr<int>("module"),sensor=p.attr<int>("sensor");
        if(module<0||module>1||sensor<0||sensor>35||!tileIds.insert(module*36+sensor).second)throw std::runtime_error("HCAL sensitive tile IDs");

      }
    }
    if(!tileIds.empty()&&tileIds.size()!=72)throw std::runtime_error("HCAL carrier must own exactly72tiles");
    if(!sensitiveLeaves.empty()) {
      // Pairwise reduction keeps boolean navigation depth logarithmic. Keep
      // every left transform identity: DDG4's native boolean conversion applies
      // only the right operand transform. Carry each group's left anchor until
      // the final physical placement, preserving all absolute core positions.
      while(sensitiveLeaves.size()>1) {
        std::vector<std::pair<Solid,Position>> next;
        for(size_t i=0;i<sensitiveLeaves.size();i+=2) {
          if(i+1==sensitiveLeaves.size()){next.push_back(sensitiveLeaves[i]);continue;}
          auto a=sensitiveLeaves[i],b=sensitiveLeaves[i+1];
          Position relative(b.second.x()-a.second.x(),b.second.y()-a.second.y(),b.second.z()-a.second.z());
          Solid joined=UnionSolid(a.first,b.first,relative);
          next.emplace_back(joined,a.second);
        }
        sensitiveLeaves=std::move(next);
      }
      Volume active(name+key+"CompoundTiles",sensitiveLeaves[0].first,detector.material("PSHost"));
      active.setSensitiveDetector(sd);volume.placeVolume(active,sensitiveLeaves[0].second);
    }
    for(xml::Collection_t p(t,"place");p;++p) {
      auto child=make(p.attr<std::string>("ref"));auto placed=volume.placeVolume(child,pose(p));
      for(auto field:{"side","sector","layer","carrier"})if(p.hasAttr(field))placed.addPhysVolID(field,p.attr<int>(field));
    }
    building.erase(key);volumes.emplace(key,volume);return volume;
  };
  auto root=make(h.attr<std::string>("root_template"));
  auto placed=detector.pickMotherVolume(result).placeVolume(root);placed.addPhysVolID("system",system);result.setPlacement(placed);
  return result;
}
}
DECLARE_DETELEMENT(nODDHCALResponsePrototype,createHCAL)
namespace { dd4hep::SegmentationObject* createGrid(const BitFieldCoder* decoder) {return new dd4hep::SegmentationWrapper<TileGrid>(decoder);} }
DECLARE_SEGMENTATION(nODDHCALTileGrid,createGrid)
