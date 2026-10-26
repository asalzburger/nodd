cmake_minimum_required(VERSION 3.24)
project(NoddPortalMaterial LANGUAGES CXX)

# This sidecar deliberately consumes an explicitly selected existing build.
# It does not configure, install, or modify ACTS or the nODD adapter.
set(NODD_ACTS_SOURCE "" CACHE PATH "ACTS source matching the selected runtime")
set(NODD_ACTS_BUILD "" CACHE PATH "Existing ACTS build with libActsCore")
if(NOT EXISTS "${NODD_ACTS_SOURCE}/Core/include/Acts/Geometry/Portal.hpp")
  message(FATAL_ERROR "NODD_ACTS_SOURCE must identify the runtime's source")
endif()
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)
set(NODD_PYBIND11_INTERNALS_VERSION 11 CACHE STRING "Internals ABI of the selected ACTS Python bindings")
find_package(Eigen3 CONFIG REQUIRED)
find_package(Boost CONFIG REQUIRED)
find_library(ACTS_CORE ActsCore PATHS "${NODD_ACTS_BUILD}/lib" NO_DEFAULT_PATH REQUIRED)
find_library(ACTS_FRAMEWORK ActsExamplesFramework PATHS "${NODD_ACTS_BUILD}/lib" NO_DEFAULT_PATH REQUIRED)
pybind11_add_module(nodd_portal_material PortalMaterial.cpp)
target_compile_features(nodd_portal_material PRIVATE cxx_std_20)
target_compile_definitions(nodd_portal_material PRIVATE
  NODD_EXPECTED_PYBIND11_INTERNALS_VERSION=${NODD_PYBIND11_INTERNALS_VERSION})
target_include_directories(nodd_portal_material PRIVATE
  "${NODD_ACTS_SOURCE}/Core/include"
  "${NODD_ACTS_SOURCE}/Plugins/FpeMonitoring/include"
  "${NODD_ACTS_SOURCE}/Examples/Framework/include"
  "${NODD_ACTS_BUILD}/Core/include")
target_link_libraries(nodd_portal_material PRIVATE
  "${ACTS_CORE}" "${ACTS_FRAMEWORK}" Eigen3::Eigen Boost::headers)
set_target_properties(nodd_portal_material PROPERTIES
  # Template material RTTI must be visible to dynamic_cast in ActsCore.
  CXX_VISIBILITY_PRESET default
  VISIBILITY_INLINES_HIDDEN OFF
  BUILD_RPATH "${NODD_ACTS_BUILD}/lib")
