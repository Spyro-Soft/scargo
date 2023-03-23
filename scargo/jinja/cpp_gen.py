# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

from pathlib import Path

from scargo.config import Config
from scargo.global_values import SCARGO_PGK_PATH
from scargo.jinja.base_gen import BaseGen
from scargo.path_utils import get_project_root


class _CppTemplateGen(BaseGen):
    """
    This class is a container cpp files creation with multilayer approach
    """

    def __init__(self, config: Config) -> None:
        self.template_dir = Path(SCARGO_PGK_PATH, "jinja", "cpp")
        self._config = config
        self._target = config.project.target
        self._src_dir = get_project_root() / self._target.source_dir
        BaseGen.__init__(self, self.template_dir)

    def _generate_bin(self, bin_name: str) -> None:
        """Function which creates main.cpp file using jinja"""
        self.create_file_from_template(
            "main.cpp.j2",
            Path(self._src_dir, f"{bin_name.lower()}.cpp"),
            template_params={"target": self._target, "bin_name": bin_name},
        )

    def _generate_lib(self, lib_name: str) -> None:
        """Function which creates a lib files using jinja"""

        lib_name = lib_name.lower()
        class_name = "".join(lib_name.replace("_", " ").title().split())

        self.create_file_from_template(
            "lib.cpp.j2",
            Path(self._src_dir, f"{lib_name}.cpp"),
            template_params={"class_name": class_name, "lib_name": lib_name},
        )
        self.create_file_from_template(
            "lib.h.j2",
            Path(self._src_dir, f"{lib_name}.h"),
            {"class_name": class_name},
        )

    def _generate_cmake(self) -> None:
        self.create_file_from_template(
            f"cmake-src-{self._target.family}.j2",
            Path(self._src_dir, "CMakeLists.txt"),
            template_params={"config": self._config},
        )

    def generate_cpp(self) -> None:
        """Generate dirs and files"""
        lib_name = self._config.project.lib_name
        if lib_name:
            self._generate_lib(lib_name)

        bin_name = self._config.project.bin_name
        if bin_name:
            self._generate_bin(bin_name)

        self._generate_cmake()


def generate_cpp(config: Config) -> None:
    cpp_template = _CppTemplateGen(config)
    cpp_template.generate_cpp()
