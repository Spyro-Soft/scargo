# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

from pathlib import Path

from scargo.config import Config
from scargo.global_values import SCARGO_PGK_PATH
from scargo.jinja.base_gen import BaseGen
from scargo.path_utils import get_project_root


class _CMakeTemplate(BaseGen):
    """Cmake template class"""

    def __init__(self) -> None:
        template_dir = Path(SCARGO_PGK_PATH, "jinja", "templates")
        BaseGen.__init__(self, template_dir)

    def generate_cmakes(self, config: Config) -> None:
        self.create_file_from_template(
            "CMakeLists.txt.j2",
            get_project_root() / "CMakeLists.txt",
            template_params={"config": config},
        )


def generate_cmake(config: Config) -> None:
    cmake_template = _CMakeTemplate()
    cmake_template.generate_cmakes(config)
