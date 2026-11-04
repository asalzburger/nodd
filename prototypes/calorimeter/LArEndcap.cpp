// DES033 isolated turbine wheel faces; no imported detector factory.
#include <DD4hep/DetFactoryHelper.h>
#include <DD4hep/detail/SegmentationsInterna.h>
#include <DDSegmentation/Segmentation.h>
#include <algorithm>
#include <cmath>
#include <map>
#include <mutex>
#include <stdexcept>
#include <tuple>
#include <vector>

namespace {
using namespace dd4hep;
using dd4hep::DDSegmentation::BitFieldCoder;
using dd4hep::DDSegmentation::CellID;
using dd4hep::DDSegmentation::VolumeID;
using dd4hep::DDSegmentation::Vector3D;
using dd4hep::DDSegmentation::SegmentationParameter;
using xml::Handle_t;

class TurbineGrid : public dd4hep::DDSegmentation::Segmentation {
  double depth=0; int axial=0;
  std::vector<double> wheelTable,referenceTable;
  struct Wheel {double inner,outer;int planes,rho;};
  mutable std::map<int,Wheel> wheels;
  mutable std::map<std::tuple<int,int,int>,Vector3D> references;
  mutable std::once_flag initialized;
  void initialize() const {
    std::call_once(initialized,[this] {
      if (!(depth>0) || axial!=10 || wheelTable.size()!=12 || referenceTable.size()%6) throw std::runtime_error("Invalid turbine readout parameters");
      for (int i=0;i<3;++i) {
        Wheel w{wheelTable[4*i]*mm,wheelTable[4*i+1]*mm,int(wheelTable[4*i+2]),int(wheelTable[4*i+3])};
        if (!(w.inner>0 && w.outer>w.inner && w.planes>0 && w.rho>0)) throw std::runtime_error("Invalid physical wheel table");
        wheels.emplace(i,w);
      }
      for (size_t i=0;i<referenceTable.size();i+=6) {
        auto key=std::make_tuple(int(referenceTable[i]),int(referenceTable[i+1]),int(referenceTable[i+2]));
        if (!references.emplace(key,Vector3D(referenceTable[i+3]*mm,referenceTable[i+4]*mm,referenceTable[i+5]*mm)).second) throw std::runtime_error("Duplicate turbine reference key");
      }
    });
  }
 public:
  explicit TurbineGrid(const BitFieldCoder* decoder):dd4hep::DDSegmentation::Segmentation(decoder) {
    _type="nODDLArEndcapGrid";
    registerParameter("sampling_depth_mm","Physical wheel sampling depth; mm",depth,0.);
    registerParameter("axial_bins","Virtual readout axial subdivisions",axial,0);
    registerParameter("wheel_table_mm","Inner/outer radius(mm), planes, radial bins per wheel",wheelTable,std::vector<double>{});
    registerParameter("reference_table_mm","Wheel/rho/z/canonical gap0 local interior x,y,z(mm)",referenceTable,std::vector<double>{});
  }
  bool cellsSpanVolumes() const override {return true;}
  Vector3D position(const CellID& id) const override {
    initialize();int wi=int(_decoder->get(id,"wheel")),plane=int(_decoder->get(id,"plane")),side=int(_decoder->get(id,"side"));
    if (!wheels.count(wi) || plane<0 || plane>=wheels.at(wi).planes || (side!=1 && side!=2) || _decoder->get(id,"gap")!=0) throw std::runtime_error("Noncanonical turbine ID");
    auto key=std::make_tuple(wi,int(_decoder->get(id,"rho")),int(_decoder->get(id,"z")));
    auto it=references.find(key);if (it==references.end()) throw std::runtime_error("No physical turbine cell reference");
    return it->second;
  }
  CellID cellID(const Vector3D& local,const Vector3D&,const VolumeID& raw) const override {
    initialize();int wi=int(_decoder->get(raw,"wheel"));
    if (!wheels.count(wi)) throw std::runtime_error("Unknown turbine wheel");
    auto w=wheels.at(wi);double r=std::hypot(local.x(),local.y()),half=depth*mm/2;
    if (r<w.inner-1e-8*mm || r>w.outer+1e-8*mm || std::abs(local.z())>half+1e-8*mm) throw std::runtime_error("Hit outside turbine wheel/depth");
    int rho=std::clamp(int(std::floor((r-w.inner)/(w.outer-w.inner)*w.rho)),0,w.rho-1);
    int z=std::clamp(int(std::floor((local.z()+half)/(2*half)*axial)),0,axial-1);
    auto result=raw;_decoder->set(result,"rho",rho);_decoder->set(result,"z",z);_decoder->set(result,"gap",0);
    position(result);return result;
  }
  VolumeID volumeID(const CellID& id) const override {
    initialize();position(id);auto result=id;_decoder->set(result,"rho",0);_decoder->set(result,"z",0);return result;
  }
};

double value(Handle_t h,const char* key) {double x=h.attr<double>(key);if (!std::isfinite(x)) throw std::runtime_error("Nonfinite turbine dimension");return x;}
Transform3D pose(Handle_t h) {
  return Transform3D(Rotation3D(value(h,"a00"),value(h,"a01"),value(h,"a02"),value(h,"a10"),value(h,"a11"),value(h,"a12"),value(h,"a20"),value(h,"a21"),value(h,"a22")),Position(value(h,"x"),value(h,"y"),value(h,"z")));
}
Solid shape(Handle_t h) {
  auto kind=h.attr<std::string>("kind");Solid solid;
  if (kind=="box") solid=Box(value(h,"sx")/2,value(h,"sy")/2,value(h,"sz")/2);
  else if (kind=="tube") solid=Tube(value(h,"rmin"),value(h,"rmax"),value(h,"length")/2);
  else if (kind=="arb8") {
    std::vector<double> xy;for (xml::Collection_t v(h,"vertex");v;++v) {xy.push_back(value(v,"x"));xy.push_back(value(v,"y"));}
    if (xy.size()!=16) throw std::runtime_error("Turbine Arb8 requires exactly8 corners");
    solid=EightPointSolid(value(h,"half_z"),xy.data());
  } else if (kind=="xtru") {
    std::vector<double>x,y;for (xml::Collection_t v(h,"vertex");v;++v) {x.push_back(value(v,"x"));y.push_back(value(v,"y"));}
    double half=value(h,"depth")/2;solid=ExtrudedPolygon(x,y,{-half,half},{0,0},{0,0},{1,1});
  } else throw std::runtime_error("Unknown turbine primitive");
  for (xml::Collection_t a(h,"annulus");a;++a) solid=IntersectionSolid(solid,Tube(value(a,"rmin"),value(a,"rmax"),value(a,"length")/2));
  for (xml::Collection_t cut(h,"cut");cut;++cut) solid=SubtractionSolid(solid,shape(cut),pose(cut));
  return solid;
}
Ref_t createTurbine(Detector& detector,Handle_t h,SensitiveDetector sd) {
  auto name=h.attr<std::string>("name");DetElement result(name,h.attr<int>("id"));Assembly assembly(name);sd.setType("calorimeter");
  std::map<int,Assembly>wheels;
  for (xml::Collection_t wheel(h,"wheel");wheel;++wheel) {
    Assembly period(wheel.attr<std::string>("name"));
    for (xml::Collection_t p(wheel,"piece");p;++p) {
      Volume v(p.attr<std::string>("name"),shape(p),detector.material(p.attr<std::string>("material")));
      bool sensitive=p.attr<std::string>("role")=="sensitive";if (sensitive)v.setSensitiveDetector(sd);
      auto placed=period.placeVolume(v,pose(p));if (sensitive)placed.addPhysVolID("gap",p.attr<int>("gap"));
    }
    if (!wheels.emplace(wheel.attr<int>("index"),period).second)throw std::runtime_error("Duplicate turbine wheel");
  }
  if (wheels.size()!=3)throw std::runtime_error("Missing turbine wheel");
  for (xml::Collection_t replica(h,"replica");replica;++replica) {
    auto p=assembly.placeVolume(wheels.at(replica.attr<int>("wheel")),pose(replica));
    for (auto key:{"side","wheel","plane"})p.addPhysVolID(key,replica.attr<int>(key));
  }
  std::map<std::string,Volume>passives;std::vector<Handle_t>pending;
  for (xml::Collection_t p(h,"piece");p;++p) {
    auto tag=p.attr<std::string>("name");Volume v(tag,shape(p),detector.material(p.attr<std::string>("material")));
    if (!passives.emplace(tag,v).second)throw std::runtime_error("Duplicate turbine passive name");pending.push_back(p);
  }
  std::map<std::string,bool>placed;
  while (!pending.empty()) {
    bool progress=false;
    for (auto it=pending.begin();it!=pending.end();) {
      auto p=*it;auto tag=p.attr<std::string>("name");bool hasParent=p.hasAttr("parent_name");auto parent=hasParent?p.attr<std::string>("parent_name"):std::string{};
      if (hasParent && !passives.count(parent))throw std::runtime_error("Unknown turbine passive parent");
      if (hasParent && !placed.count(parent)){++it;continue;}
      if (hasParent)passives.at(parent).placeVolume(passives.at(tag),pose(p));else assembly.placeVolume(passives.at(tag),pose(p));
      placed.emplace(tag,true);it=pending.erase(it);progress=true;
    }
    if (!progress)throw std::runtime_error("Cycle in turbine passive hierarchy");
  }
  auto p=detector.pickMotherVolume(result).placeVolume(assembly);p.addPhysVolID("system",h.attr<int>("id"));result.setPlacement(p);return result;
}
SegmentationObject* createGrid(const BitFieldCoder* decoder) {return new SegmentationWrapper<TurbineGrid>(decoder);}
}
DECLARE_DETELEMENT(nODDLArEndcapPrototype,createTurbine)
DECLARE_SEGMENTATION(nODDLArEndcapGrid,createGrid)
