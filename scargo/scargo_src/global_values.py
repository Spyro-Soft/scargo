# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Global values for scargo"""
import pkgutil
from pathlib import Path

DESCRIPTION = "C/C++ package and software development life cycle manager based on RUST cargo idea."

SCARGO_PGK_PATH = (
    Path(pkgutil.get_loader("scargo").path).parent
    if pkgutil.get_loader("scargo").path
    else Path(Path(__file__).absolute()).parent
)
SCARGO_DEFAULT_BUILD_ENV = "docker"
SCARGO_DOCKER_ENV = "docker"

SCARGO_LOCK_FILE = "scargo.lock"
SCARGO_DEFAULT_CONFIG_FILE = "scargo.toml"
ENV_DEFAULT_NAME = ".env"
