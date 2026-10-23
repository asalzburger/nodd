// Transport instrumentation for a geometry without sensitive detectors.
// DDG4's output action skips events whose hit-container pointer is null. Supply
// an empty owned container so it can persist MC truth, without inventing hits.
#include <DDG4/Factories.h>
#include <DDG4/Geant4EventAction.h>
#include <G4Event.hh>
#include <G4HCofThisEvent.hh>

namespace dd4hep::sim {
class nODDMuonEmptyEvent : public Geant4EventAction {
public:
  nODDMuonEmptyEvent(Geant4Context* context, const std::string& name)
      : Geant4EventAction(context, name) {}
  void begin(const G4Event* event) override {
    if (!event->GetHCofThisEvent()) {
      // G4Event assumes ownership and deletes the container at event teardown.
      const_cast<G4Event*>(event)->SetHCofThisEvent(new G4HCofThisEvent());
    }
  }
};
}
DECLARE_GEANT4ACTION(nODDMuonEmptyEvent)
