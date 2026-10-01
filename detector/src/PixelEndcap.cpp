// Standalone preliminary endcap: disc/module logic separated from passive parts.
#include "nodd/PixelComponents.hpp"
#include "nodd/PixelEndcap.hpp"
#include <DD4hep/DetFactoryHelper.h>
namespace {
using namespace dd4hep;
Ref_t createPixelEndcap(Detector& d,xml::Handle_t x,SensitiveDetector sensitive) {
  const auto name=x.attr<std::string>("name");
  DetElement result(name,x.attr<int>("id"));
  Assembly endcap(name);
  sensitive.setType("tracker");
  nodd::placeEndcapParts(d,endcap,x);
  for(xml::Collection_t disc(x,"disc");disc;++disc) {
    const auto dn=disc.attr<std::string>("name");
    const int did=disc.attr<int>("id");
    Assembly dv(dn); DetElement de(result,dn,did);
    nodd::placeEndcapParts(d,dv,disc);
    for(xml::Collection_t m(disc,"module");m;++m) {
      const int id=m.attr<int>("id");
      auto built=nodd::buildModule(d,m,sensitive);
      // Proper rotation: columns u, signed v and support-facing w.
      const double ux=m.attr<double>("ux"),uy=m.attr<double>("uy"),
                   vx=m.attr<double>("vx"),vy=m.attr<double>("vy"),nz=m.attr<double>("nz");
      auto pv=dv.placeVolume(built.volume,Transform3D(Rotation3D(ux,vx,0.,uy,vy,0.,0.,0.,nz),
        Position(m.attr<double>("x"),m.attr<double>("y"),m.attr<double>("z"))));
      pv.addPhysVolID("module",id).addPhysVolID("stave",m.attr<int>("col"));
      DetElement me(de,m.attr<std::string>("name"),id);me.setPlacement(pv);
      DetElement se(me,"substrate",0);se.setPlacement(built.substrate);
      for(const auto& [pid,pp]:built.patches) {
        DetElement pe(se,"sensor_"+std::to_string(pid),pid);pe.setPlacement(pp);
      }
    }
    auto pv=endcap.placeVolume(dv,Position(0.,0.,disc.attr<double>("z")));
    pv.addPhysVolID("layer",did);de.setPlacement(pv);
  }
  auto pv=d.pickMotherVolume(result).placeVolume(endcap);
  pv.addPhysVolID("system",x.attr<int>("id"));result.setPlacement(pv);
  return result;
}
}
DECLARE_DETELEMENT(nODDPixelEndcap,createPixelEndcap)
