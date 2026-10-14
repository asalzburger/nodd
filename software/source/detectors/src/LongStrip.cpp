// Isolated DES-022/023 prototype, not used by production.
#include <DD4hep/DetFactoryHelper.h>
#include <cmath>
#include <stdexcept>
#include <map>
namespace {
using namespace dd4hep;using xml::Handle_t;
double dim(Handle_t x,const char* k){double v=x.attr<double>(k);if(!std::isfinite(v))throw std::runtime_error("Nonfinite dimension");return v;}
Transform3D pose(Handle_t x){return Transform3D(Rotation3D(dim(x,"a00"),dim(x,"a01"),dim(x,"a02"),dim(x,"a10"),dim(x,"a11"),dim(x,"a12"),dim(x,"a20"),dim(x,"a21"),dim(x,"a22")),Position(dim(x,"x"),dim(x,"y"),dim(x,"z")));}
Solid shape(Handle_t x){auto k=x.attr<std::string>("kind");if(k=="box")return Box(dim(x,"sx")/2,dim(x,"sy")/2,dim(x,"sz")/2);if(k=="shoe"){double a=dim(x,"sx")/2,b=dim(x,"sz")/2,k=dim(x,"slope"),z=dim(x,"sy")/2;return ExtrudedPolygon({-a,a,a,-a},{-b-k*a,-b+k*a,b,b},{-z,z},{0,0},{0,0},{1,1});}if(k=="tube")return Tube(dim(x,"rmin"),dim(x,"rmax"),dim(x,"length")/2);if(k=="sector")return Tube(dim(x,"rmin"),dim(x,"rmax"),dim(x,"length")/2,dim(x,"start"),dim(x,"start")+dim(x,"angle"));if(k=="torus")return Torus(dim(x,"major"),dim(x,"rmin"),dim(x,"rmax"),dim(x,"start"),dim(x,"angle"));throw std::runtime_error("Unsupported shape");}
Ref_t createLongStrip(Detector& d,Handle_t x,SensitiveDetector sd){const auto name=x.attr<std::string>("name");DetElement result(name,x.attr<int>("id"));Assembly mother(name);sd.setType("tracker");int sensor=0;std::map<std::string,Volume> groups;std::map<std::string,DetElement> owners;
for(xml::Collection_t p(x,"piece");p;++p){auto n=p.attr<std::string>("name");auto g=p.attr<std::string>("group");if(!groups.count(g)){Assembly a(g);groups.emplace(g,a);DetElement de(result,g,groups.size());auto gp=mother.placeVolume(a);de.setPlacement(gp);owners.emplace(g,de);}Solid solid=shape(p);for(xml::Collection_t cut(p,"cut");cut;++cut)solid=SubtractionSolid(solid,shape(cut),pose(cut));Volume v(n,solid,d.material(p.attr<std::string>("material")));bool sensitive=p.hasAttr("sensitive")&&p.attr<bool>("sensitive");if(sensitive)v.setSensitiveDetector(sd);auto pv=groups.at(g).placeVolume(v,pose(p));if(sensitive){for(auto k:{"layer","stave","module","sensor"})pv.addPhysVolID(k,p.attr<int>(k));DetElement de(owners.at(g),n,sensor++);de.setPlacement(pv);}}
auto pv=d.pickMotherVolume(result).placeVolume(mother);pv.addPhysVolID("system",x.attr<int>("id"));result.setPlacement(pv);return result;}
}
DECLARE_DETELEMENT(nODDLongStrip,createLongStrip)
