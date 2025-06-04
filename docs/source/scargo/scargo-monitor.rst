.. _scargo_monitor:

Connect and monitor the serial interface.
-----------------------------------------

Usage
^^^^^

::

    scargo monitor [OPTIONS]

Description
^^^^^^^^^^^

Connect with the device using the serial interface and provide the possibility to read and write to it.
Terminate the connection using CTRL+C.

Options
^^^^^^^

::

--port DEVICE

Port where the target device of the command is connected to, e.g. /dev/ttyUSB0

::

-b, --baudrate  [default: 115200]

Baudrate as communication speed between the scargo. [default: 115200]

::

-B, --base-dir DIRECTORY

Specify the base project path. Allows running scargo commands from any directory.
