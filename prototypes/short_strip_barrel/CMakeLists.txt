cmake_minimum_required(VERSION 3.20)
project(nODDShortStripBarrelPrototype LANGUAGES CXX)
find_package(DD4hep 1.37 REQUIRED CONFIG COMPONENTS DDCore)
find_package(Python3 REQUIRED COMPONENTS Interpreter)
add_library(nODDShortStripBarrel SHARED ShortStripBarrel.cpp)
target_compile_features(nODDShortStripBarrel PRIVATE cxx_std_20)
target_link_libraries(nODDShortStripBarrel PUBLIC DD4hep::DDCore)
dd4hep_generate_rootmap(nODDShortStripBarrel)
get_filename_component(NODD_REPO "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)
set(NODD_COMPACT "${CMAKE_CURRENT_BINARY_DIR}/compact")
file(GLOB NODD_SS_INPUTS "${NODD_REPO}/tools/short_strip_barrel/*.py" "${NODD_REPO}/tools/short_strip_barrel/*.json")
add_custom_command(OUTPUT "${NODD_COMPACT}/short-strip-barrel.xml" "${NODD_COMPACT}/expected.json"
  COMMAND "${Python3_EXECUTABLE}" -B "${NODD_REPO}/tools/short_strip_barrel/export.py" --output "${NODD_COMPACT}"
  DEPENDS ${NODD_SS_INPUTS} "${NODD_REPO}/tools/pixel_barrel_dd4hep/materials.py"
  WORKING_DIRECTORY "${NODD_REPO}" VERBATIM)
add_custom_target(nodd-short-strip-compact ALL DEPENDS "${NODD_COMPACT}/short-strip-barrel.xml" "${NODD_COMPACT}/expected.json")
set(NODD_PHI_COMPACT "${CMAKE_CURRENT_BINARY_DIR}/compact-phi")
add_custom_command(OUTPUT "${NODD_PHI_COMPACT}/short-strip-barrel.xml" "${NODD_PHI_COMPACT}/expected.json"
  COMMAND "${Python3_EXECUTABLE}" -B "${NODD_REPO}/tools/short_strip_barrel/export.py"
    --input "${NODD_REPO}/tools/short_strip_barrel/inputs-phi-tilted.json" --output "${NODD_PHI_COMPACT}"
  DEPENDS ${NODD_SS_INPUTS} "${NODD_REPO}/tools/pixel_barrel_dd4hep/materials.py"
  WORKING_DIRECTORY "${NODD_REPO}" VERBATIM)
add_custom_target(nodd-short-strip-phi-compact ALL DEPENDS "${NODD_PHI_COMPACT}/short-strip-barrel.xml" "${NODD_PHI_COMPACT}/expected.json")
include(CTest)
if(BUILD_TESTING)
  add_test(NAME short-strip-model COMMAND "${Python3_EXECUTABLE}" -B -m unittest discover
    -s "${NODD_REPO}/tools/short_strip_barrel" -p "test_*.py" -v)
  add_test(NAME short-strip-native COMMAND "${Python3_EXECUTABLE}" -B "${NODD_REPO}/tools/short_strip_barrel/validate.py"
    --compact "${NODD_COMPACT}/short-strip-barrel.xml" --expected "${NODD_COMPACT}/expected.json"
    --library "$<TARGET_FILE:nODDShortStripBarrel>" --output "${CMAKE_CURRENT_BINARY_DIR}/native.json")
  add_test(NAME short-strip-phi-native COMMAND "${Python3_EXECUTABLE}" -B "${NODD_REPO}/tools/short_strip_barrel/validate.py"
    --compact "${NODD_PHI_COMPACT}/short-strip-barrel.xml" --expected "${NODD_PHI_COMPACT}/expected.json"
    --library "$<TARGET_FILE:nODDShortStripBarrel>" --output "${CMAKE_CURRENT_BINARY_DIR}/native-phi.json")
endif()
