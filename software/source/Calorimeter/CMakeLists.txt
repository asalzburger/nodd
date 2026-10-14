acts_add_library(
    Calorimeter
    "${NODD_COMPONENT_SOURCE_DIR}/src/Clustering/CalorimeterClusterer.cpp"
    "${NODD_COMPONENT_SOURCE_DIR}/src/Digitization/CalorimeterResponse.cpp"
    ACTS_INCLUDE_FOLDER "${NODD_COMPONENT_SOURCE_DIR}/include/ActsCalorimeter"
)
target_include_directories(
    ActsCalorimeter
    PUBLIC
        $<BUILD_INTERFACE:${NODD_COMPONENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)
target_link_libraries(ActsCalorimeter PUBLIC Acts::Core nODD::EDM)
nodd_compile_headers(Calorimeter GLOB "${NODD_COMPONENT_SOURCE_DIR}/include/**/*.hpp")
