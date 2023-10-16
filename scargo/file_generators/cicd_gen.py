# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

from pathlib import Path
from typing import Any, Dict

import yaml

from scargo.config import Config
from scargo.file_generators.base_gen import create_file_from_template
from scargo.logger import get_logger

logger = get_logger()


class _CicdTemplate:
    """
    This class is a container for cicd yaml files creation with multilayer approach
    """

    def __init__(self, config: Config):
        self._config = config

    @classmethod
    def merge_dictionaries(
        cls, dict1: Dict[str, Any], dict2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Marge two dictionaries recursively

        Args:
            dict1 (dict): base_dict
            dict2 (dict): custom_dict

        Returns:
            dict: merged dictionary
        """
        for key in dict2:
            if (
                key in dict1
                and isinstance(dict1[key], dict)
                and isinstance(dict2[key], dict)
            ):
                cls.merge_dictionaries(dict1[key], dict2[key])
            else:
                dict1[key] = dict2[key]
        return dict1

    def _get_cicd_content(self, cicd_dir_path: Path, file_name: str) -> Dict[str, Any]:
        file_path = cicd_dir_path / file_name

        # Check if the ci folder exists. If not, create it.
        if not cicd_dir_path.is_dir():
            cicd_dir_path.mkdir(parents=True)

        # Check if file exists. If not, create it.
        if not file_path.is_file():
            file_path.touch()

        # Read the file
        with file_path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        if not isinstance(data, dict):
            return {}
        return data

    def _generate_custom_cicd(self, custom_cicd_dict: Dict[str, Any]) -> None:
        """Generate custom cicd file"""
        # Merge custom_cicd with base_cicd
        base_cicd = self._get_cicd_content(self._config.project_root, ".gitlab-ci.yml")
        merged_dict = self.merge_dictionaries(base_cicd, custom_cicd_dict)
        with open(
            self._config.project_root / ".gitlab-ci.yml", "w", encoding="utf-8"
        ) as f:
            yaml.dump(merged_dict, f, sort_keys=False)

    def generate_cicd_env(self) -> None:
        """Generate dirs and files"""
        create_file_from_template(
            ".gitlab-ci-custom.yml.j2",
            ".devcontainer/.gitlab-ci-custom.yml",
            template_params={},
            config=self._config,
            overwrite=False,
        )

        create_file_from_template(
            ".gitlab-ci.yml.j2",
            ".gitlab-ci.yml",
            template_params={
                "project": self._config.project,
            },
            config=self._config,
        )

        project_path = self._config.project_root
        output_path = Path(project_path, ".devcontainer")

        custom_cicd = self._get_cicd_content(output_path, ".gitlab-ci-custom.yml")
        # Check if custom_cicd is empty and if so, do not merge
        if not custom_cicd:
            logger.info("Custom file is empty or currupted. Skipping cicd file merge.")
            return

        self._generate_custom_cicd(custom_cicd)


def generate_cicd(config: Config) -> None:
    """Generate cicd file with custom user layer

    Args:
        config (Config): target configuration
    """
    cicd_template = _CicdTemplate(config)
    cicd_template.generate_cicd_env()
