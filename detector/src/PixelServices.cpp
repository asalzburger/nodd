#include "nodd/PixelServices.hpp"
#include <DD4hep/Shapes.h>
#include <cmath>
#include <stdexcept>
namespace nodd {
dd4hep::Volume buildServiceSector(dd4hep::Detector& detector, dd4hep::xml::Handle_t x) {
  const double ri=x.attr<double>("rmin"), ro=x.attr<double>("rmax");
  const double length=x.attr<double>("length"), width=x.attr<double>("phi_width");
  if (!std::isfinite(ri+ro+length+width) || ri<0 || ro<=ri || length<=0 || width<=0 || width>2*M_PI)
    throw std::runtime_error("Invalid service sector dimensions");
  // Rotate the sector placement to its phi centre in the assembly factory.
  dd4hep::Volume volume(x.attr<std::string>("name"),
    dd4hep::Tube(ri,ro,length/2,0.,width),detector.material(x.attr<std::string>("material")));
  volume.setVisAttributes(detector,x.attr<std::string>("vis"));
  return volume;
}
}
