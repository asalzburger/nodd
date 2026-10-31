// DES042 observation only: no propagation, queue or random-state changes.
#pragma once
#include <nlohmann/json.hpp>
#include <map>
#include <mutex>
#include <stdexcept>
#include <string>
namespace nodd::ttbar_safe_fatras {
using Json=nlohmann::json;
struct FailureStore { std::mutex mutex;std::map<std::size_t,Json> events; };
inline FailureStore& failureStore() { static FailureStore value;return value; }
inline void resetFailureAudit() {auto& s=failureStore();std::lock_guard lock(s.mutex);s.events.clear();}
inline Json particleFailureState(const auto& p) {
  auto vector=[](const auto& v){auto j=Json::array();for(int i=0;i<v.size();++i)j.push_back(v[i]);return j;};
  return {{"id",p.particleId().asArray()},{"parent_id",p.parentParticleId().asArray()},
    {"pdg",static_cast<int>(p.pdg())},{"mass_GeV",p.mass()},{"charge",p.charge()},
    {"position4",vector(p.fourPosition())},{"direction",vector(p.direction())},{"p_GeV",p.absoluteMomentum()},
    {"proper_time",p.properTime()},{"path_X0",p.pathInX0()},{"path_L0",p.pathInL0()},
    {"n_hits",p.numberOfHits()},{"process",static_cast<int>(p.process())},{"outcome",static_cast<int>(p.outcome())},
    {"orig_particle_idx",p.origParticleIdx()},
    {"reference_geometry_id",p.hasReferenceSurface() ? Json(p.referenceSurface()->geometryId().value()):Json()}};
}
inline void recordFailures(std::size_t event,const auto& failures) {
  auto data=Json::array();for(const auto& f:failures)data.push_back({{"initial_state",particleFailureState(f.particle)},
      {"error_value",f.error.value()},{"error_category",f.error.category().name()},{"error_message",f.error.message()}});
  auto& s=failureStore();std::lock_guard lock(s.mutex);
  if(!s.events.emplace(event,Json{{"event",event},{"failures",data}}).second)
    throw std::runtime_error("Duplicate Fatras event in observational failure audit");
}
inline std::string failureAuditJson() {
  auto& s=failureStore();std::lock_guard lock(s.mutex);auto events=Json::array();
  for(const auto& [event,data]:s.events)events.push_back(data);
  return Json{{"schema_version",1},{"scope","Copy-before-erase initial particle states; diagnostic only"},{"events",events}}.dump();
}
}
