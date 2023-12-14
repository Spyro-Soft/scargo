.. _scargo_docker:

Manage docker environment: docker
----------------------------------

Usage
^^^^^
::

    scargo docker [OPTIONS] COMMAND [ARGS]...

Description
^^^^^^^^^^^
Manage docker environment. For a list of supported OPTIONS please refer to official docker documentation of corresponding SUBCOMMAND.

Common Options
^^^^^^^^^^^^^^

::

-B, --base-dir DIRECTORY

Specify the base project path. Allows running scargo commands from any directory.

Subcommands
^^^^^^^^^^^
::

    build

Build the docker environment for the chosen architecture

::

    exec

Attach to existing docker environment

::

    run

Run the docker environment bash console for this project architecture

Options
^^^^^^^

-c, --command "TEXT"

[default: bash]

Quoted text, used to select command which will be executed with `docker run`

::

    exec

Works like ``docker exec`` command. Attach to the existing container, if multiple containers were created then attach to the newest created.

Example 1
^^^^^^^^^
Command:
::

    scargo docker build

**Effects:**

::

    $ docker images


User dockerfile extension
^^^^^^^^^^^^^^^^^^^^^^^^^
The user can add a layer to the existing project docker setup. User can point to the folder where the dockerfile exist and it will be built as a custom layer in the project docker environment.

To do that user should set a relative path to the project folder of *docker_context* parameter in scargo.toml file where the custom Dockerfile is located. E.g. setup can be found below:
::

    docker-file = ".devcontainer/Dockerfile-custom"


IMPORTANT: The custom layer should be a single file and *must not* start with the following lines to properly link with previously build base layers:
::

    FROM <docker origin image>

To apply the changes please use
::

    scargo update

Adding display handling to the docker
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To add display handling to the docker firstly in scargo.toml add .devcontainer/docker-compose.yaml path to
as follow:
::

    update-exclude = [
    ".devcontainer/docker-compose.yaml"
    ]

Then modify ".devcontainer/docker-compose.yaml as presented below:
::

    volumes:
      - ..:/workspace
      - /tmp/.X11-unix:/tmp/.X11-unix
      - ~/.Xauthority:/root/.Xauthority
      - /dev:/dev
    environment:
      DISPLAY: ${DISPLAY}
      XAUTHORITY: ${XAUTHORITY}
