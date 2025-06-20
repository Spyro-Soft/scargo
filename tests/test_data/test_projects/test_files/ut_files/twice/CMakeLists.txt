add_executable(ut_twice)

add_test(NAME ut_twice COMMAND ut_twice)

target_sources(ut_twice PRIVATE ut_twice.cpp)

target_include_directories(ut_twice
    PRIVATE
        ${PROJECT_ROOT_DIR}/src
        ${PROJECT_ROOT_DIR}/main
        ${PROJECT_ROOT_DIR}/third_party
)
