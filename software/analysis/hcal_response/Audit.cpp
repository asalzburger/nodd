// HCAL PROTOTYPE worker audit. Explicit NODD_HCAL_MAX_STEP_MM controls any cap.
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
#include <vector>
#include <random>
#include <G4VSolid.hh>
#include <G4VPhysicalVolume.hh>
#include <TGeoMatrix.h>

namespace {
// Compare converted solids in each ACTUAL G4 placement frame to the frozen
// 72 original box-minus-recess domains in the carrier-centred frame. This
// catches Boolean importer transform losses which a ROOT-only audit cannot.
nlohmann::json checkHCALConvertedSolids(const dd4hep::sim::Geant4Mapping& mapping) {
  using nlohmann::json;
  json records=json::array();std::set<const G4LogicalVolume*> checked;
  auto expected=[](double x,double y,double z) {
    for(int module=0;module<2;++module)for(int row=0;row<6;++row)for(int col=0;col<6;++col) {
      const double dx=x-((module?18.:-168.)+30.*col),dy=y-(-87.+30.*row),dz=z+4.;
      if(std::abs(dx)<14.85 && std::abs(dy)<14.85 && std::abs(dz)<1.5 &&
         !(dx*dx+dy*dy<3.5*3.5 && dz>0.4))return true;
    }
    return false;
  };
  for(const auto& entry:mapping.data().g4Placements) {
    if(!entry.first.volume().isSensitive())continue;
    auto* pv=entry.second;auto* lv=pv->GetLogicalVolume();
    if(!checked.insert(lv).second)continue;
    auto* solid=lv->GetSolid();const auto rotation=pv->GetObjectRotationValue();
    const auto translation=pv->GetObjectTranslation();
    const auto* native=entry.first.ptr()->GetMatrix();
    for(int i=0;i<3;++i)
      if(std::abs(translation[i]/CLHEP::mm-native->GetTranslation()[i]/dd4hep::mm)>1e-8)
        throw std::runtime_error("Converted HCAL sensitive placement translation differs");
    unsigned long probes=0,mismatches=0;json errors=json::array();
    auto probe=[&](double x,double y,double z) {
      const auto local=rotation.inverse()*(G4ThreeVector(x,y,z)*CLHEP::mm-translation);
      const bool actual=solid->Inside(local)!=kOutside,want=expected(x,y,z);++probes;
      if(actual!=want) {
        ++mismatches;
        if(errors.size()<12)errors.push_back({{"carrier_centered_point_mm",{x,y,z}},
          {"G4_active_local_point_mm",{local.x()/CLHEP::mm,local.y()/CLHEP::mm,local.z()/CLHEP::mm}},
          {"expected_inside",want},{"G4_inside",actual}});
      }
    };
    for(int module=0;module<2;++module)for(int row=0;row<6;++row)for(int col=0;col<6;++col) {
      const double x=(module?18.:-168.)+30.*col,y=-87.+30.*row,z=-4.;
      for(double dz:{-1.499,-0.5,0.,0.3999,0.4001,1.499,1.5001})probe(x,y,z+dz);
      for(double edge:{-14.8501,-14.8499,14.8499,14.8501}) {
        probe(x+edge,y,z);probe(x,y+edge,z);
      }
      for(double radius:{3.4999,3.5001}) {
        probe(x+radius,y,z+0.95);probe(x,y+radius,z+0.95);
      }
    }
    // Board seam, reflector cracks, carrier service bay and non-core margins.
    for(double x:{-190.,-184.,-183.,-153.,-3.,0.,3.,15.,183.,184.,190.})
      for(double y:{-120.,-103.,-102.,-12.,78.,79.,90.,110.,120.})probe(x,y,-4.);
    std::mt19937 engine(202650045);std::uniform_real_distribution<double> ux(-190.,190.),uy(-120.,120.),uz(-6.,0.);
    for(int i=0;i<10000;++i)probe(ux(engine),uy(engine),uz(engine));
    records.push_back({{"volume",std::string(lv->GetName())},{"probes",probes},
      {"mismatches",mismatches},{"errors",errors},
      {"active_translation_from_carrier_center_mm",{translation.x()/CLHEP::mm,translation.y()/CLHEP::mm,translation.z()/CLHEP::mm}}});
  }
  if(checked.size()!=2)throw std::runtime_error("Expected both converted HCAL sensitive solids");
  return records;
}
}

namespace {
bool hcalMapsInitializedSerially = false;
}

// Invoked by the main-kernel initialization callback before worker creation.
// Lazy native lookup creation in a first worker hit otherwise races in DDG4.
void initializeHCALResponseMaps(const std::string& directory, unsigned long expectedRawIDs) {
  const auto start=std::chrono::steady_clock::now();
  const int thread=G4Threading::G4GetThreadId();
  if(thread>=0 || hcalMapsInitializedSerially)
    throw std::runtime_error("HCAL maps must initialize once on the main thread");
  const std::string path=directory+"/maps-initialized.json";
  if(std::filesystem::exists(path))throw std::runtime_error("Refusing map-audit overwrite");
  const auto& mapping=dd4hep::sim::Geant4Mapping::instance();
  std::cout << "HCAL_RESPONSE_G4_MAP_BEGIN" << std::endl;
  const auto g4=mapping.volumeManager();
  std::cout << "HCAL_RESPONSE_NATIVE_MAP_BEGIN" << std::endl;
  const auto native=dd4hep::VolumeManager::getVolumeManager(mapping.detectorDescription());
  if(!g4.isValid()||!native.isValid())throw std::runtime_error("Invalid HCAL volume manager");
  const auto converted=checkHCALConvertedSolids(mapping);
  unsigned long convertedErrors=0;
  for(const auto& record:converted)convertedErrors+=record["mismatches"].get<unsigned long>();
  {
    std::ofstream output(directory+"/converted-solids.json");
    output<<nlohmann::json({{"status",convertedErrors?"FAIL":"PASS"},{"solids",converted},
      {"scope","Actual converted G4 solid membership and placement versus frozen original physical core domains"}}).dump(2)<<'\n';
  }
  if(convertedErrors)throw std::runtime_error("Converted G4 HCAL solid/original core membership differs");
  std::vector<dd4hep::VolumeID> ids; ids.reserve(expectedRawIDs);
  for(const auto& entry:mapping.data().g4Paths) {
    const auto id=entry.second.volumeID;
    if((id&255)!=13&&(id&255)!=14)
      throw std::runtime_error("Unexpected/duplicate serial HCAL raw volume ID");
    ids.push_back(id);
    const auto* context=native.lookupContext(id);
    if(!context||!context->volumePlacement().volume().isSensitive())
      throw std::runtime_error("Missing serial HCAL native context");
  }
  std::sort(ids.begin(),ids.end());
  if(std::adjacent_find(ids.begin(),ids.end())!=ids.end())throw std::runtime_error("Duplicate HCAL raw tile ID");
  if(expectedRawIDs==0 || ids.size()!=expectedRawIDs)
    throw std::runtime_error("Incomplete serial HCAL volume maps");
  nlohmann::json record={{"status","PASS"},{"thread_id",thread},
    {"raw_sensitive_ids",ids.size()},{"native_contexts_checked",ids.size()},
    {"expected_raw_sensitive_ids",expectedRawIDs},
    {"scope","both volume managers and all raw contexts initialized serially before workers"},
    {"seconds",std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()}};
  std::ofstream stream(path);stream<<record.dump(2)<<'\n';stream.close();
  if(!stream)throw std::runtime_error("Cannot write serial map audit");
  hcalMapsInitializedSerially=true;
  std::cout << "HCAL_RESPONSE_MAPS_READY" << std::endl;
}

namespace dd4hep::sim {
class nODDHCALResponseAudit : public Geant4RunAction {
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
  nODDHCALResponseAudit(dd4hep::sim::Geant4Context* context,const std::string& name)
    : Geant4RunAction(context,name) {}
  void begin(const G4Run* run) override {
    using nlohmann::json;
    const int worker=G4Threading::G4GetThreadId();
    if(!hcalMapsInitializedSerially)throw std::runtime_error("Serial HCAL map initialization missing");
    const char* directory=std::getenv("NODD_HCAL_AUDIT");
    if(!directory) throw std::runtime_error("NODD_HCAL_AUDIT unset");
    m_file=std::string(directory)+"/worker-"+std::to_string(worker)+".json";
    if(std::filesystem::exists(m_file)) throw std::runtime_error("Refusing worker audit overwrite");
    m_record={{"thread_id",worker},{"run_id",run->GetRunID()},
              {"status","initialized"},{"scope","native worker begin/end-run audit"},{"maps_initialized_serially",true}};
    // User limits are shared geometry data. Serialize first installation and
    // all inspections before any audited worker begins tracking.
    static std::mutex limitsMutex;
    std::lock_guard<std::mutex> guard(limitsMutex);
    const char* stepText=std::getenv("NODD_HCAL_MAX_STEP_MM");
    if(!stepText)throw std::runtime_error("Explicit NODD_HCAL_MAX_STEP_MM unset");
    const double cap=std::stod(stepText);
    if(!std::isfinite(cap)||cap<0.)throw std::runtime_error("Invalid explicit HCAL step cap");
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
    auto& sensitive=m_record["sensitive_hcal"];sensitive=json::object();
    for(auto* volume:*G4LogicalVolumeStore::GetInstance()) {
      if(volume->GetFieldManager()) fields.insert(volume->GetFieldManager());
      auto* sd=volume->GetSensitiveDetector();if(!sd)continue;
      const std::string name=sd->GetName();if(name!="HCALBarrel"&&name!="HCALEndcaps")throw std::runtime_error("Unexpected sensitive detector: "+name);
      roles.insert(name);
      auto* material=volume->GetMaterial();
      if(std::string(material->GetName()).find("PSHost")==std::string::npos ||
         std::abs(material->GetDensity()/(CLHEP::g/CLHEP::cm3)-1.06)>1e-8)
        throw std::runtime_error("Sensitive material is not the declared PSHost proxy");
      if(material->GetIonisation()->GetBirksConstant()!=0.)
        throw std::runtime_error("Raw HCAL requires zero Birks constant");
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
    if(roles!=std::set<std::string>{"HCALBarrel","HCALEndcaps"})throw std::runtime_error("Both worker ECAL SDs must be present");
    double maxField=0.;
    for(auto* manager:fields)if(manager&&manager->GetDetectorField())
      for(double x:{0.,3130.,5720.})for(double z:{-9350.,-6760.,-6260.,0.,6260.,6760.,9350.}){
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
    for(const std::string name:{"e-","e+","gamma","pi-","proton"}){
      auto* p=G4ParticleTable::GetParticleTable()->FindParticle(name);
      auto* list=p->GetProcessManager()->GetProcessList();json names=json::array();bool limiter=false;
      for(std::size_t i=0;i<list->size();++i){const std::string process=(*list)[i]->GetProcessName();names.push_back(process);limiter=limiter||process=="StepLimiter";}
      m_record["processes"][name]=names;
      if(name!="gamma"&&!limiter)throw std::runtime_error("StepLimiter absent on charged particles");
    }
    m_record["steel_materials"]=json::array();
    for(auto* material:*G4Material::GetMaterialTable())
      if(std::string(material->GetName()).find("Steel235")!=std::string::npos)
        m_record["steel_materials"].push_back({{"name",std::string(material->GetName())},
          {"density_g_cm3",material->GetDensity()/(CLHEP::g/CLHEP::cm3)},
          {"radiation_length_mm",material->GetRadlen()/CLHEP::mm},
          {"nuclear_interaction_length_mm",material->GetNuclearInterLength()/CLHEP::mm}});
    auto* engine=G4Random::getTheEngine();
    m_record["rng_engine"]=engine->name();m_record["begin_run_rng_seed"]=engine->getSeed();
    save();
  }
  void end(const G4Run* run) override {
    m_record["events"]=run->GetNumberOfEvent();m_record["status"]="complete";save();
  }
};
}
DECLARE_GEANT4ACTION(nODDHCALResponseAudit)

// Independent positive sensitive-step deposit observer. No changes to hits,
// track state, cuts, particle weights or sensitive-detector decisions.
#include <DDG4/Geant4EventAction.h>
#include <DDG4/Geant4SteppingAction.h>
#include <DDG4/Geant4HitCollection.h>
#include <DDG4/Geant4Data.h>
#include <G4Event.hh>
#include <G4Step.hh>
#include <G4StepPoint.hh>
#include <G4HCofThisEvent.hh>
#include <G4VPhysicalVolume.hh>
#include <array>

namespace {
struct HCALObservedEvent {
  int event=-1;
  double sensitiveDeposit=0.,escapedKinetic=0.;
  unsigned long steps=0;
  std::array<double,2> deposits{};
  nlohmann::json firstInelastic=nullptr;
};
thread_local HCALObservedEvent hcalEvent;
}
namespace dd4hep::sim {
class nODDHCALStepObserver : public Geant4SteppingAction {
public:
  nODDHCALStepObserver(Geant4Context* c,const std::string& n):Geant4SteppingAction(c,n){}
  void operator()(const G4Step* step,G4SteppingManager*) override {
    const auto* pre=step->GetPreStepPoint();const auto* post=step->GetPostStepPoint();
    const auto* volume=pre->GetPhysicalVolume();
    const double energy=step->GetTotalEnergyDeposit();
    if(volume && volume->GetLogicalVolume()->GetSensitiveDetector() && energy>0.) {
      const auto name=volume->GetLogicalVolume()->GetSensitiveDetector()->GetName();
      const int role=name=="HCALBarrel"?0:name=="HCALEndcaps"?1:-1;
      if(role<0)throw std::runtime_error("Unexpected sensitive step outside HCAL");
      hcalEvent.sensitiveDeposit+=energy;
      hcalEvent.deposits[role]+=energy;++hcalEvent.steps;
    }
    if(post->GetStepStatus()==fWorldBoundary)
      hcalEvent.escapedKinetic+=post->GetKineticEnergy();
    const auto* process=post->GetProcessDefinedStep();
    if(hcalEvent.firstInelastic.is_null() && step->GetTrack()->GetTrackID()==1 && process &&
       std::string(process->GetProcessName()).find("Inelastic")!=std::string::npos) {
      const auto p=post->GetPosition();
      hcalEvent.firstInelastic={p.x()/CLHEP::mm,p.y()/CLHEP::mm,p.z()/CLHEP::mm};
    }
  }
};
class nODDHCALObserver : public Geant4EventAction {
  std::ofstream m_stream;
public:
  nODDHCALObserver(Geant4Context* c,const std::string& n):Geant4EventAction(c,n){}
  void begin(const G4Event* event) override {
    hcalEvent=HCALObservedEvent{};hcalEvent.event=event->GetEventID();
    if(!m_stream.is_open()) {
      const char* directory=std::getenv("NODD_HCAL_AUDIT");
      if(!directory)throw std::runtime_error("NODD_HCAL_AUDIT unset");
      const auto path=std::string(directory)+"/events-"+std::to_string(G4Threading::G4GetThreadId())+".jsonl";
      if(std::filesystem::exists(path))throw std::runtime_error("Refusing observer overwrite");
      m_stream.open(path);
      if(!m_stream)throw std::runtime_error("Cannot open HCAL observer");
    }
  }
  void end(const G4Event* event) override {
    if(hcalEvent.event!=event->GetEventID())throw std::runtime_error("HCAL event observer mismatch");
    std::array<double,2> sums{};std::array<double,60> layers{};
    std::array<unsigned long,2> counts{};std::array<bool,2> present{};
    auto* container=event->GetHCofThisEvent();
    if(!container)throw std::runtime_error("No native HCAL hit container");
    for(std::size_t i=0;i<container->GetCapacity();++i) {
      auto* hits=dynamic_cast<Geant4HitCollection*>(container->GetHC(i));
      if(!hits)continue;
      const auto name=hits->GetName();
      const int role=name=="HCALBarrelHits"?0:name=="HCALEndcapHits"?1:-1;
      if(role<0)throw std::runtime_error("Unexpected native hit collection: "+name);
      present[role]=true;
      for(std::size_t j=0;j<hits->GetSize();++j) {
        const auto* hit=static_cast<const Geant4Calorimeter::Hit*>(hits->hit(j).data());
        const int layer=(hit->cellID>>14)&63;
        if(layer>=60)throw std::runtime_error("Native HCAL layer outside design");
        sums[role]+=hit->energyDeposit;layers[layer]+=hit->energyDeposit;++counts[role];
      }
    }
    if(!present[0]||!present[1])throw std::runtime_error("Both native HCAL collections must exist");
    for(int i=0;i<2;++i)
      if(std::abs(sums[i]-hcalEvent.deposits[i])>1e-8*CLHEP::GeV+1e-9*std::abs(sums[i]))
        throw std::runtime_error("Sensitive step/native cell energy closure failed");
    std::vector<double> profile;
    for(double e:layers)profile.push_back(e/CLHEP::GeV);
    const nlohmann::json record={{"event",event->GetEventID()},
      {"thread_id",G4Threading::G4GetThreadId()},
      {"step_energy_GeV",hcalEvent.sensitiveDeposit/CLHEP::GeV},
      {"step_energies_GeV",{hcalEvent.deposits[0]/CLHEP::GeV,hcalEvent.deposits[1]/CLHEP::GeV}},
      {"native_hit_energy_GeV",(sums[0]+sums[1])/CLHEP::GeV},
      {"native_hit_energies_GeV",{sums[0]/CLHEP::GeV,sums[1]/CLHEP::GeV}},
      {"native_hit_counts",counts},{"positive_sensitive_steps",hcalEvent.steps},
      {"layer_energies_GeV",profile},
      {"world_escape_kinetic_GeV",hcalEvent.escapedKinetic/CLHEP::GeV},
      {"first_primary_inelastic_position_mm",hcalEvent.firstInelastic}};
    m_stream<<record.dump()<<'\n';m_stream.flush();
    if(!m_stream)throw std::runtime_error("Cannot write HCAL observer");
  }
};
}
DECLARE_GEANT4ACTION(nODDHCALStepObserver)
DECLARE_GEANT4ACTION(nODDHCALObserver)
