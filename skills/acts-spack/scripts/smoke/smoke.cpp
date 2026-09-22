// Dependency/link smoke test only; no nODD geometry or simulation is constructed.
#include <DD4hep/Detector.h>
#include <G4NistManager.hh>
#include <G4Material.hh>
#include <G4Version.hh>
#include <iostream>

int main() {
  auto& detector = dd4hep::Detector::getInstance();
  auto* silicon = G4NistManager::Instance()->FindOrBuildMaterial("G4_Si");
  if (silicon == nullptr) return 1;
  std::cout << "DD4hep Detector obtained; " << G4Version
            << "; material=" << silicon->GetName() << '\n';
  (void)detector;
  return 0;
}
