# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

cmake_minimum_required(VERSION 3.14)
set(INTERNAL_NAME {{name}})

AUX_SOURCE_DIRECTORY(${CMAKE_CURRENT_SOURCE_DIR} WILDCARD_SRC)
add_library(${INTERNAL_NAME}
	${WILDCARD_SRC}
)

target_link_libraries(${INTERNAL_NAME}
  	PUBLIC
		cmocka
		gcov
		gtest
		gtest_main
		gmock
		StaticMock
)

target_include_directories(${INTERNAL_NAME}
    INTERFACE
        ${CMAKE_CURRENT_SOURCE_DIR}
    )
