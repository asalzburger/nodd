add_library(nODDCalorimeterEDM4hep
  src/EDM4hepCalorimeterInputConverter.cpp
  src/EDM4hepCalorimeterOutputConverter.cpp
  src/EDM4hepCalorimeterClusterOutputConverter.cpp
  src/EDM4hepCalorimeterMetadata.cpp)
target_compile_features(nODDCalorimeterEDM4hep PUBLIC cxx_std_20)
target_include_directories(nODDCalorimeterEDM4hep PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>)
target_link_libraries(nODDCalorimeterEDM4hep PUBLIC
  nODDCalorimeterAlgorithms nODDActsExamplesIoPodio EDM4HEP::edm4hep)
set_target_properties(nODDCalorimeterEDM4hep PROPERTIES
  BUILD_RPATH "${NODD_ACTS_BUILD}/lib")

add_executable(nodd_calorimeter_io_fixture EDM4hepCalorimeterExample.cpp)
target_link_libraries(nodd_calorimeter_io_fixture PRIVATE
  nODDCalorimeterEDM4hep EDM4HEP::edm4hepDict podio::podioRootIO)
set_target_properties(nodd_calorimeter_io_fixture PROPERTIES
  BUILD_RPATH "${NODD_ACTS_BUILD}/lib")
