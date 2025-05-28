scargo Documentation
====================

This is the documentation for scargo - a Python-based C/C++ package and software development life cycle manager based on RUST cargo idea.

scargo can:

* Create a new project (binary or library)
* Build the project
* Run code static analyzers
* Fix chosen problem automatically base on the checker analysis
* Run unit tests
* Generate documentation from the source code
* Work with a predefine docker environment depending on the chosen architecture


Quick Start
-----------

Getting started is easy:

1) Install ``scargo``:

    ::

        $ pip install scargo

    For detailed instructions, see :ref:`installation`.

2) Run ``scargo`` commands to create a new project:

    ::

        $ scargo new my_project_name

3) Run ``scargo`` commands to check available options:

    ::

        $ scargo --help/-h

For Windows
-----------
1) Install Python >=3.8 with pip from https://www.python.org/downloads/windows/
2) Install Docker for Windows (e.g. https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe)
3) Install scargo (``pip install scargo``) and add the program to your env paths


System Properties -> Environment Variables, double click on "Path" and add entry with your scargo installation e.g.
::

    C:\Users\username\AppData\Roaming\Python\Python38\Scripts

For Ubuntu
-----------
1) Install scargo (``pip install scargo``)
2) If system does not find 'scargo' command add the installation directory to your env paths. You can find installation directory by running:
    ::

        $ find / -name "scargo"

    Then add it to the path, e.g.:
    ::

        $ export PATH=~/.local/bin:${PATH}

More Information
----------------

.. toctree::
   :maxdepth: 1

   Installation <installation>
   Guides <guides/index>
   Reference <scargo/index>
   Troubleshooting <troubleshooting>
   Versions <versions>
   Architecture model <arch/index>
   About <about>
   Contributing <contributing>

.. =========================================================
.. Project Documentation
.. =========================================================
..  .. toctree::
..    :maxdepth: 2
..    :caption: Contents

..    main_page

.. Source code
.. ==================
.. .. autosummary::
..    :toctree: _autosummary
..    :caption: Source code:
..    :template: custom-module-template.rst
..    :recursive:

..       src

.. Test code
.. ==================
.. .. autosummary::
..    :toctree: _autosummary
..    :caption: Test code:
..    :template: custom-module-template.rst
..    :recursive:

..       test


.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`


.. Diagram example
.. ==================
.. You can easily embed diagrams in the documentation!

.. .. graphviz::

..    digraph foo {
..       "bar" -> "baz";
..    }
