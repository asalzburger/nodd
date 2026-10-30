cmake_minimum_required(VERSION 3.24)
project(NoddSafeFatras LANGUAGES CXX)
set(NODD_ACTS_SOURCE "" CACHE PATH "Read-only ACTS355ea684 source matching native runtime")
set(NODD_ACTS_BUILD "" CACHE PATH "Read-only existing ACTS build")
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
  "Fatras/include/ActsFatras/Utilities/detail/FpeSafeGammaDistribution.hpp")
set(NODD_INPUT_HASHES
  "60f0570c07b45c9a3ccfc608f7dc2aa612396b851ca895eb361011af2968ba20"
  "7ec2143f967e208d43c26027dc0717deab31f0d9285326a94bcce580370ce758"
  "2b986671cb9537934274c599c47d7e446fb2d8ab22e7fe3b3d732e1c473b692c"
  "220cd2777c63277a1e143074d6c3f9f227f1f7f9563f38ff7cde3fd15be7ca0b"
  "f5706e741d1ea94a8a202d9138fb0d65c50e5fe81603d6c8621691312349a49a"
  "941667d6842089f64decc5b3151cde36f965732abe660113eaa5277e91ad2d12")
set(NODD_PROVENANCE "")
foreach(index RANGE 0 5)
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
file(READ "${NODD_ACTS_SOURCE}/Examples/Algorithms/Fatras/include/ActsExamples/Fatras/FatrasSimulation.hpp" header)
file(READ "${NODD_ACTS_SOURCE}/Examples/Algorithms/Fatras/src/FatrasSimulation.cpp" source)
replace_once(source "#include \"ActsFatras/Physics/StandardInteractions.hpp\""
  "#include \"ActsFatras/Physics/StandardInteractions.hpp\"\n#include \"SafeBetheHeitler.hpp\"")
replace_once(source "ActsFatras::StandardChargedElectroMagneticInteractions"
  "nodd::safe_fatras::ChargedInteractions")
replace_once(source "makeStandardChargedElectroMagneticInteractions(cfg.pMin)"
  "nodd::safe_fatras::makeChargedInteractions(cfg.pMin)")
replace_once(source "disable<StandardBetheHeitler>()"
  "disable<nodd::safe_fatras::StandardBetheHeitler>()")
string(REPLACE "FatrasSimulation" "NoddSafeFatrasSimulation" header "${header}")
string(REPLACE "FatrasSimulation" "NoddSafeFatrasSimulation" source "${source}")
replace_once(source "IAlgorithm(\"NoddSafeFatrasSimulation\""
  "IAlgorithm(\"FatrasSimulation\"")
file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/generated/ActsExamples/Fatras")
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/generated/ActsExamples/Fatras/NoddSafeFatrasSimulation.hpp" "${header}")
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/generated/NoddSafeFatrasSimulation.cpp" "${source}")
file(SHA256 "${CMAKE_CURRENT_BINARY_DIR}/generated/ActsExamples/Fatras/NoddSafeFatrasSimulation.hpp" NODD_GENERATED_HEADER_HASH)
file(SHA256 "${CMAKE_CURRENT_BINARY_DIR}/generated/NoddSafeFatrasSimulation.cpp" NODD_GENERATED_SOURCE_HASH)
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/generated/SafeFatrasProvenance.hpp"
  "// Generated from hash-checked ACTS inputs; not a shared source edit.\ninline pybind11::dict upstreamHashes() {\n  pybind11::dict hashes;\n${NODD_PROVENANCE}  return hashes;\n}\n")

find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 3.0.4 EXACT CONFIG REQUIRED)
find_package(Eigen3 CONFIG REQUIRED)
find_package(Boost CONFIG REQUIRED)
foreach(component Core Fatras ExamplesFramework PluginFpeMonitoring)
  find_library(ACTS_${component} Acts${component} PATHS "${NODD_ACTS_BUILD}/lib" NO_DEFAULT_PATH REQUIRED)
endforeach()
set(NODD_INCLUDE_PATHS "${CMAKE_CURRENT_SOURCE_DIR}" "${CMAKE_CURRENT_BINARY_DIR}/generated"
  "${NODD_ACTS_SOURCE}/Core/include" "${NODD_ACTS_BUILD}/Core/include"
  "${NODD_ACTS_SOURCE}/Fatras/include" "${NODD_ACTS_SOURCE}/Examples/Framework/include"
  "${NODD_ACTS_SOURCE}/Plugins/FpeMonitoring/include")
pybind11_add_module(nodd_safe_fatras Binding.cpp "${CMAKE_CURRENT_BINARY_DIR}/generated/NoddSafeFatrasSimulation.cpp")
target_compile_features(nodd_safe_fatras PRIVATE cxx_std_20)
target_compile_definitions(nodd_safe_fatras PRIVATE NODD_EXPECTED_PYBIND11_INTERNALS_VERSION=11
  NODD_GENERATED_HEADER_SHA256="${NODD_GENERATED_HEADER_HASH}"
  NODD_GENERATED_SOURCE_SHA256="${NODD_GENERATED_SOURCE_HASH}")
target_include_directories(nodd_safe_fatras PRIVATE ${NODD_INCLUDE_PATHS})
target_link_libraries(nodd_safe_fatras PRIVATE "${ACTS_Core}" "${ACTS_Fatras}" "${ACTS_ExamplesFramework}"
  Eigen3::Eigen Boost::headers)
set_target_properties(nodd_safe_fatras PROPERTIES CXX_VISIBILITY_PRESET hidden
  VISIBILITY_INLINES_HIDDEN ON BUILD_RPATH "${NODD_ACTS_BUILD}/lib")

enable_testing()
add_executable(test_safe_fatras_energy_loss test_energy_loss.cpp)
target_compile_features(test_safe_fatras_energy_loss PRIVATE cxx_std_20)
target_include_directories(test_safe_fatras_energy_loss PRIVATE ${NODD_INCLUDE_PATHS})
target_link_libraries(test_safe_fatras_energy_loss PRIVATE "${ACTS_Core}" "${ACTS_Fatras}"
  "${ACTS_PluginFpeMonitoring}" Eigen3::Eigen Boost::headers)
if(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  target_compile_options(test_safe_fatras_energy_loss PRIVATE -ffp-model=strict)
endif()
set_target_properties(test_safe_fatras_energy_loss PROPERTIES BUILD_RPATH "${NODD_ACTS_BUILD}/lib")
add_test(NAME safe_fatras_energy_loss COMMAND test_safe_fatras_energy_loss)
