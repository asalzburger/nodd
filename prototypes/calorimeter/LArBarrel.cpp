// DES032 isolated LAr barrel: independent face geometry and canonical readout.
#include <DD4hep/DetFactoryHelper.h>
#include <DD4hep/detail/SegmentationsInterna.h>
#include <DDSegmentation/Segmentation.h>
#include <cmath>
#include <map>
#include <mutex>
#include <stdexcept>
#include <utility>
#include <vector>

namespace {
using namespace dd4hep;
using namespace dd4hep::DDSegmentation;
using xml::Handle_t;

using SegmentationBase = dd4hep::DDSegmentation::Segmentation;
class LArBarrelMerged : public SegmentationBase {
  double pitch = 0, offset = 0;
  int planes = 0, phiMerge = 0;
  std::vector<int> thetaMerge;
  std::vector<double> table;
  mutable std::once_flag initialized;
  mutable std::map<std::pair<int,int>, Vector3D> references;
  void initialize() const {
    std::call_once(initialized, [this] {
      if (!(pitch > 0) || phiMerge != 2 || planes <= 0 || planes % phiMerge || thetaMerge.size() != 11 || table.size() % 5)
        throw std::runtime_error("Invalid LAr merged readout parameters");
      for (size_t i = 0; i < table.size(); i += 5) {
        int layer = int(table[i]), theta = int(table[i+1]);
        if (layer < 0 || layer >= 11 || thetaMerge[layer] <= 0 || theta % thetaMerge[layer])
          throw std::runtime_error("Invalid canonical theta reference key");
        if (!references.emplace(std::make_pair(layer,theta), Vector3D(table[i+2]*mm, table[i+3]*mm, table[i+4]*mm)).second)
          throw std::runtime_error("Duplicate canonical LAr cell");
      }
    });
  }
 public:
  explicit LArBarrelMerged(const BitFieldCoder* decoder) : SegmentationBase(decoder) {
    _type = "nODDLArBarrelMerged";
    _description = "Two-electrode/two-gap grouping, layer-dependent theta; canonical active-volume references";
    registerParameter("theta_fine_pitch_rad", "Fine physical theta-bin pitch in radians", pitch, 0.);
    registerParameter("theta_offset_rad", "Theta fine-bin zero centre in radians", offset, 0.);
    registerParameter("theta_merging", "Per-layer fine theta bins per logical cell", thetaMerge, std::vector<int>{});
    registerParameter("planes", "Physical electrode plane count", planes, 0);
    registerParameter("phi_merge", "Physical electrodes per logical phi cell", phiMerge, 0);
    registerParameter("reference_table_mm", "Layer/theta-index/local canonical gap0 interior x,y,z; mm", table, std::vector<double>{});
  }
  bool cellsSpanVolumes() const override { return true; }
  Vector3D position(const CellID& id) const override {
    initialize();
    int plane = int(_decoder->get(id, "plane"));
    if (plane < 0 || plane >= planes || plane % phiMerge || _decoder->get(id, "gap") != 0)
      throw std::runtime_error("Noncanonical merged LAr cell ID");
    auto key = std::make_pair(int(_decoder->get(id, "layer")), int(_decoder->get(id, "theta")));
    auto entry = references.find(key);
    if (entry == references.end()) throw std::runtime_error("No physical LAr cell for theta index");
    return entry->second;
  }
  CellID cellID(const Vector3D&, const Vector3D& global, const VolumeID& raw) const override {
    initialize();
    int layer = int(_decoder->get(raw, "layer")), plane = int(_decoder->get(raw, "plane")), gap = int(_decoder->get(raw, "gap"));
    if (layer < 0 || layer >= 11 || plane < 0 || plane >= planes || gap < 0 || gap > 1)
      throw std::runtime_error("Invalid raw LAr volume ID");
    double theta = std::atan2(std::hypot(global.x(), global.y()), global.z());
    int fine = int(std::floor((theta-offset)/pitch+.5));
    int merged = thetaMerge[layer]*int(std::floor(double(fine)/thetaMerge[layer]));
    CellID result = raw;
    _decoder->set(result, "theta", merged);
    _decoder->set(result, "plane", (plane/phiMerge)*phiMerge);
    _decoder->set(result, "gap", 0);
    // Reject extrapolated cells that have no physical canonical active volume.
    position(result);
    return result;
  }
  VolumeID volumeID(const CellID& id) const override {
    initialize();
    position(id);
    VolumeID result = id;
    _decoder->set(result, "theta", 0);
    return result;
  }
};

double value(Handle_t h, const char* key) {
  double v = h.attr<double>(key);
  if (!std::isfinite(v)) throw std::runtime_error("Nonfinite LAr geometry input");
  return v;
}
Transform3D pose(Handle_t h) {
  Rotation3D r(value(h,"a00"),value(h,"a01"),value(h,"a02"),value(h,"a10"),value(h,"a11"),value(h,"a12"),value(h,"a20"),value(h,"a21"),value(h,"a22"));
  return Transform3D(r,Position(value(h,"x"),value(h,"y"),value(h,"z")));
}
Solid shape(Handle_t h) {
  auto kind = h.attr<std::string>("kind");
  Solid solid;
  if (kind == "box") solid = Box(value(h,"sx")/2,value(h,"sy")/2,value(h,"sz")/2);
  else if (kind == "tube") solid = Tube(value(h,"rmin"),value(h,"rmax"),value(h,"length")/2);
  else if (kind == "xtru") {
    std::vector<double> x,y;
    for (xml::Collection_t vertex(h,"vertex"); vertex; ++vertex) {
      x.push_back(value(vertex,"x")); y.push_back(value(vertex,"y"));
    }
    double half = value(h,"depth")/2;
    solid = ExtrudedPolygon(x,y,{-half,half},{0,0},{0,0},{1,1});
  } else throw std::runtime_error("Unsupported LAr primitive");
  for (xml::Collection_t annulus(h,"annulus"); annulus; ++annulus)
    solid = IntersectionSolid(solid, Tube(value(annulus,"rmin"),value(annulus,"rmax"),value(annulus,"length")/2));
  for (xml::Collection_t cut(h,"cut"); cut; ++cut)
    solid = SubtractionSolid(solid,shape(cut),pose(cut));
  return solid;
}

Ref_t createLArBarrel(Detector& detector, Handle_t h, SensitiveDetector sd) {
  auto name = h.attr<std::string>("name");
  DetElement result(name,h.attr<int>("id"));
  Assembly assembly(name), period("LArInclinedPeriod");
  sd.setType("calorimeter");
  auto add = [&](Assembly& mother, Handle_t piece) {
    Volume volume(piece.attr<std::string>("name"),shape(piece),detector.material(piece.attr<std::string>("material")));
    bool sensitive = piece.attr<std::string>("role") == "sensitive";
    if (sensitive) volume.setSensitiveDetector(sd);
    auto placed = mother.placeVolume(volume,pose(piece));
    if (sensitive) {
      placed.addPhysVolID("layer",piece.attr<int>("layer"));
      placed.addPhysVolID("gap",piece.attr<int>("gap"));
    }
  };
  for (xml::Collection_t holder(h,"period"); holder; ++holder)
    for (xml::Collection_t piece(holder,"piece"); piece; ++piece) add(period,piece);
  for (xml::Collection_t replica(h,"replica"); replica; ++replica) {
    auto placed = assembly.placeVolume(period,pose(replica));
    placed.addPhysVolID("plane",replica.attr<int>("plane"));
  }
  // Services may be daughters of a bath: the mother retains its full shape,
  // while the expected exclusive ledger subtracts all actual daughter volumes.
  std::map<std::string,Volume> passives;
  std::vector<Handle_t> pending;
  for (xml::Collection_t piece(h,"piece"); piece; ++piece) {
    auto tag = piece.attr<std::string>("name");
    Volume v(tag,shape(piece),detector.material(piece.attr<std::string>("material")));
    if (!passives.emplace(tag,v).second) throw std::runtime_error("Duplicate passive name");
    pending.push_back(piece);
  }
  std::map<std::string,bool> placedNames;
  while (!pending.empty()) {
    bool progress = false;
    for (auto it = pending.begin(); it != pending.end();) {
      auto piece = *it;
      auto tag = piece.attr<std::string>("name");
      bool parent = piece.hasAttr("parent_name");
      auto parentName = parent ? piece.attr<std::string>("parent_name") : std::string{};
      if (parent && !passives.count(parentName)) throw std::runtime_error("Unknown passive parent");
      if (parent && !placedNames.count(parentName)) { ++it; continue; }
      if (parent) passives.at(parentName).placeVolume(passives.at(tag),pose(piece));
      else assembly.placeVolume(passives.at(tag),pose(piece));
      placedNames.emplace(tag,true); it = pending.erase(it); progress = true;
    }
    if (!progress) throw std::runtime_error("Cycle in passive parent hierarchy");
  }
  auto placed = detector.pickMotherVolume(result).placeVolume(assembly);
  placed.addPhysVolID("system",h.attr<int>("id"));
  result.setPlacement(placed);
  return result;
}
SegmentationObject* createMerged(const BitFieldCoder* decoder) {
  return new SegmentationWrapper<LArBarrelMerged>(decoder);
}
} // namespace
DECLARE_DETELEMENT(nODDLArBarrelPrototype,createLArBarrel)
DECLARE_SEGMENTATION(nODDLArBarrelMerged,createMerged)
