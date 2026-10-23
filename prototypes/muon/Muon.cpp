// DES039/040 isolated PROTOTYPE. Air reservations, no MDT response/material model.
#include <DD4hep/DetFactoryHelper.h>
#include <array>
#include <cmath>
#include <set>
#include <stdexcept>

namespace {
using namespace dd4hep;
using xml::Handle_t;

double value(Handle_t h, const char* key) {
  const double x = h.attr<double>(key);
  if (!std::isfinite(x)) throw std::runtime_error("Nonfinite muon parameter");
  return x;
}

Transform3D pose(Handle_t h) {
  return Transform3D(Rotation3D(
      value(h,"a00"), value(h,"a01"), value(h,"a02"),
      value(h,"a10"), value(h,"a11"), value(h,"a12"),
      value(h,"a20"), value(h,"a21"), value(h,"a22")),
      Position(value(h,"x"),value(h,"y"),value(h,"z")));
}

// Exact rectangular-section sweep about the rounded racetrack centreline.
// Primitive boundaries meet inside a CSG union, never as sibling placements.
Solid racetrack(Handle_t h) {
  const double hr=value(h,"half_r"), hz=value(h,"half_z");
  const double rho=value(h,"corner"), a=value(h,"normal")/2;
  const double b=value(h,"tangent")/2;
  if (!(0<a && a<rho && rho<hr && rho<hz && b>0))
    throw std::runtime_error("Invalid rounded-racetrack sweep");
  Solid shape=Box(a,hz-rho,b);
  // Work in the first straight leg's frame until all pieces are united.
  shape=UnionSolid(shape,Box(a,hz-rho,b),Position(-2*hr,0,0));
  for (int sy : {-1,1}) {
    shape=UnionSolid(shape,Box(hr-rho,a,b),Position(-hr,sy*hz,0));
  }
  for (const auto& corner : std::array<std::array<int,3>,4>{{
      {{1,1,0}}, {{-1,1,90}}, {{-1,-1,180}}, {{1,-1,270}}}}) {
    const double start=corner[2]*degree;
    shape=UnionSolid(shape,Tube(rho-a,rho+a,b,start,start+90*degree),
        Position(corner[0]*(hr-rho)-hr,corner[1]*(hz-rho),0));
  }
  return shape;
}

Transform3D coilPose(double angle, double cr, double cz, double hr) {
  const double c=std::cos(angle),s=std::sin(angle);
  // Local x = radial, y = global z, z = minus azimuthal; right handed.
  return Transform3D(Rotation3D(c,0,s, s,0,-c, 0,1,0),
                     Position((cr+hr)*c,(cr+hr)*s,cz));
}

Ref_t createMuon(Detector& detector, Handle_t h, SensitiveDetector) {
  const std::string name=h.attr<std::string>("name");
  DetElement result(name,h.attr<int>("id"));
  Assembly assembly(name);
  std::set<int> chamberIDs,groupIDs;
  for (xml::Collection_t panel(h,"chamber"); panel; ++panel) {
    const int identifier=panel.attr<int>("chamber");
    if (!chamberIDs.insert(identifier).second)
      throw std::runtime_error("Duplicate chamber ID");
    std::array<double,16> vertices{};
    int n=0;
    for (xml::Collection_t v(panel,"vertex"); v; ++v) {
      if (n>=4) throw std::runtime_error("Chamber requires four vertices");
      vertices[2*n]=vertices[8+2*n]=value(v,"x");
      vertices[2*n+1]=vertices[9+2*n]=value(v,"y");
      ++n;
    }
    const double depth=value(panel,"depth");
    if (n!=4 || depth<=0) throw std::runtime_error("Invalid chamber prism");
    Volume volume(panel.attr<std::string>("name"),
        EightPointSolid(depth/2,vertices.data()),detector.air());
    volume.setVisAttributes(detector,"MuonChamberVis");
    auto placed=assembly.placeVolume(volume,pose(panel));
    for (const char* field : {"chamber","station","side"})
      placed.addPhysVolID(field,panel.attr<int>(field));
    DetElement element(result,panel.attr<std::string>("name"),identifier);
    element.setPlacement(placed);
  }
  for (xml::Collection_t group(h,"toroid"); group; ++group) {
    const int identifier=group.attr<int>("group");
    if (!groupIDs.insert(identifier).second)
      throw std::runtime_error("Duplicate toroid group ID");
    const int folds=group.attr<int>("folds");
    if (folds!=12) throw std::runtime_error("Expected C12 toroid group");
    const double phi=value(group,"phi"),cr=value(group,"center_r");
    const double cz=value(group,"center_z"),hr=value(group,"half_r");
    const Solid loop=racetrack(group);
    const Transform3D first=coilPose(phi,cr,cz,hr);
    Solid solid=loop;
    for (int k=1;k<folds;++k) {
      solid=UnionSolid(solid,loop,
          first.Inverse()*coilPose(phi+k*2*M_PI/folds,cr,cz,hr));
    }
    Volume volume(group.attr<std::string>("name"),solid,detector.air());
    volume.setVisAttributes(detector,"MuonWarmVis");
    auto placed=assembly.placeVolume(volume,first);
    placed.addPhysVolID("group",identifier);
  }
  if (chamberIDs.size()!=936 || groupIDs.size()!=3)
    throw std::runtime_error("Muon prototype inventory is incomplete");
  auto placed=detector.pickMotherVolume(result).placeVolume(assembly);
  placed.addPhysVolID("system",h.attr<int>("id"));
  result.setPlacement(placed);
  return result;
}
}  // namespace
DECLARE_DETELEMENT(nODDMuonPrototype,createMuon)
