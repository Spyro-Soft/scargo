# Scargo 
Scargo project was written by Spyrosoft team. Find more information at [spyro-soft.com](https://spyro-soft.com/career).

# Overview
This is the documentation for scargo - a Python-based package manager based on RUST cargo idea.

scargo can:

- Create a new project (binary or library)
- Build the project
- Run static code analyzers
- Fix chosen problem automatically based on the checker analysis
- Run unit tests
- Generate documentation from the source code
- Work with the predefined docker environment depending on the chosen architecture

# Installation
To install scargo with pip in your top directory run `pip install -e .[dev]`

To prepare docker development environment run `./ci/setup.sh`

# Working with scargo

* `new`: Create new scargo project template.
* `update`: Read scargo.toml and generate CMakeLists.txt.
* `build`: Compile project.
* `clean`: Clean build directory.
* `check`: Check sources.
* `fix`: Fix problems reported by chosen checkers in source directory.
* `doc`: Generate project documentation.
* `docker`: Manage docker environment for your project.

First enter the working directory.

We are going to create a new project. There can be multiple bin but only one lib.
Project will be named `expro` and it will have two targets.
One target is an executable with name `foo`.
Another target is a library with name `bar`.
The command is:

    $ scargo new expro --bin foo --lib bar

This command creates directory `expro` and template files inside.

Enter this directory:

    $ cd expro

The content of this directory:

    $ tree
    .
    ├── CMakeLists.txt
    ├── conanfile.py
    ├── LICENSE
    ├── README.md
    ├── scargo.lock
    ├── scargo.toml
    ├── src
    │   ├── bar.cpp
    │   ├── bar.h
    │   ├── CMakeLists.txt
    │   └── foo.cpp
    └── tests
        ├── CMakeLists.txt
        ├── it
        │   └── CMakeLists.txt
        ├── mocks
        │   ├── CMakeLists.txt
        │   └── static_mock
        │       ├── CMakeLists.txt
        │       └── static_mock.h
        └── ut
            └── CMakeLists.txt
    
    6 directories, 16 files

Please look into file `scargo.toml`.

To generate or update the `CMakeLists.txt` of new options from toml file:

    $ scargo update

Compile project:

    $ scargo build

This compiles project in debug mode. Output files are in `build/Debug` directory.

If you'd like to build in release mode:

    $ scargo build --profile Release

Output files are in `build/Release` directory.

To clean build directory:

    $ scargo clean

# Project dependencies
## Working with docker (recommended)
- docker
- docker-compose version 1.29.2
- pip
- python3

## Working natively (not recommended, a lot of env setup)
Base:

- python >= 3.8
- cmake >= 3.24.2
- cppcheck bzr lib32z1 clang clang-format clang-tidy valgrind gcovr doxygen curl libcurl4-openssl-dev libcmocka0 libcmocka-dev
- lizard

Depending on the architecture:

- compiler (e.g. gcc-arm-none-eabi-9-2020-q2-update gcc-arm-none-eabi)
- flashing tools
- uC HAL and dependent files 
- much more....

# Work environment
You can always change work environment between docker or native after project is created.
Just edit the scargo.toml file ([project] -> build-env = "docker" or build-env = "native").

## Working in docker
1) If you create a new project, run `docker-compose run scargo-dev` to run project development image depending on chosen architecture. All dependencies should be already there.
Run scargo commands as you would do natively.

2) If you create a project with --docker flag (`scargo new <my_proj> --docker ...`) or with any docker flag, by default each scargo command will be triggered in docker. 

## Working natively
1) Create a project with --no-docker flag (`scargo new <my_proj> --no-docker ...`). 
