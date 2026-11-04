cmake_minimum_required(VERSION 3.24)
project(NoddMaterialRecording LANGUAGES CXX)
set(NODD_ACTS_SOURCE "" CACHE PATH "Source matching the existing ACTS runtime")
set(NODD_ACTS_BUILD "" CACHE PATH "Existing ACTS build")
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)
find_package(Eigen3 CONFIG REQUIRED)
find_package(Boost CONFIG REQUIRED)
find_package(Geant4 REQUIRED)
foreach(component Core ExamplesFramework ExamplesGeant4)
  find_library(ACTS_${component} Acts${component} PATHS "${NODD_ACTS_BUILD}/lib" NO_DEFAULT_PATH REQUIRED)
endforeach()
pybind11_add_module(nodd_material_recording_native PersistentMaterial.cpp)
target_compile_features(nodd_material_recording_native PRIVATE cxx_std_20)
target_include_directories(nodd_material_recording_native PRIVATE
  "${NODD_ACTS_SOURCE}/Core/include" "${NODD_ACTS_BUILD}/Core/include"
  "${NODD_ACTS_SOURCE}/Examples/Framework/include"
  "${NODD_ACTS_SOURCE}/Examples/Algorithms/Geant4/include" ${Geant4_INCLUDE_DIRS})
target_link_libraries(nodd_material_recording_native PRIVATE
  "${ACTS_Core}" "${ACTS_ExamplesFramework}" "${ACTS_ExamplesGeant4}"
  ${Geant4_LIBRARIES} Eigen3::Eigen Boost::headers)
set_target_properties(nodd_material_recording_native PROPERTIES
  CXX_VISIBILITY_PRESET default VISIBILITY_INLINES_HIDDEN OFF
  BUILD_RPATH "${NODD_ACTS_BUILD}/lib")
