import sys
from pathlib import Path
from typing import Optional

import tomlkit

from scargo import __version__
from scargo.config import Config, ConfigError, parse_config
from scargo.docker_utils import run_scargo_again_in_docker
from scargo.global_values import SCARGO_LOCK_FILE
from scargo.logger import get_logger
from scargo.path_utils import get_config_file_path

logger = get_logger()


def get_scargo_config_or_exit(
    config_file_path: Optional[Path] = None,
) -> Config:
    """
    :param config_file_path
    :return: project configuration as dict
    """
    if config_file_path is None:
        config_file_path = get_config_file_path(SCARGO_LOCK_FILE)
    if config_file_path is None or not config_file_path.exists():
        logger.error("File `%s` does not exist.", SCARGO_LOCK_FILE)
        logger.info("Did you run `scargo update`?")
        sys.exit(1)

    try:
        config = parse_config(config_file_path)
    except ConfigError as e:
        logger.error(e.args[0])
        sys.exit(1)

    if compiler_warning := config.project.get_compiler_warning():
        logger.warning(compiler_warning)
    return config


def prepare_config(run_in_docker: bool = True) -> Config:
    """
    Prepare configuration file

    :return: project configuration
    """
    config = get_scargo_config_or_exit()
    check_scargo_version(config)
    if run_in_docker:
        run_scargo_again_in_docker(config.project, config.project_root)
    return config


def check_scargo_version(config: Config) -> None:
    """
    Check scargo version

    :param Config config: project configuration
    :return: None
    """
    version_lock = config.scargo.version
    if __version__ != version_lock:
        logger.warning("Warning: scargo package is different then in lock file")
        logger.info("Run scargo update")


def add_version_to_scargo_lock(scargo_lock: Path) -> None:
    """
    :return: project configuration as dict
    """
    with open(scargo_lock, encoding="utf-8") as scargo_lock_file:
        config = tomlkit.load(scargo_lock_file)

    config.setdefault("scargo", tomlkit.table())["version"] = __version__
    with open(scargo_lock, "w", encoding="utf-8") as scargo_lock_file:
        tomlkit.dump(config, scargo_lock_file)
