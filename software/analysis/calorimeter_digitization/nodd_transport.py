"""DDSim steering: prospectively matched ECAL step policy and native audit.

The geometry is unchanged. Both comparison transports use the original ODD
5-mm maximum step for charged particles in sensitive ECAL silicon, before any
event. This callback also audits actual G4 fields, region cuts and silicon Birks.
"""
from DDSim.DD4hepSimulation import DD4hepSimulation


def configure_audit(kernel):
    import os
    from pathlib import Path
    import subprocess
    import ROOT

    prefix = Path(subprocess.check_output(["geant4-config", "--prefix"], text=True).strip())
    ROOT.gInterpreter.AddIncludePath(str(prefix / "include/Geant4"))
    ROOT.gInterpreter.Declare(r'''
#include <G4LogicalVolumeStore.hh>
#include <G4VSensitiveDetector.hh>
#include <G4UserLimits.hh>
#include <G4Track.hh>
#include <G4DynamicParticle.hh>
#include <G4Material.hh>
#include <G4IonisParamMat.hh>
#include <G4RegionStore.hh>
#include <G4ProductionCuts.hh>
#include <G4TransportationManager.hh>
#include <G4FieldManager.hh>
#include <G4Field.hh>
#include <G4ParticleTable.hh>
#include <G4ProcessManager.hh>
#include <G4VProcess.hh>
#include <G4SystemOfUnits.hh>
#include <nlohmann/json.hpp>
#include <set>
#include <string>
#include <cmath>
#include <stdexcept>
#include <algorithm>
std::string I118NativeTransportAudit() {
  using nlohmann::json;
  json result;
  result["scope"]="Actual initialized Geant4 field/cuts/ECAL-silicon settings before events";
  result["sensitive_si"]=json::object();
  result["regions"]=json::array();
  std::set<G4FieldManager*> fields;
  fields.insert(G4TransportationManager::GetTransportationManager()->GetFieldManager());
  auto* common=new G4UserLimits(5.*CLHEP::mm);
  auto* electron=G4ParticleTable::GetParticleTable()->FindParticle("e-");
  G4Track track(new G4DynamicParticle(electron,G4ThreeVector(1.,0.,0.),CLHEP::GeV),0.,G4ThreeVector());
  long long selected=0;
  std::set<std::string> roles;
  for(auto* volume:*G4LogicalVolumeStore::GetInstance()) {
    if(volume->GetFieldManager()) fields.insert(volume->GetFieldManager());
    auto* sd=volume->GetSensitiveDetector();
    if(!sd) continue;
    const std::string name=sd->GetName();
    bool ecal=name=="BARREL" || name=="EDGE" || name=="ECalBarrel" || name=="ECalEndcap";
    if(name=="BARREL" || name=="ECalBarrel") roles.insert("barrel");
    if(name=="EDGE" || name=="ECalEndcap") roles.insert("endcap");
    for(int i=0;i<sd->GetNumberOfCollections();++i) {
      const std::string collection=sd->GetCollectionName(i);
      ecal=ecal || collection=="BARRELHits" || collection=="EDGEHits"
        || collection=="ECalBarrelCollection" || collection=="ECalEndcapCollection";
      if(collection=="BARRELHits" || collection=="ECalBarrelCollection") roles.insert("barrel");
      if(collection=="EDGEHits" || collection=="ECalEndcapCollection") roles.insert("endcap");
    }
    if(!ecal) continue;
    auto* material=volume->GetMaterial();
    if(std::string(material->GetName()).find("Silicon")==std::string::npos)
      throw std::runtime_error("ECAL sensitive volume is not declared silicon");
    auto* limits=volume->GetUserLimits();
    if(!limits) { limits=common; volume->SetUserLimits(limits); }
    else limits->SetMaxAllowedStep(5.*CLHEP::mm);
    if(limits->GetMaxAllowedStep(track)!=5.*CLHEP::mm)
      throw std::runtime_error("ECAL silicon step-policy mismatch");
    const double birks=material->GetIonisation()->GetBirksConstant()/(CLHEP::mm/CLHEP::MeV);
    auto& row=result["sensitive_si"][name];
    if(row.is_null()) row={{"logical_volumes",0},{"max_step_mm",5.},{"Birks_mm_per_MeV",birks},
                          {"material",std::string(material->GetName())}};
    if(row["Birks_mm_per_MeV"].get<double>()!=birks)
      throw std::runtime_error("Nonuniform silicon Birks setting");
    row["logical_volumes"]=row["logical_volumes"].get<long long>()+1;
    ++selected;
  }
  if(selected==0) throw std::runtime_error("Transport audit ran before sensitive-detector initialization");
  if(roles!=std::set<std::string>{"barrel","endcap"})
    throw std::runtime_error("Both ECAL barrel/endcap identities must be initialized and audited");
  result["audited_ECAL_roles"]=roles;
  double maxfield=0.;
  for(auto* manager:fields) {
    auto* field=manager ? manager->GetDetectorField() : nullptr;
    if(!field) continue;
    for(double x:{0.,1500.,3000.}) for(double z:{-4500.,-3950.,0.,3950.,4500.}) {
      double position[4]={x*CLHEP::mm,123.*CLHEP::mm,z*CLHEP::mm,0.};
      double value[24]={}; field->GetFieldValue(position,value);
      for(int i=0;i<3;++i) maxfield=std::max(maxfield,std::abs(value[i]/CLHEP::tesla));
    }
  }
  if(maxfield!=0.) throw std::runtime_error("Nonzero actual transport magnetic field");
  result["maximum_abs_magnetic_field_tesla"]=maxfield;
  result["field_probe_points_per_manager"]=15;
  result["field_managers"]=fields.size();
  for(auto* region:*G4RegionStore::GetInstance()) {
    json row={{"name",std::string(region->GetName())},{"production_cuts_mm",json::array()}};
    auto* cuts=region->GetProductionCuts();
    if(cuts) for(int i=0;i<4;++i) row["production_cuts_mm"].push_back(cuts->GetProductionCut(i)/CLHEP::mm);
    result["regions"].push_back(row);
  }
  for(const std::string name:{"e-","e+","mu-","gamma"}) {
    auto* particle=G4ParticleTable::GetParticleTable()->FindParticle(name);
    auto* list=particle->GetProcessManager()->GetProcessList();
    json names=json::array(); bool limiter=false;
    for(int i=0;i<list->size();++i) {
      names.push_back(std::string((*list)[i]->GetProcessName()));
      limiter=limiter || (*list)[i]->GetProcessName()=="StepLimiter";
    }
    result["processes"][name]=names;
    if(name!="gamma" && !limiter) throw std::runtime_error("Charged-particle StepLimiter is absent");
  }
  result["matched_ECAL_sensitive_step_mm"]=5.;
  return result.dump();
}
''')

    def after_initialize():
        path = Path(os.environ["I118_TRANSPORT_AUDIT"])
        if path.exists():
            raise RuntimeError("Refusing transport audit overwrite")
        result = str(ROOT.I118NativeTransportAudit())
        path.write_text(result + "\n")
        print("I118 initialized native field/cut/step audit written", path, flush=True)

    # cppyy's std::function trampoline does not retain the Python callable.
    # Keep a process-lifetime reference until native kernel termination.
    callbacks = getattr(ROOT, "_i118_transport_callbacks", [])
    callbacks.append(after_initialize)
    ROOT._i118_transport_callbacks = callbacks
    kernel.get().register_initialize(after_initialize)


SIM = DD4hepSimulation()
SIM.physics.setupUserPhysics(configure_audit)
