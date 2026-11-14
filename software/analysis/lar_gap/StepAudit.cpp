// Independent PROTOTYPE accounting; no geometry, hit, track, RNG or tolerance edits.
// Semantics: DD4hep v01-38 /142cbb7eb29ec4feafb1af9317fac38775872085:
// Geant4SensDetFilters.cpp edep0; Geant4SDActions.cpp scintillator contribution;
// Geant4SensDetAction.cpp pre-touchable arithmetic-midpoint classification.
#include <DDG4/Factories.h>
#include <DDG4/Geant4EventAction.h>
#include <DDG4/Geant4SteppingAction.h>
#include <DDG4/Geant4Mapping.h>
#include <DDG4/Geant4Data.h>
#include <DDG4/Geant4VolumeManager.h>
#include <DD4hep/Detector.h>
#include <G4Step.hh>
#include <G4Track.hh>
#include <G4Event.hh>
#include <G4Run.hh>
#include <G4RunManager.hh>
#include <G4LogicalVolume.hh>
#include <G4VSensitiveDetector.hh>
#include <G4Material.hh>
#include <G4IonisParamMat.hh>
#include <G4OpticalPhoton.hh>
#include <G4TouchableHistory.hh>
#include <G4SystemOfUnits.hh>
#include <G4Threading.hh>
#include <nlohmann/json.hpp>
#include <array>
#include <cmath>
#include <cfenv>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <map>
#include <limits>
#include <memory>
#include <set>
#include <stdexcept>
#include <string>

namespace {
using StepJson=nlohmann::json;
static_assert(std::numeric_limits<double>::is_iec559 && std::numeric_limits<double>::digits==53);
static_assert(std::numeric_limits<float>::is_iec559 && std::numeric_limits<float>::digits==24);
struct Cell {double sum=0.;std::size_t steps=0;};
struct Collection {
  double all=0.,unassigned=0.;std::size_t callbacks=0,positive=0,zero=0;
  std::map<dd4hep::VolumeID,Cell> cells;StepJson failures=StepJson::array();
};
struct State {
  std::ofstream output;StepJson config;int event=-1,run=-1;std::array<Collection,2> collections;
  std::set<std::pair<int,int>> identities;
  State() {
    const char* directory=std::getenv("NODD_LAR_OBSERVER");
    if(!directory)throw std::runtime_error("Observer directory unset");
    const auto file=std::string(directory)+"/worker-"+std::to_string(G4Threading::G4GetThreadId())+".jsonl";
    if(std::filesystem::exists(file))throw std::runtime_error("Refusing observer overwrite");
    std::ifstream input(std::string(directory)+"/config.json");input>>config;
    if(!input)throw std::runtime_error("Cannot read observer config");
    output.open(file);if(!output)throw std::runtime_error("Cannot open observer output");
  }
};
thread_local std::unique_ptr<State> state;
State& data() {if(!state)state=std::make_unique<State>();return *state;}
StepJson position(const G4ThreeVector& p) {return StepJson::array({p.x()/CLHEP::mm,p.y()/CLHEP::mm,p.z()/CLHEP::mm});}
}

namespace dd4hep::sim {
class nODDLArObservedEvent : public Geant4EventAction {
public:
  nODDLArObservedEvent(Geant4Context* c,const std::string& n):Geant4EventAction(c,n) {}
  void begin(const G4Event* event) override {
    if(std::fegetround()!=FE_TONEAREST)throw std::runtime_error("Observer requires FE_TONEAREST");
    auto& d=data();if(d.event!=-1)throw std::runtime_error("Observer event not closed");
    d.event=event->GetEventID();d.run=G4RunManager::GetRunManager()->GetCurrentRun()->GetRunID();
    d.collections={};d.identities.clear();
  }
  void end(const G4Event* event) override {
    if(std::fegetround()!=FE_TONEAREST)throw std::runtime_error("Observer floating rounding mode changed");
    auto& d=data();if(d.event!=event->GetEventID() || event->IsAborted())throw std::runtime_error("Incomplete observer event");
    StepJson collections=StepJson::object();const std::array<std::string,2> names={"LArBarrelHits","LArEndcapHits"};
    for(int i=0;i<2;++i) {
      const auto& c=d.collections[i];StepJson cells=StepJson::array();
      for(const auto& entry:c.cells)cells.push_back({{"cell",entry.first},{"sum_MeV",entry.second.sum},{"steps",entry.second.steps}});
      collections[names[i]]={{"A_MeV",c.all},{"U_MeV",c.unassigned},{"sensitive_callbacks",c.callbacks},
        {"positive_steps",c.positive},{"zero_steps",c.zero},{"cells",cells},{"failures",c.failures}};
    }
    const StepJson row={{"run",d.run},{"event",d.event},{"thread",G4Threading::G4GetThreadId()},
      {"positive_identity_count",d.identities.size()},{"rounding_mode","FE_TONEAREST"},{"collections",collections}};
    d.output<<row.dump()<<'\n';d.output.flush();if(!d.output)throw std::runtime_error("Cannot retain observer event");
    d.event=-1;
  }
};

class nODDLArObservedStep : public Geant4SteppingAction {
public:
  nODDLArObservedStep(Geant4Context* c,const std::string& n):Geant4SteppingAction(c,n) {}
  void operator()(const G4Step* step,G4SteppingManager*) override {
    const auto* pre=step->GetPreStepPoint();const auto* post=step->GetPostStepPoint();
    const auto* physical=pre->GetPhysicalVolume();if(!physical)return;
    const auto* logical=physical->GetLogicalVolume();const auto* sd=logical->GetSensitiveDetector();if(!sd)return;
    const std::string role=sd->GetName();const int index=role=="LArBarrel"?0:role=="LArEndcaps"?1:-1;
    if(index<0)throw std::runtime_error("Unexpected observer sensitive detector");
    auto& d=data();if(d.event<0)throw std::runtime_error("Observer event callback missing");
    auto& c=d.collections[index];++c.callbacks;
    const auto* track=step->GetTrack();const double weight=track->GetWeight(),raw=step->GetTotalEnergyDeposit();
    if(weight!=1. || !std::isfinite(raw) || raw<0.)throw std::runtime_error("Unexpected weight or invalid sensitive edep");
    if(track->GetDefinition()==G4OpticalPhoton::OpticalPhotonDefinition())throw std::runtime_error("Optical observer policy unsupported");
    if(logical->GetMaterial()->GetIonisation()->GetBirksConstant()!=0.)throw std::runtime_error("Nonzero observer Birks policy");
    if(!(raw>0.)){++c.zero;return;} // exact edep0 filter; no track weighting
    if(std::fegetround()!=FE_TONEAREST)throw std::runtime_error("Observer floating rounding mode changed during tracking");
    const int tid=track->GetTrackID(),number=track->GetCurrentStepNumber();
    if(!d.identities.emplace(tid,number).second)throw std::runtime_error("Duplicate positive observer step");
    const auto contribution=Geant4Calorimeter::Hit::extractContribution(step,true);
    const double accepted=contribution.deposit;
    if(!std::isfinite(accepted) || accepted!=raw)throw std::runtime_error("Observer contribution differs from declared unquenched raw edep");
    ++c.positive;c.all+=accepted;
    const auto* touchable=pre->GetTouchable();
    const auto transform=touchable->GetHistory()->GetTopTransform();
    const auto global=.5*(pre->GetPosition()+post->GetPosition());
    const auto local=transform.TransformPoint(global);
    auto& detector=Geant4Mapping::instance().detectorDescription();
    const auto readout=detector.readout(index==0?"LArBarrelHits":"LArEndcapHits");
    const auto segmentation=readout.segmentation();
    const auto rawID=Geant4Mapping::instance().volumeManager().volumeID(touchable);
    const Position loc(local.x()/CLHEP::mm*dd4hep::mm,local.y()/CLHEP::mm*dd4hep::mm,local.z()/CLHEP::mm*dd4hep::mm);
    const Position glob(global.x()/CLHEP::mm*dd4hep::mm,global.y()/CLHEP::mm*dd4hep::mm,global.z()/CLHEP::mm*dd4hep::mm);
    dd4hep::VolumeID cell=0;
    try {cell=segmentation.cellID(loc,glob,rawID);}
    catch(const std::runtime_error& error) {
      c.unassigned+=accepted;
      StepJson failure={{"run",d.run},{"event",d.event},{"track",tid},{"parent",track->GetParentID()},
        {"step",number},{"pdg",track->GetDefinition()->GetPDGEncoding()},{"weight",weight},{"raw_volume",rawID},
        {"volume",logical->GetName()},{"collection",index==0?"LArBarrelHits":"LArEndcapHits"},
        {"edep_MeV",raw},{"contribution_MeV",accepted},{"reason",error.what()},
        {"pre_global_mm",position(pre->GetPosition())},{"post_global_mm",position(post->GetPosition())},
        {"mid_global_mm",position(global)},{"pre_local_mm",position(transform.TransformPoint(pre->GetPosition()))},
        {"post_local_mm",position(transform.TransformPoint(post->GetPosition()))},{"mid_local_mm",position(local)}};
      if(index==1) {
        const int wheel=readout.idSpec().decoder()->get(rawID,"wheel");
        const auto bounds=d.config.at("endcap_wheels").at(wheel);
        const double radius=std::hypot(local.x(),local.y())/CLHEP::mm;
        failure["wheel"]=wheel;failure["guard_mm"]=1e-8;
        failure["guard_deltas_mm"]={{"r_minus_inner",radius-bounds.at("inner_mm").get<double>()},
          {"outer_minus_r",bounds.at("outer_mm").get<double>()-radius},
          {"half_depth_minus_abs_z",bounds.at("half_depth_mm").get<double>()-std::abs(local.z()/CLHEP::mm)}};
      }
      c.failures.push_back(std::move(failure));
      return;
    }
    auto& target=c.cells[cell];target.sum+=accepted;++target.steps;
  }
};
}
DECLARE_GEANT4ACTION(nODDLArObservedEvent)
DECLARE_GEANT4ACTION(nODDLArObservedStep)
