#include <G4TransportationManager.hh>
#include <G4Navigator.hh>
#include <G4LogicalVolume.hh>
#include <G4Material.hh>
#include <G4SystemOfUnits.hh>
#include <G4TouchableHistory.hh>
#include <TGeoManager.h>
#include <DD4hep/Volumes.h>
#include <fstream>
#include <iomanip>
#include <stdexcept>
#include <map>

void auditMaterialGeant4(const char* input, const char* output) {
  auto* tracking = G4TransportationManager::GetTransportationManager()->GetNavigatorForTracking();
  if (!tracking || !tracking->GetWorldVolume()) throw std::runtime_error("No native Geant4 world");
  G4Navigator navigator;
  navigator.SetWorldVolume(tracking->GetWorldVolume());
  std::map<std::string,int> ddNames;
  for (auto* object : *gGeoManager->GetListOfVolumes()) ++ddNames[object->GetName()];
  std::ifstream points(input);
  std::ofstream out(output);
  out << std::setprecision(17) << "[\n";
  long long track, step;
  double fraction, x, y, z;
  bool first=true;
  while (points >> track >> step >> fraction >> x >> y >> z) {
    auto* physical = navigator.LocateGlobalPointAndSetup(G4ThreeVector(x*CLHEP::mm,y*CLHEP::mm,z*CLHEP::mm),nullptr,false,true);
    if (!physical) throw std::runtime_error("Geant4 lookup outside world");
    auto* logical = physical->GetLogicalVolume();
    auto* material = logical->GetMaterial();
    auto* dd = gGeoManager->FindVolumeFast(logical->GetName().c_str());
    const auto touchable=navigator.CreateTouchableHistoryHandle();
    std::string path;
    for (int depth=touchable->GetHistoryDepth(); depth>=0; --depth)
      path += "/"+std::string(touchable->GetVolume(depth)->GetName());
    if (!first) out << ",\n";
    first=false;
    out << "{\"track\":" << track << ",\"step\":" << step << ",\"fraction\":" << fraction
        << ",\"g4_path\":\"" << path
        << "\",\"g4_volume\":\"" << logical->GetName() << "\",\"g4_material\":\"" << material->GetName()
        << "\",\"g4_density_g_cm3\":" << material->GetDensity()/(CLHEP::g/CLHEP::cm3)
        << ",\"g4_X0_mm\":" << material->GetRadlen()/CLHEP::mm
        << ",\"g4_L0_mm\":" << material->GetNuclearInterLength()/CLHEP::mm
        << ",\"dd_volume_found\":" << (dd?"true":"false")
        << ",\"dd_name_matches\":" << ddNames[logical->GetName()];
    if(dd) out << ",\"dd_material\":\"" << dd->GetMaterial()->GetName()
        << "\",\"dd_density_g_cm3\":" << dd->GetMaterial()->GetDensity()
        << ",\"dd_sensitive\":" << (dd4hep::Volume(dd).isSensitive()?"true":"false");
    out << "}";
  }
  out << "\n]\n";
}
