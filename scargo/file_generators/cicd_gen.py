# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

from pathlib import Path
from typing import Any, Dict

import yaml  # type: ignore

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

    def _get_cicd_content(self, path: str, file_name: str) -> Dict[str, Any]:
        ci_folder = Path(path)
        file_path = ci_folder / file_name

        # Check if the ci folder exists. If not, create it.
        if not ci_folder.exists():
            ci_folder.mkdir(parents=True)

        # Check if file exists. If not, create it.
        if not file_path.exists():
            file_path.touch()

        # Read the file
        with file_path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        if not isinstance(data, dict):
            return {}
        return data

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
        custom_cicd = self._get_cicd_content(".devcontainer", ".gitlab-ci-custom.yml")

        # Check if custom_cicd is empty and if so, do not merge
        if custom_cicd is None:
            logger.info("Custom file is empty or currupted. Skipping cicd file merge.")
            return

        # Merge custom_cicd with base_cicd
        base_cicd = self._get_cicd_content(".", ".gitlab-ci.yml")
        merged_dict = self.merge_dictionaries(base_cicd, custom_cicd)
        with open(".gitlab-ci.yml", "w", encoding="utf-8") as f:
            yaml.dump(merged_dict, f, sort_keys=False)


def generate_cicd(config: Config) -> None:
    """Generate cicd file with custom user layer

    Args:
        config (Config): target configuration
    """
    cicd_template = _CicdTemplate(config)
    cicd_template.generate_cicd_env()
