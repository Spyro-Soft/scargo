# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #
"""Handle docker for project"""
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Sequence

import docker

from scargo.config_utils import get_scargo_config_or_exit
from scargo.logger import get_logger

logger = get_logger()


def scargo_docker_build(
    docker_opts: Sequence[str], project_root: Optional[Path] = None
) -> None:
    """
    Build docker

    :param docker_opts: additional docker options
    :param project_root: scargo project root path
    :raises CalledProcessError: if docker build fail
    """
    logger.debug("Build docker environment.")
    if not project_root:
        project_root = get_scargo_config_or_exit().project_root
    docker_path = _get_docker_path(project_root)

    cmd = get_docker_compose_command()
    cmd.extend(["build", *docker_opts])

    try:
        subprocess.run(cmd, cwd=docker_path, check=True)
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
    logger.debug("Run docker environment.")

    config = get_scargo_config_or_exit()
    docker_path = _get_docker_path(config.project_root)
    project_config_name = config.project.name

    cmd = get_docker_compose_command()
    cmd.extend(
        [
            "run",
            *docker_opts,
            f"{project_config_name}_dev",
        ]
    )
    if command:
        cmd.extend(["bash", "-c", command])

    try:
        subprocess.run(cmd, cwd=docker_path, check=True)
        logger.info("Stop docker environment.")
    except subprocess.CalledProcessError:
        sys.exit(1)


def scargo_docker_exec(docker_opts: List[str]) -> None:
    """
    Exec docker

    :param docker_opts: additional docker options
    :raises CalledProcessError: if docker did not start
    """
    logger.debug("Exec docker environment.")

    config = get_scargo_config_or_exit()
    image = config.project.docker_image_tag

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
    cmd = ["docker", "exec", "-it", *docker_opts, newest_container[0].id, *bash_command]
    try:
        subprocess.run(cmd, check=True)
        logger.info("Stop exec docker environment.")
    except subprocess.CalledProcessError:
        sys.exit(1)


def _get_docker_path(project_path: Path) -> Path:
    # do not rebuild dockers in the docker
    if Path("/.dockerenv").exists():
        logger.error("Cannot used docker command inside the docker container.")
        sys.exit(1)
    return Path(project_path, ".devcontainer")


def get_docker_compose_command() -> List[str]:
    """Get docker command

    Returns:
        List[str]: _description_
    """
    command = ["docker-compose"]
    # Check if docker-compose or docker compose is available
    if shutil.which("docker-compose"):
        command = ["docker-compose"]
    elif shutil.which("docker"):
        command = ["docker", "compose"]
    else:
        logger.error("Neither docker-compose nor docker compose are available.")
        sys.exit(1)

    return command
