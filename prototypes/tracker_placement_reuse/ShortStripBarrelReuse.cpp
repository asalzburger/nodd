// PR132 isolated PROTOTYPE. Derived from ShortStripBarrel.cpp at d6d2c510.
// No maintained compact or top-level CMake target selects this factory.
#include <DD4hep/DetFactoryHelper.h>
#include <algorithm>
#include <cmath>
#include <map>
#include <sstream>
#include <stdexcept>
#include <vector>

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
// Length-prefixed raw strings avoid rounding/evaluator aliases and ambiguous
// concatenations. All attributes remain, except names and outer instance pose.
std::string recipe(Handle_t x, bool outer=false) {
  std::ostringstream out;
  const auto emit=[&](const std::string& s) { out << s.size() << ':' << s; };
  emit(x.tag());
  std::vector<std::pair<std::string,std::string>> attrs;
  for (const auto a:x.attributes()) {
    const auto key=xml::_toString(x.attr_name(a));
    if (key=="name" || (outer && (key=="id" || key=="z" || key=="lift"))) continue;
    attrs.emplace_back(key,xml::_toString(x.attr_value(a)));
  }
  std::sort(attrs.begin(),attrs.end());
  out << attrs.size() << ';';
  for (const auto& [key,value]:attrs) {emit(key);emit(value);}
  for (xml::Collection_t child(x,"*");child;++child) {
    if ((outer && child.tag()!="piece") || (!outer && child.tag()!="cut"))
      throw std::runtime_error("Unsupported module recipe child");
    if (!outer && x.tag()=="cut") throw std::runtime_error("Nested cut unsupported");
    emit(recipe(child));
  }
  return out.str();
}
Solid motherShape(Handle_t envelope) {
  const double lo=dim(envelope,"wmin"),hi=dim(envelope,"wmax");
  const double u=dim(envelope,"umax"),v=dim(envelope,"vmax");
  if (!(lo<hi && u>0 && v>0)) throw std::runtime_error("Invalid reuse envelope");
  // Intersection retains the module's original local coordinate system; no
  // child/sensor/DetElement transform is translated to center the mother box.
  const double half=(hi-lo)/2,centre=(hi+lo)/2;
  Solid solid=IntersectionSolid(Box(u,v,std::max(std::abs(lo),std::abs(hi))),
                                Box(u,v,half),Position(0,0,centre));
  for (xml::Collection_t cut(envelope,"cut");cut;++cut)
    solid=SubtractionSolid(solid,shape(cut),local(cut));
  return solid;
}
Ref_t createShortStripBarrelReuse(Detector& d, Handle_t x, SensitiveDetector sd) {
  const auto mode=x.attr<std::string>("reuse_mode");
  if (mode!="cache" && mode!="mother") throw std::runtime_error("Unknown tracker reuse mode");
  const auto name=x.attr<std::string>("name");
  DetElement result(name,x.attr<int>("id"));
  Assembly barrel(name);sd.setType("tracker");
  parts(d,barrel,x,sd,result);
  std::string cacheKey;
  Volume cached;
  std::map<int,PlacedVolume> sensorPlacements;
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
        DetElement me(se,mname,m.attr<int>("id"));
        const auto key=recipe(m,true);
        if (!cached.isValid()) {
          cacheKey=key;
          const auto templateName=mname+"_reuse_template";
          if (mode=="cache") cached=Assembly(templateName);
          else {
            const auto envelope=x.child(xml::Strng_t("reuse_envelope"));
            const auto actual=d.pickMotherVolume(result).material();
            if (actual.name()!=envelope.attr<std::string>("material"))
              throw std::runtime_error("Reuse mother differs from actual enclosing material");
            cached=Volume(templateName,motherShape(envelope),actual);
          }
          parts(d,cached,m,sd,me);
          for (xml::Collection_t p(m,"piece");p;++p) {
            if (p.hasAttr("sensitive") && p.attr<bool>("sensitive")) {
              const auto id=p.attr<int>("sensor");
              if (sensorPlacements.count(id)) throw std::runtime_error("Duplicate template sensor ID");
              sensorPlacements[id]=me.child(p.attr<std::string>("name")).placement();
            }
          }
        } else {
          if (key!=cacheKey) throw std::runtime_error("Strict module recipe differs from cache");
          for (xml::Collection_t p(m,"piece");p;++p) {
            if (p.hasAttr("sensitive") && p.attr<bool>("sensitive")) {
              const auto id=p.attr<int>("sensor");
              DetElement sensor(me,p.attr<std::string>("name"),id);
              sensor.setPlacement(sensorPlacements.at(id));
            }
          }
        }
        auto pv=sv.placeVolume(cached,Position(0,dim(m,"z"),dim(m,"lift")));
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
DECLARE_DETELEMENT(nODDShortStripBarrelReuse,createShortStripBarrelReuse)
