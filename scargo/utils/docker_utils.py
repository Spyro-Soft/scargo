import sys
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List

import docker as dock
from docker import DockerClient

from scargo.config import ProjectConfig
from scargo.logger import get_logger

logger = get_logger()


def prepare_docker(project_config: ProjectConfig, project_path: Path) -> Dict[str, Any]:
    relative_path = Path.cwd().relative_to(project_path)
    path_in_docker = PurePosixPath("/workspace", relative_path)

    entrypoint = ""
    if project_config.is_esp32():
        entrypoint = "/opt/esp/entrypoint.sh"

    docker_tag = project_config.docker_image_tag
    client = dock.from_env()

    return {
        "project_path": project_path,
        "client": client,
        "path_in_docker": path_in_docker,
        "entrypoint": entrypoint,
        "docker_tag": docker_tag,
    }


def run_scargo_again_in_docker(
    project_config: ProjectConfig, project_path: Path
) -> None:
    """
    Run command in docker

    :param dict project_config: project configuration
    :param Path project_path: path to project root
    :return: None
    """

    if not project_config.is_docker_buildenv() or Path("/.dockerenv").exists():
        return

    cmd_args = sys.argv[1:]
    for idx, val in enumerate(cmd_args):
        if val in ("-B", "--base-dir"):
            cmd_args[idx + 1] = "."

    result = run_command_in_docker(
        command=["scargo", *cmd_args], **prepare_docker(project_config, project_path)
    )
    sys.exit(result["StatusCode"])


def run_command_in_docker(  # type: ignore[no-any-unimported]
    command: List[str],
    client: DockerClient,
    docker_tag: str,
    entrypoint: str,
    project_path: Path,
    path_in_docker: PurePosixPath,
) -> Dict[str, Any]:
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
    output_str = ""
    for line in output:
        print(line.decode(), end="")
        output_str += line.decode()
    result = container.wait()
    container.remove()
    return {"StatusCode": result["StatusCode"], "output": output_str}
