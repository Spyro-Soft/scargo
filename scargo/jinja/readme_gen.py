# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

from scargo.config import Config
from scargo.jinja.base_gen import create_file_from_template
from scargo.path_utils import get_project_root


def generate_readme(config: Config) -> None:
    """Generate dirs and files"""
    create_file_from_template(
        "templates/README.md.j2",
        get_project_root() / "README.md",
        overwrite=False,
        template_params={"project": config.project},
        config=config,
    )
