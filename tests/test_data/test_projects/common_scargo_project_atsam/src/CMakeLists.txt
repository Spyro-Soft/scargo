include_directories(${CMAKE_SOURCE_DIR}/${ATMEL_ARCH}_DFP/include
                    ${CMAKE_SOURCE_DIR}/CMSIS/CMSIS/Core/Include)

link_directories(${CMAKE_SOURCE_DIR}/${ATMEL_ARCH}_DFP/gcc
                 ${CMAKE_SOURCE_DIR}/${ATMEL_ARCH}_DFP/gcc/gcc)

find_file(
  STARTUP_SRC
  NAMES startup_${SAM_MCU}.c startup_${ATMEL_ARCH_LOWER}.c
  PATHS ${CMAKE_SOURCE_DIR}/${ATMEL_ARCH}_DFP/gcc
        ${CMAKE_SOURCE_DIR}/${ATMEL_ARCH}_DFP/gcc/gcc
  NO_DEFAULT_PATH)

find_file(
  SYSTEM_SRC
  NAMES system_${SAM_MCU}.c system_${ATMEL_ARCH_LOWER}.c
  PATHS ${CMAKE_SOURCE_DIR}/${ATMEL_ARCH}_DFP/gcc
        ${CMAKE_SOURCE_DIR}/${ATMEL_ARCH}_DFP/gcc/gcc
  NO_DEFAULT_PATH)

add_executable(${PROJECT_NAME}
  common_scargo_project_atsam.cpp
  ${STARTUP_SRC}
  ${SYSTEM_SRC}
)

find_file(
  LINKER_SCRIPT
  NAMES ${SAM_MCU}_flash.ld
  PATHS ${CMAKE_SOURCE_DIR}/${ATMEL_ARCH}_DFP/gcc
        ${CMAKE_SOURCE_DIR}/${ATMEL_ARCH}_DFP/gcc/gcc
  NO_DEFAULT_PATH)

target_link_options(
  ${PROJECT_NAME}
  PRIVATE
  -mthumb
  --specs=nano.specs
  -Wl,--start-group
  -lm
  -Wl,--end-group
  -Wl,--gc-sections
  -mcpu=${ARM_CPU}
  -Wl,--entry=Reset_Handler
  -T${LINKER_SCRIPT})

add_custom_command(
  TARGET ${PROJECT_NAME}
  POST_BUILD
  COMMAND ${CMAKE_OBJCOPY} -O binary $<TARGET_FILE:${PROJECT_NAME}>
          ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/${PROJECT_NAME}.bin
  BYPRODUCTS ${PROJECT_NAME}.bin
  COMMENT "Generating binary file ${PROJECT_NAME}.bin")

add_custom_command(
  TARGET ${PROJECT_NAME}
  POST_BUILD
  COMMAND ${CMAKE_OBJCOPY} -O ihex $<TARGET_FILE:${PROJECT_NAME}>
          ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/${PROJECT_NAME}.hex
  BYPRODUCTS ${PROJECT_NAME}.hex
  COMMENT "Generating hex file ${PROJECT_NAME}.hex")
