// Isolated material-preserving route prototype; absent from production CMake.
#include <DD4hep/DetFactoryHelper.h>
#include <DDG4/Factories.h>
#include <DDG4/Geant4SteppingAction.h>
#include <G4Step.hh>
#include <G4Track.hh>
#include <G4ParticleDefinition.hh>
#include <G4RunManager.hh>
#include <G4Run.hh>
#include <G4Event.hh>
#include <G4Material.hh>
#include <G4VPhysicalVolume.hh>
#include <G4LogicalVolume.hh>
#include <G4SystemOfUnits.hh>
#include <nlohmann/json.hpp>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <set>
#include <stdexcept>
#include <string>

namespace {
using namespace dd4hep;
using xml::Handle_t;
double value(Handle_t h,const char* key) {
  double v=h.attr<double>(key);
  if(!std::isfinite(v))throw std::runtime_error("Nonfinite routing input");
  return v;
}
Transform3D pose(Handle_t h) {
  return Transform3D(Rotation3D(value(h,"a00"),value(h,"a01"),value(h,"a02"),
      value(h,"a10"),value(h,"a11"),value(h,"a12"),value(h,"a20"),value(h,"a21"),value(h,"a22")),
      Position(value(h,"x"),value(h,"y"),value(h,"z")));
}
Ref_t createRouting(Detector& detector,Handle_t h,SensitiveDetector) {
  const auto name=h.attr<std::string>("name");DetElement result(name,h.attr<int>("id"));
  Assembly assembly(name);std::set<std::string> names;
  for(xml::Collection_t route(h,"route");route;++route) {
    for(xml::Collection_t segment(route,"segment");segment;++segment) {
      const auto n=segment.attr<std::string>("name");
      if(!names.insert(n).second)throw std::runtime_error("Duplicate routing segment");
      const double inner=value(segment,"rinner"),outer=value(segment,"router"),half=value(segment,"length")/2;
      const double lx=value(segment,"lox"),ly=value(segment,"loy"),lz=value(segment,"loz");
      const double tx=value(segment,"hix"),ty=value(segment,"hiy"),tz=value(segment,"hiz");
      if(!(inner>0&&outer>inner&&half>0&&lz<0&&tz>0) ||
         std::abs(lx*lx+ly*ly+lz*lz-1)>1e-10 || std::abs(tx*tx+ty*ty+tz*tz-1)>1e-10)
        throw std::runtime_error("Invalid cut-tube bounds or miter normals");
      if(2*half<=outer*std::hypot(lx/lz-tx/tz,ly/lz-ty/tz))throw std::runtime_error("Miter planes cross inside pipe disk");
      const auto transform=pose(segment);
      for(const bool core:{false,true}) {
        const std::string tag=n+(core?"_core":"_wall");
        CutTube solid(core?0.:inner,core?inner:outer,half,0.,2*M_PI,lx,ly,lz,tx,ty,tz);
        Volume volume(tag,solid,detector.material(segment.attr<std::string>(core?"core_material":"wall_material")));
        assembly.placeVolume(volume,transform);
      }
    }
  }
  if(names.empty())throw std::runtime_error("Missing route segments");
  auto placed=detector.pickMotherVolume(result).placeVolume(assembly);
  placed.addPhysVolID("system",h.attr<int>("id"));result.setPlacement(placed);return result;
}
}
DECLARE_DETELEMENT(nODDLArRoutingPrototype,createRouting)

namespace dd4hep::sim {
class nODDLArRoutingStepAudit : public Geant4SteppingAction {
  std::ofstream output;
public:
  nODDLArRoutingStepAudit(Geant4Context* context,const std::string& name):Geant4SteppingAction(context,name) {
    const char* path=std::getenv("NODD_ROUTING_STEPS");
    if(!path || std::filesystem::exists(path))throw std::runtime_error("Missing or existing routing step audit");
    output.open(path);if(!output)throw std::runtime_error("Cannot open routing step audit");
  }
  void operator()(const G4Step* step,G4SteppingManager*) override {
    const auto* before=step->GetPreStepPoint();const auto* after=step->GetPostStepPoint();
    const auto* track=step->GetTrack();auto* manager=G4RunManager::GetRunManager();
    const auto point=[](const G4ThreeVector& p) {return nlohmann::json::array({p.x()/CLHEP::mm,p.y()/CLHEP::mm,p.z()/CLHEP::mm});};
    const auto volume=[](const G4StepPoint* p) {return p->GetPhysicalVolume()?std::string(p->GetPhysicalVolume()->GetLogicalVolume()->GetName()):std::string{};};
    const auto material=[](const G4StepPoint* p) {return p->GetMaterial()?std::string(p->GetMaterial()->GetName()):std::string{};};
    const nlohmann::json record={{"run",manager->GetCurrentRun()->GetRunID()},{"event",manager->GetCurrentEvent()->GetEventID()},
      {"track",track->GetTrackID()},{"parent",track->GetParentID()},{"pdg",track->GetParticleDefinition()->GetPDGEncoding()},
      {"pre_volume",volume(before)},{"post_volume",volume(after)},{"pre_material",material(before)},{"post_material",material(after)},
      {"step_mm",step->GetStepLength()/CLHEP::mm},{"edep_GeV",step->GetTotalEnergyDeposit()/CLHEP::GeV},
      {"pre_mm",point(before->GetPosition())},{"post_mm",point(after->GetPosition())},
      {"vertex_mm",point(track->GetVertexPosition())},
      {"pre_momentum_GeV",nlohmann::json::array({before->GetMomentum().x()/CLHEP::GeV,before->GetMomentum().y()/CLHEP::GeV,before->GetMomentum().z()/CLHEP::GeV})},
      {"pre_kinetic_energy_GeV",before->GetKineticEnergy()/CLHEP::GeV},
      {"geometry_boundary",after->GetStepStatus()==fGeomBoundary}};
    output<<record.dump()<<'\n';output.flush();if(!output)throw std::runtime_error("Cannot retain routing step");
  }
};
}
DECLARE_GEANT4ACTION(nODDLArRoutingStepAudit)
