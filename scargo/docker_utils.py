import sys
from pathlib import Path
from typing import List

import docker as dock
from docker import DockerClient

from scargo.config import ProjectConfig
from scargo.global_values import SCARGO_DOCKER_ENV
from scargo.logger import get_logger

logger = get_logger()


def run_scargo_again_in_docker(
    project_config: ProjectConfig, project_path: Path
) -> None:
    """
    Run command in docker

    :param dict project_config: project configuration
    :param Path project_path: path to project root
    :return: None
    """
    build_env = project_config.build_env
    if build_env != SCARGO_DOCKER_ENV or Path("/.dockerenv").exists():
        return
    relative_path = Path.cwd().relative_to(project_path)
    path_in_docker = Path("/workspace", relative_path)

    cmd_args = sys.argv[1:]

    entrypoint = ""
    if project_config.target.family == "esp32":
        entrypoint = "/opt/esp/entrypoint.sh"

    docker_tag = project_config.docker_image_tag
    client = dock.from_env()

    run_command_in_docker(
        ["scargo", "version"],
        client,
        docker_tag,
        entrypoint,
        project_path,
        path_in_docker,
    )

    status_code = run_command_in_docker(
        ["scargo", *cmd_args],
        client,
        docker_tag,
        entrypoint,
        project_path,
        path_in_docker,
    )
    sys.exit(status_code)


def run_command_in_docker(  # type: ignore[no-any-unimported]
    command: List[str],
    client: DockerClient,
    docker_tag: str,
    entrypoint: str,
    project_path: Path,
    path_in_docker: Path,
) -> int:
    logger.info(f"Running '{' '.join(command)}' command in docker.")
    container = client.containers.run(
        docker_tag,
        command,
        volumes=[f"{project_path}:/workspace/", "/dev/:/dev/"],
        entrypoint=entrypoint,
        privileged=True,
        detach=True,
        working_dir=str(path_in_docker),
    )
    output = container.attach(stdout=True, stream=True, logs=True, stderr=True)
    for line in output:
        print(line.decode(), end="")
    result = container.wait()
    container.remove()
    return result["StatusCode"]  # type: ignore[no-any-return]
