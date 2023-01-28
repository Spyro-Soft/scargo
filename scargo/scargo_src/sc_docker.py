# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Handle docker for project"""
import subprocess
import sys
from pathlib import Path

import docker

from scargo.scargo_src.sc_config import ProjectConfig
from scargo.scargo_src.sc_logger import get_logger
from scargo.scargo_src.sc_src import get_scargo_config_or_exit
from scargo.scargo_src.utils import get_project_root


def scargo_docker(
    build_docker: bool = False,
    no_cache: bool = False,
    run_docker: bool = False,
    exec_docker: bool = False,
):
    """
    :param bool run_docker: run command in docker
    :param bool exec_docker: connect to a running container
    :param bool build_docker: build docker
    :param bool no_cache: build docker without cache
    """
    project_path = get_project_root()

    # do not rebuild dockers in the docker
    if Path(project_path, ".dockerenv").exists():
        logger = get_logger()
        logger.error("Cannot used docker command inside the docker container.")
        sys.exit(1)

    config = get_scargo_config_or_exit()
    project_config = config.project

    docker_path = Path(project_path, ".devcontainer")

    if build_docker:
        _scargo_build_docker(docker_path, no_cache)

    if run_docker:
        _scargo_run_docker(docker_path, project_config)

    if exec_docker:
        _scargo_exec_docker(project_config)


def _scargo_build_docker(docker_path: Path, no_cache: bool = False) -> None:
    """
    Build docker

    :param Path docker_path: path to dockerfile
    :param bool no_cache: with/without docker cache
    :raises CalledProcessError: if docker build fail
    """
    logger = get_logger()
    logger.debug("Build docker environment.")

    cache = "--no-cache" if no_cache else ""
    try:
        subprocess.run(f"docker-compose build {cache}", shell=True, cwd=docker_path)
        logger.info("Initialize docker environment.")
    except subprocess.CalledProcessError:
        logger.error("Build docker fail.")


def _scargo_run_docker(docker_path: Path, project_config: ProjectConfig) -> None:
    """
    Run docker

    :param docker_path: path to docker
    :param project_config: project configuration
    :raises CalledProcessError: if docker did not start
    """
    logger = get_logger()
    logger.debug("Run docker environment.")

    try:
        subprocess.run(
            f"docker-compose run {project_config.name}_dev bash",
            shell=True,
            cwd=docker_path,
        )
        logger.info("Stop docker environment.")
    except subprocess.CalledProcessError:
        logger.error("Run docker fail.")


def _scargo_exec_docker(project_config: ProjectConfig):
    """
    Exec docker

    :param project_config: project configuration
    :raises CalledProcessError: if docker did not start
    """
    logger = get_logger()
    logger.debug("Exec docker environment.")

    image = project_config.docker_image_tag

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
    cmd = ["docker", "exec", "-it", newest_container[0].id] + bash_command
    try:
        subprocess.run(cmd)
        logger.info("Stop exec docker environment.")
    except subprocess.CalledProcessError:
        logger.error("Exec docker fail.")
