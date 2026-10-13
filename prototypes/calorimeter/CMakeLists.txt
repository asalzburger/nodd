cmake_minimum_required(VERSION 3.20)
project(nODDCalorimeterPrototype LANGUAGES CXX)
find_package(DD4hep 1.38 REQUIRED CONFIG COMPONENTS DDCore)
add_library(nODDCalorimeterPrototype SHARED Calorimeter.cpp)
target_compile_features(nODDCalorimeterPrototype PRIVATE cxx_std_20)
target_link_libraries(nODDCalorimeterPrototype PUBLIC DD4hep::DDCore)
dd4hep_generate_rootmap(nODDCalorimeterPrototype)

# DES032 remains an isolated target; absent from production detector CMake.
add_library(nODDLArBarrelPrototype SHARED LArBarrel.cpp)
target_compile_features(nODDLArBarrelPrototype PRIVATE cxx_std_20)
target_link_libraries(nODDLArBarrelPrototype PUBLIC DD4hep::DDCore)
dd4hep_generate_rootmap(nODDLArBarrelPrototype)
