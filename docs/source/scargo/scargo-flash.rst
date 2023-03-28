.. _scargo_flash:

Flash using generated C/C++ project
-----------------------------------

Usage
^^^^^

::

    scargo flash [OPTIONS]

Description
^^^^^^^^^^^

Flash what is available to be flashed. This option is the default if no other options are specified.

Options
^^^^^^^
::

--app

Flash app only

::

--fs

Flash filesystem only

::

--profile TEXT

Flash base on previously built profile  [default: Debug]

::

-B, --base-dir Arg

Specify the base project path. Allows running scargo commands from any directory.
