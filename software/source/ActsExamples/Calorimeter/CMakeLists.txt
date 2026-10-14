acts_add_library(
    ExamplesCalorimeter
    "${NODD_COMPONENT_SOURCE_DIR}/src/CalorimeterClusteringAlgorithm.cpp"
    "${NODD_COMPONENT_SOURCE_DIR}/src/CalorimeterDigitizationAlgorithm.cpp"
    ACTS_INCLUDE_FOLDER "${NODD_COMPONENT_SOURCE_DIR}/include/ActsExamples"
)
target_include_directories(
    ActsExamplesCalorimeter
    PUBLIC
        $<BUILD_INTERFACE:${NODD_COMPONENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)
target_link_libraries(
    ActsExamplesCalorimeter
    PUBLIC Acts::Calorimeter Acts::ExamplesFramework
)
nodd_compile_headers(ExamplesCalorimeter GLOB "${NODD_COMPONENT_SOURCE_DIR}/include/**/*.hpp")

add_executable(ActsExampleCalorimeter "${NODD_COMPONENT_SOURCE_DIR}/CalorimeterExample.cpp")
target_link_libraries(ActsExampleCalorimeter PRIVATE Acts::ExamplesCalorimeter)
install(
    TARGETS ActsExampleCalorimeter
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
