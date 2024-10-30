# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Global values for scargo"""
import importlib.util
from pathlib import Path

DESCRIPTION = "C/C++ package and software development life cycle manager based on RUST cargo idea."

spec = importlib.util.find_spec("scargo")
SCARGO_PKG_PATH = (
    Path(spec.origin).parent if spec and spec.origin else Path(__file__).parent
)
SCARGO_DEFAULT_BUILD_ENV = "docker"
SCARGO_DOCKER_ENV = "docker"

SCARGO_LOCK_FILE = "scargo.lock"
SCARGO_DEFAULT_CONFIG_FILE = "scargo.toml"
ENV_DEFAULT_NAME = ".env"
