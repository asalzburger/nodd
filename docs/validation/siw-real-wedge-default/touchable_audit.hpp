#include <DD4hep/VolumeManager.h>
#include <DDG4/Geant4Mapping.h>
#include <G4LogicalVolume.hh>
#include <G4Material.hh>
#include <G4NavigationHistory.hh>
#include <G4PhysicalVolumeStore.hh>
#include <G4TouchableHistory.hh>
#include <G4Transform3D.hh>
#include <G4VPhysicalVolume.hh>
#include <cmath>
#include <fstream>
#include <functional>
#include <iomanip>
#include <set>
#include <stdexcept>

void auditCombinedWedges(const std::string& directory) {
  const auto& mapping = dd4hep::sim::Geant4Mapping::instance();
  const auto& data = mapping.data();
  const auto manager = mapping.volumeManager();
  const auto nativeManager = dd4hep::VolumeManager::getVolumeManager(mapping.detectorDescription());
  if (!nativeManager.isValid()) {
    throw std::runtime_error("Invalid native DD4hep volume manager");
  }
  auto* world = data.m_world;
  double maximumCenterDelta = 0.;
  double maximumAxisDelta = 0.;
  G4NavigationHistory history;
  history.SetFirstEntry(world);
  std::set<dd4hep::VolumeID> ids;
  std::ofstream sensors(directory + "/sensors.tsv");
  sensors << std::setprecision(17);

  std::function<void(G4LogicalVolume*, const G4Transform3D&)> visit;
  visit = [&](G4LogicalVolume* mother, const G4Transform3D& transform) {
    for (int i = 0; i < mother->GetNoDaughters(); ++i) {
      auto* daughter = mother->GetDaughter(i);
      auto* logical = daughter->GetLogicalVolume();
      const bool sensitive = logical->GetSensitiveDetector() != nullptr;
      if (!sensitive && logical->GetNoDaughters() == 0) {
        continue;
      }
      if (daughter->IsReplicated() || daughter->IsParameterised()) {
        throw std::runtime_error("Unexpected parameterised placement");
      }
      history.NewLevel(daughter, kNormal, daughter->GetCopyNo());
      const auto global = transform * G4Transform3D(daughter->GetObjectRotationValue(),
                                                    daughter->GetObjectTranslation());
      if (sensitive) {
        const G4TouchableHistory touchable(history);
        const auto id = manager.volumeID(&touchable);
        if (((id & 255) != 8 && (id & 255) != 9) || !ids.insert(id).second) {
          throw std::runtime_error("Missing or duplicate ECAL touchable ID");
        }
        const auto p = global.getTranslation();
        const auto r = global.getRotation();
        const auto* context = nativeManager.lookupContext(id);
        // A pad bit must resolve through the same sensitive-volume mask.
        if (context != nativeManager.lookupContext(id | (1ULL << 30)) ||
            !context->volumePlacement().volume().isSensitive()) {
          throw std::runtime_error("Native DD4hep context disagrees with the DDG4 sensor");
        }
        const auto nativeOrigin = context->localToWorld(dd4hep::Position{});
        const G4ThreeVector origin(nativeOrigin.x()/dd4hep::mm, nativeOrigin.y()/dd4hep::mm,
                                   nativeOrigin.z()/dd4hep::mm);
        maximumCenterDelta = std::max(maximumCenterDelta, (origin-p).mag());
        for (int axis = 0; axis < 3; ++axis) {
          G4ThreeVector basis;
          basis[axis] = 1.;
          const auto endpoint = context->localToWorld(dd4hep::Position(
              basis.x()*dd4hep::mm, basis.y()*dd4hep::mm, basis.z()*dd4hep::mm));
          const auto nativeAxis = G4ThreeVector(endpoint.x()/dd4hep::mm, endpoint.y()/dd4hep::mm,
                                                endpoint.z()/dd4hep::mm) - origin;
          maximumAxisDelta = std::max(maximumAxisDelta, (nativeAxis-r*basis).mag());
        }
        sensors << id << '\t' << p.x() << '\t' << p.y() << '\t' << p.z()
                << '\t' << r.xx() << '\t' << r.xy() << '\t' << r.xz()
                << '\t' << r.yx() << '\t' << r.yy() << '\t' << r.yz()
                << '\t' << r.zx() << '\t' << r.zy() << '\t' << r.zz()
                << '\t' << logical->GetMaterial()->GetName() << '\n';
      }
      visit(logical, global);
      history.BackLevel();
    }
  };
  visit(world->GetLogicalVolume(), G4Transform3D{});
  if (!sensors || ids.size() != data.g4Paths.size()) {
    throw std::runtime_error("ECAL sensor dump and volume manager counts differ");
  }
  if (maximumCenterDelta > 1e-7 || maximumAxisDelta > 1e-10) {
    throw std::runtime_error("Native DD4hep and DDG4 transforms differ");
  }
  std::size_t imprints = 0;
  for (const auto& entry : data.g4VolumeImprints) {
    imprints += entry.second.size();
  }
  std::ofstream summary(directory + "/mapping-audit.tsv");
  summary << ids.size() << '\t' << G4PhysicalVolumeStore::GetInstance()->size()
          << '\t' << imprints << '\t' << maximumCenterDelta << '\t' << maximumAxisDelta << '\n';
  if (!summary) {
    throw std::runtime_error("Could not record mapping audit");
  }
}
