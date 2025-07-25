"""Global values for scargo"""

import importlib.util
from pathlib import Path

DESCRIPTION = "C/C++ package and software development life cycle manager based on RUST cargo idea."

spec = importlib.util.find_spec("scargo")
SCARGO_PKG_PATH = Path(spec.origin).parent if spec and spec.origin else Path(__file__).parent
SCARGO_DEFAULT_BUILD_ENV = "docker"
SCARGO_DOCKER_ENV = "docker"

SCARGO_LOCK_FILE = "scargo.lock"
SCARGO_DEFAULT_CONFIG_FILE = "scargo.toml"
ENV_DEFAULT_NAME = ".env"

SCARGO_HEADER_EXTENSIONS_DEFAULT = (".h", ".hpp", ".hxx", ".hh", ".inc", ".inl")
SCARGO_SRC_EXTENSIONS_DEFAULT = (".c", ".cpp", ".cxx", ".cc", ".s", ".S", ".asm")

SCARGO_UT_COV_FILES_PREFIX = "ut-coverage"
