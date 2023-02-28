# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

from pathlib import Path

from scargo.config import Config
from scargo.global_values import SCARGO_PGK_PATH
from scargo.jinja.base_gen import BaseGen
from scargo.path_utils import get_project_root


class _ConanTemplate(BaseGen):
    """
    This class is a container for cmake file which is used by cmake.
    """

    def __init__(self) -> None:
        template_dir = Path(SCARGO_PGK_PATH, "jinja", "conan")
        BaseGen.__init__(self, template_dir)

    def generate_conanfile(self, config: Config) -> None:
        self.create_file_from_template(
            "conanfile.py.j2",
            get_project_root() / "conanfile.py",
            template_params={"config": config},
        )

    def generate_conanfile_tests(self, config: Config) -> None:
        self.create_file_from_template(
            "conanfiletest.j2",
            get_project_root() / "tests/conanfile.py",
            template_params={"config": config},
        )


def generate_conanfile(config: Config) -> None:
    conanfile_template = _ConanTemplate()
    conanfile_template.generate_conanfile(config)
    conanfile_template.generate_conanfile_tests(config)
