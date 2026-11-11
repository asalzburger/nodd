// Shared placement logic for the DES030/031 Si-W compact factories.
#ifndef NODD_PROTOTYPES_SIW_WEDGE_ENVELOPE_H
#define NODD_PROTOTYPES_SIW_WEDGE_ENVELOPE_H

#include <DD4hep/DetFactoryHelper.h>

#include <algorithm>
#include <array>
#include <cmath>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace nodd::siw {
inline void placeReplicas(dd4hep::xml::Handle_t xml, dd4hep::Assembly detector,
                          dd4hep::Volume mother,
                          const std::map<std::string, dd4hep::Assembly>& regions,
                          dd4hep::Solid (*shape)(dd4hep::xml::Handle_t),
                          dd4hep::Transform3D (*pose)(dd4hep::xml::Handle_t)) {
  using namespace dd4hep;
  const auto envelope = xml.child(dd4hep::xml::Strng_t("wedge_envelope"), false);
  if (!envelope) {
    for (dd4hep::xml::Collection_t replica(xml, "replica"); replica; ++replica) {
      auto placed = detector.placeVolume(regions.at(replica.attr<std::string>("region")), pose(replica));
      for (auto field : {"side", "sector", "layer"}) {
        placed.addPhysVolID(field, replica.attr<int>(field));
      }
    }
    return;
  }

  struct Replica {
    std::string region;
    int layer;
    Transform3D transform;
  };
  std::map<std::pair<int, int>, std::vector<Replica>> wedges;
  for (dd4hep::xml::Collection_t replica(xml, "replica"); replica; ++replica) {
    wedges[{replica.attr<int>("side"), replica.attr<int>("sector")}].push_back(
        {replica.attr<std::string>("region"), replica.attr<int>("layer"), pose(replica)});
  }
  if (wedges.empty()) {
    throw std::runtime_error("Missing Si-W wedge replicas");
  }

  const auto frameRegion = envelope.attr<std::string>("frame_region");
  const double center = envelope.attr<double>("center_z");
  if (!std::isfinite(center)) {
    throw std::runtime_error("Invalid Si-W wedge envelope center");
  }
  const Transform3D centerShift(Rotation3D{}, Position(0, 0, center));
  const auto wedgePose = [&](const auto& replicas) {
    const auto isFrame = [&](const auto& replica) { return replica.region == frameRegion; };
    const auto frame = std::find_if(replicas.begin(), replicas.end(), isFrame);
    if (frame == replicas.end() || std::count_if(replicas.begin(), replicas.end(), isFrame) != 1) {
      throw std::runtime_error("Expected one frame in each Si-W wedge");
    }
    return frame->transform * centerShift;
  };

  Volume wedge(std::string(detector.name()) + "_wedge", shape(envelope), mother.material());
  const auto& reference = wedges.begin()->second;
  const auto inverseReference = wedgePose(reference).Inverse();
  std::set<std::pair<std::string, int>> regionLayers;
  std::vector<Transform3D> localTransforms;
  for (const auto& replica : reference) {
    if (!regionLayers.emplace(replica.region, replica.layer).second) {
      throw std::runtime_error("Duplicate region and layer in Si-W wedge");
    }
    const auto local = inverseReference * replica.transform;
    auto placed = wedge.placeVolume(regions.at(replica.region), local);
    placed.addPhysVolID("layer", replica.layer);
    localTransforms.push_back(local);
  }

  for (const auto& [identity, replicas] : wedges) {
    const auto placement = wedgePose(replicas);
    const auto inverse = placement.Inverse();
    if (replicas.size() != reference.size()) {
      throw std::runtime_error("Si-W wedge replica count differs from the reference");
    }
    for (std::size_t i = 0; i < replicas.size(); ++i) {
      const auto& replica = replicas[i];
      if (replica.region != reference[i].region || replica.layer != reference[i].layer) {
        throw std::runtime_error("Si-W wedge region or layer differs from the reference");
      }
      std::array<double, 12> expected, actual;
      localTransforms[i].GetComponents(expected.begin(), expected.end());
      (inverse * replica.transform).GetComponents(actual.begin(), actual.end());
      for (std::size_t j = 0; j < expected.size(); ++j) {
        const double tolerance = j % 4 == 3 ? 1e-9 * mm : 1e-12;
        if (std::abs(actual[j] - expected[j]) > tolerance) {
          throw std::runtime_error("Si-W wedge transform differs from the reference");
        }
      }
    }
    auto placed = detector.placeVolume(wedge, placement);
    placed.addPhysVolID("side", identity.first);
    placed.addPhysVolID("sector", identity.second);
  }
}
}  // namespace nodd::siw

#endif
