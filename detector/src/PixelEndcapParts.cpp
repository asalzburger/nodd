#include "nodd/PixelEndcap.hpp"
#include "nodd/PixelDisplay.hpp"
#include <DD4hep/Shapes.h>
#include <DD4hep/Objects.h>
#include <DD4hep/DD4hepUnits.h>
#include <cmath>
#include <stdexcept>
namespace nodd {
namespace {
double dim(dd4hep::xml::Handle_t x,const char* key) {
  double v=x.attr<double>(key);
  if(!std::isfinite(v)) throw std::runtime_error("Non-finite endcap dimension");
  return v;
}
double pos(dd4hep::xml::Handle_t x,const char* key) {
  double v=dim(x,key);
  if(v<=0) throw std::runtime_error("Non-positive endcap dimension");
  return v;
}
}
dd4hep::Volume buildEndcapPart(dd4hep::Detector& d,dd4hep::xml::Handle_t x) {
  using namespace dd4hep;
  const auto type=x.attr<std::string>("shape");
  Solid solid;
  if(type=="box") solid=Box(pos(x,"dx")/2,pos(x,"dy")/2,pos(x,"dz")/2);
  else if(type=="sector") {
    const double lo=dim(x,"rmin"),hi=pos(x,"rmax"),angle=pos(x,"angle");
    if(lo<0 || lo>=hi || angle>2*M_PI+1e-12) throw std::runtime_error("Invalid annular sector");
    solid=Tube(lo,hi,pos(x,"dz")/2,0.,angle);
  } else if(type=="torus") {
    const double lo=dim(x,"rmin"),hi=pos(x,"rmax"),r=pos(x,"radius");
    if(lo<0 || lo>=hi || hi>=r) throw std::runtime_error("Invalid cooling torus");
    solid=Torus(r,lo,hi,0.,2*M_PI);
  } else if(type=="tongue") {
    // A rectangular tongue minus its overlap with the circular plate.
    const double a=pos(x,"start"),b=pos(x,"end"),w=pos(x,"width"),r=pos(x,"radius"),t=pos(x,"dz");
    if(a>=r || b<=r || std::hypot(a,w/2)>=r) throw std::runtime_error("Invalid tongue/plate partition");
    solid=SubtractionSolid(Box((b-a)/2,w/2,t/2),Tube(0.,r,t),Position(-(a+b)/2,0.,0.));
  } else throw std::runtime_error("Unknown endcap part shape: "+type);
  Volume result(x.attr<std::string>("name"),solid,d.material(x.attr<std::string>("material")));
  applyDisplay(d,result,x.attr<std::string>("vis"));
  placeEndcapParts(d,result,x);
  return result;
}
void placeEndcapParts(dd4hep::Detector& d,dd4hep::Volume mother,dd4hep::xml::Handle_t x) {
  using namespace dd4hep;
  for(xml::Collection_t part(x,"part");part;++part) {
    mother.placeVolume(buildEndcapPart(d,part),Transform3D(
      RotationZYX(dim(part,"rz"),dim(part,"ry"),dim(part,"rx")),
      Position(dim(part,"x"),dim(part,"y"),dim(part,"z"))));
  }
}
}
