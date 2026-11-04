// DES031 isolated SiW barrel; logical board reuse with physical parent IDs.
#include <DD4hep/DetFactoryHelper.h>
#include <cmath>
#include <map>
#include <stdexcept>
#include <vector>
namespace {
using namespace dd4hep;
using xml::Handle_t;
double value(Handle_t h,const char* k) {double v=h.attr<double>(k);if(!std::isfinite(v))throw std::runtime_error("Nonfinite barrel parameter");return v;}
Transform3D pose(Handle_t h) {return Transform3D(Rotation3D(value(h,"a00"),value(h,"a01"),value(h,"a02"),value(h,"a10"),value(h,"a11"),value(h,"a12"),value(h,"a20"),value(h,"a21"),value(h,"a22")),Position(value(h,"x"),value(h,"y"),value(h,"z")));}
Solid shape(Handle_t h) {
  auto k=h.attr<std::string>("kind");
  if(k=="box")return Box(value(h,"sx")/2,value(h,"sy")/2,value(h,"sz")/2);
  if(k=="tube")return Tube(value(h,"rmin"),value(h,"rmax"),value(h,"length")/2);
  if(k=="xtru") {std::vector<double>x,y;for(xml::Collection_t v(h,"vertex");v;++v){x.push_back(value(v,"x"));y.push_back(value(v,"y"));}double z=value(h,"depth")/2;return ExtrudedPolygon(x,y,{-z,z},{0,0},{0,0},{1,1});}
  throw std::runtime_error("Unknown barrel shape");
}
void pieces(Detector& d,Handle_t h,Assembly& a,SensitiveDetector sd) {
  for(xml::Collection_t p(h,"piece");p;++p) {
    Solid s=shape(p);for(xml::Collection_t c(p,"cut");c;++c)s=SubtractionSolid(s,shape(c),pose(c));
    Volume v(p.attr<std::string>("name"),s,d.material(p.attr<std::string>("material")));
    if(p.attr<std::string>("role")=="sensitive")v.setSensitiveDetector(sd);
    a.placeVolume(v,pose(p));
  }
}
Ref_t createBarrel(Detector& d,Handle_t h,SensitiveDetector sd) {
  auto name=h.attr<std::string>("name");DetElement result(name,h.attr<int>("id"));Assembly detector(name);sd.setType("calorimeter");std::map<std::string,Assembly>boards,regions;
  for(xml::Collection_t b(h,"board");b;++b){auto n=b.attr<std::string>("name");Assembly a("barrel_board_"+n);pieces(d,b,a,sd);if(!boards.emplace(n,a).second)throw std::runtime_error("Duplicate board");}
  for(xml::Collection_t r(h,"region");r;++r){auto n=r.attr<std::string>("name");Assembly a(n);pieces(d,r,a,sd);
    for(xml::Collection_t b(r,"board_instance");b;++b){auto p=a.placeVolume(boards.at(b.attr<std::string>("template")),pose(b));p.addPhysVolID("module",b.attr<int>("module"));}
    if(!regions.emplace(n,a).second)throw std::runtime_error("Duplicate barrel region");
  }
  for(xml::Collection_t r(h,"replica");r;++r){auto p=detector.placeVolume(regions.at(r.attr<std::string>("region")),pose(r));for(auto k:{"side","sector","layer"})p.addPhysVolID(k,r.attr<int>(k));}
  auto p=d.pickMotherVolume(result).placeVolume(detector);p.addPhysVolID("system",h.attr<int>("id"));result.setPlacement(p);return result;
}
}
DECLARE_DETELEMENT(nODDEcalBarrelPrototype,createBarrel)
