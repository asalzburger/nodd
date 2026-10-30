cmake_minimum_required(VERSION 3.24)
project(NoddTrackerReconstruction LANGUAGES CXX)
set(NODD_ACTS_SOURCE "" CACHE PATH "Matching installed ACTS source")
set(NODD_ACTS_BUILD "" CACHE PATH "Existing read-only ACTS build")
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)
find_package(Eigen3 CONFIG REQUIRED)
find_package(Boost CONFIG REQUIRED)
find_package(nlohmann_json CONFIG REQUIRED)
find_library(ACTS_CORE ActsCore PATHS "${NODD_ACTS_BUILD}/lib" NO_DEFAULT_PATH REQUIRED)
find_library(ACTS_FRAMEWORK ActsExamplesFramework PATHS "${NODD_ACTS_BUILD}/lib" NO_DEFAULT_PATH REQUIRED)
pybind11_add_module(nodd_reconstruction Reconstruction.cpp)
target_compile_features(nodd_reconstruction PRIVATE cxx_std_20)
target_compile_definitions(nodd_reconstruction PRIVATE NODD_EXPECTED_PYBIND11_INTERNALS_VERSION=11)
target_include_directories(nodd_reconstruction PRIVATE "${NODD_ACTS_SOURCE}/Core/include"
  "${NODD_ACTS_SOURCE}/Fatras/include" "${NODD_ACTS_SOURCE}/Examples/Framework/include"
  "${NODD_ACTS_SOURCE}/Plugins/FpeMonitoring/include" "${NODD_ACTS_BUILD}/Core/include")
target_link_libraries(nodd_reconstruction PRIVATE "${ACTS_CORE}" "${ACTS_FRAMEWORK}"
  Eigen3::Eigen Boost::headers nlohmann_json::nlohmann_json)
set_target_properties(nodd_reconstruction PROPERTIES CXX_VISIBILITY_PRESET default
  VISIBILITY_INLINES_HIDDEN OFF BUILD_RPATH "${NODD_ACTS_BUILD}/lib")
