// macOS dyld interposition: observe native phase boundaries without changing them.
#include <DDG4/Geant4Converter.h>
#include <XML/DocumentHandler.h>
#include <G4GeometryManager.hh>
#include <G4LogicalVolumeStore.hh>
#include <G4MaterialCutsCouple.hh>
#include <G4Material.hh>
#include <G4ProductionCutsTable.hh>
#include <G4ProductionCuts.hh>
#include <G4Region.hh>
#include <G4RegionStore.hh>
#include <G4TransportationManager.hh>
#include <G4RunManager.hh>
#include <G4UserSteppingAction.hh>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <dlfcn.h>
// This two-pointer section is the dyld interposition ABI.
#define DYLD_INTERPOSE(REPLACEMENT, TARGET) \
__attribute__((used)) static const struct { const void* replacement; const void* target; } \
interpose_##TARGET __attribute__((section("__DATA,__interpose"))) = { \
reinterpret_cast<const void*>(&REPLACEMENT), reinterpret_cast<const void*>(&TARGET) };

namespace {
using Clock = std::chrono::steady_clock;
bool userEnergyCutsConfigured=false;
size_t originalCoupleUpdates=0;
struct StepStats { size_t count=0; double wall=0, cpu=0; } stepStats;
struct ObservedStepping final : G4UserSteppingAction {
  G4UserSteppingAction* inner;
  explicit ObservedStepping(G4UserSteppingAction* action) : inner(action) {}
  ~ObservedStepping() override { delete inner; }
  void UserSteppingAction(const G4Step* step) override {
    const auto wall=Clock::now();
    const auto cpu=std::clock();
    inner->UserSteppingAction(step);
    stepStats.cpu+=double(std::clock()-cpu)/CLOCKS_PER_SEC;
    stepStats.wall+=std::chrono::duration<double>(Clock::now()-wall).count();
    ++stepStats.count;
  }
};
struct Timer {
  const char* name;
  Clock::time_point wall=Clock::now();
  clock_t cpu=std::clock();
  ~Timer() {
    const char* path=std::getenv("MATERIAL_NATIVE_TIMING");
    if (!path) return;
    if (auto* f=std::fopen(path,"a")) {
      std::fprintf(f,"{\"name\":\"%s\",\"wall_s\":%.9f,\"cpu_s\":%.9f}\n", name,
        std::chrono::duration<double>(Clock::now()-wall).count(),
        double(std::clock()-cpu)/CLOCKS_PER_SEC);
      std::fclose(f);
    }
  }
};
// Opt-in prototype for immutable, single-world material recording. Validate
// the actual association of EVERY volume; a count-only cache would be unsafe.
bool associationsAlreadyCorrect(G4ProductionCutsTable* table, G4VPhysicalVolume* world) {
  if (userEnergyCutsConfigured || !G4GeometryManager::GetInstance()->IsGeometryClosed() || table->IsModified() ||
      table->GetTableSize()==0 ||
      G4TransportationManager::GetTransportationManager()->GetNoWorlds()!=1) return false;
  G4Region* region=nullptr;
  for (auto* r : *G4RegionStore::GetInstance()) {
    if (!r->IsInMassGeometry()) continue;
    if (region || r->GetWorldPhysical()!=world || r->GetNumberOfRootVolumes()!=1) return false;
    region=r;
  }
  if (!region || *region->GetRootLogicalVolumeIterator()!=world->GetLogicalVolume() ||
      region->GetNumberOfMaterials()!=table->GetTableSize()) return false;
  for (auto* volume : *G4LogicalVolumeStore::GetInstance()) {
    auto* couple=volume->GetMaterialCutsCouple();
    if (volume->GetRegion()!=region || !couple || !couple->IsUsed() ||
        couple->GetIndex()<0 || size_t(couple->GetIndex())>=table->GetTableSize() ||
        table->GetMaterialCutsCouple(couple->GetIndex())!=couple ||
        couple->GetMaterial()!=volume->GetMaterial() ||
        couple->GetProductionCuts()!=region->GetProductionCuts() ||
        region->FindCouple(volume->GetMaterial())!=couple) return false;
  }
  return true;
}
}

extern "C" void target_energy_cuts(void*,const std::vector<double>&,size_t)
  asm("__ZN21G4ProductionCutsTable18SetEnergyCutVectorERKNSt3__16vectorIdNS0_9allocatorIdEEEEm");
extern "C" void observe_energy_cuts(void* self,const std::vector<double>& values,size_t index) {
  userEnergyCutsConfigured=true;
  target_energy_cuts(self,values,index);
}
DYLD_INTERPOSE(observe_energy_cuts,target_energy_cuts);

extern "C" void materialProfileInstallSteppingTimer() {
  auto* run=G4RunManager::GetRunManager();
  auto* original=const_cast<G4UserSteppingAction*>(run->GetUserSteppingAction());
  if (!original) std::abort();
  run->SetUserAction(new ObservedStepping(original));
}

// Adverse controls run only AFTER transport and restore each changed pointer.
extern "C" void observe_couples(void*,void*);
extern "C" const char* materialProfileGuardChecks() {
  if (const auto* path=std::getenv("MATERIAL_NATIVE_TIMING")) {
    if (auto* f=std::fopen(path,"a")) {
      std::fprintf(f,"{\"name\":\"post_transport_checks_begin\"}\n");
      std::fclose(f);
    }
  }
  auto* world=G4TransportationManager::GetTransportationManager()->GetNavigatorForTracking()->GetWorldVolume();
  auto* table=G4ProductionCutsTable::GetProductionCutsTable();
  auto check=[&] { return associationsAlreadyCorrect(table,world); };
  const bool initial=check();
  auto* volume=world->GetLogicalVolume();
  auto* material=volume->GetMaterial();
  G4Material* alternate=nullptr;
  for (auto* m : *G4Material::GetMaterialTable()) if (m!=material) { alternate=m; break; }
  volume->SetMaterial(alternate);
  const bool materialRejected=!check();
  volume->SetMaterial(material);
  auto* region=volume->GetRegion();
  volume->SetRegion(nullptr);
  const bool regionRejected=!check();
  volume->SetRegion(region);
  auto* cuts=region->GetProductionCuts();
  G4ProductionCuts alternateCuts;
  region->SetProductionCuts(&alternateCuts);
  const bool cutsRejected=!check();
  region->SetProductionCuts(cuts);
  const double originalCut=cuts->GetProductionCut(0);
  cuts->SetProductionCut(originalCut+1.0,0);  // post-transport adverse fixture only
  const bool cutValueRejected=!check();
  cuts->SetProductionCut(originalCut,0);
  table->PhysicsTableUpdated();  // initial guard required all flags unmodified
  auto* couple=const_cast<G4MaterialCutsCouple*>(volume->GetMaterialCutsCouple());
  volume->SetMaterialCutsCouple(nullptr);
  const bool nullCoupleRejected=!check();
  volume->SetMaterialCutsCouple(couple);
  const auto originalIndex=couple->GetIndex();
  couple->SetIndex(int(table->GetTableSize()));
  const bool staleIndexRejected=!check();
  couple->SetIndex(originalIndex);
  bool extraRegionRejected=false;
  {
    G4Region extra("material-profile-adverse-extra-region");
    extra.UsedInMassGeometry(true);
    extraRegionRejected=!check();
  }
  G4GeometryManager::GetInstance()->OpenGeometry();
  const bool openGeometryRejected=!check();
  G4GeometryManager::GetInstance()->CloseGeometry(true,false);
  const bool restored=check();
  // Last control deliberately disables the optimization for the remaining
  // process lifetime. No further event is transported after these controls.
  observe_energy_cuts(table,std::vector<double>(table->GetTableSize(),0.001),0);
  const bool energyVectorRejected=!check();
  const auto updatesBefore=originalCoupleUpdates;
  observe_couples(table,world);
  const bool fallbackExecuted=originalCoupleUpdates==updatesBefore+1;
  const auto* energy=table->GetEnergyCutsVector(0);
  const bool energyValuesUpdated=energy && energy->size()==table->GetTableSize() &&
    std::all_of(energy->begin(),energy->end(),[](double value) { return value==0.001; });
  static std::string result;
  result=std::string("{\"initial_valid\":")+(initial?"true":"false")+
    ",\"changed_material_rejected\":"+(materialRejected?"true":"false")+
    ",\"changed_region_rejected\":"+(regionRejected?"true":"false")+
    ",\"changed_cuts_rejected\":"+(cutsRejected?"true":"false")+
    ",\"changed_cut_value_rejected\":"+(cutValueRejected?"true":"false")+
    ",\"null_couple_rejected\":"+(nullCoupleRejected?"true":"false")+
    ",\"stale_index_rejected\":"+(staleIndexRejected?"true":"false")+
    ",\"extra_region_rejected\":"+(extraRegionRejected?"true":"false")+
    ",\"open_geometry_rejected\":"+(openGeometryRejected?"true":"false")+
    ",\"restored_valid\":"+(restored?"true":"false")+
    ",\"energy_vector_config_rejected\":"+(energyVectorRejected?"true":"false")+
    ",\"energy_vector_fallback_executed\":"+(fallbackExecuted?"true":"false")+
    ",\"energy_vector_values_updated\":"+(energyValuesUpdated?"true":"false")+"}";
  return result.c_str();
}

#define OBSERVE_VOID(LABEL, SYMBOL) \
extern "C" void target_##LABEL(void*) asm("_" SYMBOL); \
extern "C" void observe_##LABEL(void* self) { \
  Timer t{#LABEL}; target_##LABEL(self); \
} \
DYLD_INTERPOSE(observe_##LABEL, target_##LABEL)

OBSERVE_VOID(g4_initialize, "_ZN12G4RunManager10InitializeEv");
OBSERVE_VOID(g4_initialize_geometry, "_ZN12G4RunManager18InitializeGeometryEv");
OBSERVE_VOID(g4_initialize_physics, "_ZN12G4RunManager17InitializePhysicsEv");
OBSERVE_VOID(g4_run_initialization, "_ZN12G4RunManager17RunInitializationEv");

extern "C" void target_couples(void*,void*)
  asm("__ZN21G4ProductionCutsTable17UpdateCoupleTableEP17G4VPhysicalVolume");
extern "C" void observe_couples(void* self,void* world) {
  Timer t{"g4_update_couple_table"};
  const char* reuse=std::getenv("MATERIAL_REUSE_STATIC_COUPLES");
  if (reuse && std::string(reuse)=="1") {
    Timer guard{"g4_validate_unchanged_material_couples"};
    if (associationsAlreadyCorrect(static_cast<G4ProductionCutsTable*>(self),
                                  static_cast<G4VPhysicalVolume*>(world))) return;
  }
  ++originalCoupleUpdates;
  target_couples(self,world);
}
DYLD_INTERPOSE(observe_couples,target_couples);

extern "C" bool target_close(void*,bool,bool,void*)
  asm("__ZN17G4GeometryManager13CloseGeometryEbbP17G4VPhysicalVolume");
extern "C" bool observe_close(void* self,bool optimise,bool verbose,void* world) {
  Timer t{"g4_close_geometry_voxelization"}; return target_close(self,optimise,verbose,world);
}
DYLD_INTERPOSE(observe_close,target_close);

extern "C" void target_event(void*,void*) asm("__ZN14G4EventManager15ProcessOneEventEP7G4Event");
extern "C" void observe_event(void* self,void* event) {
  const auto before=stepStats;
  Timer t{"g4_event_transport_and_recording"}; target_event(self,event);
  if (stepStats.count>before.count) {
    if (auto* f=std::fopen(std::getenv("MATERIAL_NATIVE_TIMING"),"a")) {
      std::fprintf(f,"{\"name\":\"material_stepping_recording_instrumented\",\"steps\":%zu,\"wall_s\":%.9f,\"cpu_s\":%.9f}\n",
        stepStats.count-before.count,stepStats.wall-before.wall,stepStats.cpu-before.cpu);
      std::fclose(f);
    }
  }
}
DYLD_INTERPOSE(observe_event,target_event);

extern "C" void target_process(void*,int) asm("__ZN12G4RunManager15ProcessOneEventEi");
extern "C" void observe_process(void* self,int n) {
  Timer t{"g4_process_one_event"}; target_process(self,n);
}
DYLD_INTERPOSE(observe_process,target_process);

using Converter=dd4hep::sim::Geant4Converter;
Converter& target_convert(Converter*,dd4hep::DetElement)
  asm("__ZN6dd4hep3sim15Geant4Converter6createENS_10DetElementE");
Converter& observe_convert(Converter* self,dd4hep::DetElement top) {
  Timer t{"dd4hep_to_geant4_converter_create"}; return target_convert(self,top);
}
DYLD_INTERPOSE(observe_convert,target_convert);

using Handler=dd4hep::xml::DocumentHandler;
using Document=dd4hep::xml::Document;
using Reader=dd4hep::xml::UriReader;
Document target_xml(const Handler*,const std::string&,Reader*)
  asm("__ZNK6dd4hep3xml15DocumentHandler4loadERKNSt3__112basic_stringIcNS2_11char_traitsIcEENS2_9allocatorIcEEEEPNS0_9UriReaderE");
Document observe_xml(const Handler* self,const std::string& path,Reader* reader) {
  Timer t{"xml_document_load"}; return target_xml(self,path,reader);
}
DYLD_INTERPOSE(observe_xml,target_xml);

extern "C" void target_parse(void*,const void*)
  asm("__ZN11xercesc_3_317AbstractDOMParser5parseERKNS_11InputSourceE");
extern "C" void observe_parse(void* self,const void* source) {
  Timer t{"xerces_dom_parse"}; target_parse(self,source);
}
DYLD_INTERPOSE(observe_parse,target_parse);

extern "C" void target_parse_path(void*,const char*)
  asm("__ZN11xercesc_3_317AbstractDOMParser5parseEPKc");
extern "C" void observe_parse_path(void* self,const char* path) {
  Timer t{"xerces_dom_parse_path"}; target_parse_path(self,path);
}
DYLD_INTERPOSE(observe_parse_path,target_parse_path);

extern "C" void target_parse_wide(void*,const char16_t*)
  asm("__ZN11xercesc_3_317AbstractDOMParser5parseEPKDs");
extern "C" void observe_parse_wide(void* self,const char16_t* path) {
  Timer t{"xerces_dom_parse_wide_path"}; target_parse_wide(self,path);
}
DYLD_INTERPOSE(observe_parse_wide,target_parse_wide);
