# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Update project"""
import shutil
import subprocess
from pathlib import Path

from scargo import __version__ as ver
from scargo.jinja.cicd_gen import generate_cicd
from scargo.jinja.cmake_gen import generate_cmake
from scargo.jinja.conan_gen import generate_conanfile
from scargo.jinja.docker_gen import generate_docker_compose
from scargo.jinja.env_gen import generate_env
from scargo.jinja.readme_gen import generate_readme
from scargo.jinja.tests_gen import generate_tests
from scargo.scargo_src.global_values import (
    SCARGO_DOCKER_ENV,
    SCARGO_LOCK_FILE,
    SCARGO_PGK_PATH,
)
from scargo.scargo_src.sc_docker import scargo_docker
from scargo.scargo_src.sc_logger import get_logger
from scargo.scargo_src.sc_src import check_scargo_version, get_scargo_config_or_exit
from scargo.scargo_src.utils import get_project_root


def copy_file_if_not_exists() -> None:
    """
    Copy file from scargo pkg

    :return: None
    """
    files_to_copy = Path(SCARGO_PGK_PATH, "templates").glob("*")
    project_abs_path = get_project_root()
    for file in files_to_copy:
        if not Path(project_abs_path, file.name).exists():
            shutil.copy2(file, project_abs_path)


def scargo_update(config_file_path: Path) -> None:
    """
    Update project

    :param config_file_path: path to .toml configuration file (e.g. scargo.toml)
    :return: None
    """
    logger = get_logger()
    project_path = get_project_root()
    docker_path = Path(project_path, ".devcontainer")
    config = get_scargo_config_or_exit(config_file_path)
    if not config.project:
        logger.error("File `%s`: Section `project` not found.", config_file_path)
        return

    if not config.project.name:
        logger.error(
            "File `{config_file_path}`: `name` not found under `project` section."
        )
        return

    # Copy templates project files to repo directory
    copy_file_if_not_exists()

    # Copy config file and create lock file.
    shutil.copyfile(config_file_path, project_path / SCARGO_LOCK_FILE)
    ###########################################################################
    config = get_scargo_config_or_exit()
    check_scargo_version(config)
    project_config = config.project
    target = project_config.target

    # Copy docker env files to repo directory
    generate_docker_compose(docker_path, project_config, ver)
    generate_env(docker_path)

    generate_cmake(config)
    generate_conanfile(config)

    if target.family == "esp32":
        Path(target.source_dir, "fs").mkdir(parents=True, exist_ok=True)
        with open(Path(project_path, "version.txt"), "w", encoding="utf-8") as out:
            out.write(project_config.version)
        with open(Path(project_path, "partitions.csv"), "w", encoding="utf-8") as out:
            out.write(
                "# ESP-IDF Partition Table\n# Name,   Type, SubType, Offset,  Size, Flags\n"
            )
            partitions = config.esp32.partitions
            for line in partitions:
                out.write(line + "\n")
            out.write("\n")

    generate_cicd(project_config=project_config)
    generate_tests(target, config.tests)
    generate_readme(project_config)

    # do not rebuild dockers in the docker
    if target.family == "stm32" and not Path("third-party/stm32-cmake").is_dir():
        subprocess.run("conan source .", shell=True, cwd=project_path)

    if project_config.build_env == SCARGO_DOCKER_ENV:
        scargo_docker(build_docker=True)
