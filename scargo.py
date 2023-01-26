#!/usr/bin/env python

# This executable script is a thin wrapper around the main functionality
# in the scargo Python package

import contextlib
import os
import sys

if os.name != "nt":
    # Linux/macOS: remove current script directory to avoid importing this file
    # as a module; we want to import the installed scargo module instead
    with contextlib.suppress(ValueError):
        if sys.path[0].endswith("/bin"):
            sys.path.pop(0)
        sys.path.remove(os.path.dirname(sys.executable))

    # Linux/macOS: delete imported module entry to force Python to load
    # the module from scratch; this enables importing scargo module in
    # other Python scripts
    with contextlib.suppress(KeyError):
        del sys.modules["scargo"]

import scargo

if __name__ == "__main__":
    scargo.cli()
