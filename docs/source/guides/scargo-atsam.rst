.. _scargo_atsam:

Atmel SAM support in scargo
===========================

Creating a project
------------------
::

    scargo new --target atsam --chip <atsam...> [project_name]


When building the project for the first time scargo will fetch CMSIS and DFP packs for your chip.
It's also possible to change the chip in *scargo.toml* file and run scargo update command to update project accordingly.

Flashing
--------
Flashing the Atmel SAM series is currently not supported, but it will be implemented

Debugging
---------
Debugging the Atmel SAM series is currently not supported, but it will be implemented
