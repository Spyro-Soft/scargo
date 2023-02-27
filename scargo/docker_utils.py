import sys
from pathlib import Path

import docker as dock

from scargo.config import ProjectConfig
from scargo.logger import get_logger
from scargo.path_utils import get_project_root


def run_scargo_again_in_docker(project_config: ProjectConfig) -> None:
    """
    Run command in docker

    :param dict project_config: project configuration
    :return: None
    """
    project_path = get_project_root()
    relative_path = Path.cwd().absolute().relative_to(project_path)

    cmd_args = " ".join(sys.argv[1:])

    entrypoint = ""
    if project_config.target.family == "esp32":
        entrypoint = "/opt/esp/entrypoint.sh"

    cmd = f'/bin/bash -c "scargo version || true; cd {relative_path} && scargo {cmd_args}"'

    docker_tag = project_config.docker_image_tag
    logger = get_logger()

    if project_path:
        logger.info("Running scargo %s command in docker.", cmd_args)

        client = dock.from_env()
        container = client.containers.run(
            f"{docker_tag}",
            cmd,
            volumes=[str(project_path) + ":/workspace/", "/dev/:/dev/"],
            entrypoint=entrypoint,
            privileged=True,
            detach=True,
        )
        output = container.attach(stdout=True, stream=True, logs=True)
        for line in output:
            print(line.decode(), end="")
        result = container.wait()
        container.remove()
        sys.exit(result["StatusCode"])
