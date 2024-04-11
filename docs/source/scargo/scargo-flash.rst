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

-p, --profile PROFILE           [default: Debug]


Flash base on previously built profile  [default: Debug]

::

--port DEVICE

(esp32 only) port where the target device of the command is connected to, e.g. /dev/ttyUSB0

::

-t, --target [atsam|esp32|stm32|x86]

Flash specified target. Releavant only for multitarget projects.

::

--app           [default: false]

Flash app only. Releavant only for esp32 projects.

::

--fs           [default: false]

Flash filesystem only. Relevant only for esp32 projects

::

--no-erase           [default: false]

Don't erase target memory. Relevant only for stm32 projects

::

--bank

Switch between app flash banks. If the bank is not defined then no switch action will be done. Relevant only for stm32 projects
Example usage:  scargo flash --bank 0

::

-B, --base-dir DIRECTORY

Specify the base project path. Allows running scargo commands from any directory.
