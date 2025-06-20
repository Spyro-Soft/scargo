add_executable(ut_pow3)

add_test(NAME ut_pow3 COMMAND ut_pow3)

target_sources(ut_pow3 PRIVATE ut_pow3.cpp)

target_include_directories(ut_pow3
    PRIVATE
        ${PROJECT_ROOT_DIR}/src
        ${PROJECT_ROOT_DIR}/main
        ${PROJECT_ROOT_DIR}/third_party
)
