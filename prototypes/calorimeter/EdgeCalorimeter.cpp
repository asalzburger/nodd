// DES030 isolated prototype and mask-aware edge-electrode segmentation.
#include <DD4hep/DetFactoryHelper.h>
#include <DD4hep/detail/SegmentationsInterna.h>
#include <DDSegmentation/CartesianGridXY.h>
#include <cmath>
#include <map>
#include <mutex>
#include <stdexcept>
#include <tuple>
#include <vector>

namespace {
using namespace dd4hep;
using xml::Handle_t;
using namespace dd4hep::DDSegmentation;

class EdgeGrid : public CartesianGridXY {
  struct Entry { int x,y; double px,py,dx,dy; };
  using Key=std::tuple<int,int,int>;
  std::vector<double> table,polygons;
  mutable std::once_flag initialized;
  mutable std::map<Key,Entry> entries;
  mutable std::map<int,std::vector<std::pair<double,double>>> masks;
  void initialize() const {
    std::call_once(initialized,[this] {
      if (table.size()%9) throw std::runtime_error("Invalid edge cell table");
      for (size_t i=0;i<table.size();i+=9) {
        Key key{int(table[i]),int(table[i+1]),int(table[i+2])};
        Entry e{int(table[i+3]),int(table[i+4]),table[i+5]*mm,table[i+6]*mm,table[i+7]*mm,table[i+8]*mm};
        if (!entries.emplace(key,e).second) throw std::runtime_error("Duplicate edge cell");
      }
      for (size_t i=0;i<polygons.size();) {
        if (i+2>polygons.size()) throw std::runtime_error("Invalid mask header");
        int module=int(polygons[i++]),n=int(polygons[i++]);
        if (n<3 || i+2*n>polygons.size() || masks.count(module)) throw std::runtime_error("Invalid mask vertices");
        auto& p=masks[module];
        for (int j=0;j<n;++j) { p.emplace_back(polygons[i]*mm,polygons[i+1]*mm);i+=2; }
      }
    });
  }
  bool inside(int module,double x,double y) const {
    const auto& p=masks.at(module);
    for (size_t i=0;i<p.size();++i) {
      auto a=p[i],b=p[(i+1)%p.size()];
      if ((b.first-a.first)*(y-a.second)-(b.second-a.second)*(x-a.first)<-1e-9*mm*mm) return false;
    }
    return true;
  }
  Key key(CellID id) const { return {int(_decoder->get(id,"module")),int(_decoder->get(id,_xId)),int(_decoder->get(id,_yId))}; }
 public:
  explicit EdgeGrid(const BitFieldCoder* d):CartesianGridXY(d) {
    _type="nODDEdgeGrid";
    registerParameter("cell_table_mm","module/raw-bin/merged-bin/interior-point/bounds; lengths in mm",table,std::vector<double>{},SegmentationParameter::NoUnit,true);
    registerParameter("sensor_polygons_mm","module/nvertices/local-active-vertices; lengths in mm",polygons,std::vector<double>{});
  }
  Vector3D position(const CellID& id) const override {
    initialize();auto p=CartesianGridXY::position(id);auto it=entries.find(key(id));
    if (it!=entries.end()) p=Vector3D(it->second.px,it->second.py,0);
    if (!inside(int(_decoder->get(id,"module")),p.X,p.Y)) throw std::runtime_error("Cell position outside active edge mask");
    return p;
  }
  CellID cellID(const Vector3D& p,const Vector3D& global,const VolumeID& volume) const override {
    initialize();int module=int(_decoder->get(volume,"module"));
    if (!inside(module,p.X,p.Y)) throw std::runtime_error("Hit outside active edge mask");
    auto raw=CartesianGridXY::cellID(p,global,volume);
    int ix=int(_decoder->get(raw,_xId)),iy=int(_decoder->get(raw,_yId));
    // A closed sensor boundary can coincide with the upper grid edge. Assign
    // that zero-width tie to an existing interior electrode, never a ghost bin.
    for (int dx:{0,-1}) for (int dy:{0,-1}) {
      if (dx && std::abs(p.X-(ix*_gridSizeX+_offsetX-_gridSizeX/2))>1e-7*mm) continue;
      if (dy && std::abs(p.Y-(iy*_gridSizeY+_offsetY-_gridSizeY/2))>1e-7*mm) continue;
      auto id=raw;_decoder->set(id,_xId,ix+dx);_decoder->set(id,_yId,iy+dy);
      auto it=entries.find(key(id));auto point=CartesianGridXY::position(id);
      if (it!=entries.end()) { point=Vector3D(it->second.px,it->second.py,0);_decoder->set(id,_xId,it->second.x);_decoder->set(id,_yId,it->second.y); }
      if (inside(module,point.X,point.Y)) return id;
    }
    throw std::runtime_error("No physical edge electrode for hit");
  }
  std::vector<double> cellDimensions(const CellID& id) const override {
    initialize();auto it=entries.find(key(id));
    if (it!=entries.end()) return {it->second.dx,it->second.dy};
    return CartesianGridXY::cellDimensions(id);
  }
};

double value(Handle_t h,const char* k) { double x=h.attr<double>(k);if (!std::isfinite(x)) throw std::runtime_error("Nonfinite geometry parameter");return x; }
Transform3D pose(Handle_t h) {
  return Transform3D(Rotation3D(value(h,"a00"),value(h,"a01"),value(h,"a02"),value(h,"a10"),value(h,"a11"),value(h,"a12"),value(h,"a20"),value(h,"a21"),value(h,"a22")),Position(value(h,"x"),value(h,"y"),value(h,"z")));
}
Solid shape(Handle_t h) {
  auto kind=h.attr<std::string>("kind");
  if (kind=="box") return Box(value(h,"sx")/2,value(h,"sy")/2,value(h,"sz")/2);
  if (kind=="tube") return Tube(value(h,"rmin"),value(h,"rmax"),value(h,"length")/2);
  if (kind=="xtru") {
    std::vector<double> x,y;
    for (xml::Collection_t v(h,"vertex");v;++v) { x.push_back(value(v,"x"));y.push_back(value(v,"y")); }
    double half=value(h,"depth")/2;return ExtrudedPolygon(x,y,{-half,half},{0,0},{0,0},{1,1});
  }
  throw std::runtime_error("Unknown edge primitive");
}
Ref_t createEdgeCalorimeter(Detector& d,Handle_t h,SensitiveDetector sd) {
  auto name=h.attr<std::string>("name");DetElement result(name,h.attr<int>("id"));Assembly detector(name);sd.setType("calorimeter");
  std::map<std::string,Assembly> regions;
  for (xml::Collection_t region(h,"region");region;++region) {
    auto tag=region.attr<std::string>("name");Assembly assembly(tag);
    for (xml::Collection_t piece(region,"piece");piece;++piece) {
      Solid solid=shape(piece);
      for (xml::Collection_t cut(piece,"cut");cut;++cut) solid=SubtractionSolid(solid,shape(cut),pose(cut));
      Volume v(piece.attr<std::string>("name"),solid,d.material(piece.attr<std::string>("material")));
      if (piece.hasAttr("module")) v.setSensitiveDetector(sd);
      auto p=assembly.placeVolume(v,pose(piece));
      if (piece.hasAttr("module")) p.addPhysVolID("module",piece.attr<int>("module"));
    }
    if (!regions.emplace(tag,assembly).second) throw std::runtime_error("Duplicate edge region");
  }
  for (xml::Collection_t replica(h,"replica");replica;++replica) {
    auto p=detector.placeVolume(regions.at(replica.attr<std::string>("region")),pose(replica));
    for (auto k:{"side","sector","layer"})p.addPhysVolID(k,replica.attr<int>(k));
  }
  auto p=d.pickMotherVolume(result).placeVolume(detector);p.addPhysVolID("system",h.attr<int>("id"));result.setPlacement(p);return result;
}
dd4hep::SegmentationObject* createEdgeGrid(const dd4hep::DDSegmentation::BitFieldCoder* decoder) {
  return new dd4hep::SegmentationWrapper<EdgeGrid>(decoder);
}
}
DECLARE_DETELEMENT(nODDEcalEdgePrototype,createEdgeCalorimeter)
DECLARE_SEGMENTATION(nODDEdgeGrid,createEdgeGrid)
