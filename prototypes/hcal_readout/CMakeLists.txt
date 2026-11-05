# DES036 unsigned isolated prototype; never add_subdirectory from production.
cmake_minimum_required(VERSION 3.20)
project(nODDHCALReadoutPrototype LANGUAGES CXX)
find_package(DD4hep 1.38 REQUIRED CONFIG COMPONENTS DDCore)
add_library(nODDHCALReadoutPrototype SHARED Readout.cpp)
target_compile_features(nODDHCALReadoutPrototype PRIVATE cxx_std_20)
target_link_libraries(nODDHCALReadoutPrototype PUBLIC DD4hep::DDCore)
dd4hep_generate_rootmap(nODDHCALReadoutPrototype)
