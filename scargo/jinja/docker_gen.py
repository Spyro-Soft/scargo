# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

from pathlib import Path

from scargo.jinja.base_gen import BaseGen
from scargo.scargo_src.global_values import SCARGO_PGK_PATH
from scargo.scargo_src.sc_config import ProjectConfig
from scargo.scargo_src.sc_logger import get_logger
from scargo.scargo_src.utils import get_project_root


class _DockerComposeTemplate(BaseGen):
    """
    This class is a container for docker compose yaml files creation with multilayer approach
    """

    def __init__(self, project_config: ProjectConfig, docker_path: Path):
        template_dir = Path(SCARGO_PGK_PATH, "jinja", "docker")
        BaseGen.__init__(self, template_dir)
        self.docker_path = docker_path
        # List of files to generate (template_path, output_path)
        self._gen_file_list = [
            ("docker-compose.yaml.j2", docker_path / "docker-compose.yaml"),
            ("Dockerfile.j2", docker_path / "Dockerfile"),
            ("requirements.txt.j2", docker_path / "requirements.txt"),
            ("devcontainer.json.j2", docker_path / "devcontainer.json"),
        ]
        if project_config.target.family == "stm32":
            self._gen_file_list.extend([("stm32.cfg.j2", docker_path / "stm32.cfg")])
        self.project_config = project_config

    def generate_docker_env(self, scargo_version: str):
        """Generate dirs and files"""
        custom_docker = ""
        self.create_file_from_template(
            "Dockerfile-custom.j2",
            self.docker_path / "Dockerfile-custom",
            overwrite=False,
        )

        project_root = get_project_root()
        custom_docker_path = project_root / self.project_config.docker_file
        if custom_docker_path.is_file():
            custom_docker = custom_docker_path.read_text()

        logger = get_logger()
        logger.debug(
            "Custom docker file path: %s", custom_docker_path.relative_to(project_root)
        )

        for template, output_path in self._gen_file_list:
            self.create_file_from_template(
                template,
                output_path,
                project=self.project_config,
                scargo_version=scargo_version,
                custom_docker=custom_docker,
            )


def generate_docker_compose(
    docker_path: Path, project_config: ProjectConfig, scargo_version: str
):
    docker_compose_template = _DockerComposeTemplate(project_config, docker_path)
    docker_compose_template.generate_docker_env(scargo_version)
