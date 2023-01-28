# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

from pathlib import Path

from scargo.jinja.base_gen import BaseGen
from scargo.scargo_src.global_values import SCARGO_PGK_PATH
from scargo.scargo_src.sc_config import Config
from scargo.scargo_src.utils import get_project_root


class _CMakeTemplate(BaseGen):
    """Cmake template class"""

    def __init__(self):
        template_dir = Path(SCARGO_PGK_PATH, "jinja", "templates")
        BaseGen.__init__(self, template_dir)

    def generate_cmakes(self, config: Config):
        self.create_file_from_template(
            "CMakeLists.txt.j2",
            get_project_root() / "CMakeLists.txt",
            config=config,
        )


def generate_cmake(config: Config):
    cmake_template = _CMakeTemplate()
    cmake_template.generate_cmakes(config)
