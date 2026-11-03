cmake_minimum_required(VERSION 3.20)
project(nODDShortStripRedesignPrototype LANGUAGES CXX)
find_package(DD4hep 1.38 REQUIRED CONFIG COMPONENTS DDCore)
find_package(Python3 REQUIRED COMPONENTS Interpreter)
# Reuse the unchanged generic primitive/CSG factory, in an isolated plugin.
add_library(nODDShortStripRedesign SHARED ../short_strip_endcap/ShortStripEndcap.cpp)
target_compile_features(nODDShortStripRedesign PRIVATE cxx_std_20)
target_link_libraries(nODDShortStripRedesign PUBLIC DD4hep::DDCore)
dd4hep_generate_rootmap(nODDShortStripRedesign)
get_filename_component(NODD_REPO "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)
option(NODD_RED_FULL "Construct all twelve discs instead of the first mirrored pair" OFF)
set(NODD_RED_ARGS)
if(NODD_RED_FULL)
  list(APPEND NODD_RED_ARGS --full)
endif()
set(NODD_COMPACT "${CMAKE_CURRENT_BINARY_DIR}/compact")
file(GLOB NODD_RED_INPUTS "${NODD_REPO}/tools/short_strip_redesign/*.py" "${NODD_REPO}/tools/short_strip_redesign/*.json")
add_custom_command(OUTPUT "${NODD_COMPACT}/short-strip-redesign.xml" "${NODD_COMPACT}/expected.json" "${NODD_COMPACT}/materials.xml"
  COMMAND "${Python3_EXECUTABLE}" -B "${NODD_REPO}/tools/short_strip_redesign/native.py" --output "${NODD_COMPACT}" ${NODD_RED_ARGS}
  DEPENDS ${NODD_RED_INPUTS} "${NODD_REPO}/tools/pixel_barrel_dd4hep/materials.py"
  WORKING_DIRECTORY "${NODD_REPO}" VERBATIM)
add_custom_target(nodd-short-strip-redesign-compact ALL DEPENDS "${NODD_COMPACT}/short-strip-redesign.xml" "${NODD_COMPACT}/expected.json")
include(CTest)
if(BUILD_TESTING)
  add_test(NAME short-strip-redesign-portable COMMAND "${Python3_EXECUTABLE}" -B -m unittest discover -s "${NODD_REPO}/tools/short_strip_redesign" -p test_native.py -v)
  add_test(NAME short-strip-redesign-native COMMAND "${Python3_EXECUTABLE}" -B "${NODD_REPO}/tools/short_strip_redesign/validate_native.py"
    --compact "${NODD_COMPACT}/short-strip-redesign.xml" --expected "${NODD_COMPACT}/expected.json"
    --library "$<TARGET_FILE:nODDShortStripRedesign>" --output "${CMAKE_CURRENT_BINARY_DIR}/native.json")
  set_tests_properties(short-strip-redesign-native PROPERTIES ENVIRONMENT "DD4HEP_LIBRARY_PATH=${CMAKE_CURRENT_BINARY_DIR}:$ENV{DD4HEP_LIBRARY_PATH};LD_LIBRARY_PATH=${CMAKE_CURRENT_BINARY_DIR}:$ENV{LD_LIBRARY_PATH};DYLD_LIBRARY_PATH=${CMAKE_CURRENT_BINARY_DIR}:$ENV{DYLD_LIBRARY_PATH}")
endif()
