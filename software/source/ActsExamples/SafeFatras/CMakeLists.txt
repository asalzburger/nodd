cmake_minimum_required(VERSION 3.24)
project(NoddSafeFatras LANGUAGES CXX)
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
  "// Generated from hash-checked ACTS inputs; not a shared source edit.\ninline pybind11::dict upstreamHashes() {\n  pybind11::dict hashes;\n${NODD_PROVENANCE}  return hashes;\n}\ninline const char* nativeCompileFlags() { return R\"nodd(${NODD_NATIVE_FLAGS})nodd\"; }\ninline const char* nativeCompileDefines() { return R\"nodd(${NODD_NATIVE_DEFINES})nodd\"; }\ninline const char* nativeFlagBlockHash() { return \"${NODD_NATIVE_BLOCK_HASH}\"; }\n")

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
pybind11_add_module(nodd_safe_fatras NO_EXTRAS Binding.cpp "${CMAKE_CURRENT_BINARY_DIR}/generated/NoddSafeFatrasSimulation.cpp")
target_compile_features(nodd_safe_fatras PRIVATE cxx_std_20)
target_compile_options(nodd_safe_fatras PRIVATE ${NODD_NATIVE_COMPILE_FLAGS})
target_compile_definitions(nodd_safe_fatras PRIVATE NODD_EXPECTED_PYBIND11_INTERNALS_VERSION=11
  NODD_GENERATED_HEADER_SHA256="${NODD_GENERATED_HEADER_HASH}"
  NODD_GENERATED_SOURCE_SHA256="${NODD_GENERATED_SOURCE_HASH}")
target_include_directories(nodd_safe_fatras PRIVATE ${NODD_INCLUDE_PATHS})
target_link_libraries(nodd_safe_fatras PRIVATE "${ACTS_Core}" "${ACTS_Fatras}" "${ACTS_ExamplesFramework}"
  Eigen3::Eigen Boost::headers)
set_target_properties(nodd_safe_fatras PROPERTIES CXX_VISIBILITY_PRESET hidden
  VISIBILITY_INLINES_HIDDEN ON BUILD_RPATH "${NODD_ACTS_BUILD}/lib")

enable_testing()
foreach(test_target test_safe_fatras_energy_loss test_safe_fatras_energy_loss_strict)
  add_executable(${test_target} test_energy_loss.cpp)
  target_compile_features(${test_target} PRIVATE cxx_std_20)
  target_compile_options(${test_target} PRIVATE ${NODD_NATIVE_COMPILE_FLAGS})
  target_include_directories(${test_target} PRIVATE ${NODD_INCLUDE_PATHS})
  target_link_libraries(${test_target} PRIVATE "${ACTS_Core}" "${ACTS_Fatras}"
    "${ACTS_PluginFpeMonitoring}" Eigen3::Eigen Boost::headers)
  set_target_properties(${test_target} PROPERTIES BUILD_RPATH "${NODD_ACTS_BUILD}/lib")
endforeach()
target_compile_definitions(test_safe_fatras_energy_loss_strict PRIVATE NODD_TEST_STRICT_FP=1)
if(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  target_compile_options(test_safe_fatras_energy_loss_strict PRIVATE -ffp-model=strict)
endif()
add_test(NAME safe_fatras_energy_loss COMMAND test_safe_fatras_energy_loss)
add_test(NAME safe_fatras_energy_loss_strict COMMAND test_safe_fatras_energy_loss_strict)
