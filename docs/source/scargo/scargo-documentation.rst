.. _scargo_documentation:

Generate documentation from project comments: doc
--------------------------------------------------

Usage
^^^^^
::

    scargo doc [OPTIONS]

Description
^^^^^^^^^^^
Generate documentation from project comments using doxygen. Comments should be in line with doxygen style

Options
^^^^^^^

::

-B, --base-dir DIRECTORY

Specify the base project path. Allows running scargo commands from any directory.

Example 1
^^^^^^^^^
Command:
::

    scargo doc

**Effects:**

Documentation will be generated in the build directory


