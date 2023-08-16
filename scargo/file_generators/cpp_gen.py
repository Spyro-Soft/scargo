# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #
from typing import Any, Dict

from scargo.config import Config
from scargo.file_generators.base_gen import create_file_from_template


class _CppTemplateGen:
    """
    This class is a container cpp files creation with multilayer approach
    """

    def __init__(self, config: Config) -> None:
        self._config = config
        self._src_dir = config.source_dir_path
        self._inc_dir = config.include_dir_path

    def _generate_bin(self, bin_name: str) -> None:
        """Function which creates main.cpp file using jinja"""
        self._create_file_from_template(
            "cpp/main.cpp.j2",
            f"{bin_name.lower()}.cpp",
            template_params={
                "target": self._config.project.target,
                "bin_name": bin_name,
            },
        )

    def _generate_test_package(self, class_name: str) -> None:
        create_file_from_template(
            "conan/test_package/CMakeLists.txt.j2",
            "test_package/CMakeLists.txt",
            template_params={"config": self._config},
            config=self._config,
        )

        create_file_from_template(
            "conan/test_package/conanfile.py.j2",
            "test_package/conanfile.py",
            template_params={"config": self._config},
            config=self._config,
        )

        create_file_from_template(
            "conan/test_package/example.cpp.j2",
            "test_package/src/example.cpp",
            template_params={"config": self._config, "class_name": class_name},
            config=self._config,
        )

    def _generate_lib(self, lib_name: str) -> None:
        """Function which creates a lib files using jinja"""

        lib_name = lib_name.lower()
        class_name = "".join(lib_name.replace("_", " ").title().split())

        create_file_from_template(
            "cpp/lib.cpp.j2",
            self._src_dir / f"{self._config.project.target.source_dir}/{lib_name}.cpp",
            template_params={"class_name": class_name, "lib_name": lib_name},
            config=self._config,
        )
        create_file_from_template(
            "cpp/lib.h.j2",
            self._inc_dir / f"{lib_name}.h",
            template_params={"class_name": class_name},
            config=self._config,
        )

        self._generate_test_package(class_name)

    def _generate_cmake(self) -> None:
        self._create_file_from_template(
            f"cpp/cmake-src-{self._config.project.target.family}.j2",
            "CMakeLists.txt",
            template_params={"config": self._config},
        )

    def _create_file_from_template(
        self,
        template_path: str,
        output_filename: str,
        template_params: Dict[str, Any],
    ) -> None:
        create_file_from_template(
            template_path,
            self._src_dir / output_filename,
            template_params=template_params,
            config=self._config,
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
