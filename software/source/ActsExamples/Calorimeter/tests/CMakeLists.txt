find_package(Boost CONFIG REQUIRED COMPONENTS unit_test_framework)
set(NODD_CALORIMETER_IO_TESTS
  "${CMAKE_CURRENT_SOURCE_DIR}/../../../Calorimeter/tests")
function(nodd_calorimeter_test name source)
  add_executable(${name} "${source}")
  target_compile_definitions(${name} PRIVATE BOOST_TEST_DYN_LINK BOOST_TEST_MODULE=${name})
  target_include_directories(${name} PRIVATE
    "${NODD_ACTS_SOURCE}/Tests/CommonHelpers/include"
    "${CMAKE_CURRENT_SOURCE_DIR}/../EDM4hep" "${NODD_CALORIMETER_IO_TESTS}")
  target_link_libraries(${name} PRIVATE nODDCalorimeterEDM4hep Boost::unit_test_framework
    EDM4HEP::edm4hepDict podio::podioRootIO)
  set_target_properties(${name} PROPERTIES BUILD_RPATH "${NODD_ACTS_BUILD}/lib")
  add_test(NAME ${name} COMMAND ${name})
endfunction()
nodd_calorimeter_test(CalorimeterEDM4hep
  "${NODD_CALORIMETER_IO_TESTS}/CalorimeterEDM4hepTests.cpp")
nodd_calorimeter_test(CalorimeterEDM4hepClusters
  "${NODD_CALORIMETER_IO_TESTS}/CalorimeterEDM4hepReconstructionTests.cpp")
nodd_calorimeter_test(CalorimeterAlgorithmSkeletons
  "${CMAKE_CURRENT_SOURCE_DIR}/AlgorithmSkeletonTests.cpp")
add_test(NAME CalorimeterEDM4hepRootRoundTrip
  COMMAND nodd_calorimeter_io_fixture "${CMAKE_CURRENT_BINARY_DIR}/root-round-trip")
if(TARGET nodd_marlin_silicon_backend)
  nodd_calorimeter_test(CalorimeterSiliconDigitization
    "${CMAKE_CURRENT_SOURCE_DIR}/SiliconDigitizationTests.cpp")
  target_compile_definitions(CalorimeterSiliconDigitization PRIVATE
    NODD_SILICON_BACKEND="$<TARGET_FILE:nodd_marlin_silicon_backend>")
  add_dependencies(CalorimeterSiliconDigitization nodd_marlin_silicon_backend)
endif()
