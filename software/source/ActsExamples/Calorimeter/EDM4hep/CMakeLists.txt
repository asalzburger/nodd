find_package(EDM4HEP 1.0 CONFIG REQUIRED)
find_package(podio 1.7 CONFIG REQUIRED)

acts_add_library(
    ExamplesCalorimeterEDM4hep
    "${NODD_COMPONENT_SOURCE_DIR}/src/EDM4hepCalorimeterInputConverter.cpp"
    "${NODD_COMPONENT_SOURCE_DIR}/src/EDM4hepCalorimeterOutputConverter.cpp"
    "${NODD_COMPONENT_SOURCE_DIR}/src/EDM4hepCalorimeterClusterOutputConverter.cpp"
    "${NODD_COMPONENT_SOURCE_DIR}/src/EDM4hepCalorimeterMetadata.cpp"
    ACTS_INCLUDE_FOLDER "${NODD_COMPONENT_SOURCE_DIR}/include/ActsExamples"
)
target_include_directories(
    ActsExamplesCalorimeterEDM4hep
    PUBLIC
        $<BUILD_INTERFACE:${NODD_COMPONENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)
target_link_libraries(
    ActsExamplesCalorimeterEDM4hep
    PUBLIC Acts::ExamplesCalorimeter Acts::ExamplesIoPodio EDM4HEP::edm4hep
)
nodd_compile_headers(ExamplesCalorimeterEDM4hep GLOB "${NODD_COMPONENT_SOURCE_DIR}/include/**/*.hpp")

add_executable(ActsExampleCalorimeterEDM4hep "${NODD_COMPONENT_SOURCE_DIR}/EDM4hepCalorimeterExample.cpp")
target_link_libraries(
    ActsExampleCalorimeterEDM4hep
    PRIVATE Acts::ExamplesCalorimeterEDM4hep EDM4HEP::edm4hepDict
)
install(
    TARGETS ActsExampleCalorimeterEDM4hep
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

if(NODD_BUILD_CALORIMETER_JETS)
  nodd_include_component("${NODD_COMPONENT_SOURCE_DIR}/Jets")
endif()
