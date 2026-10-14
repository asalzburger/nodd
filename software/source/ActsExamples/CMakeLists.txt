# Included at the end of upstream configuration by the external project hook.
set(NODD_ACTS_EXAMPLES_SOURCE "${CMAKE_CURRENT_LIST_DIR}")
get_filename_component(NODD_SOFTWARE_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
if(NOT TARGET Acts::ExamplesDetectorDD4hep OR NOT TARGET Acts::PythonUtilities)
  message(FATAL_ERROR "Build through make software-configure with ACTS DD4hep examples/Python enabled")
endif()
include("${NODD_ACTS_EXAMPLES_SOURCE}/Nodd/CMakeLists.txt")
