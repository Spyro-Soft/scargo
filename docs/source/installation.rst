.. _installation:

Installation and Dependencies
=============================

You will need `Python 3.8 or newer <https://www.python.org/downloads/>`_ installed on your system to use the latest version of ``scargo``.

The latest stable scargo release can be installed from `PyPI <https://pypi.org/project/scargo/>`_ via pip:

::

   $ pip install scargo

With some Python installations this may not work and you’ll receive an error, try ``python -m pip install scargo`` or ``pip3 install scargo``, or consult your `Python installation manual <https://pip.pypa.io/en/stable/installation/>`_ for information about how to access pip.

`Setuptools <https://setuptools.pypa.io/en/latest/userguide/quickstart.html>`_ is also a requirement which is not available on all systems by default. You can install it by a package manager of your operating system, or by ``pip install setuptools``.

After installing, you will have ``scargo`` installed into the default Python executables directory and you should be able to run it with the command ``scargo`` or ``python -m scargo``. Please note that probably only ``python -m scargo`` will work for Pythons installed from Windows Store.

If system does not find 'scargo' command after installing, add the installation directory to your env paths. On Ubuntu you can find installation directory by running:

::

   $ find / -name "scargo"

Then add to  PATH:

::

   $ export PATH=~/.local/bin:${PATH}
