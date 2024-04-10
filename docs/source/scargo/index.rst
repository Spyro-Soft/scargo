.. _scargo:

scargo commands
===============

Use ``scargo -h`` to see a summary of all available commands and command line options.

To see all options for a particular command, append ``-h`` to the command name. ie ``scargo build -h``.
::

   Usage: scargo [OPTIONS] COMMAND [ARGS]...

   C/C++ package and software development life cycle manager based on RUST
   cargo idea.

   Options:
   --install-completion Install completion for the current shell.
   --show-completion    Show completion for the current shell, to copy it or
                        customize the installation.
   -h, --help           Show this message and exit.

   Commands:
   build               Compile sources.
   check               Check source code in the directory `src`.
   clean               Remove directory `build`.
   debug               Use gdb CLI to debug
   doc                 Create project documentation
   docker              Manage the docker environment for the project
   fix                 Fix violations reported by the command `check`.
   flash               Flash the target.
   monitor             Connect and monitor the serial interface.
   gen                 Manage the auto file generator
   new                 Create a new project template.
   publish             Upload conan pkg to repo
   run                 Build and run project
   setup_autocomplete  Setup scargo autocomplete for shell
   test                Compile and run all tests in directory `test`.
   update              Read .toml config file and generate `CMakeLists.txt`.
   version             Get scargo version


Scargo commands reference
-------------------------

.. toctree::
   :maxdepth: 1

   Build command <scargo-build>
   Check command <scargo-check>
   Clean command <scargo-clean>
   Debug command <scargo-debug>
   Doc command <scargo-documentation>
   Docker command <scargo-docker>
   Fix command <scargo-fix>
   Flash command <scargo-flash>
   Monitor command <scargo-monitor>
   Gen command <scargo-gen>
   New command <scargo-new>
   Publish command <scargo-publish>
   Run command <scargo-run>
   Test command <scargo-test>
   Update command <scargo-update>
   Version command <scargo-version>


See also
--------

.. toctree::
   :maxdepth: 1

   Scargo Toml file configuration <scargo-toml>

