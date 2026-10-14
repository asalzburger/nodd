// DES-020 isolated prototype. No production detector entry point uses this factory.
#include <DD4hep/DetFactoryHelper.h>
#include <cmath>
#include <stdexcept>

namespace {
using namespace dd4hep;
using xml::Handle_t;
double dim(Handle_t x, const char* key) {
  const double v=x.attr<double>(key);
  if (!std::isfinite(v)) throw std::runtime_error("Nonfinite short-strip dimension");
  return v;
}
Solid shape(Handle_t x) {
  const auto kind=x.attr<std::string>("kind");
  if (kind=="box") return Box(dim(x,"sx")/2,dim(x,"sy")/2,dim(x,"sz")/2);
  if (kind=="shoe") {
    const double a=dim(x,"sx")/2,b=dim(x,"sz")/2,k=dim(x,"slope"),z=dim(x,"sy")/2;
    return ExtrudedPolygon({-a,a,a,-a},{-b-k*a,-b+k*a,b,b},{-z,z},{0,0},{0,0},{1,1});
  }
  if (kind=="tube") return Tube(dim(x,"rmin"),dim(x,"rmax"),dim(x,"length")/2);
  if (kind=="sector") return Tube(dim(x,"rmin"),dim(x,"rmax"),dim(x,"length")/2,dim(x,"start"),dim(x,"start")+dim(x,"angle"));
  if (kind=="torus") return Torus(dim(x,"major"),dim(x,"rmin"),dim(x,"rmax"),dim(x,"start"),dim(x,"angle"));
  throw std::runtime_error("Unsupported short-strip shape: "+kind);
}
Transform3D local(Handle_t x) {
  const auto kind=x.attr<std::string>("kind");
  const bool tube=kind=="tube" || kind=="shoe";
  return Transform3D(RotationZYX(0,0,tube ? M_PI/2 : 0),Position(dim(x,"u"),dim(x,"v"),dim(x,"w")));
}
void parts(Detector& d, Volume parent, Handle_t x, SensitiveDetector sd, DetElement owner) {
  for (xml::Collection_t p(x,"piece");p;++p) {
    const auto name=p.attr<std::string>("name");
    Solid solid=shape(p);
    for (xml::Collection_t cut(p,"cut");cut;++cut)
      solid=SubtractionSolid(solid,shape(cut),local(cut));
    Volume volume(name,solid,d.material(p.attr<std::string>("material")));
    const auto material=p.attr<std::string>("material");
    volume->SetLineColor(material=="Silicon" ? 4 : material=="Titanium" ? 920 : material=="CO2" ? 6 : material=="Copper" ? 800 : 3);
    const bool sensitive=p.hasAttr("sensitive") && p.attr<bool>("sensitive");
    if (sensitive) volume.setSensitiveDetector(sd);
    auto pv=parent.placeVolume(volume,local(p));
    if (sensitive) {
      pv.addPhysVolID("sensor",p.attr<int>("sensor"));
      DetElement sensor(owner,name,p.attr<int>("sensor")); sensor.setPlacement(pv);
    }
  }
}
Ref_t createShortStripBarrel(Detector& d, Handle_t x, SensitiveDetector sd) {
  const auto name=x.attr<std::string>("name");
  DetElement result(name,x.attr<int>("id"));
  Assembly barrel(name);sd.setType("tracker");
  parts(d,barrel,x,sd,result);
  for (xml::Collection_t l(x,"layer");l;++l) {
    const auto lname=l.attr<std::string>("name");
    Assembly lv(lname);DetElement le(result,lname,l.attr<int>("id"));
    parts(d,lv,l,sd,le);
    for (xml::Collection_t s(l,"stave");s;++s) {
      const auto sname=s.attr<std::string>("name");
      Assembly sv(sname);DetElement se(le,sname,s.attr<int>("id"));
      parts(d,sv,s,sd,se);
      for (xml::Collection_t m(s,"module");m;++m) {
        const auto mname=m.attr<std::string>("name");
        Assembly mv(mname);DetElement me(se,mname,m.attr<int>("id"));
        parts(d,mv,m,sd,me);
        auto pv=sv.placeVolume(mv,Position(0,dim(m,"z"),dim(m,"lift")));
        pv.addPhysVolID("module",m.attr<int>("id"));me.setPlacement(pv);
      }
      const double phi=dim(s,"phi"),r=dim(s,"radius"),tilt=s.hasAttr("tilt") ? dim(s,"tilt") : 0;
      const double co=std::cos(phi+tilt),si=std::sin(phi+tilt);
      auto pv=lv.placeVolume(sv,Transform3D(Rotation3D(-si,0,co,co,0,si,0,1,0),Position(r*std::cos(phi),r*std::sin(phi),0)));
      pv.addPhysVolID("stave",s.attr<int>("id"));se.setPlacement(pv);
    }
    auto pv=barrel.placeVolume(lv);pv.addPhysVolID("layer",l.attr<int>("id"));le.setPlacement(pv);
  }
  auto pv=d.pickMotherVolume(result).placeVolume(barrel);
  pv.addPhysVolID("system",x.attr<int>("id"));result.setPlacement(pv);
  return result;
}
}
DECLARE_DETELEMENT(nODDShortStripBarrel,createShortStripBarrel)
