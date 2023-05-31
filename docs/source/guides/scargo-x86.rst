.. _scargo_x86:

Creating and working with x86 cpp project
=========================================
.. image:: ../_static/scargo_flow_docker.svg
   :alt: scargo x86 flow
   :align: center

Creating x86 cpp project
------------------------


To create *Hello world* x86 cpp project we will use :doc:`scargo new command </scargo/scargo-new>`:

Open the command line and run: ::

    scargo new --target x86 --bin hello_world hello_world_project

This will create a new dockerized x86 cpp project inside hello_world_project directory.
If you want to create a native project you can add *--no-docker* argument.

This is how the project directory will look like: ::

    └── hello_world_project
        ├── CMakeLists.txt
        ├── conanfile.py
        ├── LICENSE
        ├── README.md
        ├── scargo.lock
        ├── scargo.toml
        ├── src
        │   ├── CMakeLists.txt
        │   └── hello_world.cpp
        └── tests
            ├── CMakeLists.txt
            ├── it
            │   └── CMakeLists.txt
            ├── mocks
            │   ├── CMakeLists.txt
            │   └── static_mock
            │       ├── CMakeLists.txt
            │       └── static_mock.h
            └── ut
                └── CMakeLists.txt


For scargo the most important file is *scargo.toml*. This is the file in which you write your project configuration.
If you want to update some settings in *scargo.toml* make sure you run scargo update command to update the project with
the newly modified configuration.

More on this can be read in :doc:`/scargo/scargo-toml`

Building the project
--------------------

To build the project we can change into project directory and run :doc:`scargo build command </scargo/scargo-build>`.
Let's run the build command and build our project in *Release* ::

    cd hello_world_project
    scargo build --profile Release

By default, scargo builds in *Debug*, but you can switch it by running it with --profile argument (e.g. --profile=Release).
Scargo will use conan to download all necessary dependencies and build the project.
After the build is finished we should see that *build/Release* directory was created and the build files are inside.

Running the binary
------------------

To run the binary we can simply use :doc:`scargo run command </scargo/scargo-run>`: ::

    scargo run --profile Release --skip-build

After running the command we will see *Hello world!* text in the terminal.
If the project wasn't built for the profile that we want to run, scargo will automatically build it first.

Debugging
---------

Scargo also supports debugging through gdb cli. We will first build our project in Debug and then we can run :doc:`scargo debug command </scargo/scargo-debug>`: ::

    scargo build --profile Debug
    scargo debug

