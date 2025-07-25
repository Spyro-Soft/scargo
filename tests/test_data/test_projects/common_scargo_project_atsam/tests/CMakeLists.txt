cmake_minimum_required(VERSION 3.22)

set(CMAKE_C_COMPILER   "gcc")

set(CMAKE_CXX_COMPILER "g++")

set(CMAKE_CXX_STANDARD )

set(CMAKE_C_FLAGS   "-Wall -Wextra -Og --coverage -fkeep-inline-functions -fkeep-static-consts")

set(CMAKE_CXX_FLAGS "-Wall -Wextra -Og --coverage -fkeep-inline-functions -fkeep-static-consts")


project(tests LANGUAGES C CXX ASM)

find_package(GTest REQUIRED)
link_libraries(GTest::GTest GTest::Main)

enable_testing()

set(PROJECT_ROOT_DIR "${PROJECT_SOURCE_DIR}/..")

add_subdirectory(mocks)
add_subdirectory(ut)
add_subdirectory(it)