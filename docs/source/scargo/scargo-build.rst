.. _scargo_build:

Build C/C++ project: build
---------------------------
.. image:: ../_static/scargo_clean_build_docker.svg
   :alt: scargo clean and build example
   :align: center

Usage
^^^^^
::

    scargo build [OPTIONS]

Description
^^^^^^^^^^^
Compile sources.

Options
^^^^^^^
::

-p, --profile PROFILE           [default: Debug]

This option specifies the profile. PROFILE can be Debug, Release, RelWIthDebugInfo, MinSizeRel or custom profile specified in toml.
Custom user profiles should be added under the ``[profile.(custom tag)]`` section in scargo.toml file.

If this option is not used, then the default profile is Debug.

::

-t, --target [atsam|esp32|stm32|x86]

Build project for specified target. Releavant only for multitarget projects.


::

-a, --all                      [default: False]

Build project for all targets.


::

-B, --base-dir DIRECTORY

Specify the base project path. Allows running scargo commands from any directory.

Example 1
^^^^^^^^^
Command:
::

    scargo build

**Effects:**

It will use conan to download all dependencies and build the project in build/Debug dir

NOTES: This command has the same effects as scargo build --profile Debug

Example 2
^^^^^^^^^
Command:
::

    scargo build --profile Release

**Effects:**

It will use conan to download all dependencies and build the project in build/Release dir


Note 1
^^^^^^^
scargo by default defines four profiles:

- Debug
- Release
- RelWithDebugInfo
- MinSizeRel

The user can define their own profiles.
