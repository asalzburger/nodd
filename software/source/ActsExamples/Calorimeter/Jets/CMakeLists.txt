acts_add_library(
    ExamplesCalorimeterJets
    "${NODD_COMPONENT_SOURCE_DIR}/src/CalorimeterJetAlgorithm.cpp"
    ACTS_INCLUDE_FOLDER "${NODD_COMPONENT_SOURCE_DIR}/include/ActsExamples"
)
target_include_directories(
    ActsExamplesCalorimeterJets
    PUBLIC
        $<BUILD_INTERFACE:${NODD_COMPONENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)
target_link_libraries(
    ActsExamplesCalorimeterJets
    PUBLIC Acts::CalorimeterJets Acts::ExamplesFramework
)
nodd_compile_headers(ExamplesCalorimeterJets GLOB "${NODD_COMPONENT_SOURCE_DIR}/include/**/*.hpp")

add_executable(ActsExampleCalorimeterJets "${NODD_COMPONENT_SOURCE_DIR}/../CalorimeterExample.cpp")
target_compile_definitions(
    ActsExampleCalorimeterJets
    PRIVATE ACTS_EXAMPLE_CALORIMETER_JETS
)
target_link_libraries(
    ActsExampleCalorimeterJets
    PRIVATE Acts::ExamplesCalorimeter Acts::ExamplesCalorimeterJets
)
install(
    TARGETS ActsExampleCalorimeterJets
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
