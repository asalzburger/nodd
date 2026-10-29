// Isolated DES040 prototype. Delegate all material mixing to pinned ActsCore.
#include "Acts/Material/Material.hpp"
#include "Acts/Material/MaterialSlab.hpp"
#include "Acts/Definitions/Units.hpp"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <cmath>
#include <vector>
namespace py=pybind11;
static_assert(PYBIND11_INTERNALS_VERSION==11);
Acts::MaterialSlab readSlab(const py::dict& input) {
  Acts::Material material=Acts::Material::Vacuum();
  if(!input["material"].is_none()) {
    const auto parameters=py::cast<std::vector<float>>(input["material"]);
    if(parameters.size()!=5) throw std::invalid_argument("Expected pinned ACTS five opaque material parameters");
    Acts::Material::ParametersVector values;
    for(int i=0;i<5;++i)values[i]=parameters[i];
    material=Acts::Material(values);
  }
  const auto thickness=py::cast<float>(input["thickness"]);
  if(!std::isfinite(thickness)||thickness<0)throw std::invalid_argument("Invalid slab thickness");
  return Acts::MaterialSlab(material,thickness);
}
py::dict encode(const Acts::MaterialSlab& slab) {
  py::dict result;
  if(slab.material().isVacuum())result["material"]=py::none();
  else { const auto v=slab.material().parameters();std::vector<float> p(v.data(),v.data()+v.size());result["material"]=p; }
  result["thickness"]=slab.thickness();return result;
}
PYBIND11_MODULE(nodd_tracker_material,m) {
  m.def("homogenize",[](const py::list& inputs,const std::vector<double>& weights) {
    if(inputs.size()!=weights.size()||inputs.empty())throw std::invalid_argument("Missing slabs/area weights");
    double total=0;for(auto w:weights){if(!std::isfinite(w)||w<0)throw std::invalid_argument("Invalid area weight");total+=w;}
    if(total<=0)throw std::invalid_argument("Zero total area");
    std::vector<Acts::MaterialSlab> slabs;std::size_t i=0;
    for(auto input:inputs){auto slab=readSlab(py::cast<py::dict>(input));slab.scaleThickness(weights[i++]/total);slabs.push_back(slab);}
    return encode(Acts::MaterialSlab::combineLayers(slabs));
  });
  m.def("budget",[](const py::dict& input){auto slab=readSlab(input);py::dict b;b["X0"]=slab.thicknessInX0();b["L0"]=slab.thicknessInL0();b["areal_mass_g_mm2"]=slab.material().massDensity()*slab.thickness()/Acts::UnitConstants::g;return b;});
  m.attr("pybind11_version")="3.0.4";
}
