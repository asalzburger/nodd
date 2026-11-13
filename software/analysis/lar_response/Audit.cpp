// LAr PROTOTYPE worker audit. Explicit NODD_LAR_MAX_STEP_MM controls any cap.
// Raw deposited energy only; no charge, drift, shaping or electronics response.
#include <DDG4/Factories.h>
#include <DDG4/Geant4Mapping.h>
#include <DD4hep/VolumeManager.h>
#include <DDG4/Geant4RunAction.h>
#include <G4LogicalVolumeStore.hh>
#include <G4VSensitiveDetector.hh>
#include <G4UserLimits.hh>
#include <G4Track.hh>
#include <G4DynamicParticle.hh>
#include <G4Material.hh>
#include <G4Element.hh>
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
#include <chrono>
#include <iostream>
#include <filesystem>
#include <fstream>
#include <mutex>
#include <set>
#include <map>
#include <limits>
#include <stdexcept>

namespace {
bool larMapsInitializedSerially = false;
}

// Invoked by the main-kernel initialization callback before worker creation.
// Lazy native lookup creation in a first worker hit otherwise races in DDG4.
void initializeLArResponseMaps(const std::string& directory) {
  const auto start=std::chrono::steady_clock::now();
  const int thread=G4Threading::G4GetThreadId();
  if(thread>=0 || larMapsInitializedSerially)
    throw std::runtime_error("LAr maps must initialize once on the main thread");
  const std::string path=directory+"/maps-initialized.json";
  if(std::filesystem::exists(path))throw std::runtime_error("Refusing map-audit overwrite");
  const auto& mapping=dd4hep::sim::Geant4Mapping::instance();
  std::cout << "LAR_RESPONSE_G4_MAP_BEGIN" << std::endl;
  const auto g4=mapping.volumeManager();
  std::cout << "LAR_RESPONSE_NATIVE_MAP_BEGIN" << std::endl;
  const auto native=dd4hep::VolumeManager::getVolumeManager(mapping.detectorDescription());
  if(!g4.isValid()||!native.isValid())throw std::runtime_error("Invalid LAr volume manager");
  std::set<dd4hep::VolumeID> ids;
  for(const auto& entry:mapping.data().g4Paths) {
    const auto id=entry.second.volumeID;
    if(((id&255)!=10&&(id&255)!=11)||!ids.insert(id).second)
      throw std::runtime_error("Unexpected/duplicate serial LAr raw volume ID");
    const auto* context=native.lookupContext(id);
    if(!context||!context->volumePlacement().volume().isSensitive())
      throw std::runtime_error("Missing serial LAr native context");
  }
  if(ids.size()!=43648)throw std::runtime_error("Incomplete serial LAr volume maps");
  nlohmann::json record={{"status","PASS"},{"thread_id",thread},
    {"raw_sensitive_ids",ids.size()},{"native_contexts_checked",ids.size()},
    {"scope","both volume managers and all raw contexts initialized serially before workers"},
    {"seconds",std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()}};
  std::ofstream stream(path);stream<<record.dump(2)<<'\n';stream.close();
  if(!stream)throw std::runtime_error("Cannot write serial map audit");
  larMapsInitializedSerially=true;
  std::cout << "LAR_RESPONSE_MAPS_READY" << std::endl;
}

namespace dd4hep::sim {
class nODDLArResponseAudit : public Geant4RunAction {
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
  nODDLArResponseAudit(dd4hep::sim::Geant4Context* context,const std::string& name)
    : Geant4RunAction(context,name) {}
  void begin(const G4Run* run) override {
    using nlohmann::json;
    const int worker=G4Threading::G4GetThreadId();
    if(!larMapsInitializedSerially)throw std::runtime_error("Serial LAr map initialization missing");
    const char* directory=std::getenv("NODD_LAR_AUDIT");
    if(!directory) throw std::runtime_error("NODD_LAR_AUDIT unset");
    m_file=std::string(directory)+"/worker-"+std::to_string(worker)+".json";
    if(std::filesystem::exists(m_file)) throw std::runtime_error("Refusing worker audit overwrite");
    m_record={{"thread_id",worker},{"run_id",run->GetRunID()},
              {"status","initialized"},{"scope","native worker begin/end-run audit"},{"maps_initialized_serially",true}};
    // User limits are shared geometry data. Serialize first installation and
    // all inspections before any audited worker begins tracking.
    static std::mutex limitsMutex;
    std::lock_guard<std::mutex> guard(limitsMutex);
    const char* stepText=std::getenv("NODD_LAR_MAX_STEP_MM");
    if(!stepText)throw std::runtime_error("Explicit NODD_LAR_MAX_STEP_MM unset");
    const double cap=std::stod(stepText);
    if(!std::isfinite(cap)||cap<0.)throw std::runtime_error("Invalid explicit LAr step cap");
    m_record["requested_max_step_mm"]=cap;
    m_record["step_policy"]=cap==0.?"native unmodified":"explicit common numeric cap; preserve smaller native limits";
    // Geometry and user limits can be shared by workers. Remember pre-install
    // values once so later workers do not mistake the installed cap for native.
    static std::map<const G4LogicalVolume*,json> installation;
    auto* electron=G4ParticleTable::GetParticleTable()->FindParticle("e-");
    G4Track track(new G4DynamicParticle(electron,G4ThreeVector(1.,0.,0.),CLHEP::GeV),0.,G4ThreeVector());
    std::set<G4FieldManager*> fields;
    fields.insert(G4TransportationManager::GetTransportationManager()->GetFieldManager());
    std::set<std::string> roles;
    auto& sensitive=m_record["sensitive_lar"];sensitive=json::object();
    for(auto* volume:*G4LogicalVolumeStore::GetInstance()) {
      if(volume->GetFieldManager()) fields.insert(volume->GetFieldManager());
      auto* sd=volume->GetSensitiveDetector();if(!sd)continue;
      const std::string name=sd->GetName();if(name!="LArBarrel"&&name!="LArEndcaps")throw std::runtime_error("Unexpected sensitive detector: "+name);
      roles.insert(name);
      auto* material=volume->GetMaterial();
      if(material->GetNumberOfElements()!=1 ||
         std::abs(material->GetElement(0)->GetZ()-18.)>1e-12 ||
         std::abs(material->GetDensity()/(CLHEP::g/CLHEP::cm3)-1.396)>1e-8)
        throw std::runtime_error("Sensitive material is not the declared LAr proxy");
      if(!installation.count(volume)) {
        auto* prior=volume->GetUserLimits();
        const double native=prior?prior->GetMaxAllowedStep(track)/CLHEP::mm:std::numeric_limits<double>::infinity();
        const bool apply=cap>0. && native>cap;
        if(apply) {
          auto* limits=prior?new G4UserLimits(*prior):new G4UserLimits();
          limits->SetMaxAllowedStep(cap*CLHEP::mm);volume->SetUserLimits(limits);
        }
        auto* effective=volume->GetUserLimits();
        const double step=effective?effective->GetMaxAllowedStep(track)/CLHEP::mm:std::numeric_limits<double>::infinity();
        installation[volume]={{"name",std::string(volume->GetName())},
          {"material",std::string(material->GetName())},{"density_g_cm3",material->GetDensity()/(CLHEP::g/CLHEP::cm3)},
          {"native_max_step_mm",std::isfinite(native)&&native<1e300?json(native):json(nullptr)},
          {"max_step_mm",std::isfinite(step)&&step<1e300?json(step):json(nullptr)},
          {"numeric_cap_applied",apply},
          {"Birks_mm_per_MeV",material->GetIonisation()->GetBirksConstant()/(CLHEP::mm/CLHEP::MeV)}};
      }
      if(sensitive[name].is_null())sensitive[name]={{"logical_volumes",0},{"volumes",json::array()}};
      sensitive[name]["logical_volumes"]=sensitive[name]["logical_volumes"].get<int>()+1;
      sensitive[name]["volumes"].push_back(installation.at(volume));
    }
    if(roles!=std::set<std::string>{"LArBarrel","LArEndcaps"})throw std::runtime_error("Both worker ECAL SDs must be present");
    double maxField=0.;
    for(auto* manager:fields)if(manager&&manager->GetDetectorField())
      for(double x:{0.,1500.,3000.})for(double z:{-5900.,-5460.,-3950.,0.,3950.,5460.,5900.}){
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
DECLARE_GEANT4ACTION(nODDLArResponseAudit)
