// Isolated PROTOTYPE: parameters and provisional materials belong to the XML,
// not to these reusable construction functions. See DES-012.
#include "nodd/PixelComponents.hpp"

#include <DD4hep/Objects.h>
#include <DD4hep/Shapes.h>
#include <DD4hep/DD4hepUnits.h>

#include <cmath>
#include <set>
#include <stdexcept>

namespace nodd {
namespace {
using namespace dd4hep;
using xml::Handle_t;

double dim(Handle_t node, const char* field) {
  const double value = node.attr<double>(field);
  if (!std::isfinite(value)) {
    throw std::runtime_error(std::string("Non-finite component parameter: ") + field);
  }
  return value;
}

double positive(Handle_t node, const char* field) {
  const double value = dim(node, field);
  if (value <= 0) {
    throw std::runtime_error(std::string("Non-positive component dimension: ") + field);
  }
  return value;
}

void decorate(Detector& detector, Volume volume, Handle_t node) {
  if (node.hasAttr("vis")) {
    volume.setVisAttributes(detector, node.attr<std::string>("vis"));
  }
}

Volume box(Detector& detector, const std::string& name, Handle_t node,
           double length) {
  Volume result(name, Box(positive(node, "width") / 2, length / 2,
                          positive(node, "thickness") / 2),
                detector.material(node.attr<std::string>("material")));
  decorate(detector, result, node);
  return result;
}
}  // namespace

ModuleBuild buildModule(dd4hep::Detector& detector, dd4hep::xml::Handle_t xml,
                        dd4hep::SensitiveDetector sensitive) {
  using namespace dd4hep;
  const std::string name = xml.attr<std::string>("name");
  ModuleBuild result{Assembly(name), {}, {}};
  const auto sensorXml = xml.child(xml::Strng_t("sensor"));
  const double sensorWidth = positive(sensorXml, "width");
  const double sensorLength = positive(sensorXml, "length");
  const double thickness = positive(sensorXml, "thickness");
  auto substrate = box(detector, name + "_substrate", sensorXml, sensorLength);
  result.substrate = result.volume.placeVolume(substrate,
      Position(dim(sensorXml, "u"), dim(sensorXml, "v"), 0 * mm));
  std::set<int> patchIds;
  for (xml::Collection_t patch(sensorXml, "patch"); patch; ++patch) {
    const int id = patch.attr<int>("id");
    const double width = positive(patch, "width");
    const double length = positive(patch, "length");
    const double u = dim(patch, "u"), v = dim(patch, "v");
    if (!patchIds.insert(id).second || id < 0 ||
        std::abs(u) + width / 2 > sensorWidth / 2 ||
        std::abs(v) + length / 2 > sensorLength / 2) {
      throw std::runtime_error(name + ": duplicate/negative sensor ID or patch outside substrate");
    }
    // Same material daughters replace the substrate material in their occupied
    // region. This retains passive silicon guards/seams without double counting.
    Volume active(name + "_sensor_" + std::to_string(id),
                  Box(width / 2, length / 2, thickness / 2), substrate.material());
    active.setSensitiveDetector(sensitive);
    decorate(detector, active, sensorXml);
    auto placement = substrate.placeVolume(active, Position(u, v, 0 * mm));
    placement.addPhysVolID("sensor", id);
    result.patches.emplace_back(id, placement);
  }
  if (result.patches.empty()) {
    throw std::runtime_error(name + ": no sensitive patches");
  }
  for (const char* tag : {"die", "passive"}) {
    for (xml::Collection_t part(xml, tag); part; ++part) {
      auto volume = box(detector, name + "_" + part.attr<std::string>("name"),
                        part, positive(part, "length"));
      result.volume.placeVolume(volume,
          Position(dim(part, "u"), dim(part, "v"), dim(part, "w")));
    }
  }
  return result;
}

dd4hep::Assembly buildStave(dd4hep::Detector& detector,
                           dd4hep::xml::Handle_t xml) {
  using namespace dd4hep;
  const std::string name = xml.attr<std::string>("name");
  const double length = positive(xml, "length");
  Assembly result(name);
  for (xml::Collection_t slab(xml, "slab"); slab; ++slab) {
    auto volume = box(detector, name + "_" + slab.attr<std::string>("name"),
                      slab, length);
    result.placeVolume(volume, Position(0 * mm, dim(slab, "center_y"), dim(slab, "w")));
  }
  for (xml::Collection_t core(xml, "core"); core; ++core) {
    const std::string coreName = name + "_" + core.attr<std::string>("name");
    const double width = positive(core, "width");
    const double depth = positive(core, "thickness");
    const double outer = positive(core, "tube_outer");
    const double inner = positive(core, "tube_inner");
    const double offset = positive(core, "tube_offset");
    if (inner >= outer || offset + outer >= width / 2 ||
        outer >= depth / 2 || offset <= outer) {
      throw std::runtime_error(coreName + ": cooling tubes do not fit separately within core");
    }
    // Tube axes are local v (beam). Daughters replace parent material: the
    // solid Ti cylinders replace foam, and CO2 replaces their inner titanium.
    // Every exclusive material volume can therefore be calculated analytically
    // from primitive capacities, without stochastic Boolean-solid integration.
    const RotationZYX tubeRotation(0, 0, M_PI / 2);
    Volume coreVolume(coreName, Box(width / 2, length / 2, depth / 2),
                      detector.material(core.attr<std::string>("material")));
    decorate(detector, coreVolume, core);
    const double centreY = dim(core, "center_y"), w = dim(core, "w");
    result.placeVolume(coreVolume, Position(0 * mm, centreY, w));
    for (int sign : {-1, 1}) {
      const std::string suffix = sign < 0 ? "_0" : "_1";
      Volume pipe(name + "_tube" + suffix,
                  Tube(0 * mm, outer, length / 2),
                  detector.material(core.attr<std::string>("tube_material")));
      Volume coolant(name + "_coolant" + suffix,
                     Tube(0 * mm, inner, length / 2),
                     detector.material(core.attr<std::string>("coolant_material")));
      pipe.placeVolume(coolant);
      coreVolume.placeVolume(pipe,
          Transform3D(tubeRotation, Position(sign * offset, 0 * mm, 0 * mm)));
    }
  }
  return result;
}

dd4hep::Volume buildRing(dd4hep::Detector& detector, dd4hep::xml::Handle_t xml) {
  using namespace dd4hep;
  const double inner = positive(xml, "rmin"), outer = positive(xml, "rmax");
  if (inner >= outer) throw std::runtime_error("Mounting ring radii are inverted");
  Volume result(xml.attr<std::string>("name"),
                Tube(inner, outer, positive(xml, "length") / 2),
                detector.material(xml.attr<std::string>("material")));
  decorate(detector, result, xml);
  return result;
}

dd4hep::Volume buildFoot(dd4hep::Detector& detector, dd4hep::xml::Handle_t xml) {
  using namespace dd4hep;
  const double width = positive(xml, "width"), length = positive(xml, "length");
  const double back = positive(xml, "back_radius"), outer = positive(xml, "outer_radius");
  if (outer <= back || std::hypot(back, width / 2) >= outer) {
    throw std::runtime_error("Mounting foot has no positive radial depth at edge");
  }
  const double centre = (back + outer) / 2;
  const Box bounds(width / 2, length / 2, (outer - back) / 2);
  const Tube ringInterior(0 * mm, outer, length / 2);
  const IntersectionSolid shape(bounds, ringInterior,
      Transform3D(RotationZYX(0, 0, M_PI / 2), Position(0 * mm, 0 * mm, -centre)));
  Volume result(xml.attr<std::string>("name"), shape,
                detector.material(xml.attr<std::string>("material")));
  decorate(detector, result, xml);
  return result;
}
}  // namespace nodd
