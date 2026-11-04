cmake_minimum_required(VERSION 3.24)
project(NoddTruthTracking LANGUAGES CXX)
set(NODD_ACTS_SOURCE "" CACHE PATH "Source matching the existing ACTS runtime")
set(NODD_ACTS_BUILD "" CACHE PATH "Existing ACTS build")
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)
find_package(Eigen3 CONFIG REQUIRED)
find_package(Boost CONFIG REQUIRED)
find_package(ROOT CONFIG REQUIRED COMPONENTS Core Tree RIO)
find_package(Geant4 REQUIRED)
find_library(ACTS_GEANT4 ActsExamplesGeant4 PATHS "${NODD_ACTS_BUILD}/lib" NO_DEFAULT_PATH REQUIRED)
find_library(ACTS_CORE ActsCore PATHS "${NODD_ACTS_BUILD}/lib" NO_DEFAULT_PATH REQUIRED)
find_library(ACTS_FRAMEWORK ActsExamplesFramework PATHS "${NODD_ACTS_BUILD}/lib" NO_DEFAULT_PATH REQUIRED)
pybind11_add_module(nodd_truth_tracking TruthTracking.cpp)
target_compile_features(nodd_truth_tracking PRIVATE cxx_std_20)
target_compile_definitions(nodd_truth_tracking PRIVATE NODD_EXPECTED_PYBIND11_INTERNALS_VERSION=11)
target_include_directories(nodd_truth_tracking PRIVATE
  "${NODD_ACTS_SOURCE}/Core/include" "${NODD_ACTS_SOURCE}/Fatras/include"
  "${NODD_ACTS_SOURCE}/Plugins/FpeMonitoring/include"
  "${NODD_ACTS_SOURCE}/Examples/Framework/include"
  "${NODD_ACTS_SOURCE}/Examples/Algorithms/Geant4/include"
  "${NODD_ACTS_BUILD}/Core/include" ${Geant4_INCLUDE_DIRS})
target_link_libraries(nodd_truth_tracking PRIVATE "${ACTS_CORE}" "${ACTS_FRAMEWORK}"
  "${ACTS_GEANT4}" ${Geant4_LIBRARIES} Eigen3::Eigen Boost::headers ROOT::Core ROOT::Tree ROOT::RIO)
set_target_properties(nodd_truth_tracking PROPERTIES CXX_VISIBILITY_PRESET default
  VISIBILITY_INLINES_HIDDEN OFF BUILD_RPATH "${NODD_ACTS_BUILD}/lib")
