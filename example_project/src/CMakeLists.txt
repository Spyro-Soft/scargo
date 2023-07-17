add_executable(example_project)
target_sources(example_project PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/example_project.cpp)
target_include_directories(example_project PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

add_library(bar STATIC)
target_sources(bar PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/bar.cpp)
target_include_directories(bar PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

