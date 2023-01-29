.. _scargo_run:

Run C/C++ project binary (x86 only)
-----------------------------------
.. image:: ../_static/scargo_flow_docker.gif
   :alt: scargo x86 flow
   :align: center

Usage
^^^^^

::

    scargo run [OPTIONS] [BIN_PARAMS]...

Description
^^^^^^^^^^^

Run scargo build and execute the binary file generated.

Parameters passed after "--" will be passed to the binary.

Options
^^^^^^^

::

-b, --bin FILE

Relative path to a binary file to run.

::

-p, --profile TEXT

Profile to run  [default: Debug]
This option specifies which profile binary should be built and run.

::

--skip-build

Skip running scargo build.
