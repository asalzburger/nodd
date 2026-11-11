// PROTOTYPE: expanded native Geant4 sensor identity, independent of volume names.
#include <DDG4/Geant4Mapping.h>
#include <G4NavigationHistory.hh>
#include <G4TouchableHistory.hh>
#include <G4TransportationManager.hh>
#include <G4Box.hh>
#include <G4LogicalVolume.hh>
#include <G4Material.hh>
#include <G4Region.hh>
#include <G4SystemOfUnits.hh>
#include <nlohmann/json.hpp>
#include <functional>
#include <set>

std::string trackerGeant4Sensors() {
  using nlohmann::json;
  json sensors=json::array();
  auto manager=dd4hep::sim::Geant4Mapping::instance().volumeManager();
  auto* world=G4TransportationManager::GetTransportationManager()->GetNavigatorForTracking()->GetWorldVolume();
  G4NavigationHistory history;
  history.SetFirstEntry(world);
  std::set<dd4hep::VolumeID> ids;
  auto vector=[](G4ThreeVector v) { return json::array({v.x(),v.y(),v.z()}); };
  std::function<void(G4VPhysicalVolume*)> visit=[&](G4VPhysicalVolume* pv) {
    auto* volume=pv->GetLogicalVolume();
    if (volume->GetSensitiveDetector()) {
      G4TouchableHistory touch(history);
      const auto id=manager.volumeID(&touch);
      if (id==manager.InvalidPath || id==manager.Insensitive || id==manager.NonExisting || !ids.insert(id).second)
        throw std::runtime_error("Invalid or duplicate expanded Geant4 sensor ID");
      auto* box=dynamic_cast<G4Box*>(volume->GetSolid());
      if (!box) throw std::runtime_error("Unsupported non-box sensor");
      const auto transform=history.GetTopTransform().Inverse();
      sensors.push_back({{"id",id}, {"center_mm",vector(transform.TransformPoint({0,0,0})/CLHEP::mm)},
        {"u",vector(transform.TransformAxis({1,0,0}))},
        {"v",vector(transform.TransformAxis({0,1,0}))},
        {"normal",vector(transform.TransformAxis({0,0,1}))},
        {"size_mm",{2*box->GetXHalfLength()/CLHEP::mm,2*box->GetYHalfLength()/CLHEP::mm,2*box->GetZHalfLength()/CLHEP::mm}},
        {"material",volume->GetMaterial()->GetName()},
        {"density_g_cm3",volume->GetMaterial()->GetDensity()/(CLHEP::g/CLHEP::cm3)},
        {"region",volume->GetRegion() ? volume->GetRegion()->GetName() : ""}});
    }
    for (int i=0;i<volume->GetNoDaughters();++i) {
      auto* child=volume->GetDaughter(i);
      if (child->IsReplicated() || child->IsParameterised())
        throw std::runtime_error("Unsupported replicated/parameterised placement");
      history.NewLevel(child,kNormal,child->GetCopyNo());
      visit(child);
      history.BackLevel();
    }
  };
  visit(world);
  return sensors.dump();
}
