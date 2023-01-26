"""feature function for scargo"""
from scargo.scargo_src.global_values import __version__ as ver


def scargo_version():
    print(f"scargo version: {ver}")
