import os
import sys
from pathlib import Path
from typing import Optional

import tomlkit

from scargo import __version__
from scargo.config import Config, ConfigError, ScargoTarget, Target, parse_config
from scargo.global_values import SCARGO_LOCK_FILE
from scargo.logger import get_logger
from scargo.utils.docker_utils import run_scargo_again_in_docker
from scargo.utils.path_utils import get_config_file_path

logger = get_logger()


def set_up_environment_variables(config: Config) -> None:
    os.environ["SCARGO_PROJECT_ROOT"] = str(config.project_root.absolute())
    if config.project.in_repo_conan_cache:
        os.environ["CONAN_HOME"] = f"{config.project_root}/.conan2"


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
    except Exception as e:  # pylint: disable=W0718
        logger.error("Error while parsing config file %s: %s", config_file_path, e)
        sys.exit(1)

    return config


def prepare_config(run_in_docker: bool = True) -> Config:
    """
    Prepare configuration file and set up eniromnent variables

    :return: project configuration
    """
    config = get_scargo_config_or_exit()
    check_scargo_version(config)
    set_up_environment_variables(config)
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


def get_target_or_default(config: Config, target: Optional[ScargoTarget]) -> Target:
    if target:
        if target.value not in config.project.target_id:
            logger.error("Target %s not defined in scargo toml", target.value)
            sys.exit(1)
        return Target.get_target_by_id(target.value)
    return config.project.default_target
