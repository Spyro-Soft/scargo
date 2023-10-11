.. _scargo_stm32:

STM32 support in scargo
=======================

Creating a project
------------------
::

    scargo new --target stm32 --chip <stm32...> [project_name]

Configure STM32 project
------------------------
To configure your project for chosen STM32 chipset use --chip when initializing the project.
It's also possible to change it in scargo.toml file in **[stm32]** section and run scargo update.

Add and use the external dependencies
-------------------------------------
Some of the external dependencies such as CMSIS or HAL are added to the project configuration by default. They will be managed by conan.
Please check the stm32-cmake project to get knowledge how to use HAL and CMSIS dependencies (https://github.com/ObKo/stm32-cmake#hal)
To use it in your cmake libraries please add proper includes in target_link_libraries to your CMakeLists.txt file as in the following example:
::

    target_link_libraries(${PROJECT_NAME}
        CMSIS::STM32::${STM32_TYPE}
        HAL::STM32::${STM32_FAMILY}::PWREx
        HAL::STM32::${STM32_FAMILY}::RCC
        HAL::STM32::${STM32_FAMILY}::RCCEx
        HAL::STM32::${STM32_FAMILY}::CORTEX
        bsp
    )

Generate a certs
---------------------
Generate certs needed by azure base on dev id
::

    scargo gen --certs <dev id as string>

It will generate certs in build/certs/fs dir. This cert should be used in two-way authentication with azure IoTHub.
