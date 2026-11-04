// Isolated PROTOTYPE: decorate existing Gen3 portals; no geometry construction.
#include "Acts/Geometry/Portal.hpp"
#include "Acts/Geometry/TrackingGeometry.hpp"
#include "Acts/Geometry/TrackingGeometryVisitor.hpp"
#include "Acts/Material/ProtoSurfaceMaterial.hpp"
#include "Acts/Material/BinnedSurfaceMaterial.hpp"
#include "Acts/Material/HomogeneousSurfaceMaterial.hpp"
#include "Acts/Material/detail/MaterialSurfaceRegistry.hpp"
#include "Acts/Surfaces/CylinderBounds.hpp"
#include "Acts/Surfaces/CylinderSurface.hpp"
#include "Acts/Surfaces/DiscSurface.hpp"
#include "Acts/Surfaces/RadialBounds.hpp"
#include "Acts/Surfaces/Surface.hpp"
#include "Acts/Utilities/BinUtility.hpp"
#include "ActsExamples/Framework/AlgorithmContext.hpp"
#include "ActsExamples/Framework/DataHandle.hpp"
#include "ActsExamples/Framework/IAlgorithm.hpp"
#include "Acts/Material/MaterialInteraction.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <algorithm>
#include <cmath>
#include <map>
#include <numbers>
#include <set>
#include <stdexcept>
#include <unordered_map>

namespace py = pybind11;
static_assert(PYBIND11_INTERNALS_VERSION == NODD_EXPECTED_PYBIND11_INTERNALS_VERSION,
              "pybind11 headers do not match the selected ACTS Python internals ABI");
namespace {
constexpr double tolerance = 1.e-8;  // Export precision check in mm, not clearance.

struct Inventory : Acts::TrackingGeometryMutableVisitor {
  std::set<Acts::Surface*> all;
  std::set<Acts::Surface*> portals;
  std::set<Acts::TrackingVolume*> volumes;
  void visitSurface(Acts::Surface& s) override { all.insert(&s); }
  void visitPortal(Acts::Portal& p) override {
    portals.insert(&p.surface());
    all.insert(&p.surface());
  }
  void visitVolume(Acts::TrackingVolume& v) override { volumes.insert(&v); }
};

using Segment = std::array<std::array<double, 2>, 2>;
std::pair<std::string, Segment> shape(const Acts::Surface& s,
                                    const Acts::GeometryContext& gctx) {
  auto tr = s.localToGlobalTransform(gctx);
  if (std::hypot(tr.translation().x(), tr.translation().y()) > tolerance ||
      std::abs(std::abs(tr.linear()(2, 2)) - 1.) > tolerance) {
    throw std::invalid_argument("Only coaxial, axisymmetric portals are supported");
  }
  const double z = tr.translation().z();
  if (const auto* c = dynamic_cast<const Acts::CylinderSurface*>(&s)) {
    const auto& b = c->bounds();
    if (std::abs(b.get(Acts::CylinderBounds::eHalfPhiSector) - std::numbers::pi) > tolerance) {
      throw std::invalid_argument("Partial-phi cylinder rejected");
    }
    double r = b.get(Acts::CylinderBounds::eR);
    double hz = b.get(Acts::CylinderBounds::eHalfLengthZ);
    return {"cylinder", {{{r, z - hz}, {r, z + hz}}}};
  }
  if (const auto* d = dynamic_cast<const Acts::DiscSurface*>(&s)) {
    const auto* b = dynamic_cast<const Acts::RadialBounds*>(&d->bounds());
    if (b == nullptr || std::abs(b->get(Acts::RadialBounds::eHalfPhiSector) - std::numbers::pi) > tolerance) {
      throw std::invalid_argument("Only full-phi radial disc bounds are supported");
    }
    return {"disc", {{{b->get(Acts::RadialBounds::eMinR), z},
                       {b->get(Acts::RadialBounds::eMaxR), z}}}};
  }
  throw std::invalid_argument("Selected surface is neither cylinder nor disc");
}

py::dict configure(Acts::TrackingGeometry& geometry,
                   const Acts::GeometryContext& gctx, const py::list& selection) {
  Inventory inventory;
  geometry.apply(inventory);
  std::map<std::uint64_t, Acts::Surface*> portals;
  for (auto* s : inventory.portals) {
    if (!portals.emplace(s->geometryId().value(), s).second) {
      throw std::invalid_argument("Distinct native portal surfaces share a geometry ID");
    }
  }
  struct Assignment { Acts::Surface* surface; std::shared_ptr<const Acts::ISurfaceMaterial> material; };
  std::vector<Assignment> assignments;
  std::set<std::uint64_t> ids;
  std::set<std::string> keys;
  py::list selected;
  // Validate the complete request before mutating the geometry.
  for (auto item : selection) {
    py::dict record = py::cast<py::dict>(item);
    auto id = py::cast<std::uint64_t>(record["geometry_id"]);
    auto key = py::cast<std::string>(record["material_key"]);
    if (!ids.insert(id).second || key.empty() || !keys.insert(key).second) {
      throw std::invalid_argument("Duplicate geometry ID or empty/duplicate material key");
    }
    auto found = portals.find(id);
    if (found == portals.end()) throw std::invalid_argument("Selected geometry ID is not a native portal");
    auto* surface = found->second;
    auto [type, segment] = shape(*surface, gctx);
    if (type != py::cast<std::string>(record["type"])) {
      throw std::invalid_argument("Manifest/native surface type mismatch");
    }
    auto expected = py::cast<Segment>(record["rz_segment_mm"]);
    for (std::size_t i = 0; i < 2; ++i) {
      for (std::size_t j = 0; j < 2; ++j) {
        if (!std::isfinite(expected[i][j]) || std::abs(expected[i][j] - segment[i][j]) > tolerance) {
          throw std::invalid_argument("Manifest/native finite bounds mismatch");
        }
      }
    }
    py::dict bins = py::cast<py::dict>(record["bins"]);
    const auto phi = py::cast<std::size_t>(bins["phi"]);
    const auto other = py::cast<std::size_t>(bins[type == "cylinder" ? "z" : "r"]);
    if (phi == 0 || other == 0) throw std::invalid_argument("Bin counts must be positive");
    Acts::BinUtility binning(phi, -std::numbers::pi, std::numbers::pi,
                            Acts::closed, Acts::AxisDirection::AxisPhi);
    binning += Acts::BinUtility(other, 0., 1., Acts::open,
        type == "cylinder" ? Acts::AxisDirection::AxisZ : Acts::AxisDirection::AxisR);
    auto material = std::make_shared<const Acts::ProtoSurfaceMaterial>(
        binning, Acts::MappingType::Default, key);
    assignments.push_back({surface, material});
    py::dict entry;
    entry["geometry_id"] = id;
    entry["material_key"] = key;
    entry["type"] = type;
    entry["rz_segment_mm"] = segment;
    entry["bins"] = bins;
    selected.append(entry);
  }
  if (assignments.empty()) throw std::invalid_argument("No selected material portals");
  std::size_t cleared = 0, clearedVolumes = 0;
  for (auto* s : inventory.all) {
    if (s->surfaceMaterial()) ++cleared;
    s->assignSurfaceMaterial(nullptr);
  }
  for (auto* v : inventory.volumes) {
    if (v->volumeMaterial()) ++clearedVolumes;
    v->assignVolumeMaterial(nullptr);
  }
  for (auto& assignment : assignments) {
    assignment.surface->assignSurfaceMaterial(std::move(assignment.material));
  }
  py::list surfaces;
  for (const auto& assignment : assignments) {
    surfaces.append(py::cast(assignment.surface, py::return_value_policy::reference));
  }
  py::dict result;
  result["surfaces"] = surfaces;
  result["selected"] = selected;
  result["cleared_native_surface_materials"] = cleared;
  result["cleared_native_volume_materials"] = clearedVolumes;
  result["native_portal_surfaces"] = portals.size();
  result["selected_count"] = assignments.size();
  return result;
}

py::list materialInventory(Acts::TrackingGeometry& geometry) {
  Inventory inventory;
  geometry.apply(inventory);
  py::list result;
  for (auto* surface : inventory.all) {
    const auto* material = surface->surfaceMaterial();
    if (material == nullptr) continue;
    py::dict entry;
    entry["geometry_id"] = surface->geometryId().value();
    if (const auto* proto = dynamic_cast<const Acts::ProtoSurfaceMaterial*>(material)) {
      entry["type"] = "proto";
      entry["material_key"] = proto->materialKey();
      entry["core_material_key"] = Acts::detail::materialKey(material);
      entry["axis_bin_counts"] = std::array<std::size_t, 2>{proto->binning().bins(0), proto->binning().bins(1)};
    } else if (const auto* binned = dynamic_cast<const Acts::BinnedSurfaceMaterial*>(material)) {
      entry["type"] = "binned";
      entry["axis_bin_counts"] = std::array<std::size_t, 2>{binned->binUtility().bins(0), binned->binUtility().bins(1)};
      std::size_t empty = 0, total = 0;
      for (const auto& row : binned->fullMaterial()) {
        for (const auto& slab : row) {
          ++total;
          if (slab.thickness() == 0.) ++empty;
        }
      }
      entry["material_bins"] = total;
      entry["empty_bins"] = empty;
    } else if (const auto* homogeneous = dynamic_cast<const Acts::HomogeneousSurfaceMaterial*>(material)) {
      entry["type"] = "homogeneous";
      entry["axis_bin_counts"] = std::array<std::size_t, 2>{1, 1};
      entry["material_bins"] = 1;
      entry["empty_bins"] = homogeneous->materialSlab().thickness() == 0. ? 1 : 0;
    } else {
      entry["type"] = "other";
    }
    result.append(entry);
  }
  return result;
}

// The ROOT reader preserves Geant4 pre-step positions. Move only the position
// to the physical midpoint; all constituent slabs and per-track totals survive.
class MidpointMaterial final : public ActsExamples::IAlgorithm {
 public:
  using Tracks = std::unordered_map<std::size_t, Acts::RecordedMaterialTrack>;
  MidpointMaterial(const std::string& input, const std::string& output)
      : IAlgorithm("NoddMaterialMidpoints", Acts::getDefaultLogger("NoddMaterialMidpoints", Acts::Logging::INFO)) {
    m_input.initialize(input);
    m_output.initialize(output);
  }
  ActsExamples::ProcessCode execute(const ActsExamples::AlgorithmContext& ctx) const override {
    Tracks tracks = m_input(ctx);
    for (auto& [id, track] : tracks) {
      for (auto& step : track.second.materialInteractions) {
        const auto norm = step.direction.norm();
        if (!std::isfinite(norm) || std::abs(norm - 1.) > 1.e-5) {
          throw std::invalid_argument("Midpoint correction requires unit recorded directions");
        }
        step.position += 0.5 * step.materialSlab.thickness() * step.direction;
      }
    }
    m_output(ctx, std::move(tracks));
    return ActsExamples::ProcessCode::SUCCESS;
  }
 private:
  ActsExamples::ReadDataHandle<Tracks> m_input{this, "InputMaterialTracks"};
  ActsExamples::WriteDataHandle<Tracks> m_output{this, "OutputMaterialTracks"};
};
}  // namespace

PYBIND11_MODULE(nodd_portal_material, module) {
  module.doc() = "Isolated Gen3 portal ProtoSurfaceMaterial and Geant4 midpoint adapter";
  module.attr("pybind11_internals_version") = PYBIND11_INTERNALS_VERSION;
  module.attr("pybind11_version") = std::to_string(PYBIND11_VERSION_MAJOR) + "." +
      std::to_string(PYBIND11_VERSION_MINOR) + "." + std::to_string(PYBIND11_VERSION_PATCH);
  module.def("configure", &configure, py::arg("geometry"), py::arg("context"), py::arg("selection"));
  module.def("material_inventory", &materialInventory, py::arg("geometry"));
  module.def("midpoint_algorithm", [](const std::string& input, const std::string& output) {
    return std::static_pointer_cast<ActsExamples::IAlgorithm>(std::make_shared<MidpointMaterial>(input, output));
  });
}
