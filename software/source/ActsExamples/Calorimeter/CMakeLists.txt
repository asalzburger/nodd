cmake_minimum_required(VERSION 3.24)
project(NoddCalorimeterIO LANGUAGES CXX)

# Standalone consumer of an existing ACTS build; never inject into or rebuild it.
set(NODD_ACTS_SOURCE "" CACHE PATH "Pristine ACTS source matching runtime355ea684")
set(NODD_ACTS_BUILD "" CACHE PATH "Existing matching ACTS build; never modified")
find_package(Git REQUIRED)
execute_process(COMMAND "${GIT_EXECUTABLE}" -C "${NODD_ACTS_SOURCE}" rev-parse HEAD
  OUTPUT_VARIABLE NODD_ACTS_REVISION OUTPUT_STRIP_TRAILING_WHITESPACE
  COMMAND_ERROR_IS_FATAL ANY)
if(NOT NODD_ACTS_REVISION STREQUAL "355ea68493b326956756c9386d2fd9eaf9328568")
  message(FATAL_ERROR "Calorimeter I/O requires ACTS355ea684; got ${NODD_ACTS_REVISION}")
endif()
execute_process(COMMAND "${GIT_EXECUTABLE}" -C "${NODD_ACTS_SOURCE}" diff --quiet HEAD
  RESULT_VARIABLE NODD_ACTS_SOURCE_DIRTY)
if(NOT NODD_ACTS_SOURCE_DIRTY EQUAL 0)
  message(FATAL_ERROR "Calorimeter I/O requires unmodified tracked ACTS source")
endif()
# Match the existing build's configured source to the checked pin.
if(NOT EXISTS "${NODD_ACTS_BUILD}/CMakeCache.txt")
  message(FATAL_ERROR "NODD_ACTS_BUILD must identify an existing configured ACTS build")
endif()
load_cache("${NODD_ACTS_BUILD}" READ_WITH_PREFIX NODD_BUILD_ CMAKE_HOME_DIRECTORY)
file(REAL_PATH "${NODD_ACTS_SOURCE}" NODD_ACTS_SOURCE_REAL)
file(REAL_PATH "${NODD_BUILD_CMAKE_HOME_DIRECTORY}" NODD_BUILD_SOURCE_REAL)
if(NOT NODD_BUILD_SOURCE_REAL STREQUAL NODD_ACTS_SOURCE_REAL)
  message(FATAL_ERROR "ACTS build/source mismatch: ${NODD_BUILD_CMAKE_HOME_DIRECTORY}")
endif()
find_package(Eigen3 CONFIG REQUIRED)
find_package(Boost CONFIG REQUIRED)
find_package(TBB CONFIG REQUIRED)
find_package(nlohmann_json CONFIG REQUIRED)
find_package(EDM4HEP 1.0 CONFIG REQUIRED)
find_package(podio 1.7 CONFIG REQUIRED)

foreach(component Core ExamplesFramework ExamplesIoPodio)
  find_library(NODD_ACTS_${component} NAMES Acts${component}
    PATHS "${NODD_ACTS_BUILD}/lib" NO_DEFAULT_PATH REQUIRED)
  add_library(nODDActs${component} SHARED IMPORTED)
  set_target_properties(nODDActs${component} PROPERTIES
    IMPORTED_LOCATION "${NODD_ACTS_${component}}")
endforeach()
target_include_directories(nODDActsCore INTERFACE
  "${NODD_ACTS_SOURCE}/Core/include" "${NODD_ACTS_BUILD}/Core/include")
target_link_libraries(nODDActsCore INTERFACE Eigen3::Eigen Boost::headers
  nlohmann_json::nlohmann_json)
target_include_directories(nODDActsExamplesFramework INTERFACE
  "${NODD_ACTS_SOURCE}/Examples/Framework/include"
  "${NODD_ACTS_SOURCE}/Plugins/FpeMonitoring/include")
target_link_libraries(nODDActsExamplesFramework INTERFACE nODDActsCore TBB::tbb)
target_include_directories(nODDActsExamplesIoPodio INTERFACE
  "${NODD_ACTS_SOURCE}/Examples/Io/Podio/include"
  "${NODD_ACTS_SOURCE}/Plugins/EDM4hep/include")
target_link_libraries(nODDActsExamplesIoPodio INTERFACE
  nODDActsExamplesFramework podio::podio EDM4HEP::edm4hep)

add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../../EDM" "EDM")
add_library(nODDCalorimeterAlgorithms
  src/CalorimeterDigitizationAlgorithm.cpp src/CalorimeterClusteringAlgorithm.cpp)
target_compile_features(nODDCalorimeterAlgorithms PUBLIC cxx_std_20)
target_include_directories(nODDCalorimeterAlgorithms PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>)
target_link_libraries(nODDCalorimeterAlgorithms PUBLIC nODD::EDM nODDActsExamplesFramework)
set_target_properties(nODDCalorimeterAlgorithms PROPERTIES
  BUILD_RPATH "${NODD_ACTS_BUILD}/lib")
add_subdirectory(EDM4hep)

include(CTest)
if(BUILD_TESTING)
  add_subdirectory(tests)
endif()
