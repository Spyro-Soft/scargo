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

If system does not find 'scargo' command after installing, add the installation directory to your env paths. On Ubuntu you can find installation directory by running:

```$ pip show "scargo"```

Then add to PATH e.g.:

```$ export PATH=~/.local/bin:${PATH}```

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
1) If you create a new project, run `docker compose run scargo-dev` to run project development image depending on chosen architecture. All dependencies should be already there.
Run scargo commands as you would do natively.

2) If you create a project with --docker flag (`scargo new <my_proj> --docker ...`) or with any docker flag, by default each scargo command will be triggered in docker.

## Working natively
1) Create a project with --no-docker flag (`scargo new <my_proj> --no-docker ...`).

## Create the requirements for docker env
From version 2.3.2 the scargo is install in docker but overload by docker compose volume data, to get present version from your native env.
During deployment the requirements file is created using following command

 - `pip-compile --all-extras --output-file=ci/requirements.txt pyproject.toml`
 - `pip-compile --output-file=scargo/file_generators/templates/docker/requirements.txt.j2 pyproject.toml`

to have all newest dependencies. This solutions allow as to have scargo install in docker for ci/cd and be able to use newest features without official releases.  

## Testing custom scargo generated project locally
You can make changes in scargo and install it locally using ```pip install .``` command when you are in the main project folder.
To test the custom scargo version and have this custom scargo available also inside the docker (crucial for testing), in created project update  docker-compose.yaml:

    volumes:

      - ..:/workspace
      - /dev:/dev
      - ~/.local/lib/python3.10/site-packages/scargo:/usr/local/lib/python3.8/dist-packages/scargo

Where ```~/.local/lib/python3.10/site-packages/scargo``` is a path to scargo on your local machine. It the following path is not working, find installation dir using ```pip show scargo```.

To keep this setup between ```scargo update``` commands, in scargo.toml file update also ```update-exclude``` as in following example:

    update-exclude = [".devcontainer/docker-compose.yaml"]

# Known Issues

## MacOs with ARM processors
- On macOS devices with ARM processors (such as M1 and M3), USB device passthrough to Docker containers is not supported. While most development tasks can be performed within the Docker container, actions that involve direct interaction with USB devices, such as flashing firmware or monitoring hardware, must be executed natively on the host system.

## Windows

- On Windows devices, USB device passthrough is not supported in Docker containers when using Docker Desktop. To work around this limitation, you can use WSL2 (Windows Subsystem for Linux) or run a virtual machine with a Linux distribution like Ubuntu 22.04 to enable USB device access.


# Contributing

See contributing guide on https://spyro-soft.github.io/scargo/contributing.html
