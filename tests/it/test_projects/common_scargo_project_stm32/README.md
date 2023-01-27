# Overview

<Add project overview here>

# Set the docker environment

`scargo update`

# Run docker environment

`scargo docker run`

# Basic work with project

scargo clean -> scargo build -> scargo check -> scargo test

- `build`: Compile the project.
- `clean`: Clean build directory.
- `check`: Check sources.
- `fix`: Fix problems reported by chosen checkers in the source directory.
- `doc`: Generate project documentation.
- `docker`: Manage the docker environment for your project.
- `publish`: Publish lib or binary to conan artifactory.
- `update`: Read scargo.toml and generate CMakeLists.txt.
- `gen`: Generate certificate and other artifacts for chosen targets

First position yourself in the project directory.

IMPORTANT! If you make any changes to the configuration in the scargo.toml file, then scargo update` command needs to be triggered to apply those changes to the project.

## Publish lib or bin using conan

Please set the `CONAN_LOGIN_USERNAME=""` and `CONAN_PASSWORD=""` parameters in .devcontainer/.env file with your conan credential.
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
- docker-compose version 1.29.2

