# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

from pathlib import Path

from scargo.jinja.base_gen import BaseGen
from scargo.scargo_src.global_values import SCARGO_PGK_PATH
from scargo.scargo_src.sc_config import Config, Target
from scargo.scargo_src.utils import get_project_root


class _CppTemplateGen(BaseGen):
    """
    This class is a container cpp files creation with multilayer approach
    """

    def __init__(self):
        self.template_dir = Path(SCARGO_PGK_PATH, "jinja", "cpp")
        BaseGen.__init__(self, self.template_dir)

    def _set_src_dir(self, target: Target):
        self._src_dir = get_project_root() / target.source_dir

    def _generate_bin(self, target: str, bin_name: str):
        """Function which creates main.cpp file using jinja"""
        self.create_file_from_template(
            "main.cpp.j2",
            Path(self._src_dir, f"{bin_name.lower()}.cpp"),
            target=target,
            bin_name=bin_name,
        )

    def _generate_lib(self, lib_name: str):
        """Function which creates a lib files using jinja"""
        self.create_file_from_template(
            "lib.cpp.j2",
            Path(self._src_dir, f"{lib_name.lower()}.cpp"),
            lib_name=lib_name,
        )
        self.create_file_from_template(
            "lib.h.j2", Path(self._src_dir, f"{lib_name.lower()}.h"), lib_name=lib_name
        )

    def _generate_cmake(self, config: Config):
        target = config.project.target

        self.create_file_from_template(
            f"cmake-src-{target.family}.j2",
            Path(self._src_dir, "CMakeLists.txt"),
            config=config,
        )

    def generate_cpp(self, config: Config):
        """Generate dirs and files"""
        target = config.project.target
        self._set_src_dir(target)

        lib_name = config.project.lib_name
        if lib_name:
            self._generate_lib(lib_name)

        bin_name = config.project.bin_name
        if bin_name:
            self._generate_bin(target, bin_name)

        self._generate_cmake(config)


def generate_cpp(config: Config):
    cpp_template = _CppTemplateGen()
    cpp_template.generate_cpp(config)
