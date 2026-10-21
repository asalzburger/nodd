#include <DD4hep/Detector.h>
#include <G4LogicalVolumeStore.hh>
#include <G4PhysicalVolumeStore.hh>
#include <G4SolidStore.hh>
#include <G4Material.hh>
#include <G4RegionStore.hh>
#include <G4ProductionCutsTable.hh>
#include <G4RunManager.hh>
#include <G4TransportationManager.hh>
#include <TGeoManager.h>
#include <TGeoVolume.h>
#include <nlohmann/json.hpp>
#include <map>
#include <functional>

std::string materialProfileInventory() {
  using nlohmann::json;
  json result;
  auto* geo = gGeoManager;
  std::map<std::string, size_t> shapes;
  size_t edges = 0, maxDaughters = 0;
  for (auto* obj : *geo->GetListOfVolumes()) {
    auto* vol = static_cast<TGeoVolume*>(obj);
    shapes[vol->GetShape()->ClassName()]++;
    edges += vol->GetNdaughters();
    maxDaughters = std::max(maxDaughters, size_t(vol->GetNdaughters()));
  }
  std::map<TGeoVolume*, std::pair<size_t,size_t>> memo;
  std::function<std::pair<size_t,size_t>(TGeoVolume*)> walk = [&](TGeoVolume* v) {
    if (memo.count(v)) return memo.at(v);
    size_t nodes = 1, depth = 1;
    for (int i=0; i<v->GetNdaughters(); ++i) {
      auto sub=walk(v->GetNode(i)->GetVolume());
      nodes += sub.first; depth=std::max(depth,sub.second+1);
    }
    return memo[v]={nodes,depth};
  };
  const auto [nodes, depth] = walk(geo->GetTopVolume());
  result["tgeo"] = {{"volumes",geo->GetListOfVolumes()->GetEntries()},
    {"materials",geo->GetListOfMaterials()->GetEntries()},
    {"unique_daughter_edges",edges}, {"max_daughters",maxDaughters},
    {"world_daughters",geo->GetTopVolume()->GetNdaughters()},
    {"expanded_nodes_including_world",nodes},{"max_depth",depth},{"shapes",shapes}};
  result["tgeo"]["world_children"]=json::array();
  for (int i=0; i<geo->GetTopVolume()->GetNdaughters(); ++i) {
    result["tgeo"]["world_children"].push_back(geo->GetTopVolume()->GetNode(i)->GetVolume()->GetName());
  }
  auto* store=G4LogicalVolumeStore::GetInstance();
  shapes.clear(); maxDaughters=0; edges=0;
  json heavy=json::array();
  for (auto* vol : *store) {
    shapes[vol->GetSolid()->GetEntityType()]++;
    const size_t daughters=vol->GetNoDaughters();
    edges+=daughters; maxDaughters=std::max(maxDaughters,daughters);
    if (daughters>1000) heavy.push_back({{"name",vol->GetName()}, {"daughters",daughters}});
  }
  auto* world=G4TransportationManager::GetTransportationManager()->GetNavigatorForTracking()->GetWorldVolume();
  std::map<G4LogicalVolume*, std::pair<size_t,size_t>> gmemo;
  std::function<std::pair<size_t,size_t>(G4LogicalVolume*)> gwalk = [&](G4LogicalVolume* v) {
    if (gmemo.count(v)) return gmemo.at(v);
    size_t n=1, d=1;
    for (size_t i=0; i<v->GetNoDaughters(); ++i) {
      auto sub=gwalk(v->GetDaughter(i)->GetLogicalVolume());
      n+=sub.first; d=std::max(d,sub.second+1);
    }
    return gmemo[v]={n,d};
  };
  const auto [gnodes,gdepth]=gwalk(world->GetLogicalVolume());
  result["geant4"]={{"logical_volumes",store->size()},
    {"physical_volumes",G4PhysicalVolumeStore::GetInstance()->size()},
    {"solids",G4SolidStore::GetInstance()->size()},
    {"materials",G4Material::GetMaterialTable()->size()},
    {"unique_daughter_edges",edges},{"max_daughters",maxDaughters},
    {"world_daughters",world->GetLogicalVolume()->GetNoDaughters()},
    {"expanded_nodes_including_world",gnodes},{"max_depth",gdepth},
    {"large_mothers",heavy},{"shapes",shapes}};
  result["geant4"]["world_material"]=world->GetLogicalVolume()->GetMaterial()->GetName();
  result["geant4"]["regions"]=json::array();
  for (auto* r : *G4RegionStore::GetInstance()) {
    result["geant4"]["regions"].push_back({{"name",r->GetName()},
      {"materials",r->GetNumberOfMaterials()},{"root_volumes",r->GetNumberOfRootVolumes()}});
  }
  result["geant4"]["material_cut_couples"]=G4ProductionCutsTable::GetProductionCutsTable()->GetTableSize();
  return result.dump(2);
}
