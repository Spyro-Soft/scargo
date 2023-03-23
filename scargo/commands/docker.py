# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Handle docker for project"""
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Sequence

import docker

from scargo.config import ProjectConfig
from scargo.config_utils import get_scargo_config_or_exit
from scargo.logger import get_logger
from scargo.path_utils import get_project_root


def scargo_docker_build(docker_opts: Sequence[str]) -> None:
    """
    Build docker

    :param docker_opts: additional docker options
    :raises CalledProcessError: if docker build fail
    """
    logger = get_logger()
    logger.debug("Build docker environment.")

    docker_path = _get_docker_path()

    try:
        subprocess.run(
            ["docker-compose", "build", *docker_opts], cwd=docker_path, check=True
        )
        logger.info("Initialize docker environment.")
    except subprocess.CalledProcessError:
        logger.error("Build docker fail.")
        sys.exit(1)


def scargo_docker_run(
    docker_opts: Sequence[str],
    command: Optional[str] = None,
) -> None:
    """
    Run docker

    :param docker_opts: additional docker options
    :param command: command to run in the container
    :raises CalledProcessError: if docker did not start
    """
    logger = get_logger()
    logger.debug("Run docker environment.")

    docker_path = _get_docker_path()
    project_config_name = _get_project_config().name

    cmd = [
        "docker-compose",
        "run",
        *docker_opts,
        f"{project_config_name}_dev",
    ]
    if command:
        cmd.extend(["bash", "-c", command])

    try:
        subprocess.run(cmd, cwd=docker_path, check=True)
        logger.info("Stop docker environment.")
    except subprocess.CalledProcessError:
        logger.error("Run docker fail.")
        sys.exit(1)


def scargo_docker_exec(docker_opts: List[str]) -> None:
    """
    Exec docker

    :param docker_opts: additional docker options
    :raises CalledProcessError: if docker did not start
    """
    logger = get_logger()
    logger.debug("Exec docker environment.")

    image = _get_project_config().docker_image_tag

    if not image:
        logger.error("docker-image-tag not defined in .toml under project section")
        sys.exit(1)

    client = docker.from_env()
    newest_container = client.containers.list(
        limit=1, filters={"ancestor": image, "status": "running"}
    )
    if not newest_container:
        logger.error("No running containers using image `%s` to attach to!", image)
        logger.info("Use scargo docker run to run container.")
        sys.exit(1)

    bash_command = ["bash"]
    cmd = ["docker", "exec"] + docker_opts + [newest_container[0].id] + bash_command
    try:
        subprocess.run(cmd, check=True)
        logger.info("Stop exec docker environment.")
    except subprocess.CalledProcessError:
        logger.error("Exec docker fail.")
        sys.exit(1)


def _get_docker_path() -> Path:
    project_path = get_project_root()
    # do not rebuild dockers in the docker
    if Path(project_path, ".dockerenv").exists():
        logger = get_logger()
        logger.error("Cannot used docker command inside the docker container.")
        sys.exit(1)
    return Path(project_path, ".devcontainer")


def _get_project_config() -> ProjectConfig:
    return get_scargo_config_or_exit().project
