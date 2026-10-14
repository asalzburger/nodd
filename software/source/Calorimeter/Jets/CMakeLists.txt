acts_add_library(
    CalorimeterJets
    "${NODD_COMPONENT_SOURCE_DIR}/src/CalorimeterJetReconstruction.cpp"
    ACTS_INCLUDE_FOLDER "${NODD_COMPONENT_SOURCE_DIR}/include/ActsCalorimeter"
)
target_include_directories(
    ActsCalorimeterJets
    PUBLIC
        $<BUILD_INTERFACE:${NODD_COMPONENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)
target_link_libraries(
    ActsCalorimeterJets
    PUBLIC Acts::Calorimeter
    PRIVATE FastJet::FastJet
)
nodd_compile_headers(CalorimeterJets GLOB "${NODD_COMPONENT_SOURCE_DIR}/include/**/*.hpp")
