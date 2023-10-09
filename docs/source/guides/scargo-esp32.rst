.. _scargo_esp32:

ESP32 support in scargo
=======================

Creating a project
------------------
::

    scargo new --target esp32 --chip <esp32...> [project_name]

Generate a filesystem
---------------------
All files which should be included in the filesystem must be located in the main/fs dir before the command is run.
::

    scargo gen --fs

It will generate spiffs.bin file in the build dir

Generate a certs
----------------
Generate certs needed by azure base on dev id
::

    scargo gen --certs <dev id as string>

It will generate certs in build/certs/fs dir. This cert should be used in two-way authentication with azure IoTHub.

Generate a single binary image
------------------------------
Generate the single binary image from all binary partitions.
::

    scargo gen --bin

It will generate build/flash_image.bin file. This file can be used with a Quick Emulator (qemu).

Building a project
------------------
The project can be built using both scargo build of idf.py build commands.

Configure ESP32 project
------------------------
To configure your project for chosen esp32 chipset use --chip when initializing the project.
It's also possible to change it in scargo.toml file in **[esp32]** section and run scargo update.
Presently following chips are supported 'esp32', 'esp32c2', 'esp32c3', 'esp32s2', 'esp32s3'.