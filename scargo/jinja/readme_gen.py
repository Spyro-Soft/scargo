# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

from pathlib import Path

from scargo.config import ProjectConfig
from scargo.global_values import SCARGO_PGK_PATH
from scargo.jinja.base_gen import BaseGen
from scargo.path_utils import get_project_root


class _ReadmeTemplate(BaseGen):
    """This class is a container for readme md file"""

    def __init__(self) -> None:
        self.template_dir = Path(SCARGO_PGK_PATH, "jinja", "templates")
        BaseGen.__init__(self, self.template_dir)

    def generate_readme(self, project_config: ProjectConfig) -> None:
        """Generate dirs and files"""
        self.create_file_from_template(
            "README.md.j2",
            get_project_root() / "README.md",
            overwrite=False,
            template_params={"project": project_config},
        )


def generate_readme(project_config: ProjectConfig) -> None:
    readme_template = _ReadmeTemplate()
    readme_template.generate_readme(project_config)
