Contributing to scargo
======================

This guide assumes working on Linux with ``apt`` package manager.

All shell commands should be executed in the ``scargo`` repository root, unless stated otherwise.


Install dependencies
--------------------

While ``scargo`` can run in a docker container with all its dependencies,
for testing and debugging it's often beneficial to have it working without docker.
In order to use ``scargo`` without docker in a new project,
you need to pass the ``--no-docker`` option to ``scargo new``.

Look through the ``ci/Dockerfile`` and install all packages from ``apt install`` and ``apt-get install`` lines.

Install scargo in editable mode with dev dependencies enabled:

    ::

        pip install -e .[dev]

It's also strongly recommended to install pre-commit:

    ::

        pip install pre-commit
        pre-commit install


Dev setup for docker
--------------------

In some cases it's not possible to avoid working with a docker setup.
By default, ``scargo`` is installed in docker from the PyPI repository,
which makes it impossible to include local changes.
You can override it by setting the ``SCARGO_DOCKER_INSTALL_LOCAL``
environment variable to the location of the wheel package
(which can be generated with ``flit build``). e.g.:

    ::

        export SCARGO_DOCKER_INSTALL_LOCAL=dist/scargo-1.1.0-py3-none-any.whl


With this variable in the environment, any new or updated project will use the local wheel package.


Running tests
-------------

To run tests you can use the ``run.py`` script:

    ::

        ./run.py -u  # run unit tests
        ./run.py -t  # run integration tests

You can also run them directly with ``pytest``:

    ::

        pytest tests/ut  # run unit tests
        pytest tests/it  # run integration tests

