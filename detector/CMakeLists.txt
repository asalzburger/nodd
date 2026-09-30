add_library(nODDPixelBarrel SHARED src/PixelBarrel.cpp src/PixelComponents.cpp src/PixelServices.cpp)
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
