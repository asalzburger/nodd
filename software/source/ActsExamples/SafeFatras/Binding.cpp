// DES041 isolated PROTOTYPE; no upstream symbol interposition or FPE masks.
#include "ActsExamples/Fatras/NoddSafeFatrasSimulation.hpp"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <cfenv>
#include <stdexcept>

#include "SafeFatrasProvenance.hpp"

namespace py = pybind11;
using ActsExamples::NoddSafeFatrasSimulation;
static_assert(PYBIND11_INTERNALS_VERSION == NODD_EXPECTED_PYBIND11_INTERNALS_VERSION);

PYBIND11_MODULE(nodd_safe_fatras, module) {
  py::class_<NoddSafeFatrasSimulation, ActsExamples::IAlgorithm,
             std::shared_ptr<NoddSafeFatrasSimulation>>(module, "SafeFatrasSimulation");
  module.attr("source_revision") = "355ea68493b326956756c9386d2fd9eaf9328568";
  module.attr("upstream_sha256") = upstreamHashes();
  module.attr("generated_header_sha256") = NODD_GENERATED_HEADER_SHA256;
  module.attr("generated_source_sha256") = NODD_GENERATED_SOURCE_SHA256;
  module.attr("pybind11_version") = "3.0.4";
  module.attr("pybind11_internals_version") = PYBIND11_INTERNALS_VERSION;
  module.attr("native_compile_flags") = nativeCompileFlags();
  module.attr("native_compile_defines") = nativeCompileDefines();
  module.attr("native_flag_block_sha256") = nativeFlagBlockHash();
  module.def("schedule", [](py::object sequence,
      std::shared_ptr<const Acts::TrackingGeometry> geometry,
      std::shared_ptr<const Acts::MagneticFieldProvider> field,
      std::shared_ptr<const ActsExamples::RandomNumbers> random,
      Acts::Logging::Level level) {
    if (std::fegetround() != FE_TONEAREST) {
      throw std::runtime_error("SafeFatras requires native round-to-nearest; rounding mode was not changed");
    }
    NoddSafeFatrasSimulation::Config config;
    config.inputParticles = "particles_generated";
    config.outputParticles = "particles_simulated";
    config.outputSimHits = "simhits";
    config.trackingGeometry = std::move(geometry);
    config.magneticField = std::move(field);
    config.randomNumbers = std::move(random);
    auto algorithm = std::make_shared<NoddSafeFatrasSimulation>(config,
        Acts::getDefaultLogger("FatrasSimulation", level));
    sequence.attr("addAlgorithm")(algorithm);
    sequence.attr("addWhiteboardAlias")("particles", "particles_simulated");
    sequence.attr("addWhiteboardAlias")("particles_simulated_selected", "particles_simulated");
    py::dict effective;
    effective["algorithm_name"] = "FatrasSimulation";
    effective["cpp_type"] = "ActsExamples::NoddSafeFatrasSimulation";
    effective["inputParticles"] = config.inputParticles;
    effective["outputParticles"] = config.outputParticles;
    effective["outputSimHits"] = config.outputSimHits;
    effective["pMin_GeV"] = config.pMin / Acts::UnitConstants::GeV;
    effective["emScattering"] = config.emScattering;
    effective["emEnergyLossIonisation"] = config.emEnergyLossIonisation;
    effective["emEnergyLossRadiation"] = config.emEnergyLossRadiation;
    effective["emPhotonConversion"] = config.emPhotonConversion;
    effective["generateHitsOnSensitive"] = config.generateHitsOnSensitive;
    effective["generateHitsOnMaterial"] = config.generateHitsOnMaterial;
    effective["generateHitsOnPassive"] = config.generateHitsOnPassive;
    effective["maxStepSize_mm"] = config.maxStepSize / Acts::UnitConstants::mm;
    effective["pathLimit_mm"] = config.pathLimit / Acts::UnitConstants::mm;
    effective["averageHitsPerParticle"] = config.averageHitsPerParticle;
    effective["bethe_heitler_guard"] = "0 <= u < 2^-54: +0; u > 40: -1; otherwise original exp(-u)-1";
    effective["native_compile_flags"] = nativeCompileFlags();
    effective["native_compile_defines"] = nativeCompileDefines();
    effective["native_flag_block_sha256"] = nativeFlagBlockHash();
    effective["rng_draws"] = "Unchanged gamma draw and four angular draws in original expression order";
    effective["fpe_monitoring"] = "Unchanged; no mask or exception-control modification";
    return effective;
  }, py::arg("seq"), py::arg("geometry"), py::arg("field"), py::arg("rnd"), py::arg("level"));
}
