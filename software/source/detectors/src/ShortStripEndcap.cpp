// DES021 isolated prototype; no production entry point uses this factory.
#include <DD4hep/DetFactoryHelper.h>
#include <cmath>
#include <stdexcept>
namespace {
using namespace dd4hep;
using xml::Handle_t;
double dim(Handle_t x,const char* key) {
  const double v=x.attr<double>(key);
  if(!std::isfinite(v))throw std::runtime_error("Nonfinite endcap dimension");
  return v;
}
Solid shape(Handle_t x) {
  const auto k=x.attr<std::string>("kind");
  if(k=="box")return Box(dim(x,"sx")/2,dim(x,"sy")/2,dim(x,"sz")/2);
  if(k=="tube")return Tube(dim(x,"rmin"),dim(x,"rmax"),dim(x,"length")/2);
  if(k=="sector")return Tube(dim(x,"rmin"),dim(x,"rmax"),dim(x,"length")/2,dim(x,"start"),dim(x,"start")+dim(x,"angle"));
  if(k=="torus")return Torus(dim(x,"major"),dim(x,"rmin"),dim(x,"rmax"),dim(x,"start"),dim(x,"angle"));
  throw std::runtime_error("Unknown endcap solid");
}
Transform3D pose(Handle_t x) {
  return Transform3D(RotationZ(dim(x,"rz"))*RotationY(dim(x,"ry"))*RotationX(dim(x,"rx")),Position(dim(x,"u"),dim(x,"v"),dim(x,"w")));
}
void parts(Detector& d,Volume parent,Handle_t x,SensitiveDetector sd,DetElement owner) {
  for(xml::Collection_t p(x,"piece");p;++p) {
    Solid solid=shape(p);
    for(xml::Collection_t cut(p,"cut");cut;++cut)solid=SubtractionSolid(solid,shape(cut),pose(cut));
    const auto name=p.attr<std::string>("name"),material=p.attr<std::string>("material");
    Volume v(name,solid,d.material(material));v->SetLineColor(material=="Silicon"?4:material=="Titanium"?920:material=="CO2"?6:material=="Copper"?800:3);
    const bool sensitive=p.hasAttr("sensitive")&&p.attr<bool>("sensitive");
    if(sensitive)v.setSensitiveDetector(sd);
    auto pv=parent.placeVolume(v,pose(p));
    if(sensitive){pv.addPhysVolID("sensor",0);DetElement se(owner,name,0);se.setPlacement(pv);}
  }
}
Ref_t createShortStripEndcap(Detector& d,Handle_t x,SensitiveDetector sd) {
  const auto name=x.attr<std::string>("name");DetElement result(name,x.attr<int>("id"));Assembly endcap(name);sd.setType("tracker");
  parts(d,endcap,x,sd,result);
  for(xml::Collection_t disc(x,"disc");disc;++disc) {
    const auto dn=disc.attr<std::string>("name");Assembly dv(dn);DetElement de(result,dn,disc.attr<int>("id"));parts(d,dv,disc,sd,de);
    for(xml::Collection_t petal(disc,"petal");petal;++petal) {
      const auto pn=petal.attr<std::string>("name");Assembly pv(pn);DetElement pe(de,pn,petal.attr<int>("id"));parts(d,pv,petal,sd,pe);
      for(xml::Collection_t module(petal,"module");module;++module) {
        const auto mn=module.attr<std::string>("name");Assembly mv(mn);DetElement me(pe,mn,module.attr<int>("id"));parts(d,mv,module,sd,me);
        const double phi=dim(module,"phi"),r=dim(module,"radius"),co=std::cos(phi),si=std::sin(phi);
        auto placed=pv.placeVolume(mv,Transform3D(Rotation3D(-si,-co,0,co,-si,0,0,0,1),Position(r*co,r*si,dim(module,"lift"))));
        placed.addPhysVolID("ring",module.attr<int>("ring")).addPhysVolID("module",module.attr<int>("id"));me.setPlacement(placed);
      }
      auto placed=dv.placeVolume(pv,Transform3D(RotationZ(dim(petal,"phi")),Position()));placed.addPhysVolID("petal",petal.attr<int>("id"));pe.setPlacement(placed);
    }
    const double side=disc.attr<int>("side");
    auto placed=endcap.placeVolume(dv,Transform3D(Rotation3D(1,0,0,0,side,0,0,0,side),Position(0,0,side*dim(disc,"z"))));
    placed.addPhysVolID("layer",disc.attr<int>("id"));de.setPlacement(placed);
  }
  auto placed=d.pickMotherVolume(result).placeVolume(endcap);placed.addPhysVolID("system",x.attr<int>("id"));result.setPlacement(placed);return result;
}
}
DECLARE_DETELEMENT(nODDShortStripEndcap,createShortStripEndcap)
