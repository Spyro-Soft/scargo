# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

from pathlib import Path

from scargo.jinja.base_gen import BaseGen
from scargo.scargo_src.global_values import SCARGO_PGK_PATH
from scargo.scargo_src.sc_config import Config
from scargo.scargo_src.utils import get_project_root


class _CppTemplateGen(BaseGen):
    """
    This class is a container cpp files creation with multilayer approach
    """

    def __init__(self, config: Config):
        self.template_dir = Path(SCARGO_PGK_PATH, "jinja", "cpp")
        BaseGen.__init__(self, self.template_dir)
        self._config = config
        self._src_dir = get_project_root() / config.project.target.source_dir

    def _generate_bin(self):
        """Function which creates main.cpp file using jinja"""
        if bin_name := self._config.project.bin_name:
            self.create_file_from_template(
                "main.cpp.j2",
                Path(self._src_dir, f"{bin_name.lower()}.cpp"),
                target=self._config.project.target,
                bin_name=bin_name,
            )

    def _generate_lib(self):
        """Function which creates a lib files using jinja"""
        if lib_name := self._config.project.lib_name:
            self.create_file_from_template(
                "lib.cpp.j2",
                Path(self._src_dir, f"{lib_name.lower()}.cpp"),
                lib_name=lib_name,
            )
            self.create_file_from_template(
                "lib.h.j2",
                Path(self._src_dir, f"{lib_name.lower()}.h"),
                lib_name=lib_name,
            )

    def _generate_cmake(self):
        target_family = self._config.project.target.family

        self.create_file_from_template(
            f"cmake-src-{target_family}.j2",
            Path(self._src_dir, "CMakeLists.txt"),
            config=self._config,
        )

    def generate_cpp(self):
        """Generate dirs and files"""
        self._generate_lib()
        self._generate_bin()
        self._generate_cmake()


def generate_cpp(config: Config):
    cpp_template = _CppTemplateGen(config)
    cpp_template.generate_cpp()
