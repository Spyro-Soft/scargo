.. _scargo_clean:

Clean C/C++ project artifacts
-----------------------------
.. image:: ../_static/scargo_clean_build_docker.gif
   :alt: scargo clean and build example
   :align: center

Usage
^^^^^
::

    scargo clean [OPTIONS]

Description
^^^^^^^^^^^

Remove directory build.

Options
^^^^^^^

::

-B, --base-dir Arg

Specify the base project path. Allows running scargo commands from any directory.

Example
^^^^^^^

Command:
::

    scargo clean

**Effects:**

Removes directory build

Removes directory test/build