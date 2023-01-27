add_executable(test_bin)
target_sources(test_bin PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/test_bin.cpp)
target_include_directories(test_bin PRIVATE ${CMAKE_CURRENT_SOURCE_DIR} ${CONAN_LIB_DIRS})

target_link_libraries(test_bin ${CONAN_LIBS})

add_library(test_lib STATIC ${CMAKE_CURRENT_SOURCE_DIR}/test_lib.cpp)
target_include_directories(test_lib PRIVATE ${CONAN_INCLUDES})
configure_file(test_lib.h ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/test_lib.h COPYONLY)

target_link_libraries(test_lib ${CONAN_LIBS})
