cmake_minimum_required(VERSION 3.24)
project(NoddTtbarSafeFatras LANGUAGES CXX)
set(NODD_ACTS_SOURCE "" CACHE PATH "Read-only ACTS355ea684 source matching native runtime")
set(NODD_ACTS_BUILD "" CACHE PATH "Read-only existing ACTS build")

# Reuse the actual native Fatras object's numerical flags/macros. The prior
# O0/LTO sidecar was not compiler-equivalent to the native O2/NDEBUG object.
file(READ "${NODD_ACTS_BUILD}/build.ninja" NODD_NATIVE_NINJA)
set(NODD_NATIVE_OBJECT "build Examples/Algorithms/Fatras/CMakeFiles/ActsExamplesFatras.dir/src/FatrasSimulation.cpp.o:")
string(FIND "${NODD_NATIVE_NINJA}" "${NODD_NATIVE_OBJECT}" NODD_NATIVE_START)
if(NODD_NATIVE_START EQUAL -1)
  message(FATAL_ERROR "Pinned native Fatras object flags not found in read-only build.ninja")
endif()
string(SUBSTRING "${NODD_NATIVE_NINJA}" ${NODD_NATIVE_START} -1 NODD_NATIVE_TAIL)
string(FIND "${NODD_NATIVE_TAIL}" "\n\n" NODD_NATIVE_END)
string(SUBSTRING "${NODD_NATIVE_TAIL}" 0 ${NODD_NATIVE_END} NODD_NATIVE_BLOCK)
string(REGEX MATCH "  FLAGS = ([^\n]+)" NODD_NATIVE_MATCH "${NODD_NATIVE_BLOCK}")
set(NODD_NATIVE_FLAGS "${CMAKE_MATCH_1}")
if(NOT NODD_NATIVE_FLAGS MATCHES "-O2 -g -DNDEBUG -std=gnu\\+\\+20 -fPIC -D_GNU_SOURCE"
   OR NODD_NATIVE_FLAGS MATCHES "fast-math|Ofast|flto")
  message(FATAL_ERROR "Unexpected native Fatras numerical flags: ${NODD_NATIVE_FLAGS}")
endif()
string(REGEX MATCH "  DEFINES = ([^\n]+)" NODD_NATIVE_MATCH "${NODD_NATIVE_BLOCK}")
set(NODD_NATIVE_DEFINES "${CMAKE_MATCH_1}")
if(NOT NODD_NATIVE_DEFINES STREQUAL "-DActsExamplesFatras_EXPORTS -DROOT_CORE_THREAD_TBB")
  message(FATAL_ERROR "Unexpected native Fatras macros: ${NODD_NATIVE_DEFINES}")
endif()
separate_arguments(NODD_NATIVE_COMPILE_FLAGS NATIVE_COMMAND "${NODD_NATIVE_FLAGS} ${NODD_NATIVE_DEFINES}")
string(SHA256 NODD_NATIVE_BLOCK_HASH "${NODD_NATIVE_BLOCK}")
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${NODD_ACTS_BUILD}/build.ninja")
file(STRINGS "${NODD_ACTS_BUILD}/CMakeCache.txt" NODD_NATIVE_COMPILER_LINE REGEX "^CMAKE_CXX_COMPILER:FILEPATH=")
string(REPLACE "CMAKE_CXX_COMPILER:FILEPATH=" "" NODD_NATIVE_COMPILER "${NODD_NATIVE_COMPILER_LINE}")
file(REAL_PATH "${NODD_NATIVE_COMPILER}" NODD_NATIVE_COMPILER_REAL)
file(REAL_PATH "${CMAKE_CXX_COMPILER}" NODD_COMPILER_REAL)
if(NOT NODD_NATIVE_COMPILER_REAL STREQUAL NODD_COMPILER_REAL)
  message(FATAL_ERROR "Sidecar compiler differs from native Fatras: ${CMAKE_CXX_COMPILER} versus ${NODD_NATIVE_COMPILER}")
endif()
find_package(Git REQUIRED)
execute_process(COMMAND "${GIT_EXECUTABLE}" -C "${NODD_ACTS_SOURCE}" rev-parse HEAD
  OUTPUT_VARIABLE NODD_ACTS_REVISION OUTPUT_STRIP_TRAILING_WHITESPACE COMMAND_ERROR_IS_FATAL ANY)
if(NOT NODD_ACTS_REVISION STREQUAL "355ea68493b326956756c9386d2fd9eaf9328568")
  message(FATAL_ERROR "SafeFatras requires ACTS355ea684 matching native runtime; got ${NODD_ACTS_REVISION}")
endif()

set(NODD_INPUT_NAMES
  "Examples/Algorithms/Fatras/include/ActsExamples/Fatras/FatrasSimulation.hpp"
  "Examples/Algorithms/Fatras/src/FatrasSimulation.cpp"
  "Fatras/include/ActsFatras/Physics/ElectroMagnetic/BetheHeitler.hpp"
  "Fatras/include/ActsFatras/Physics/StandardInteractions.hpp"
  "Fatras/src/Physics/StandardInteractions.cpp"
  "Fatras/include/ActsFatras/Utilities/detail/FpeSafeGammaDistribution.hpp"
  "Fatras/include/ActsFatras/Kernel/MultiParticleSimulation.hpp")
set(NODD_INPUT_HASHES
  "60f0570c07b45c9a3ccfc608f7dc2aa612396b851ca895eb361011af2968ba20"
  "7ec2143f967e208d43c26027dc0717deab31f0d9285326a94bcce580370ce758"
  "2b986671cb9537934274c599c47d7e446fb2d8ab22e7fe3b3d732e1c473b692c"
  "220cd2777c63277a1e143074d6c3f9f227f1f7f9563f38ff7cde3fd15be7ca0b"
  "f5706e741d1ea94a8a202d9138fb0d65c50e5fe81603d6c8621691312349a49a"
  "941667d6842089f64decc5b3151cde36f965732abe660113eaa5277e91ad2d12"
  "165dc2fba855ab80b0f16143b391b74110acf8871dd3a887894edf98cda8d2e6")
set(NODD_PROVENANCE "")
foreach(index RANGE 0 6)
  list(GET NODD_INPUT_NAMES ${index} name)
  list(GET NODD_INPUT_HASHES ${index} expected)
  file(SHA256 "${NODD_ACTS_SOURCE}/${name}" observed)
  if(NOT observed STREQUAL expected)
    message(FATAL_ERROR "SafeFatras upstream input changed: ${name}; expected ${expected}, got ${observed}")
  endif()
  string(APPEND NODD_PROVENANCE "  hashes[\"${name}\"] = \"${observed}\";\n")
  set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${NODD_ACTS_SOURCE}/${name}")
endforeach()

# The complete upstream algorithm stays in the task-owned build directory.
# Every changed anchor must occur exactly once in the pinned source.
function(replace_once variable before after)
  string(FIND "${${variable}}" "${before}" first)
  if(first EQUAL -1)
    message(FATAL_ERROR "SafeFatras source anchor absent: ${before}")
  endif()
  string(LENGTH "${before}" length)
  math(EXPR next "${first}+${length}")
  string(SUBSTRING "${${variable}}" ${next} -1 rest)
  string(FIND "${rest}" "${before}" duplicate)
  if(NOT duplicate EQUAL -1)
    message(FATAL_ERROR "SafeFatras source anchor duplicated: ${before}")
  endif()
  string(REPLACE "${before}" "${after}" changed "${${variable}}")
  set(${variable} "${changed}" PARENT_SCOPE)
endfunction()
# Generate distinct utility/template types; never shadow upstream include paths.
file(READ "${NODD_ACTS_SOURCE}/Fatras/include/ActsFatras/Utilities/detail/FpeSafeGammaDistribution.hpp" gamma)
string(REPLACE "namespace ActsFatras::detail" "namespace nodd::ttbar_safe_fatras" gamma "${gamma}")
string(REPLACE "FpeSafeGammaDistribution" "ZeroObservableGammaDistribution" gamma "${gamma}")
set(gamma_terminal [=[    // Check if this would cause underflow
    const double invAlpha = 1. / params.alpha;
    if (std::log(u2) * invAlpha + std::log(uPlus1) <
        std::log(std::numeric_limits<double>::min())) {
      // This would be underflow - get 0.0 right away
      return 0.;
    } else {
      return uPlus1 * std::pow(u2, invAlpha);
    }
]=])
replace_once(gamma "${gamma_terminal}" [=[    const double invAlpha = 1. / params.alpha;
    return finishSample(uPlus1, u2, invAlpha);
]=])
replace_once(gamma "  /// Provide standard comparison operators" [=[  // Bethe-Heitler-only observable guard, after ALL original random draws.
  // For valid finite inputs, uPlus1<=2^256 and logPow<-512 bounds the
  // gamma product far below 2^-54. The original rounded energy loss is +0.
  // The internal gamma value may change; no other gamma consumer uses this type.
  static double finishSample(double uPlus1, double u2, double invAlpha) {
    if (std::isfinite(uPlus1) && uPlus1 >= 0. && uPlus1 <= 0x1p256 &&
        std::isfinite(invAlpha) && std::log(u2) * invAlpha < -512.) return 0.;
    // Original arithmetic and expression order outside the proven-zero region.
    if (std::log(u2) * invAlpha + std::log(uPlus1) <
        std::log(std::numeric_limits<double>::min())) return 0.;
    return uPlus1 * std::pow(u2, invAlpha);
  }

  /// Provide standard comparison operators]=])
file(READ "${NODD_ACTS_SOURCE}/Fatras/include/ActsFatras/Kernel/MultiParticleSimulation.hpp" multi)
string(REPLACE "MultiParticleSimulation" "TtbarMultiParticleSimulation" multi "${multi}")
string(REPLACE "FailedParticle" "TtbarFailedParticle" multi "${multi}")
replace_once(multi "        if (!result.ok()) {"
  "        if (!result.ok()) {\n          const auto failedParticleCopy = initialParticle;")
replace_once(multi "failedParticles.push_back({initialParticle, result.error()});"
  "failedParticles.push_back({failedParticleCopy, result.error()});")
file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/generated/nodd/ttbar_safe_fatras")
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/generated/nodd/ttbar_safe_fatras/ZeroObservableGammaDistribution.hpp" "${gamma}")
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/generated/nodd/ttbar_safe_fatras/TtbarMultiParticleSimulation.hpp" "${multi}")
file(READ "${NODD_ACTS_SOURCE}/Examples/Algorithms/Fatras/include/ActsExamples/Fatras/FatrasSimulation.hpp" header)
file(READ "${NODD_ACTS_SOURCE}/Examples/Algorithms/Fatras/src/FatrasSimulation.cpp" source)
replace_once(source "#include \"ActsFatras/Physics/StandardInteractions.hpp\""
  "#include \"ActsFatras/Physics/StandardInteractions.hpp\"\n#include \"TtbarSafeBetheHeitler.hpp\"")
replace_once(source "ActsFatras::StandardChargedElectroMagneticInteractions"
  "nodd::ttbar_safe_fatras::ChargedInteractions")
replace_once(source "makeStandardChargedElectroMagneticInteractions(cfg.pMin)"
  "nodd::ttbar_safe_fatras::makeChargedInteractions(cfg.pMin)")
replace_once(source "disable<StandardBetheHeitler>()"
  "disable<nodd::ttbar_safe_fatras::StandardBetheHeitler>()")
replace_once(source "#include \"ActsFatras/Kernel/MultiParticleSimulation.hpp\""
  "#include \"nodd/ttbar_safe_fatras/TtbarMultiParticleSimulation.hpp\"\n#include \"FailureAudit.hpp\"")
replace_once(source "ActsFatras::MultiParticleSimulation<" "ActsFatras::TtbarMultiParticleSimulation<")
replace_once(source "ActsFatras::FailedParticle" "ActsFatras::TtbarFailedParticle")
replace_once(source "  // failed particles are just logged. assumes that failed particles are due"
  "  nodd::ttbar_safe_fatras::recordFailures(ctx.eventNumber, ret.value());\n  // failed particles are just logged. assumes that failed particles are due")
string(REPLACE "FatrasSimulation" "NoddTtbarSafeFatrasSimulation" header "${header}")
string(REPLACE "FatrasSimulation" "NoddTtbarSafeFatrasSimulation" source "${source}")
replace_once(source "IAlgorithm(\"NoddTtbarSafeFatrasSimulation\""
  "IAlgorithm(\"FatrasSimulation\"")
file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/generated/ActsExamples/Fatras")
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/generated/ActsExamples/Fatras/NoddTtbarSafeFatrasSimulation.hpp" "${header}")
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/generated/NoddTtbarSafeFatrasSimulation.cpp" "${source}")
file(SHA256 "${CMAKE_CURRENT_BINARY_DIR}/generated/ActsExamples/Fatras/NoddTtbarSafeFatrasSimulation.hpp" NODD_GENERATED_HEADER_HASH)
file(SHA256 "${CMAKE_CURRENT_BINARY_DIR}/generated/NoddTtbarSafeFatrasSimulation.cpp" NODD_GENERATED_SOURCE_HASH)
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/generated/SafeFatrasProvenance.hpp"
  "// Generated from hash-checked ACTS inputs; not a shared source edit.\ninline pybind11::dict upstreamHashes() {\n  pybind11::dict hashes;\n${NODD_PROVENANCE}  return hashes;\n}\ninline const char* nativeCompileFlags() { return R\"nodd(${NODD_NATIVE_FLAGS})nodd\"; }\ninline const char* nativeCompileDefines() { return R\"nodd(${NODD_NATIVE_DEFINES})nodd\"; }\ninline const char* nativeFlagBlockHash() { return \"${NODD_NATIVE_BLOCK_HASH}\"; }\n")

set(NODD_GENERATED_PROVENANCE "")
foreach(name IN ITEMS "ActsExamples/Fatras/NoddTtbarSafeFatrasSimulation.hpp" "NoddTtbarSafeFatrasSimulation.cpp"
    "nodd/ttbar_safe_fatras/ZeroObservableGammaDistribution.hpp" "nodd/ttbar_safe_fatras/TtbarMultiParticleSimulation.hpp")
  file(SHA256 "${CMAKE_CURRENT_BINARY_DIR}/generated/${name}" digest)
  string(APPEND NODD_GENERATED_PROVENANCE "  hashes[\"${name}\"] = \"${digest}\";\n")
endforeach()
file(APPEND "${CMAKE_CURRENT_BINARY_DIR}/generated/SafeFatrasProvenance.hpp"
  "inline pybind11::dict generatedHashes() { pybind11::dict hashes;\n${NODD_GENERATED_PROVENANCE}return hashes; }\n")
# Bind the actual local inputs into the compiled module as well as the runtime
# inventory. This rejects a stale module after any local source/header edit.
set(NODD_LOCAL_PROVENANCE "")
foreach(name IN ITEMS CMakeLists.txt Binding.cpp TtbarSafeBetheHeitler.hpp FailureAudit.hpp test_energy_loss.cpp test_failure_identity.cpp)
  file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/${name}" digest)
  string(APPEND NODD_LOCAL_PROVENANCE "  hashes[\"${name}\"] = \"${digest}\";\n")
  set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/${name}")
endforeach()
file(APPEND "${CMAKE_CURRENT_BINARY_DIR}/generated/SafeFatrasProvenance.hpp"
  "inline pybind11::dict localSourceHashes() { pybind11::dict hashes;\n${NODD_LOCAL_PROVENANCE}return hashes; }\n")
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 3.0.4 EXACT CONFIG REQUIRED)
find_package(Eigen3 CONFIG REQUIRED)
find_package(Boost CONFIG REQUIRED)
find_package(nlohmann_json CONFIG REQUIRED)
foreach(component Core Fatras ExamplesFramework PluginFpeMonitoring)
  find_library(ACTS_${component} Acts${component} PATHS "${NODD_ACTS_BUILD}/lib" NO_DEFAULT_PATH REQUIRED)
endforeach()
set(NODD_INCLUDE_PATHS "${CMAKE_CURRENT_SOURCE_DIR}" "${CMAKE_CURRENT_BINARY_DIR}/generated"
  "${NODD_ACTS_SOURCE}/Core/include" "${NODD_ACTS_BUILD}/Core/include"
  "${NODD_ACTS_SOURCE}/Fatras/include" "${NODD_ACTS_SOURCE}/Examples/Framework/include"
  "${NODD_ACTS_SOURCE}/Plugins/FpeMonitoring/include")
pybind11_add_module(nodd_ttbar_safe_fatras NO_EXTRAS Binding.cpp "${CMAKE_CURRENT_BINARY_DIR}/generated/NoddTtbarSafeFatrasSimulation.cpp")
target_compile_features(nodd_ttbar_safe_fatras PRIVATE cxx_std_20)
target_include_directories(nodd_ttbar_safe_fatras BEFORE PRIVATE ${pybind11_INCLUDE_DIRS})
target_compile_options(nodd_ttbar_safe_fatras PRIVATE ${NODD_NATIVE_COMPILE_FLAGS})
target_compile_definitions(nodd_ttbar_safe_fatras PRIVATE NODD_EXPECTED_PYBIND11_INTERNALS_VERSION=11
  NODD_GENERATED_HEADER_SHA256="${NODD_GENERATED_HEADER_HASH}"
  NODD_GENERATED_SOURCE_SHA256="${NODD_GENERATED_SOURCE_HASH}")
target_include_directories(nodd_ttbar_safe_fatras PRIVATE ${NODD_INCLUDE_PATHS})
target_link_libraries(nodd_ttbar_safe_fatras PRIVATE "${ACTS_Core}" "${ACTS_Fatras}" "${ACTS_ExamplesFramework}"
  Eigen3::Eigen Boost::headers nlohmann_json::nlohmann_json)
set_target_properties(nodd_ttbar_safe_fatras PROPERTIES CXX_VISIBILITY_PRESET hidden
  VISIBILITY_INLINES_HIDDEN ON BUILD_RPATH "${NODD_ACTS_BUILD}/lib")

enable_testing()
foreach(test_target test_ttbar_energy_loss test_ttbar_energy_loss_strict test_ttbar_failure_identity)
  set(test_source test_energy_loss.cpp)
  if(test_target STREQUAL "test_ttbar_failure_identity")
    set(test_source test_failure_identity.cpp)
  endif()
  add_executable(${test_target} ${test_source})
  target_compile_features(${test_target} PRIVATE cxx_std_20)
  target_compile_options(${test_target} PRIVATE ${NODD_NATIVE_COMPILE_FLAGS})
  target_include_directories(${test_target} PRIVATE ${NODD_INCLUDE_PATHS})
  target_link_libraries(${test_target} PRIVATE "${ACTS_Core}" "${ACTS_Fatras}"
    "${ACTS_PluginFpeMonitoring}" Eigen3::Eigen Boost::headers nlohmann_json::nlohmann_json)
  set_target_properties(${test_target} PROPERTIES BUILD_RPATH "${NODD_ACTS_BUILD}/lib")
endforeach()
target_compile_definitions(test_ttbar_energy_loss_strict PRIVATE NODD_TEST_STRICT_FP=1)
if(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  target_compile_options(test_ttbar_energy_loss_strict PRIVATE -ffp-model=strict)
endif()
add_test(NAME safe_fatras_energy_loss COMMAND test_ttbar_energy_loss)
add_test(NAME safe_fatras_energy_loss_strict COMMAND test_ttbar_energy_loss_strict)

add_test(NAME ttbar_failure_identity COMMAND test_ttbar_failure_identity)
