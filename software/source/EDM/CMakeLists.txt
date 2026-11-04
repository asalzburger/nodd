add_library(nODDEdm INTERFACE)
add_library(nODD::EDM ALIAS nODDEdm)
target_compile_features(nODDEdm INTERFACE cxx_std_20)
target_include_directories(nODDEdm INTERFACE
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>)
target_link_libraries(nODDEdm INTERFACE nODDActsCore)
