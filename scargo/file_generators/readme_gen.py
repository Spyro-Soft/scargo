# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

from scargo.config import Config
from scargo.file_generators.base_gen import create_file_from_template


def generate_readme(config: Config) -> None:
    """Generate dirs and files"""
    create_file_from_template(
        "README.md.j2",
        "README.md",
        overwrite=False,
        template_params={"project": config.project},
        config=config,
    )
