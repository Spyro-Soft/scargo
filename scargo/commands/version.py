# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""feature function for scargo"""
from scargo import __version__


def scargo_version() -> None:
    print(f"scargo version: {__version__}")
