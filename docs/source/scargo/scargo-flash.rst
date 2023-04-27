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

--port DEVICE

(esp32 only) port where the target device of the command is connected to, e.g. /dev/ttyUSB0

::

--no-erase

(stm32 only) Don't erase target memory

::

-B, --base-dir Arg

Specify the base project path. Allows running scargo commands from any directory.
