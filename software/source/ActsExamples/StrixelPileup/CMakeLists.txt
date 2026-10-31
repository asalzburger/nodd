cmake_minimum_required(VERSION 3.24)
project(NoddStrixelPileup LANGUAGES CXX)
set(NODD_ACTS_SOURCE "" CACHE PATH "Matching installed ACTS source")
set(NODD_ACTS_BUILD "" CACHE PATH "Existing read-only ACTS build")
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 3.0.4 EXACT CONFIG REQUIRED)
find_package(Git REQUIRED)
execute_process(COMMAND "${GIT_EXECUTABLE}" -C "${NODD_ACTS_SOURCE}" rev-parse HEAD
  OUTPUT_VARIABLE NODD_ACTS_REVISION OUTPUT_STRIP_TRAILING_WHITESPACE COMMAND_ERROR_IS_FATAL ANY)
if(NOT NODD_ACTS_REVISION STREQUAL "355ea68493b326956756c9386d2fd9eaf9328568")
  message(FATAL_ERROR "Pileup sidecar requires ACTS355ea source matching runtime")
endif()
find_package(Eigen3 CONFIG REQUIRED)
find_package(Boost CONFIG REQUIRED)
find_package(nlohmann_json CONFIG REQUIRED)
find_package(HepMC3 CONFIG REQUIRED)
find_package(ZLIB REQUIRED)
find_path(PYTHIA8_INCLUDE_DIR Pythia8/Pythia.h REQUIRED)
find_library(PYTHIA8_LIBRARY pythia8 REQUIRED)
find_library(ACTS_CORE ActsCore PATHS "${NODD_ACTS_BUILD}/lib" NO_DEFAULT_PATH REQUIRED)
find_library(ACTS_FRAMEWORK ActsExamplesFramework PATHS "${NODD_ACTS_BUILD}/lib" NO_DEFAULT_PATH REQUIRED)
find_library(ACTS_FPE ActsPluginFpeMonitoring PATHS "${NODD_ACTS_BUILD}/lib" NO_DEFAULT_PATH REQUIRED)
# Fail a whole event on an unsuccessful subevent, without retrying or consuming
# another draw. The shared ACTS checkout remains untouched.
set(NODD_PYTHIA_ORIGINAL "${NODD_ACTS_SOURCE}/Examples/Algorithms/GeneratorsPythia8/ActsExamples/Generators/Pythia8ProcessGenerator.cpp")
file(SHA256 "${NODD_PYTHIA_ORIGINAL}" NODD_PYTHIA_ORIGINAL_SHA)
if(NOT NODD_PYTHIA_ORIGINAL_SHA STREQUAL "9604bce7ab12e252d712470982148b8ddb1fade5998262f53c92023855798c51")
  message(FATAL_ERROR "Pythia generator source differs from the reviewed ACTS355ea input")
endif()
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${NODD_PYTHIA_ORIGINAL}")
file(READ "${NODD_PYTHIA_ORIGINAL}" NODD_PYTHIA_SOURCE)
set(NODD_PYTHIA_OLD "m_pythia8->next();")
set(NODD_PYTHIA_NEW "noddRequirePythiaSuccess(m_pythia8->next());")
string(REPLACE "${NODD_PYTHIA_OLD}" "${NODD_PYTHIA_NEW}" NODD_PYTHIA_PATCHED "${NODD_PYTHIA_SOURCE}")
if(NODD_PYTHIA_PATCHED STREQUAL NODD_PYTHIA_SOURCE)
  message(FATAL_ERROR "Expected unchecked Pythia next() call is absent")
endif()
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/PythiaGenerationGuard.hpp" [=[
#pragma once
#include <stdexcept>
namespace ActsExamples {
inline void noddRequirePythiaSuccess(bool success) {
  if (!success) throw std::runtime_error("Pythia8 next() failed; whole event aborted without retry or resampling");
}
}
]=])
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/GuardedPythia8ProcessGenerator.cpp"
  "#include \"PythiaGenerationGuard.hpp\"\n${NODD_PYTHIA_PATCHED}")
file(SHA256 "${CMAKE_CURRENT_BINARY_DIR}/PythiaGenerationGuard.hpp" NODD_PYTHIA_GUARD_SHA)
file(SHA256 "${CMAKE_CURRENT_BINARY_DIR}/GuardedPythia8ProcessGenerator.cpp" NODD_PYTHIA_GENERATED_SHA)
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/PythiaGuardProvenance.hpp"
  "#pragma once\n#define NODD_PYTHIA_ORIGINAL_SHA \"${NODD_PYTHIA_ORIGINAL_SHA}\"\n#define NODD_PYTHIA_GENERATED_SHA \"${NODD_PYTHIA_GENERATED_SHA}\"\n#define NODD_PYTHIA_GUARD_SHA \"${NODD_PYTHIA_GUARD_SHA}\"\n")
pybind11_add_module(nodd_strixel_pileup PythiaBinding.cpp PileupAudit.cpp
  "${CMAKE_CURRENT_BINARY_DIR}/GuardedPythia8ProcessGenerator.cpp")
target_include_directories(nodd_strixel_pileup PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")
target_compile_features(nodd_strixel_pileup PRIVATE cxx_std_20)
# Exact headers must precede the dependency view, which also exposes newer pybind11.
target_include_directories(nodd_strixel_pileup BEFORE PRIVATE ${pybind11_INCLUDE_DIRS})
target_compile_definitions(nodd_strixel_pileup PRIVATE NODD_EXPECTED_PYBIND11_INTERNALS_VERSION=11)
target_include_directories(nodd_strixel_pileup PRIVATE "${NODD_ACTS_SOURCE}/Core/include"
  "${NODD_ACTS_SOURCE}/Fatras/include" "${NODD_ACTS_SOURCE}/Examples/Framework/include"
  "${NODD_ACTS_SOURCE}/Plugins/FpeMonitoring/include" "${NODD_ACTS_BUILD}/Core/include"
  "${NODD_ACTS_SOURCE}/Examples/Algorithms/GeneratorsPythia8" "${PYTHIA8_INCLUDE_DIR}")
target_link_libraries(nodd_strixel_pileup PRIVATE "${ACTS_CORE}" "${ACTS_FRAMEWORK}" "${ACTS_FPE}"
  Eigen3::Eigen Boost::headers nlohmann_json::nlohmann_json HepMC3::HepMC3 ZLIB::ZLIB "${PYTHIA8_LIBRARY}")
set_target_properties(nodd_strixel_pileup PROPERTIES CXX_VISIBILITY_PRESET default
  VISIBILITY_INLINES_HIDDEN OFF BUILD_RPATH "${NODD_ACTS_BUILD}/lib")
