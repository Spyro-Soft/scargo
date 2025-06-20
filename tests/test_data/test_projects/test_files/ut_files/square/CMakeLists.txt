add_executable(ut_square)

add_test(NAME ut_square COMMAND ut_square)

target_sources(ut_square PRIVATE ut_square.cpp)

target_include_directories(ut_square
    PRIVATE
        ${PROJECT_ROOT_DIR}/src
        ${PROJECT_ROOT_DIR}/main
        ${PROJECT_ROOT_DIR}/third_party
)
