add_library(nODDPixelBarrel SHARED src/PixelBarrel.cpp src/PixelComponents.cpp src/PixelServices.cpp src/PixelEndcap.cpp src/PixelEndcapParts.cpp)
target_compile_features(nODDPixelBarrel PUBLIC cxx_std_20)
target_include_directories(nODDPixelBarrel PRIVATE include)
target_link_libraries(nODDPixelBarrel PUBLIC DD4hep::DDCore)
set(LIBRARY_OUTPUT_PATH "${CMAKE_CURRENT_BINARY_DIR}")
dd4hep_generate_rootmap(nODDPixelBarrel)
set(NODD_COMPACT_DIR "${CMAKE_CURRENT_BINARY_DIR}/compact")
file(GLOB NODD_EXPORT_INPUTS CONFIGURE_DEPENDS
  "${PROJECT_SOURCE_DIR}/tools/pixel_barrel_dd4hep/*.py"
  "${PROJECT_SOURCE_DIR}/tools/pixel_support/*.json"
  "${PROJECT_SOURCE_DIR}/tools/pixel_support/*.py"
  "${PROJECT_SOURCE_DIR}/tools/module_layout/*.py"
  "${PROJECT_SOURCE_DIR}/tools/module_layout/*.json"
  "${CMAKE_CURRENT_SOURCE_DIR}/config/*.json")
add_custom_command(OUTPUT "${NODD_COMPACT_DIR}/pixel-barrel.xml" "${NODD_COMPACT_DIR}/expected.json"
  COMMAND "${Python3_EXECUTABLE}" -B "${PROJECT_SOURCE_DIR}/tools/pixel_barrel_dd4hep/export.py" --output "${NODD_COMPACT_DIR}"
  DEPENDS ${NODD_EXPORT_INPUTS}
    "${PROJECT_SOURCE_DIR}/docs/validation/DES-013-pixel-z/data/packed-200um/layout.json.gz"
    "${PROJECT_SOURCE_DIR}/docs/validation/DES-012/PR34/engineering/routing.json.gz"
    "${PROJECT_SOURCE_DIR}/docs/validation/DES-012/PR34/engineering/screening.json"
    "${PROJECT_SOURCE_DIR}/docs/validation/DES-011-optimization/cases/p190-s680-b1-l1287.33-front_loaded-original-pockets/layout.json.gz"
    "${PROJECT_SOURCE_DIR}/docs/validation/DES-002/outward-A-services/routing.json.gz"
    "${PROJECT_SOURCE_DIR}/docs/validation/DES-002/outward-A-services/screening.json"
  WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}" VERBATIM)
add_custom_target(nodd-pixel-compact ALL DEPENDS "${NODD_COMPACT_DIR}/pixel-barrel.xml" "${NODD_COMPACT_DIR}/expected.json")
if(BUILD_TESTING)
  add_test(NAME pixel-export-tests COMMAND "${Python3_EXECUTABLE}" -B -m unittest discover
    -s "${PROJECT_SOURCE_DIR}/tools/pixel_barrel_dd4hep" -p "test_*.py" -v)
  add_test(NAME pixel-dd4hep-validation COMMAND "${Python3_EXECUTABLE}" -B
    "${PROJECT_SOURCE_DIR}/tools/pixel_barrel_dd4hep/validate.py"
    --compact "${NODD_COMPACT_DIR}/pixel-barrel.xml" --expected "${NODD_COMPACT_DIR}/expected.json"
    --library "$<TARGET_FILE:nODDPixelBarrel>" --output "${CMAKE_CURRENT_BINARY_DIR}/validation.json")
  add_test(NAME pixel-root-display-roundtrip COMMAND "${Python3_EXECUTABLE}" -B
    "${PROJECT_SOURCE_DIR}/tools/pixel_barrel_dd4hep/export_root.py"
    --compact "${NODD_COMPACT_DIR}/pixel-barrel.xml" --library "$<TARGET_FILE:nODDPixelBarrel>"
    --output "${CMAKE_CURRENT_BINARY_DIR}/pixel-barrel.root")
endif()
install(TARGETS nODDPixelBarrel LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})
install(DIRECTORY "${NODD_COMPACT_DIR}/" DESTINATION share/nODD/pixel-barrel)

# The combined preliminary pixel baseline stays separate from the barrel entry point.
file(GLOB NODD_COMBINED_INPUTS CONFIGURE_DEPENDS
  "${PROJECT_SOURCE_DIR}/tools/pixel_detector_dd4hep/*.py"
  "${PROJECT_SOURCE_DIR}/tools/pixel_endcap_support/*.py"
  "${PROJECT_SOURCE_DIR}/tools/pixel_endcap_support/*.json"
  "${CMAKE_CURRENT_SOURCE_DIR}/src/PixelEndcap*.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/include/nodd/PixelEndcap.hpp")
set(NODD_PIXEL_DIR "${CMAKE_CURRENT_BINARY_DIR}/pixel-detector")
add_custom_command(OUTPUT "${NODD_PIXEL_DIR}/pixel-detector.xml" "${NODD_PIXEL_DIR}/expected.json"
  COMMAND "${Python3_EXECUTABLE}" -B "${PROJECT_SOURCE_DIR}/tools/pixel_detector_dd4hep/export.py" --output "${NODD_PIXEL_DIR}"
  DEPENDS ${NODD_COMBINED_INPUTS} ${NODD_EXPORT_INPUTS}
    "${NODD_COMPACT_DIR}/pixel-barrel.xml"
    "${PROJECT_SOURCE_DIR}/docs/validation/DES-014-pixel-endcap-support/screening.json"
    "${PROJECT_SOURCE_DIR}/docs/validation/DES-017/four-single-two-quad-layout.json"
    "${PROJECT_SOURCE_DIR}/docs/validation/DES-018/screening.json"
    "${PROJECT_SOURCE_DIR}/tools/pixel_disc_optimization/radial-inputs.json"
    "${PROJECT_SOURCE_DIR}/tools/pixel_disc_support_variants/inputs.json"
  WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}" VERBATIM)
add_custom_target(nodd-pixel-detector ALL DEPENDS "${NODD_PIXEL_DIR}/pixel-detector.xml" "${NODD_PIXEL_DIR}/expected.json")
if(BUILD_TESTING)
  add_test(NAME pixel-detector-export-tests COMMAND "${Python3_EXECUTABLE}" -B -m unittest discover
    -s "${PROJECT_SOURCE_DIR}/tools/pixel_detector_dd4hep" -p "test_*.py" -v)
  add_test(NAME pixel-detector-validation COMMAND "${Python3_EXECUTABLE}" -B
    "${PROJECT_SOURCE_DIR}/tools/pixel_barrel_dd4hep/validate.py"
    --compact "${NODD_PIXEL_DIR}/pixel-detector.xml" --expected "${NODD_PIXEL_DIR}/expected.json"
    --library "$<TARGET_FILE:nODDPixelBarrel>" --output "${CMAKE_CURRENT_BINARY_DIR}/pixel-detector-validation.json")
  add_test(NAME pixel-detector-root-roundtrip COMMAND "${Python3_EXECUTABLE}" -B
    "${PROJECT_SOURCE_DIR}/tools/pixel_barrel_dd4hep/export_root.py"
    --compact "${NODD_PIXEL_DIR}/pixel-detector.xml" --library "$<TARGET_FILE:nODDPixelBarrel>"
    --output "${CMAKE_CURRENT_BINARY_DIR}/pixel-detector.root")
endif()
install(DIRECTORY "${NODD_PIXEL_DIR}/" DESTINATION share/nODD/pixel-detector)

# DES-024: independently testable interaction-region component.
add_library(nODDBeamPipe SHARED src/BeamPipe.cpp)
target_compile_features(nODDBeamPipe PUBLIC cxx_std_20)
target_link_libraries(nODDBeamPipe PUBLIC DD4hep::DDCore)
dd4hep_generate_rootmap(nODDBeamPipe)
set(NODD_BEAMPIPE_DIR "${CMAKE_CURRENT_BINARY_DIR}/beampipe")
add_custom_command(OUTPUT "${NODD_BEAMPIPE_DIR}/beampipe.xml" "${NODD_BEAMPIPE_DIR}/materials.xml" "${NODD_BEAMPIPE_DIR}/expected.json"
  COMMAND "${Python3_EXECUTABLE}" -B "${PROJECT_SOURCE_DIR}/tools/beampipe/export.py" --output "${NODD_BEAMPIPE_DIR}"
  DEPENDS "${PROJECT_SOURCE_DIR}/tools/beampipe/export.py" "${CMAKE_CURRENT_SOURCE_DIR}/config/beampipe.json" "${CMAKE_CURRENT_SOURCE_DIR}/config/elements.json"
  VERBATIM)
add_custom_target(nodd-beampipe-compact ALL DEPENDS "${NODD_BEAMPIPE_DIR}/beampipe.xml" "${NODD_BEAMPIPE_DIR}/materials.xml" "${NODD_BEAMPIPE_DIR}/expected.json")
if(BUILD_TESTING)
  add_test(NAME beampipe-export-tests COMMAND "${Python3_EXECUTABLE}" -B -m unittest discover -s "${PROJECT_SOURCE_DIR}/tools/beampipe" -p "test_*.py" -v)
  add_test(NAME beampipe-dd4hep-validation COMMAND "${Python3_EXECUTABLE}" -B "${PROJECT_SOURCE_DIR}/tools/beampipe/validate.py"
    --compact "${NODD_BEAMPIPE_DIR}/beampipe.xml" --expected "${NODD_BEAMPIPE_DIR}/expected.json"
    --library "$<TARGET_FILE:nODDBeamPipe>" --output "${CMAKE_CURRENT_BINARY_DIR}/beampipe-validation.json")
endif()
install(TARGETS nODDBeamPipe LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})
install(DIRECTORY "${NODD_BEAMPIPE_DIR}/" DESTINATION share/nODD/beampipe)
