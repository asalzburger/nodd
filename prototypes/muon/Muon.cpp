// DES039/040 isolated PROTOTYPE. Air reservations, no MDT response/material model.
#include <DD4hep/DetFactoryHelper.h>
#include <array>
#include <cmath>
#include <set>
#include <map>
#include <iomanip>
#include <sstream>
#include <cctype>
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
  std::set<std::string> chamberNames,usedTemplates;
  std::map<std::string,Volume> templates;
  std::map<std::string,std::string> kinds;
  for (xml::Collection_t t(h.child(xml::Strng_t("chamber_templates")),"chamber_template"); t; ++t) {
    const std::string key=t.attr<std::string>("name");
    const std::string kind=t.attr<std::string>("kind");
    if (kind!="barrel" && kind!="endcap") throw std::runtime_error("Invalid template kind");
    std::array<double,16> vertices{};
    int n=0;
    for (xml::Collection_t v(t,"vertex"); v; ++v) {
      if (n>=4) throw std::runtime_error("Chamber requires four vertices");
      vertices[2*n]=vertices[8+2*n]=value(v,"x");
      vertices[2*n+1]=vertices[9+2*n]=value(v,"y");
      ++n;
    }
    const double depth=value(t,"depth");
    if (n!=4 || depth<=0) throw std::runtime_error("Invalid chamber template");
    for (int i=0;i<4;++i) {
      const int j=(i+1)%4,k=(i+2)%4;
      const double cross=(vertices[2*j]-vertices[2*i])*(vertices[2*k+1]-vertices[2*j+1])-
                         (vertices[2*j+1]-vertices[2*i+1])*(vertices[2*k]-vertices[2*j]);
      if (!(cross<0)) throw std::runtime_error("Template must be convex clockwise");
    }
    Volume volume("MuonTemplate_"+key,EightPointSolid(depth/2,vertices.data()),detector.air());
    volume.setVisAttributes(detector,"MuonChamberVis");
    if (!templates.emplace(key,volume).second) throw std::runtime_error("Duplicate template");
    kinds.emplace(key,kind);
  }
  if (templates.size()!=22) throw std::runtime_error("Expected22 chamber templates");
  auto place=[&](const std::string& key,const std::string& source,int identifier,
                 int station,int side,const Transform3D& transform) {
    if (!templates.count(key)) throw std::runtime_error("Unknown chamber template");
    if (identifier<1 || identifier>936 || station<1 || station>3 || side< -1 || side>1 ||
        (kinds.at(key)=="barrel")!=(side==0)) throw std::runtime_error("Invalid chamber identity");
    if (!chamberIDs.insert(identifier).second) throw std::runtime_error("Duplicate chamber ID");
    std::string chamberName="MuonChamber_";
    for (unsigned char c : source) {
      if (!(std::isalnum(c) || c=='_' || c=='/')) throw std::runtime_error("Invalid source name");
      chamberName+=(c=='/'?'_':c);
    }
    if (!chamberNames.insert(chamberName).second) throw std::runtime_error("Duplicate chamber name");
    auto placed=assembly.placeVolume(templates.at(key),transform);
    placed->SetName(chamberName.c_str());
    placed.addPhysVolID("chamber",identifier).addPhysVolID("station",station).addPhysVolID("side",side);
    DetElement element(result,chamberName,identifier);
    element.setPlacement(placed);
    usedTemplates.insert(key);
  };
  for (xml::Collection_t orbit(h,"chamber_orbit"); orbit; ++orbit) {
    const std::string kind=orbit.attr<std::string>("kind");
    const int count=orbit.attr<int>("count"),index0=orbit.attr<int>("index0");
    const int indexStep=orbit.attr<int>("index_step");
    const int station=orbit.attr<int>("station"),side=orbit.attr<int>("side");
    const double phase=value(orbit,"phi0"),pitch=value(orbit,"dphi"),radius=value(orbit,"radius");
    if (count<1 || count>936 || radius<=0 || (count>1 && (pitch<=0 || indexStep<=0 || pitch*(count-1)>=2*M_PI-1e-12)))
      throw std::runtime_error("Invalid phi recurrence");
    for (xml::Collection_t row(orbit,"row"); row; ++row) {
      const std::string key=row.attr<std::string>("template");
      if (!kinds.count(key) || kinds.at(key)!=kind) throw std::runtime_error("Orbit template kind mismatch");
      const int nz=row.attr<int>("count"),zi=row.attr<int>("z_index0"),zs=row.attr<int>("z_index_step");
      const int id=row.attr<int>("chamber0"),idp=row.attr<int>("chamber_phi_step"),idz=row.attr<int>("chamber_z_step");
      const double tangent=value(row,"tangent"),z0=value(row,"z0"),dz=value(row,"dz");
      if (nz<1 || nz>936 || nz*count>936 || (nz>1 && (dz<=0 || zs<=0)))
        throw std::runtime_error("Invalid longitudinal recurrence");
      for (int iphi=0;iphi<count;++iphi) {
        const double phi=phase+iphi*pitch,c=std::cos(phi),s=std::sin(phi);
        const Rotation3D rotation=(kind=="barrel"?Rotation3D(-s,0,c,c,0,s,0,1,0):Rotation3D(c,-s,0,s,c,0,0,0,1));
        for (int iz=0;iz<nz;++iz) {
          std::string source=row.attr<std::string>("source_pattern");
          for (const auto& replacement : std::array<std::pair<std::string,int>,2>{{
              {"{phi:02d}",index0+iphi*indexStep},{"{z:02d}",zi+iz*zs}}}) {
            std::ostringstream digits;digits<<std::setfill('0')<<std::setw(2)<<replacement.second;
            auto offset=source.find(replacement.first);
            if (offset!=std::string::npos) source.replace(offset,replacement.first.size(),digits.str());
          }
          place(key,source,id+iphi*idp+iz*idz,station,side,
              Transform3D(rotation,Position(radius*c-tangent*s,radius*s+tangent*c,z0+iz*dz)));
        }
      }
    }
  }
  for (xml::Collection_t p(h,"chamber_placement"); p; ++p) {
    const std::string source=p.attr<std::string>("source_id");
    place(p.attr<std::string>("template"),source,p.attr<int>("chamber"),p.attr<int>("station"),p.attr<int>("side"),pose(p));
  }
  if (usedTemplates.size()!=22) throw std::runtime_error("Unused chamber template");
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
