// PR29 pixel-barrel assembly. Reusable solids live in separate components.
#include "nodd/PixelComponents.hpp"
#include "nodd/PixelServices.hpp"
#include <DD4hep/DetFactoryHelper.h>
#include <cmath>

namespace {
using namespace dd4hep;
using xml::Handle_t;
// Columns of the rotation matrix are tangent, beam and outward radial.
Transform3D staveFrame(double phi, double radius, double beamZ=0.) {
  const double c=std::cos(phi),s=std::sin(phi);
  return Transform3D(Rotation3D(-s,0,c,c,0,s,0,1,0),Position(radius*c,radius*s,beamZ));
}
Ref_t createPixelBarrel(Detector& detector, Handle_t x, SensitiveDetector sensitive) {
  const auto name=x.attr<std::string>("name");
  DetElement result(name,x.attr<int>("id"));
  Assembly barrel(name);
  sensitive.setType("tracker");
  for (xml::Collection_t layer(x,"layer"); layer; ++layer) {
    const auto lname=layer.attr<std::string>("name");
    const int lid=layer.attr<int>("id");
    Assembly layerVolume(lname);
    DetElement layerElement(result,lname,lid);
    for (xml::Collection_t stave(layer,"stave"); stave; ++stave) {
      const auto sname=stave.attr<std::string>("name");
      const int sid=stave.attr<int>("id");
      Assembly staveVolume=nodd::buildStave(detector,stave);
      DetElement staveElement(layerElement,sname,sid);
      for (xml::Collection_t module(stave,"module"); module; ++module) {
        const int mid=module.attr<int>("id");
        auto built=nodd::buildModule(detector,module,sensitive);
        auto placement=staveVolume.placeVolume(built.volume,Position(0.,module.attr<double>("z"),0.));
        placement.addPhysVolID("module",mid);
        DetElement moduleElement(staveElement,module.attr<std::string>("name"),mid);
        moduleElement.setPlacement(placement);
        DetElement substrateElement(moduleElement,"substrate",0);
        substrateElement.setPlacement(built.substrate);
        for (const auto& [patchId,patchPlacement]:built.patches) {
          DetElement patchElement(substrateElement,"sensor_"+std::to_string(patchId),patchId);
          patchElement.setPlacement(patchPlacement);
        }
      }
      auto placement=layerVolume.placeVolume(staveVolume,staveFrame(stave.attr<double>("phi"),stave.attr<double>("radius")));
      placement.addPhysVolID("stave",sid);staveElement.setPlacement(placement);
    }
    for (xml::Collection_t ring(layer,"ring"); ring; ++ring)
      layerVolume.placeVolume(nodd::buildRing(detector,ring),Position(0.,0.,ring.attr<double>("z")));
    for (xml::Collection_t foot(layer,"foot"); foot; ++foot) {
      const double radius=(foot.attr<double>("back_radius")+foot.attr<double>("outer_radius"))/2;
      layerVolume.placeVolume(nodd::buildFoot(detector,foot),staveFrame(foot.attr<double>("phi"),radius,foot.attr<double>("z")));
    }
    auto placement=barrel.placeVolume(layerVolume);
    placement.addPhysVolID("layer",lid);layerElement.setPlacement(placement);
  }
  for (xml::Collection_t service(x,"service"); service; ++service) {
    const double phi=service.attr<double>("phi")-service.attr<double>("phi_width")/2;
    barrel.placeVolume(nodd::buildServiceSector(detector,service),
      Transform3D(RotationZYX(phi,0.,0.),Position(0.,0.,service.attr<double>("z"))));
  }
  auto placement=detector.pickMotherVolume(result).placeVolume(barrel);
  placement.addPhysVolID("system",x.attr<int>("id"));result.setPlacement(placement);
  return result;
}
}
DECLARE_DETELEMENT(nODDPixelBarrel,createPixelBarrel)
