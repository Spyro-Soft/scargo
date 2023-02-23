# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

cmake_minimum_required(VERSION 3.14)
set(INTERNAL_NAME StaticMock)

file( GLOB WILDCARD_SRC *.cpp *.h )

add_library(${INTERNAL_NAME}
    OBJECT
        ${WILDCARD_SRC}
)

target_include_directories(${INTERNAL_NAME}
    PUBLIC
        .
)
