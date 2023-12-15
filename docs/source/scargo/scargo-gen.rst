.. _scargo_gen:

Generate C/C++ project source code or artifacts
-----------------------------------------------

Usage
^^^^^
::

    scargo gen [OPTIONS] [PARAM]

Description
^^^^^^^^^^^

Manage the auto files generator

Options
^^^^^^^
::

-p, --profile TEXT

Profile to run  [default: Debug]
This option specifies which profile binary should be built and run.

::

    -u, --unit-test FILE

Generate a unit test skeleton with in tests/ut folder with a path mirroring the sources. The file is a path to the source file to which we would like to gen ut

::

    -m, --mock FILE

Generate mock of the chosen file. The .h or .hpp file shall be used. It will then generate mock in tests/mock folder with a path mirroring the sources.

::

    -c, --certs <DEVICE ID>

Generate certs for azure IoTHub.

::

    -t, --type [all, device]

Mode for generating certificates.

::

    -i, --in PATH

Directory with root and intermediate certificates.

::

    -p, --passwd <PASSWORD>

 Password to be set for generated certificates.

::

    -f, --fs

(Only for uC) Build the filesystem, based on spiffs dir content.
For esp32 file, the system will be generated based on the interior of main/fs dir.


::

    -b, --bin

(Only for uC) Generate the single binary image from all binary partitions.
For esp32 file, the system will generate build/flash_image.bin file

::

    -B, --base-dir DIRECTORY

Specify the base project path. Allows running scargo commands from any directory.
