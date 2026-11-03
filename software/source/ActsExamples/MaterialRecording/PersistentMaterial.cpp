// Isolated immutable-geometry PROTOTYPE, following the existing TruthTracking
// adapter. Geant4 and ACTS retain generation, physics, stepping and event seeds.
#include "ActsExamples/Geant4/Geant4Manager.hpp"
#include "ActsExamples/Geant4/MaterialPhysicsList.hpp"
#include <G4RunManager.hh>
#include <G4StateManager.hh>
#include <pybind11/pybind11.h>
#include <memory>
#include <stdexcept>

static_assert(PYBIND11_INTERNALS_VERSION == 11, "Match the pinned ACTS pybind ABI");
namespace py = pybind11;
using ActsExamples::Geant4Handle;
class PersistentMaterialRunManager final : public G4RunManager {
 public:
  explicit PersistentMaterialRunManager(int count) : expected(count) {
    if (count <= 0) throw std::invalid_argument("Expected event count must be positive");
  }
  void BeamOn(G4int count, const char* macro=nullptr, G4int select=-1) override {
    if (count!=1 || macro || select!=-1 || finished || processed>=expected)
      throw std::runtime_error("Require exactly one event per call in a fixed case");
    if (!started) {
      if (!ConfirmBeamOnCondition()) throw std::runtime_error("Initialization rejected");
      numberOfEventToBeProcessed=expected;
      RunInitialization();
      ++initializations;
      if (G4StateManager::GetStateManager()->GetCurrentState()!=G4State_GeomClosed)
        throw std::runtime_error("Native run initialization did not close geometry");
      InitializeEventLoop(expected,nullptr,-1);
      ++loopInitializations;
      started=true;
    }
    if (runAborted) throw std::runtime_error("Native run aborted before event");
    ProcessOneEvent(processed);
    TerminateOneEvent();
    ++processed;
    if (runAborted) throw std::runtime_error("Native run aborted during event");
    if (processed==expected) finish(true);
  }
  void finish(bool requireComplete) {
    if (started && !finished) {
      TerminateEventLoop();
      ++loopTerminations;
      RunTermination();
      ++terminations;
      finished=true;
    }
    if (requireComplete && (!started || !finished || processed!=expected || runAborted))
      throw std::runtime_error("Persistent material run did not complete expected events");
  }
  py::dict report() const {
    py::dict d;
    d["expected_events"]=expected; d["processed_events"]=processed;
    d["run_initializations"]=initializations; d["event_loop_initializations"]=loopInitializations;
    d["run_terminations"]=terminations; d["event_loop_terminations"]=loopTerminations;
    d["finished"]=finished; d["aborted"]=runAborted;
    d["physics_list"]="MaterialPhysicsList";
    d["geometry_policy"]="Immutable geometry/materials/regions/cuts/physics/actions; one thread";
    return d;
  }
 private:
  int expected,processed=0,initializations=0,loopInitializations=0;
  int terminations=0,loopTerminations=0;
  bool started=false,finished=false;
};
PersistentMaterialRunManager& manager(Geant4Handle& h) {
  auto* m=dynamic_cast<PersistentMaterialRunManager*>(h.runManager.get());
  if (!m) throw std::invalid_argument("Not a persistent material handle");
  return *m;
}
PYBIND11_MODULE(nodd_material_recording_native,m) {
  m.def("persistent_handle",[](int events) {
    static bool created=false;
    if (events<=0) throw std::invalid_argument("Expected event count must be positive");
    if (created || G4RunManager::GetRunManager()!=nullptr ||
        ActsExamples::Geant4Manager::instance().currentHandle())
      throw std::runtime_error("Only one Geant4 manager is allowed in this process");
    auto result=std::make_shared<Geant4Handle>(
      std::make_unique<PersistentMaterialRunManager>(events),
      std::make_unique<ActsExamples::Geant4::MaterialPhysicsList>(),"MaterialPhysicsList");
    created=true;
    return result;
  });
  m.def("finish",[](Geant4Handle& h,bool complete) { manager(h).finish(complete); },
        py::arg("handle"),py::arg("require_complete")=true);
  m.def("report",[](Geant4Handle& h) { return manager(h).report(); });
}
