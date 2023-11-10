# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

import os
import shutil
from pathlib import Path
from typing import Any, Dict

from scargo import __version__
from scargo.config import Config
from scargo.file_generators.base_gen import create_file_from_template
from scargo.global_values import SCARGO_PKG_PATH
from scargo.target_helpers import atsam_helper, stm32_helper


class _DockerComposeTemplate:
    """
    This class is a container for docker compose yaml files creation with multilayer approach
    """

    def __init__(self, config: Config, docker_path: Path):
        self.docker_path = docker_path
        self._config = config

    def generate_docker_env(self) -> None:
        """Generate dirs and files"""
        self._create_file_from_template(
            "docker/Dockerfile-custom.j2",
            "Dockerfile-custom",
            template_params={"project": self._config.project},
            overwrite=False,
        )
        self._create_file_from_template(
            "docker/docker-compose.yaml.j2",
            "docker-compose.yaml",
            template_params={"config": self._config},
        )
        self._create_file_from_template(
            "docker/devcontainer.json.j2",
            "devcontainer.json",
            template_params={"project": self._config.project},
        )
        if self._config.project.target.family == "stm32":
            stm32_helper.generate_openocd_script(self.docker_path, self._config)
        if self._config.project.target.family == "atsam":
            atsam_helper.generate_openocd_script(self.docker_path, self._config)

        custom_docker = self._get_dockerfile_custom_content()
        scargo_package_version = self._set_up_package_version()

        self._create_file_from_template(
            "docker/Dockerfile.j2",
            "Dockerfile",
            template_params={
                "project": self._config.project,
                "scargo_package_version": scargo_package_version,
                "custom_docker": custom_docker,
            },
        )

    def _create_file_from_template(
        self,
        template_path: str,
        output_filename: str,
        template_params: Dict[str, Any],
        overwrite: bool = True,
    ) -> None:
        create_file_from_template(
            template_path,
            self.docker_path / output_filename,
            template_params=template_params,
            config=self._config,
            overwrite=overwrite,
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
