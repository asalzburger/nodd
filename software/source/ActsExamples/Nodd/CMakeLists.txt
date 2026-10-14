# Local nODD sources are added after all upstream ACTS targets exist.
set(NODD_BINDING_SOURCE "${CMAKE_CURRENT_LIST_DIR}")
acts_add_library(ExamplesNodd "${NODD_BINDING_SOURCE}/src/DD4hepNoddDetector.cpp"
  ACTS_INCLUDE_FOLDER "${NODD_BINDING_SOURCE}/include/ActsExamples")
target_include_directories(ActsExamplesNodd PUBLIC
  $<BUILD_INTERFACE:${NODD_BINDING_SOURCE}/include>)
target_link_libraries(ActsExamplesNodd PUBLIC Acts::ExamplesDetectorDD4hep)

pybind11_add_module(ActsExamplesPythonBindingsNodd "${NODD_BINDING_SOURCE}/python/Nodd.cpp")
target_link_libraries(ActsExamplesPythonBindingsNodd PRIVATE
  Acts::ExamplesNodd Acts::PythonUtilities)
set_target_properties(ActsExamplesPythonBindingsNodd PROPERTIES
  LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/python/acts/examples"
  INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_LIBDIR}")
# Upstream creates a regular Python package; put the extension into that package.
file(MAKE_DIRECTORY "${CMAKE_BINARY_DIR}/python/acts/examples")
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${NODD_BINDING_SOURCE}/python/nodd.py")
file(READ "${NODD_BINDING_SOURCE}/python/nodd.py" _nodd_helpers)
file(WRITE "${CMAKE_BINARY_DIR}/python/acts/examples/nodd.py"
  "from .ActsExamplesPythonBindingsNodd import DD4hepNoddDetector\n${_nodd_helpers}")
install(TARGETS ActsExamplesPythonBindingsNodd
  DESTINATION "${_acts_python_install_dir}/examples")
install(FILES "${CMAKE_BINARY_DIR}/python/acts/examples/nodd.py"
  DESTINATION "${_acts_python_install_dir}/examples")
# Building the local Python extension also builds upstream's required modules.
add_dependencies(ActsExamplesPythonBindingsNodd ActsPythonBindings)
add_custom_target(nodd-extensions DEPENDS ActsExamplesPythonBindingsNodd)
