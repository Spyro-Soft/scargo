# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Update project"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

from scargo.commands.docker import get_docker_compose_command, scargo_docker_build
from scargo.config import Config
from scargo.config_utils import add_version_to_scargo_lock, get_scargo_config_or_exit
from scargo.file_generators.cicd_gen import generate_cicd
from scargo.file_generators.cmake_gen import generate_cmake
from scargo.file_generators.conan_gen import generate_conanfile, generate_conanprofile
from scargo.file_generators.docker_gen import generate_docker_compose
from scargo.file_generators.env_gen import generate_env
from scargo.file_generators.readme_gen import generate_readme
from scargo.file_generators.tests_gen import generate_tests
from scargo.file_generators.vscode_gen import generate_vscode
from scargo.global_values import SCARGO_DOCKER_ENV, SCARGO_LOCK_FILE, SCARGO_PKG_PATH
from scargo.logger import get_logger

logger = get_logger()


def copy_file_if_not_exists(project_path: Path) -> None:
    """
    Copy file from scargo pkg

    :return: None
    """
    files_to_copy = Path(SCARGO_PKG_PATH, "templates").glob("*")
    for file in files_to_copy:
        if not Path(project_path, file.name).exists():
            shutil.copy2(file, project_path)


def scargo_update(config_file_path: Path) -> None:
    """
    Update project

    :param config_file_path: path to .toml configuration file (e.g. scargo.toml)
    :return: None
    """
    project_path = config_file_path.parent
    docker_path = Path(project_path, ".devcontainer")
    vscode_path = Path(project_path, ".vscode")
    config = get_scargo_config_or_exit(config_file_path)
    if not config.project:
        logger.error("File `%s`: Section `project` not found.", config_file_path)
        sys.exit(1)

    if not config.project.name:
        logger.error(
            "File `{config_file_path}`: `name` not found under `project` section."
        )
        sys.exit(1)

    # Copy templates project files to repo directory
    copy_file_if_not_exists(project_path)

    # Copy config file and create lock file.
    lock_path = project_path / SCARGO_LOCK_FILE
    shutil.copyfile(config_file_path, lock_path)
    ###########################################################################
    add_version_to_scargo_lock(lock_path)
    project_config = config.project
    target = project_config.target

    # Copy docker env files to repo directory
    generate_docker_compose(docker_path, config)
    generate_env(docker_path, config)

    generate_vscode(vscode_path, config)

    generate_cmake(config)
    generate_conanfile(config)
    generate_conanprofile(config)

    conan_add_remote(project_path, config)
    conan_source(project_path)

    if target.family == "esp32":
        Path(config.source_dir_path, "fs").mkdir(parents=True, exist_ok=True)
        with open(Path(project_path, "version.txt"), "w", encoding="utf-8") as out:
            out.write(project_config.version)
        with open(Path(project_path, "partitions.csv"), "w", encoding="utf-8") as out:
            out.write(
                "# ESP-IDF Partition Table\n# Name,   Type, SubType, Offset,  Size, Flags\n"
            )
            partitions = config.get_esp32_config().partitions
            for line in partitions:
                out.write(line + "\n")
            out.write("\n")

    generate_cicd(config)
    generate_tests(config)
    generate_readme(config)

    # do not rebuild dockers in the docker
    if project_config.build_env == SCARGO_DOCKER_ENV:
        if not Path("/.dockerenv").exists():
            if not pull_docker_image(docker_path):
                scargo_docker_build([], config.project_root)
        else:
            logger.warning("Cannot run docker inside docker")


def pull_docker_image(docker_path: Path) -> bool:
    logger.info("Pulling the image from docker registry...")
    try:
        cmd = get_docker_compose_command()
        cmd.extend(["pull"])
        result = subprocess.run(
            cmd,
            cwd=docker_path,
            stderr=subprocess.PIPE,
            check=True,
        )
    except subprocess.CalledProcessError:
        logger.info(
            "No docker image does exist yet in the registry or you are not login"
        )
    else:
        # happens for the default tag, like "myproject-dev:1.0"
        if (
            "Some service image(s) must be built from source"
            not in result.stderr.decode()
        ):
            logger.info("Docker image pulled successfully")
            return True
    return False


def conan_add_remote(project_path: Path, config: Config) -> None:
    """
    Add conan remote repository

    :param Path project_path: path to project
    :param Config config:
    :return: None
    """
    conan_repo = config.conan.repo
    for repo_name, repo_url in conan_repo.items():
        try:
            subprocess.run(
                ["conan", "remote", "add", repo_name, repo_url],
                cwd=project_path,
                check=True,
                stderr=subprocess.PIPE,
            )
        except subprocess.CalledProcessError as e:
            if b"already exists in remotes" not in e.stderr:
                logger.error(e.stderr.decode().strip())
                logger.error("Unable to add remote repository")
        conan_add_user(repo_name)


def conan_add_user(remote: str) -> None:
    """
    Add conan user

    :param str remote: name of remote repository
    :return: None
    """
    conan_user = subprocess.run(
        "conan user", capture_output=True, shell=True, check=False
    ).stdout.decode("utf-8")

    env_conan_user = os.environ.get("CONAN_LOGIN_USERNAME", "")
    env_conan_passwd = os.environ.get("CONAN_PASSWORD", "")

    if env_conan_user not in conan_user:
        try:
            subprocess.check_call(
                ["conan", "user", "-p", env_conan_passwd, "-r", remote, env_conan_user],
            )
        except subprocess.CalledProcessError:
            logger.error("Unable to add user")


def conan_source(project_dir: Path) -> None:
    try:
        subprocess.check_call(
            [
                "conan",
                "source",
                ".",
            ],
            cwd=project_dir,
        )
    except subprocess.CalledProcessError:
        logger.error("Unable to source")
