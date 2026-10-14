set(unittest_extra_libraries Acts::Calorimeter Acts::ExamplesCalorimeter)
add_unittest(CalorimeterResponse "${NODD_COMPONENT_SOURCE_DIR}/CalorimeterResponseTests.cpp")
add_unittest(CalorimeterClustering "${NODD_COMPONENT_SOURCE_DIR}/CalorimeterClusteringTests.cpp")
add_test(NAME CalorimeterExample COMMAND ActsExampleCalorimeter)
add_dependencies(unit_tests ActsExampleCalorimeter)
if(NODD_BUILD_CALORIMETER_JETS)
    list(APPEND unittest_extra_libraries Acts::ExamplesCalorimeterJets)
    add_unittest(CalorimeterJets "${NODD_COMPONENT_SOURCE_DIR}/CalorimeterJetsTests.cpp")
    add_test(NAME CalorimeterJetExample COMMAND ActsExampleCalorimeterJets)
    add_dependencies(unit_tests ActsExampleCalorimeterJets)
endif()
if(NODD_BUILD_CALORIMETER_EDM4HEP)
    list(APPEND unittest_extra_libraries Acts::ExamplesCalorimeterEDM4hep)
    add_unittest(CalorimeterEDM4hep "${NODD_COMPONENT_SOURCE_DIR}/CalorimeterEDM4hepTests.cpp")
    add_unittest(CalorimeterEDM4hepReconstruction "${NODD_COMPONENT_SOURCE_DIR}/CalorimeterEDM4hepReconstructionTests.cpp")
    target_include_directories(
        ActsUnitTestCalorimeterEDM4hep
        PRIVATE ${NODD_ACTS_EXAMPLES_SOURCE}/Calorimeter/EDM4hep
    )
    target_include_directories(
        ActsUnitTestCalorimeterEDM4hepReconstruction
        PRIVATE ${NODD_ACTS_EXAMPLES_SOURCE}/Calorimeter/EDM4hep
    )
    add_test(
        NAME CalorimeterEDM4hepExample
        COMMAND
            ActsExampleCalorimeterEDM4hep
            ${CMAKE_BINARY_DIR}/nodd-tests/edm4hep-example
    )
    add_dependencies(unit_tests ActsExampleCalorimeterEDM4hep)
    if(NODD_BUILD_CALORIMETER_JETS)
        list(
            APPEND unittest_extra_libraries
            Acts::ExamplesCalorimeterJetsEDM4hep
        )
        add_unittest(CalorimeterEDM4hepJets "${NODD_COMPONENT_SOURCE_DIR}/CalorimeterEDM4hepJetsTests.cpp")
        target_include_directories(
            ActsUnitTestCalorimeterEDM4hepJets
            PRIVATE ${NODD_ACTS_EXAMPLES_SOURCE}/Calorimeter/EDM4hep
        )
        add_test(
            NAME CalorimeterEDM4hepJetExample
            COMMAND
                ActsExampleCalorimeterJetsEDM4hep
                ${CMAKE_BINARY_DIR}/nodd-tests/edm4hep-jet-example
        )
        add_dependencies(unit_tests ActsExampleCalorimeterJetsEDM4hep)
    endif()
endif()
