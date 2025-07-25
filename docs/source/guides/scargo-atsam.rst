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
Flashing the Atmel SAM series is currently supported by using openocd in the background.
Run the :doc:`scargo flash command </scargo/scargo-flash>` to flash the board.

This flashing procedure might not work for all boards.
If you have any problems you can  `open issue on github <https://github.com/Spyro-Soft/scargo/issues/new/choose>`_.

Debugging
---------
If you plan on debugging make sure that your board has debugger or you are connected to the board using debugger.
First build the project in Debug and then you can run :doc:`scargo debug command </scargo/scargo-debug>`: ::

    scargo build --profile Debug
    scargo debug
