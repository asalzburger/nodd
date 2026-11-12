// Task-local worker audit; reproduces PR133's 5 mm silicon step policy.
#include <DDG4/Factories.h>
#include <DDG4/Geant4RunAction.h>
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
#include <G4Threading.hh>
#include <G4Run.hh>
#include <Randomize.hh>
#include <nlohmann/json.hpp>
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <mutex>
#include <set>
#include <stdexcept>

namespace dd4hep::sim {
class nODDAngularAudit : public Geant4RunAction {
  nlohmann::json m_record;
  std::string m_file;
  void save() {
    const std::string tmp=m_file+".tmp";
    std::ofstream output(tmp);
    output << m_record.dump(2) << '\n'; output.close();
    if(!output) throw std::runtime_error("Cannot write worker audit");
    std::filesystem::rename(tmp,m_file);
  }
public:
  nODDAngularAudit(dd4hep::sim::Geant4Context* context,const std::string& name)
    : Geant4RunAction(context,name) {}
  void begin(const G4Run* run) override {
    using nlohmann::json;
    const int worker=G4Threading::G4GetThreadId();
    const char* directory=std::getenv("NODD_ANGULAR_AUDIT");
    if(!directory) throw std::runtime_error("NODD_ANGULAR_AUDIT unset");
    m_file=std::string(directory)+"/worker-"+std::to_string(worker)+".json";
    if(std::filesystem::exists(m_file)) throw std::runtime_error("Refusing worker audit overwrite");
    m_record={{"thread_id",worker},{"run_id",run->GetRunID()},
              {"status","initialized"},{"scope","native worker begin/end-run audit"}};
    // User limits are shared geometry data. Serialize first installation and
    // all inspections before any audited worker begins tracking.
    static std::mutex limitsMutex;
    std::lock_guard<std::mutex> guard(limitsMutex);
    static auto* common=new G4UserLimits(5.*CLHEP::mm);
    auto* electron=G4ParticleTable::GetParticleTable()->FindParticle("e-");
    G4Track track(new G4DynamicParticle(electron,G4ThreeVector(1.,0.,0.),CLHEP::GeV),0.,G4ThreeVector());
    std::set<G4FieldManager*> fields;
    fields.insert(G4TransportationManager::GetTransportationManager()->GetFieldManager());
    std::set<std::string> roles;
    auto& sensitive=m_record["sensitive_si"];sensitive=json::object();
    for(auto* volume:*G4LogicalVolumeStore::GetInstance()) {
      if(volume->GetFieldManager()) fields.insert(volume->GetFieldManager());
      auto* sd=volume->GetSensitiveDetector();if(!sd)continue;
      const std::string name=sd->GetName();if(name!="BARREL"&&name!="EDGE")continue;
      roles.insert(name);
      auto* material=volume->GetMaterial();
      if(std::string(material->GetName()).find("Silicon")==std::string::npos)
        throw std::runtime_error("ECAL sensitive material is not silicon");
      auto* limits=volume->GetUserLimits();
      if(!limits){volume->SetUserLimits(common);limits=common;}
      if(limits->GetMaxAllowedStep(track)!=5.*CLHEP::mm)
        throw std::runtime_error("Sensitive step policy differs from PR133");
      const double birks=material->GetIonisation()->GetBirksConstant()/(CLHEP::mm/CLHEP::MeV);
      if(birks!=0.)throw std::runtime_error("Unexpected silicon Birks constant");
      if(sensitive[name].is_null())sensitive[name]={{"logical_volumes",0},{"max_step_mm",5.},{"Birks_mm_per_MeV",birks}};
      sensitive[name]["logical_volumes"]=sensitive[name]["logical_volumes"].get<int>()+1;
    }
    if(roles!=std::set<std::string>{"BARREL","EDGE"})throw std::runtime_error("Both worker ECAL SDs must be present");
    double maxField=0.;
    for(auto* manager:fields)if(manager&&manager->GetDetectorField())
      for(double x:{0.,1500.,3000.})for(double z:{-4500.,-3950.,0.,3950.,4500.}){
        double position[4]={x*CLHEP::mm,123.*CLHEP::mm,z*CLHEP::mm,0.},value[24]={};
        manager->GetDetectorField()->GetFieldValue(position,value);
        for(int i=0;i<3;++i)maxField=std::max(maxField,std::abs(value[i]/CLHEP::tesla));
      }
    if(maxField!=0.)throw std::runtime_error("Unexpected magnetic field");
    m_record["maximum_abs_magnetic_field_tesla"]=maxField;
    m_record["region_cuts"]=json::array();
    for(auto* region:*G4RegionStore::GetInstance()){
      auto* cuts=region->GetProductionCuts();json values=json::array();
      if(cuts)for(int i=0;i<4;++i)values.push_back(cuts->GetProductionCut(i)/CLHEP::mm);
      m_record["region_cuts"].push_back({{"name",std::string(region->GetName())},{"mm",values}});
    }
    for(const std::string name:{"e-","e+","gamma"}){
      auto* p=G4ParticleTable::GetParticleTable()->FindParticle(name);
      auto* list=p->GetProcessManager()->GetProcessList();json names=json::array();bool limiter=false;
      for(std::size_t i=0;i<list->size();++i){const std::string process=(*list)[i]->GetProcessName();names.push_back(process);limiter=limiter||process=="StepLimiter";}
      m_record["processes"][name]=names;
      if(name!="gamma"&&!limiter)throw std::runtime_error("StepLimiter absent on charged particles");
    }
    auto* engine=G4Random::getTheEngine();
    m_record["rng_engine"]=engine->name();m_record["begin_run_rng_seed"]=engine->getSeed();
    save();
  }
  void end(const G4Run* run) override {
    m_record["events"]=run->GetNumberOfEvent();m_record["status"]="complete";save();
  }
};
}
DECLARE_GEANT4ACTION(nODDAngularAudit)
