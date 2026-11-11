cmake_minimum_required(VERSION 3.20)
project(nODDTrackerPlacementReusePrototype LANGUAGES CXX)
find_package(DD4hep 1.37 REQUIRED CONFIG COMPONENTS DDCore)
# Isolated PR132 experiment: deliberately absent from the maintained build.
add_library(nODDShortStripBarrelReuse SHARED ShortStripBarrelReuse.cpp)
target_compile_features(nODDShortStripBarrelReuse PRIVATE cxx_std_20)
target_link_libraries(nODDShortStripBarrelReuse PUBLIC DD4hep::DDCore)
dd4hep_generate_rootmap(nODDShortStripBarrelReuse)
