# Scargo
Scargo project was written by Spyrosoft team. Find more information at [spyro-soft.com](https://spyro-soft.com/career).
<p align="center">
    <img src="https://raw.githubusercontent.com/Spyro-Soft/scargo/develop/docs/source/_static/spyrosoft_solutions_logo_color.png" alt="drawing" width="200"/>
</p>

# Overview
This is the documentation for scargo - a Python-based C/C++ package and software development life cycle manager inspired by RUST cargo idea.

scargo can:

- Create a new project (binary or library)
- Build the project
- Run static code analyzers
- Fix chosen problem automatically based on the checker analysis
- Run unit tests
- Generate documentation from the source code
- Work with the predefined docker environment depending on the chosen architecture

# Installation
Scargo is available on [pypi](https://pypi.org/project/scargo/), so you can install it with pip:

```pip install scargo```

# Working with scargo
You can find all information on how to work with scargo on official documentation webpage: https://spyro-soft.github.io/scargo/index.html
![Scargo flow animation](https://raw.githubusercontent.com/Spyro-Soft/scargo/develop/docs/source/_static/scargo_flow_docker.svg)

# Project dependencies
## Working with docker (recommended)
- docker
- docker-compose
- pip
- python3

## Working natively (not recommended, a lot of env setup)
Base:

- python >= 3.8
- cmake >= 3.24.2
- cppcheck lib32z1 clang clang-format clang-tidy gcovr doxygen libcmocka0 libcmocka-dev
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

# Contributing

See contributing guide on https://spyro-soft.github.io/scargo/contributing.html
