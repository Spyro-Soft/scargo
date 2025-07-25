cmake_minimum_required(VERSION 3.22)

set(CMAKE_C_COMPILER   "gcc")
set(CMAKE_CXX_COMPILER "g++")

set(CMAKE_C_FLAGS   "-Wall -Wextra -Og --coverage -fkeep-inline-functions -fkeep-static-consts")
set(CMAKE_CXX_FLAGS "-Wall -Wextra -Og --coverage -fkeep-inline-functions -fkeep-static-consts")

project(tests LANGUAGES C CXX ASM)
enable_testing()

set(PROJECT_ROOT_DIR "${PROJECT_SOURCE_DIR}/..")
set(PROJECT_DIR "${PROJECT_SOURCE_DIR}/..")
set(PROJECT_SOURCE_DIR "${PROJECT_DIR}/main/")

message(STATUS "Project dir: ${PROJECT_DIR}")
message(STATUS "Project source dir: ${PROJECT_SOURCE_DIR}")
#build google test together with the project
execute_process(COMMAND ${CMAKE_COMMAND} . WORKING_DIRECTORY /opt/googletest)
execute_process(COMMAND ${CMAKE_COMMAND} --build . WORKING_DIRECTORY /opt/googletest)

add_subdirectory(mocks)
add_subdirectory(ut)
add_subdirectory(it)