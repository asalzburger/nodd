// DES036 unsigned PROTOTYPE; independent factory, no production integration.
#include <DD4hep/DetFactoryHelper.h>
#include <cmath>
#include <stdexcept>
#include <set>

namespace {
using namespace dd4hep;
using xml::Handle_t;

double value(Handle_t h, const char* key) {
  double v = h.attr<double>(key);
  if (!std::isfinite(v)) throw std::runtime_error("Nonfinite HCAL dimension");
  return v;
}

Transform3D pose(Handle_t h) {
  return Transform3D(Rotation3D(
      value(h,"a00"),value(h,"a01"),value(h,"a02"),
      value(h,"a10"),value(h,"a11"),value(h,"a12"),
      value(h,"a20"),value(h,"a21"),value(h,"a22")),
      Position(value(h,"x"),value(h,"y"),value(h,"z")));
}

Solid shape(Handle_t h) {
  std::string kind=h.attr<std::string>("kind");
  if (kind=="box") {
    auto x=value(h,"sx"), y=value(h,"sy"), z=value(h,"sz");
    if (x<=0 || y<=0 || z<=0) throw std::runtime_error("Nonpositive HCAL box");
    return Box(x/2,y/2,z/2);
  }
  if (kind=="tube") {
    auto a=value(h,"rmin"), b=value(h,"rmax"), l=value(h,"length");
    if (a<0 || b<=a || l<=0) throw std::runtime_error("Invalid HCAL tube");
    return Tube(a,b,l/2);
  }
  throw std::runtime_error("Unsupported HCAL primitive");
}

Ref_t createReadout(Detector& detector, Handle_t h, SensitiveDetector sd) {
  std::string name=h.attr<std::string>("name");
  DetElement result(name,h.attr<int>("id"));
  Assembly carrier(name+"Carrier");
  sd.setType("calorimeter");
  std::set<std::string> names;
  std::set<int> ids;
  for (xml::Collection_t piece(h,"piece");piece;++piece) {
    auto partName=piece.attr<std::string>("name");
    if (!names.insert(partName).second) throw std::runtime_error("Duplicate HCAL part");
    Solid solid=shape(piece);
    for (xml::Collection_t cut(piece,"cut");cut;++cut) {
      solid=SubtractionSolid(solid,shape(cut),pose(cut));
    }
    Volume volume(partName,solid,detector.material(piece.attr<std::string>("material")));
    if (piece.hasAttr("sensor")) volume.setSensitiveDetector(sd);
    auto placed=carrier.placeVolume(volume,pose(piece));
    if (piece.hasAttr("sensor")) {
      int module=piece.attr<int>("module"), sensor=piece.attr<int>("sensor");
      if (module<0 || module>1 || sensor<0 || sensor>35 || !ids.insert(module*36+sensor).second)
        throw std::runtime_error("Invalid HCAL module/sensor ID");
      placed.addPhysVolID("module",module).addPhysVolID("sensor",sensor);
    }
  }
  if (ids.size()!=72) throw std::runtime_error("HCAL requires 72 sensitive tile IDs");
  auto placed=detector.pickMotherVolume(result).placeVolume(carrier);
  placed.addPhysVolID("system",h.attr<int>("id"));
  for (auto key : {"side","sector","layer","carrier"}) placed.addPhysVolID(key,0);
  result.setPlacement(placed);
  return result;
}
}
DECLARE_DETELEMENT(nODDHCALReadoutPrototype,createReadout)
