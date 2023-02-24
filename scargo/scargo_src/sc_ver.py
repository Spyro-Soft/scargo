# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""feature function for scargo"""
from scargo.scargo_src.global_values import SCARGO_VERSION


def scargo_version() -> None:
    print(f"scargo version: {SCARGO_VERSION}")
