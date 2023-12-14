.. _scargo_publish:

Publish C/C++ project lib or bin
--------------------------------

Usage
^^^^^
::

    scargo publish [OPTIONS]

Description
^^^^^^^^^^^

Publish generated library or binary to predefined conan repository. The conan repository URLs shall be added into scargo.toml file under [conan.repo]
section in following manner ``<short repo name>=<url>``

::

    my_artifactory = "https://my_artifactory/api/conan/conanlocal"


This option require the following credential to be set in .devcontainer/.env file:
::

    CONAN_LOGIN_USERNAME=""
    CONAN_PASSWORD=""

For GitLab CONAN_PASSWORD can be generated using User Settings -> Access Tokens by a set of your Token name.

Options
^^^^^^^

::

    -r --repo CONAN_REPO_NAME

Publish conan artifact to particular repo defined by its name. Should be in line with the names provided in scargo.toml file.

::

    -p, --profile PROFILE       [default: Release]

Profile to use. Uses Release profile by default if not specified.

::

    -B, --base-dir DIRECTORY

Specify the base project path. Allows running scargo commands from any directory.

Example
^^^^^^^

Command:
::

    scargo publish

**Effects:**

Push build conan artifact (such as a library) into the conan repo