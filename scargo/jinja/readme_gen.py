# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

from pathlib import Path

from scargo.jinja.base_gen import BaseGen
from scargo.scargo_src.global_values import SCARGO_PGK_PATH
from scargo.scargo_src.sc_config import ProjectConfig
from scargo.scargo_src.utils import get_project_root


class _ReadmeTemplate(BaseGen):
    """This class is a container for readme md file"""

    def __init__(self):
        self.template_dir = Path(SCARGO_PGK_PATH, "jinja", "templates")
        BaseGen.__init__(self, self.template_dir)

    def generate_readme(self, project_config: ProjectConfig):
        """Generate dirs and files"""
        self.create_file_from_template(
            "README.md.j2",
            get_project_root() / "README.md",
            overwrite=False,
            project=project_config,
        )


def generate_readme(project_config: ProjectConfig):
    readme_template = _ReadmeTemplate()
    readme_template.generate_readme(project_config)
