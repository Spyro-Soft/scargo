# Configuration file for the Sphinx doc builder.
#
# This file only contains a selection of the most common options. For a full
# list see the doc:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# doc root, use os.path.abspath to make it absolute, like shown here.
#
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parents[2]))
# Extend sys.path with sources folders
src_root = Path(__file__).parents[2] / "scargo"
src_paths = [
    str(f) for f in src_root.rglob("**") if f.is_dir() and f.name != "__pycache__"
]
sys.path.extend(src_paths)

# -- Project information -----------------------------------------------------
project = "scargo"  # pylint: disable=redefined-builtin
copyright = "2022, Spyrosoft Solution S.A."  # pylint: disable=redefined-builtin
author = "Spyrosoft Solution S.A."

# The full version, including alpha/beta/rc tags
release = "1.0.0"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",  # Core library for html generation from docstrings
    "sphinx.ext.autosummary",  # Create neat summary tables
    "sphinx.ext.napoleon",  # Support for NumPy and Google style docstrings
    "sphinx.ext.viewcode",  # Add links to highlighted source code
    "sphinx.ext.doctest",  # Test code snippets in the doc
    "sphinx.ext.mathjax",  # Math support for HTML outputs
    "sphinx.ext.intersphinx",  # Generate automatic links to the doc of objects in other projects
    # "sphinx.ext.autosectionlabel",  # Auto-generate section labels.
    "sphinx.ext.inheritance_diagram",  # Include inheritance diagrams, rendered via the Graphviz
    "sphinx.ext.graphviz",  # Graphviz extension
    "recommonmark",  # Support for markdown .md style doc
    "sphinxcontrib.plantuml",
]
autosummary_generate = True  # Turn on sphinx.ext.autosummary
inheritance_graph_attrs = {"rankdir": "TB", "size": '""'}  # TB=Top to bottom view
graphviz_output_format = "svg"

plantuml_output_format = "svg"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns: List[str] = [r"modules/*.rst"]  # ignore any warning from modules

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the doc for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named 'default.css' will overwrite the builtin 'default.css'.
html_static_path = ["_static"]
html_logo = "_static/spyrosoft_solutions_logo_color.png"
