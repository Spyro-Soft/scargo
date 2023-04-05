# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

import os
import shutil
from pathlib import Path

from scargo import __version__
from scargo.config import Config
from scargo.file_generators.base_gen import create_file_from_template
from scargo.global_values import SCARGO_PKG_PATH


class _DockerComposeTemplate:
    """
    This class is a container for docker compose yaml files creation with multilayer approach
    """

    def __init__(self, config: Config, docker_path: Path):
        self.docker_path = docker_path
        # List of files to generate (template_path, output_path)
        self._gen_file_list = [
            ("docker/docker-compose.yaml.j2", docker_path / "docker-compose.yaml"),
            ("docker/Dockerfile.j2", docker_path / "Dockerfile"),
            ("docker/devcontainer.json.j2", docker_path / "devcontainer.json"),
        ]
        if config.project.target.family == "stm32":
            self._gen_file_list.extend(
                [("docker/stm32.cfg.j2", docker_path / "stm32.cfg")]
            )
        self._config = config

    def generate_docker_env(self) -> None:
        """Generate dirs and files"""
        create_file_from_template(
            "docker/Dockerfile-custom.j2",
            self.docker_path / "Dockerfile-custom",
            template_params={},
            overwrite=False,
            config=self._config,
        )

        custom_docker = self._get_dockerfile_custom_content()
        scargo_package_version = self._set_up_package_version()

        for template, output_path in self._gen_file_list:
            create_file_from_template(
                template,
                output_path,
                template_params={
                    "project": self._config.project,
                    "scargo_package_version": scargo_package_version,
                    "custom_docker": custom_docker,
                },
                config=self._config,
            )

    def _get_dockerfile_custom_content(self) -> str:
        project_root = self._config.project_root
        custom_docker_path = project_root / self._config.project.docker_file
        if custom_docker_path.is_file():
            return custom_docker_path.read_text()
        return ""

    def _set_up_package_version(self) -> str:
        if whl_path_str := os.getenv("SCARGO_DOCKER_INSTALL_LOCAL"):
            repo_root = SCARGO_PKG_PATH.parent
            whl_path = repo_root / whl_path_str
            shutil.copy(whl_path, self.docker_path)
            return whl_path.name
        return f"scargo=={__version__}"


def generate_docker_compose(docker_path: Path, config: Config) -> None:
    docker_compose_template = _DockerComposeTemplate(config, docker_path)
    docker_compose_template.generate_docker_env()
