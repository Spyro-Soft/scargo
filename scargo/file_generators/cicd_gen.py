# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

from scargo.config import Config
from scargo.file_generators.base_gen import create_file_from_template


def generate_cicd(config: Config) -> None:
    """Create a gitlab-ci.yml file"""
    create_file_from_template(
        ".gitlab-ci.yml.j2",
        ".gitlab-ci.yml",
        template_params={"project": config.project},
        config=config,
    )
