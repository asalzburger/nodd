#include <DD4hep/Volumes.h>
#include <TGeoManager.h>
#include <TGeoNode.h>
#include <TGeoVolume.h>
#include <G4RunManager.hh>
#include <G4LogicalVolume.hh>
#include <G4LogicalVolumeStore.hh>
#include <G4Step.hh>
#include <G4Track.hh>
#include <G4SystemOfUnits.hh>
#include <G4UserSteppingAction.hh>
#include <G4TransportationManager.hh>
#include <G4Navigator.hh>
#include "ActsExamples/Geant4/SteppingActionList.hpp"
#include <array>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <map>
#include <memory>
#include <set>
#include <stdexcept>
#include <string>
#include <typeinfo>
#include <unordered_map>

namespace nodd_hits {
struct Ray {
  double eta=0, phi=0, x=0, y=0, z=0, dx=0, dy=0, dz=0;
  std::array<std::set<int>,3> sensors;
  long long sensitiveSteps=0;
};
struct Counter final : G4UserSteppingAction {
  std::map<std::string,int> placement;
  std::map<int,Ray> rays;
  std::ofstream csv;
  int currentEvent=-1, completedEvents=0;
  long long positiveSensitiveSteps=0, zeroSensitiveSteps=0, distinctHits=0;
  int ddSensitiveNames=0, ddSensitivePlacements=0, g4SensitivePlacements=0;
  explicit Counter(const char* path) : csv(path) {
    if(!csv) throw std::runtime_error("Cannot open hit table");
    csv << "event_id,track_id,eta,phi,x_mm,y_mm,z_mm,dx,dy,dz,pixel,short_strip,long_strip,total,sensitive_steps\n" << std::setprecision(17);
  }
  void UserSteppingAction(const G4Step* step) override {
    if(currentEvent<0) throw std::runtime_error("Hit counter event not started");
    const auto* track=step->GetTrack();
    if(track->GetParentID()!=0) throw std::runtime_error("Expected primary geantinos only");
    const int id=track->GetTrackID();
    auto [it,inserted]=rays.try_emplace(id);
    auto& ray=it->second;
    if(inserted) {
      const auto& d=track->GetVertexMomentumDirection();
      const auto& p=track->GetVertexPosition();
      ray.eta=std::asinh(d.z()/std::hypot(d.x(),d.y())); ray.phi=std::atan2(d.y(),d.x());
      ray.x=p.x()/CLHEP::mm;ray.y=p.y()/CLHEP::mm;ray.z=p.z()/CLHEP::mm;
      ray.dx=d.x();ray.dy=d.y();ray.dz=d.z();
    }
    const auto& touch=step->GetPreStepPoint()->GetTouchableHandle();
    // Positive length in the actual pre-step physical volume; no rounded lookup.
    const auto* logical=touch->GetVolume()->GetLogicalVolume();
    if(!sensitive.count(logical)) return;
    if(step->GetStepLength()==0) {++zeroSensitiveSteps;return;}
    if(!(step->GetStepLength()>0)) throw std::runtime_error("Invalid Geant4 step");
    std::string path;
    for(int depth=touch->GetHistoryDepth();depth>=0;--depth)
      path+="/"+std::string(touch->GetVolume(depth)->GetName())+"#"+std::to_string(touch->GetCopyNumber(depth));
    auto found=placement.find(path);
    if(found==placement.end()) throw std::runtime_error("Unknown sensitive physical path");
    int component=-1;
    if(path.find("Pixel")!=std::string::npos) component=0;
    else if(path.find("ShortStrip")!=std::string::npos) component=1;
    else if(path.find("LongStrip")!=std::string::npos) component=2;
    if(component<0) throw std::runtime_error("Unknown sensitive subsystem");
    ray.sensors[component].insert(found->second);
    ++ray.sensitiveSteps; ++positiveSensitiveSteps;
  }
  std::set<const G4LogicalVolume*> sensitive;
  void begin(int event) {
    if(currentEvent>=0 || event!=completedEvents) throw std::runtime_error("Noncontiguous counter event");
    rays.clear(); currentEvent=event;
  }
  void end(int event,int expectedTracks) {
    if(event!=currentEvent || int(rays.size())!=expectedTracks) throw std::runtime_error("Incomplete hit event");
    for(const auto& [id,r]:rays) {
      const auto p=r.sensors[0].size(),s=r.sensors[1].size(),l=r.sensors[2].size();
      distinctHits+=p+s+l;
      csv<<event<<','<<id<<','<<r.eta<<','<<r.phi<<','<<r.x<<','<<r.y<<','<<r.z<<','
         <<r.dx<<','<<r.dy<<','<<r.dz<<','<<p<<','<<s<<','<<l<<','<<(p+s+l)<<','<<r.sensitiveSteps<<'\n';
    }
    csv.flush();currentEvent=-1;++completedEvents;
  }
};
static std::shared_ptr<Counter> counter;

void countDD(TGeoNode* node,int& count) {
  if(dd4hep::Volume(node->GetVolume()).isSensitive()) ++count;
  for(int i=0;i<node->GetNdaughters();++i) countDD(node->GetDaughter(i),count);
}
void countG4(G4VPhysicalVolume* physical,const std::string& parent,Counter& c) {
  const auto path=parent+"/"+std::string(physical->GetName())+"#"+std::to_string(physical->GetCopyNo());
  auto* logical=physical->GetLogicalVolume();
  if(c.sensitive.count(logical)) {
    const int id=c.placement.size();
    if(!c.placement.emplace(path,id).second) throw std::runtime_error("Nonunique sensitive physical path");
    ++c.g4SensitivePlacements;
  }
  for(int i=0;i<logical->GetNoDaughters();++i) countG4(logical->GetDaughter(i),path,c);
}
void install(const char* output,int expectedSensors) {
  if(counter) throw std::runtime_error("Hit counter already installed");
  auto* manager=G4RunManager::GetRunManager();
  if(!manager) throw std::runtime_error("No initialized Geant4 manager");
  auto* original=const_cast<G4UserSteppingAction*>(manager->GetUserSteppingAction());
  if(!original || std::string(typeid(*original).name()).find("MaterialSteppingAction")==std::string::npos)
    throw std::runtime_error("Expected native ACTS MaterialSteppingAction");
  auto c=std::make_shared<Counter>(output);
  std::map<std::string,TGeoVolume*> ddSensitive;
  for(auto* object:*gGeoManager->GetListOfVolumes()) {
    auto* volume=static_cast<TGeoVolume*>(object);
    if(dd4hep::Volume(volume).isSensitive() && !ddSensitive.emplace(volume->GetName(),volume).second)
      throw std::runtime_error("Nonunique DD4hep sensitive logical name");
  }
  c->ddSensitiveNames=ddSensitive.size();
  std::set<std::string> matched;
  for(auto* logical:*G4LogicalVolumeStore::GetInstance()) {
    auto dd=ddSensitive.find(logical->GetName());
    if(dd==ddSensitive.end()) continue;
    const auto* material=logical->GetMaterial();
    const auto* source=dd->second->GetMaterial();
    const double density=material->GetDensity()/(CLHEP::g/CLHEP::cm3);
    if(material->GetName()!=source->GetName() || std::abs(density-source->GetDensity())>5e-6*source->GetDensity())
      throw std::runtime_error("Sensitive Geant4/DD4hep material identity mismatch");
    c->sensitive.insert(logical); matched.insert(logical->GetName());
  }
  if(matched.size()!=ddSensitive.size()) throw std::runtime_error("Unmatched DD4hep sensitive logical volumes");
  countDD(gGeoManager->GetTopNode(),c->ddSensitivePlacements);
  auto* world=G4TransportationManager::GetTransportationManager()->GetNavigatorForTracking()->GetWorldVolume();
  if(!world) throw std::runtime_error("No initialized Geant4 world");
  countG4(world,"",*c);
  if(c->ddSensitivePlacements!=expectedSensors || c->g4SensitivePlacements!=expectedSensors)
    throw std::runtime_error("Sensitive placement inventory mismatch");
  // Follow the upstream multiple-action pattern; list owns the original action.
  ActsExamples::Geant4::SteppingActionList::Config cfg;
  cfg.actions={std::shared_ptr<G4UserSteppingAction>(original),c};
  manager->SetUserAction(new ActsExamples::Geant4::SteppingActionList(cfg));
  counter=c;
}
void begin(int event) {if(!counter) throw std::runtime_error("No hit counter");counter->begin(event);}
void end(int event,int tracks) {counter->end(event,tracks);}
void report(const char* path) {
  if(!counter || counter->currentEvent>=0) throw std::runtime_error("Incomplete hit counter");
  const auto& c=*counter;
  std::ofstream out(path);
  out<<"{\"events\":"<<c.completedEvents<<",\"dd_sensitive_names\":"<<c.ddSensitiveNames
     <<",\"dd_sensitive_placements\":"<<c.ddSensitivePlacements<<",\"g4_sensitive_placements\":"<<c.g4SensitivePlacements
     <<",\"positive_sensitive_steps\":"<<c.positiveSensitiveSteps<<",\"zero_length_sensitive_steps\":"<<c.zeroSensitiveSteps
     <<",\"distinct_hits\":"<<c.distinctHits<<",\"split_steps_removed\":"<<(c.positiveSensitiveSteps-c.distinctHits)<<"}\n";
}
}
