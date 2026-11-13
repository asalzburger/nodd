// Startup-only LAr placement audit: no event transport or response model.
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
#include <iostream>
#include <set>
#include <stdexcept>

void auditLArPlacement(const std::string& directory) {
  const auto& mapping = dd4hep::sim::Geant4Mapping::instance();
  const auto& data = mapping.data();
  std::cout << "LAR_PLACE_G4_MAP_BEGIN" << std::endl;
  const auto manager = mapping.volumeManager();
  std::cout << "LAR_PLACE_G4_MAP_END" << std::endl;
  std::cout << "LAR_PLACE_NATIVE_MAP_BEGIN" << std::endl;
  const auto native = dd4hep::VolumeManager::getVolumeManager(mapping.detectorDescription());
  std::cout << "LAR_PLACE_NATIVE_MAP_END" << std::endl;
  if (!native.isValid()) throw std::runtime_error("Invalid native volume manager");
  G4NavigationHistory history;
  history.SetFirstEntry(data.m_world);
  std::set<dd4hep::VolumeID> ids;
  std::ofstream sensitive(directory + "/sensitive.tsv"), leaves(directory + "/leaves.tsv");
  sensitive << std::setprecision(17); leaves << std::setprecision(17);
  double centerDelta = 0., axisDelta = 0.;
  std::size_t leafCount = 0;
  auto pose = [](std::ostream& out, const G4Transform3D& global) {
    const auto p = global.getTranslation(); const auto r = global.getRotation();
    out << '\t' << p.x() << '\t' << p.y() << '\t' << p.z()
        << '\t' << r.xx() << '\t' << r.xy() << '\t' << r.xz()
        << '\t' << r.yx() << '\t' << r.yy() << '\t' << r.yz()
        << '\t' << r.zx() << '\t' << r.zy() << '\t' << r.zz();
  };
  std::function<void(G4LogicalVolume*, const G4Transform3D&)> visit;
  visit = [&](G4LogicalVolume* mother, const G4Transform3D& transform) {
    for (int i = 0; i < mother->GetNoDaughters(); ++i) {
      auto* daughter = mother->GetDaughter(i); auto* logical = daughter->GetLogicalVolume();
      if (daughter->IsReplicated() || daughter->IsParameterised())
        throw std::runtime_error("Unexpected replicated/parameterised placement");
      history.NewLevel(daughter, kNormal, daughter->GetCopyNo());
      const auto global = transform * G4Transform3D(daughter->GetObjectRotationValue(), daughter->GetObjectTranslation());
      if (logical->GetNoDaughters() == 0) {
        leaves << logical->GetName(); pose(leaves, global);
        leaves << '\t' << logical->GetMaterial()->GetName() << '\t'
               << logical->GetMaterial()->GetDensity() << '\n'; ++leafCount;
      }
      if (logical->GetSensitiveDetector()) {
        const G4TouchableHistory touchable(history);
        const auto id = manager.volumeID(&touchable);
        if (((id & 255) != 10 && (id & 255) != 11) || !ids.insert(id).second)
          throw std::runtime_error("Missing, duplicate or wrong LAr touchable ID");
        const auto* context = native.lookupContext(id);
        if (context != native.lookupContext(id | (1ULL << 24)) ||
            !context->volumePlacement().volume().isSensitive())
          throw std::runtime_error("Native readout context disagrees");
        const auto originNative = context->localToWorld(dd4hep::Position{});
        const G4ThreeVector origin(originNative.x()/dd4hep::mm, originNative.y()/dd4hep::mm, originNative.z()/dd4hep::mm);
        centerDelta = std::max(centerDelta, (origin-global.getTranslation()).mag());
        for (int axis=0; axis<3; ++axis) {
          G4ThreeVector basis; basis[axis]=1.;
          const auto q = context->localToWorld(dd4hep::Position(basis.x()*dd4hep::mm, basis.y()*dd4hep::mm, basis.z()*dd4hep::mm));
          const G4ThreeVector nativeAxis(q.x()/dd4hep::mm, q.y()/dd4hep::mm, q.z()/dd4hep::mm);
          axisDelta = std::max(axisDelta, (nativeAxis-origin-global.getRotation()*basis).mag());
        }
        sensitive << id; pose(sensitive, global); sensitive << '\t' << logical->GetMaterial()->GetName() << '\n';
      }
      visit(logical, global); history.BackLevel();
    }
  };
  visit(data.m_world->GetLogicalVolume(), G4Transform3D{});
  if (!sensitive || !leaves || ids.size()!=data.g4Paths.size() || ids.size()!=43648)
    throw std::runtime_error("Incomplete full LAr placement audit");
  if (centerDelta>1e-7 || axisDelta>1e-10)
    throw std::runtime_error("Native and Geant4 placement transforms differ");
  std::size_t imprints=0;
  for (const auto& entry:data.g4VolumeImprints) imprints+=entry.second.size();
  std::ofstream summary(directory+"/mapping-audit.tsv");
  summary << std::setprecision(17) << ids.size() << '\t' << leafCount << '\t'
          << G4PhysicalVolumeStore::GetInstance()->size() << '\t' << imprints << '\t'
          << centerDelta << '\t' << axisDelta << '\n';
  if(!summary)throw std::runtime_error("Cannot write placement summary");
  std::cout << "LAR_PLACE_AUDIT_DONE" << std::endl;
}
