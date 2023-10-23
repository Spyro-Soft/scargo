# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #


from pathlib import Path
from typing import Any, Dict

from scargo.config import Config
from scargo.file_generators.base_gen import create_file_from_template


class _VSCodeTemplate:
    """
    This class is a container for docker compose yaml files creation with multilayer approach
    """

    def __init__(self, config: Config, vscode_path: Path):
        self.vscode_path = vscode_path
        self._config = config

    def generate_vscode_env(self) -> None:
        """Generate dirs and files"""

        self._create_file_from_template(
            "vscode/tasks.json.j2",
            "tasks.json",
            template_params={"project": self._config.project},
        )

    def generate_launch_json(self, elf_path: Path) -> None:
        self._create_file_from_template(
            "vscode/launch.json.j2",
            "launch.json",
            template_params={"bin_path": elf_path},
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
            self.vscode_path / output_filename,
            template_params=template_params,
            config=self._config,
            overwrite=overwrite,
        )


def generate_vscode(vscode_path: Path, config: Config) -> None:
    vscode_template = _VSCodeTemplate(config, vscode_path)
    vscode_template.generate_vscode_env()


def generate_launch_json(vscode_path: Path, config: Config, elf_path: Path) -> None:
    vscode_template = _VSCodeTemplate(config, vscode_path)
    vscode_template.generate_launch_json(elf_path)
