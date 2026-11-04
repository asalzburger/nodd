// DES042 isolated PROTOTYPE. Only unsuccessful upstream Pythia next() calls abort.
#include "PythiaGenerationGuard.hpp"
#include "PythiaGuardProvenance.hpp"
#include "ActsExamples/Generators/Pythia8ProcessGenerator.hpp"
#include <HepMC3/GenEvent.h>
#include <HepMC3/GenParticle.h>
#include <HepMC3/GenVertex.h>
#include <HepMC3/Attribute.h>
#include <Pythia8/Pythia.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
namespace py=pybind11;
using namespace ActsExamples;
static_assert(PYBIND11_INTERNALS_VERSION==NODD_EXPECTED_PYBIND11_INTERNALS_VERSION);
void bindPileupAudit(py::module_&);
class TaggedPythia final: public ParticlesGenerator {
 public:
  TaggedPythia(bool hard,Acts::Logging::Level level):isHard(hard),generator(configuration(hard),level) {}
  static Pythia8Generator::Config configuration(bool hard) {
    Pythia8Generator::Config c;
    c.pdgBeam0=Acts::PdgParticle::eProton;c.pdgBeam1=Acts::PdgParticle::eProton;
    c.cmsEnergy=14*Acts::UnitConstants::TeV;
    c.settings={hard ? "Top:qqbar2ttbar=on" : "SoftQCD:all=on"};
    c.initializationSeed=42;c.printShortEventListing=false;c.printLongEventListing=false;
    return c;
  }
  std::shared_ptr<HepMC3::GenEvent> operator()(RandomEngine& rng) override {
    auto event=generator(rng);
    const int index=isHard ? 0 : 1+static_cast<int>(calls%200);
    ++calls;
    for(const auto& p:event->particles()) p->add_attribute("nodd_interaction",std::make_shared<HepMC3::IntAttribute>(index));
    for(const auto& v:event->vertices()) v->add_attribute("nodd_interaction",std::make_shared<HepMC3::IntAttribute>(index));
    return event;
  }
 private: bool isHard;std::size_t calls=0;Pythia8Generator generator;
};
PYBIND11_MODULE(nodd_strixel_pileup,m) {
  m.def("generator",[](bool hard,Acts::Logging::Level level)->std::shared_ptr<ParticlesGenerator>{return std::make_shared<TaggedPythia>(hard,level);});
  m.def("_check_generation_success", &noddRequirePythiaSuccess);
  m.attr("pythia_original_source_sha256")=NODD_PYTHIA_ORIGINAL_SHA;
  m.attr("pythia_generated_source_sha256")=NODD_PYTHIA_GENERATED_SHA;
  m.attr("pythia_guard_header_sha256")=NODD_PYTHIA_GUARD_SHA;
  m.attr("pythia_generation_success_policy")="Every next() must return true; false aborts the whole event, without retry, filtering or resampling";
  m.attr("pythia_version")=PYTHIA_VERSION;
  m.attr("pythia_version_integer")=PYTHIA_VERSION_INTEGER;
  m.attr("acts_source_revision")="355ea68493b326956756c9386d2fd9eaf9328568";
  m.attr("upstream_pythia_fpe_scope")="Pinned upstream Pythia8Generator temporarily disables FPE monitoring inside Pythia next(); Fatras and reconstruction monitors remain intact";
  bindPileupAudit(m);
}
