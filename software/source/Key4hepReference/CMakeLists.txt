cmake_minimum_required(VERSION 3.24)
project(nODDKey4hepReference LANGUAGES CXX)
include(GNUInstallDirs)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)
set(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_LIBDIR}")
find_package(Gaudi REQUIRED)
find_package(k4FWCore 1.3 REQUIRED)
find_package(EDM4HEP REQUIRED)
find_package(DD4hep REQUIRED COMPONENTS DDCore DDRec DDG4)
find_package(Geant4 REQUIRED)
find_package(ROOT REQUIRED COMPONENTS Core Hist)
find_package(CLHEP REQUIRED CONFIG)
get_filename_component(SUBMODULES "${CMAKE_CURRENT_LIST_DIR}/../../submodules" ABSOLUTE)
# Compile the complete upstream algorithms and their upstream Gaudi registration.
# The other k4RecCalorimeter packages need unrelated reconstruction dependencies.
add_subdirectory("${SUBMODULES}/k4RecCalorimeter/RecCaloDigi" RecCaloDigi)
# GeoSvc is owned by k4SimGeant4, not k4FWCore. Build its original implementation
# without the unrelated simulation actions and detector factories.
set(GEOSVC "${SUBMODULES}/k4SimGeant4/Detector/DetComponents/src")
gaudi_add_module(nODDReferenceGeoPlugins
  SOURCES "${GEOSVC}/GeoSvc.cpp" "${GEOSVC}/GeoConstruction.cpp"
  LINK Gaudi::GaudiKernel k4FWCore::k4FWCore k4FWCore::k4Interface
       DD4hep::DDCore DD4hep::DDRec DD4hep::DDG4 ${Geant4_LIBRARIES})
target_include_directories(nODDReferenceGeoPlugins PRIVATE ${Geant4_INCLUDE_DIRS})
install(TARGETS nODDReferenceGeoPlugins LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}")
install(EXPORT k4RecCalorimeterTargets NAMESPACE k4RecCalorimeter::
        DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/nODDKey4hepReference")
