# CMake's project hook schedules local target definitions after upstream ACTS.
# ACTS remains the top-level source project; its source/commit metadata is retained.
get_filename_component(_nodd_extensions "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)
cmake_language(EVAL CODE
  "cmake_language(DEFER CALL include [[${_nodd_extensions}/CMakeLists.txt]])")
