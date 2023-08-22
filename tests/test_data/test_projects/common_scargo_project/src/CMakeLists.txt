add_executable(common_scargo_project_path)
target_sources(common_scargo_project_path PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/common_scargo_project_path.cpp)
target_include_directories(common_scargo_project_path PRIVATE ${CMAKE_CURRENT_SOURCE_DIR} ${CONAN_LIB_DIRS})

target_link_libraries(common_scargo_project_path ${CONAN_LIBS})

