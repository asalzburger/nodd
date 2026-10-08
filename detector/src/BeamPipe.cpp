// DES-024: user-authorized straight-pipe simulation baseline; design DRAFT.
#include <DD4hep/DetFactoryHelper.h>
#include <DD4hep/DetType.h>
#include <cmath>
#include <stdexcept>

static dd4hep::Ref_t createBeamPipe(dd4hep::Detector& d,
                                  dd4hep::xml::Handle_t h,
                                  dd4hep::SensitiveDetector) {
  using namespace dd4hep;
  xml::DetElement x(h);
  auto dimensions = x.child(xml::Strng_t("dimensions"));
  const double ri = dimensions.attr<double>("rmin");
  const double ro = dimensions.attr<double>("rmax");
  const double hz = dimensions.attr<double>("half_length");
  if (!std::isfinite(ri) || !std::isfinite(ro) || !std::isfinite(hz) ||
      ri <= 0 || ro <= ri || hz <= 0) {
    throw std::runtime_error("Invalid nODD beampipe dimensions");
  }
  const std::string name = x.nameStr();
  DetElement result(name, x.id());
  result.setTypeFlag(DetType::BEAMPIPE | DetType::TRACKER);
  Volume wall(name + "_wall", Tube(ri, ro, hz), d.material("Beryllium"));
  wall.setVisAttributes(d, "BeamPipeVis");
  Volume bore(name + "_bore", Tube(0, ri, hz), d.material("Vacuum"));
  bore.setVisAttributes(d, "BoreVis");
  auto mother = d.pickMotherVolume(result);
  mother.placeVolume(bore);
  auto placement = mother.placeVolume(wall);
  placement.addPhysVolID("system", x.id());
  result.setPlacement(placement);
  return result;
}
DECLARE_DETELEMENT(nODDBeamPipe, createBeamPipe)
