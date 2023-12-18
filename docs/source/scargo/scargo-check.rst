.. _scargo_check:

Check C/C++ project with static tool analyzers: check
-----------------------------------------------------
.. image:: ../_static/scargo_check_fix_docker.svg
   :alt: scargo check and fix example
   :align: center

Usage
^^^^^

::

    scargo check [OPTIONS]

Description
^^^^^^^^^^^

Check source code in directory src and all subdirectories and report warnings and errors.
With no params scargo will perform all checks and exist on the first failing.

Options
^^^^^^^

::

--clang-format

Run clang-format.

::

--clang-tidy

Run clang-tidy.

::

--copyright

Check if there is copyright info at the top of each file. Uses description filed from [check.copyright] section from the project config file.

::

--cppcheck

Run cppcheck.

::

--cyclomatic

Run python-lizard.

::

--pragma

Check if there is #pragma once at the top of each header file.

::

--todo

Check if there is TODO in any file.

::

--silent

Show less output.

::

-B, --base-dir DIRECTORY

Specify the base project path. Allows running scargo commands from any directory.

Exclusions
^^^^^^^^^^
There is a possibility to exclude directories or single files from all checkers or from particular checkers only.
To exclude the dir or file from all checkers please add the relative path in the [check] section
::

    [check]
    exclude = [<my exclude path e.g src/bsp>]

To exclude dir or file from a particular checker only please add the relative path in this checker section e.g:
::

    [check.pragma]
    exclude = [<my exclude path e.g src/bsp>]
