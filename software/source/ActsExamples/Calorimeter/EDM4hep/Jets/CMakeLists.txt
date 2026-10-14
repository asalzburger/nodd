acts_add_library(
    ExamplesCalorimeterJetsEDM4hep
    "${NODD_COMPONENT_SOURCE_DIR}/src/EDM4hepCalorimeterJetOutputConverter.cpp"
    ACTS_INCLUDE_FOLDER "${NODD_COMPONENT_SOURCE_DIR}/include/ActsExamples"
)
target_include_directories(
    ActsExamplesCalorimeterJetsEDM4hep
    PUBLIC
        $<BUILD_INTERFACE:${NODD_COMPONENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
    PRIVATE ${NODD_COMPONENT_SOURCE_DIR}/../src
)
target_link_libraries(
    ActsExamplesCalorimeterJetsEDM4hep
    PUBLIC Acts::ExamplesCalorimeterEDM4hep Acts::ExamplesCalorimeterJets
)
nodd_compile_headers(ExamplesCalorimeterJetsEDM4hep GLOB "${NODD_COMPONENT_SOURCE_DIR}/include/**/*.hpp")

add_executable(
    ActsExampleCalorimeterJetsEDM4hep
    "${NODD_COMPONENT_SOURCE_DIR}/../EDM4hepCalorimeterExample.cpp"
)
target_compile_definitions(
    ActsExampleCalorimeterJetsEDM4hep
    PRIVATE ACTS_CALORIMETER_EDM4HEP_JETS
)
target_link_libraries(
    ActsExampleCalorimeterJetsEDM4hep
    PRIVATE Acts::ExamplesCalorimeterJetsEDM4hep EDM4HEP::edm4hepDict
)
install(
    TARGETS ActsExampleCalorimeterJetsEDM4hep
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
