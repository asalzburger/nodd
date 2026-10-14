// DES028 isolated hardware prototype; absent from production CMake.
#include <DD4hep/DetFactoryHelper.h>
#include <cmath>
#include <stdexcept>
#include <map>
#include <vector>

namespace {
using namespace dd4hep;
using xml::Handle_t;

double value(Handle_t h, const char* key) {
  double result = h.attr<double>(key);
  if (!std::isfinite(result)) throw std::runtime_error("Nonfinite dimension");
  return result;
}

Solid shape(Handle_t h) {
  std::string kind = h.attr<std::string>("kind");
  if (kind == "box") {
    return Box(value(h, "sx") / 2, value(h, "sy") / 2, value(h, "sz") / 2);
  }
  if (kind == "tube") {
    return Tube(value(h, "rmin"), value(h, "rmax"), value(h, "length") / 2);
  }
  if (kind == "xtru") {
    std::vector<double> x, y;
    for (xml::Collection_t vertex(h, "vertex"); vertex; ++vertex) {
      x.push_back(value(vertex, "x")); y.push_back(value(vertex, "y"));
    }
    double half = value(h, "depth") / 2;
    return ExtrudedPolygon(x, y, {-half, half}, {0, 0}, {0, 0}, {1, 1});
  }
  throw std::runtime_error("Unsupported primitive");
}

Transform3D pose(Handle_t h) {
  return Transform3D(
      Rotation3D(value(h, "a00"), value(h, "a01"), value(h, "a02"),
                 value(h, "a10"), value(h, "a11"), value(h, "a12"),
                 value(h, "a20"), value(h, "a21"), value(h, "a22")),
      Position(value(h, "x"), value(h, "y"), value(h, "z")));
}

Ref_t createCalorimeter(Detector& detector, Handle_t h, SensitiveDetector sd) {
  std::string name = h.attr<std::string>("name");
  DetElement result(name, h.attr<int>("id"));
  Assembly unit(name + "Cassette");
  sd.setType("calorimeter");
  for (xml::Collection_t piece(h, "piece"); piece; ++piece) {
    Solid solid = shape(piece);
    for (xml::Collection_t cut(piece, "cut"); cut; ++cut) {
      solid = SubtractionSolid(solid, shape(cut),
                              Position(value(cut, "x"), value(cut, "y"), value(cut, "z")));
    }
    Volume volume(piece.attr<std::string>("name"), solid,
                  detector.material(piece.attr<std::string>("material")));
    if (piece.hasAttr("sensor")) volume.setSensitiveDetector(sd);
    auto placed = unit.placeVolume(volume, pose(piece));
    if (piece.hasAttr("sensor")) placed.addPhysVolID("sensor", piece.attr<int>("sensor"));
  }
  Assembly assembly(name);
  for (xml::Collection_t placement(h, "placement"); placement; ++placement) {
    auto placed = assembly.placeVolume(unit, Position(value(placement, "x"),
        value(placement, "y"), value(placement, "z")));
    for (auto key : {"side", "sector", "layer", "cassette"}) {
      placed.addPhysVolID(key, placement.attr<int>(key));
    }
  }
  std::map<std::string, Assembly> regions;
  for (xml::Collection_t region(h, "region"); region; ++region) {
    std::string regionName = region.attr<std::string>("name");
    Assembly sector(regionName);
    for (xml::Collection_t piece(region, "passive"); piece; ++piece) {
      Volume volume(piece.attr<std::string>("name"), shape(piece),
                    detector.material(piece.attr<std::string>("material")));
      sector.placeVolume(volume, pose(piece));
    }
    for (xml::Collection_t placement(region, "placement"); placement; ++placement) {
      auto placed = sector.placeVolume(unit, pose(placement));
      for (auto key : {"layer", "cassette"}) {
        placed.addPhysVolID(key, placement.attr<int>(key));
      }
    }
    if (!regions.emplace(regionName, sector).second) {
      throw std::runtime_error("Duplicate sector template");
    }
  }
  for (xml::Collection_t replica(h, "replica"); replica; ++replica) {
    auto placed = assembly.placeVolume(regions.at(replica.attr<std::string>("region")), pose(replica));
    for (auto key : {"side", "sector"}) {
      placed.addPhysVolID(key, replica.attr<int>(key));
    }
  }
  auto placed = detector.pickMotherVolume(result).placeVolume(assembly);
  placed.addPhysVolID("system", h.attr<int>("id"));
  result.setPlacement(placed);
  return result;
}
}  // namespace
DECLARE_DETELEMENT(nODDCalorimeterPrototype, createCalorimeter)
