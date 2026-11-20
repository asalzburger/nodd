# DES045 isolated DRAFT/PROTOTYPE; not connected to production entry points.
cmake_minimum_required(VERSION 3.20)
project(nODDHCALResponsePrototype LANGUAGES CXX)
find_package(DD4hep 1.38 REQUIRED CONFIG COMPONENTS DDCore)
add_library(nODDHCALResponsePrototype SHARED HCAL.cpp)
target_compile_features(nODDHCALResponsePrototype PRIVATE cxx_std_20)
target_link_libraries(nODDHCALResponsePrototype PUBLIC DD4hep::DDCore)
dd4hep_generate_rootmap(nODDHCALResponsePrototype)
