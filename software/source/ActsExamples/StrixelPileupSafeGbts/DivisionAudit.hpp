// DES042 observational diagnostics only. No FPE masks or numerical guard.
#pragma once
#include <nlohmann/json.hpp>
#include <bit>
#include <cmath>
#include <cstdint>
#include <string>

namespace nodd::gbts {
using Json=nlohmann::json;
inline thread_local std::size_t currentEvent=0, updateNumber=0;
inline Json& records() {static thread_local Json value=Json::array();return value;}
inline void resetAudit(std::size_t event) {currentEvent=event;updateNumber=0;records()=Json::array();}
inline void nextUpdate() {++updateNumber;}
inline Json bits(float x) {return std::bit_cast<std::uint32_t>(x);}
template<class T> Json bits(const T& xs) {Json j=Json::array();for(const auto& x:xs) j.push_back(bits(x));return j;}
template<class State,class Node> bool observe(const char* name,float denominator,
    const State& ts,const Node& n1,const Node& n2) {
  if(denominator!=0 && std::isfinite(denominator) && denominator>0) return false;
  Json chain=Json::array();for(const auto* edge:ts.vs) chain.push_back({{"n1",edge->n1},{"n2",edge->n2},{"level",edge->level}});
  auto node=[](const Node& n) {return Json{{"index",n.index()},{"layer",n.layer()},{"xyzr_bits",{bits(n.x()),bits(n.y()),bits(n.z()),bits(n.r())}}};};
  records().push_back({{"event",currentEvent},{"update",updateNumber},{"division",name},
    {"denominator_bits",bits(denominator)},{"n1",node(n1)},{"n2",node(n2)},
    {"state_x_bits",bits(ts.x)},{"state_y_bits",bits(ts.y)},
    {"cov_x_bits",bits(ts.cx)},{"cov_y_bits",bits(ts.cy)},
    {"ref_bits",{bits(ts.refX),bits(ts.refY),bits(ts.c),bits(ts.s)}},
    {"score_bits",bits(ts.j)},{"chain",chain}});
  return true;
}
inline std::string auditJson() {return records().dump();}
}
