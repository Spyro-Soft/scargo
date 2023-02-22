# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

from pathlib import Path

from scargo.jinja.base_gen import BaseGen
from scargo.scargo_src.global_values import SCARGO_PGK_PATH
from scargo.scargo_src.sc_config import ProjectConfig
from scargo.scargo_src.utils import get_project_root


class _CiCdTemplate(BaseGen):
    """This class is a container for CI/CD yaml file which create pipeline"""

    def __init__(self):
        self.template_dir = Path(SCARGO_PGK_PATH, "jinja", "templates")
        BaseGen.__init__(self, self.template_dir)

    def generate_cicd_file(self, project_config: ProjectConfig):
        """Function which creates a cicd yaml file using jinja"""
        self.create_file_from_template(
            ".gitlab-ci.yml.j2",
            get_project_root() / ".gitlab-ci.yml",
            project=project_config,
        )


def generate_cicd(project_config: ProjectConfig):
    cicd_template = _CiCdTemplate()
    cicd_template.generate_cicd_file(project_config)
