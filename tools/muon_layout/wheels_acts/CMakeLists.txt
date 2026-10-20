cmake_minimum_required(VERSION 3.24)
project(nodd_muon_wheels_acts LANGUAGES CXX)
find_package(Acts CONFIG REQUIRED COMPONENTS Core)
find_package(Python3 REQUIRED COMPONENTS Interpreter)
set(FROZEN_SOURCE "${CMAKE_CURRENT_SOURCE_DIR}/../acts/propagate.cpp")
set(VARIANT_SOURCE "${CMAKE_CURRENT_BINARY_DIR}/propagate.cpp")
execute_process(COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/variant.py"
  --source "${FROZEN_SOURCE}" --output "${VARIANT_SOURCE}"
  COMMAND_ERROR_IS_FATAL ANY)
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
  "${FROZEN_SOURCE}" "${CMAKE_CURRENT_SOURCE_DIR}/variant.py")
add_executable(nodd-muon-wheels-propagate "${VARIANT_SOURCE}")
target_compile_features(nodd-muon-wheels-propagate PRIVATE cxx_std_20)
target_link_libraries(nodd-muon-wheels-propagate PRIVATE Acts::Core)
target_compile_options(nodd-muon-wheels-propagate PRIVATE -Wall -Wextra -Wpedantic)
target_compile_definitions(nodd-muon-wheels-propagate PRIVATE
  NODD_ACTS_DISCOVERY="normal-config-world-entrance-variant")
