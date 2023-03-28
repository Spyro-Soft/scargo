# Overview

<Add project overview here>

# Set docker environment

`scargo update`

# Run docker environment

`scargo docker run`

# Basic work with project

scargo clean -> scargo build -> scargo check -> scargo test

- `build`: Compile project.
- `clean`: Clean build directory.
- `check`: Check sources.
- `fix`: Fix problems reported by chosen checkers in source directory.
- `doc`: Generate project documentation.
- `docker`: Manage docker environment for you project.
- `publish`: Publish lib or binary to conan artifactory.
- `update`: Read scargo.toml and generate CMakeLists.txt.
- `gen`: Generate certificate and other artifacts for chosen targets
- `flash`: flash microcontroller board

First position yourself into working directory.

IMPORTANT! if you make any changes of configuration in scargo.toml file then `scargo update` command need to be trigger to apply those changes into the project.

## Publish lib or bin using conan

Please set the `CONAN_LOGIN_USERNAME=""` and `CONAN_PASSWORD=""` parameter in .devcontainer/.env file with you conan credential.
and run:

`scargo docker build`
or
`cd .devcontainer && docker-compose build`

to update the environment with your credential.

# Project dependencies

## Working with docker (recommended)

- python3
- pip
- scargo
- docker
- docker-compose

# STM32 configure
External dependencies are delivered with conan package "stm32_cmake/0.1.0" . It consist of cmsis and HAL from stm.
Presently only L4, F4 and F7 series are supported. Those dependencies can be refer using:
`${CONAN_STM32_CMAKE_ROOT}`
To get the conan build time dependencies into your project it is recommended to use CMake FetchContent functionality.
Model of the microcontroller is taken from the model set in scargo.toml file e.g.:  
`[stm32] -> chip = "STM32L496AGI6"`

## Debug

### debug in console

openocd gdb

### debug in vsc

- run debug in vscode
