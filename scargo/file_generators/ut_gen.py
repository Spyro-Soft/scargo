# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #
from pathlib import Path
from typing import List, Sequence

from scargo.config import Config
from scargo.file_generators.base_gen import create_file_from_template
from scargo.file_generators.clang_parser.header_parser import parse_file

HEADER_EXTENSIONS = (".h", ".hpp")
SRC_EXTENSIONS = (".c", ".cpp")


class _UnitTestsGen:
    def __init__(self, config: Config):
        self._config = config
        self._project_path = config.project_root
        self._ut_dir = self._project_path / "tests/ut"

    def generate_tests(self, input_path: Path, overwrite: bool) -> None:
        """Generates unit test files and corresponding cmake file

        :param Path input_path: Path to src file or src directory
        :param bool overwrite: overwrite files if exist
        """
        if input_path.is_file():
            ut_path = self._get_unit_test_path(input_path)
            self._generate_unit_test(input_path, ut_path, overwrite)
            self._generate_cmake(input_path.parent, ut_path.parent)

        elif input_path.is_dir():
            headers = self._get_paths_with_ext(input_path, HEADER_EXTENSIONS)
            ut_path = None
            for hdr in headers:
                ut_path = self._get_unit_test_path(hdr)
                self._generate_unit_test(hdr, ut_path, overwrite)
            if ut_path:
                self._generate_cmake(input_path, ut_path.parent)

    def _generate_unit_test(
        self, input_file_path: Path, output_file_path: Path, overwrite: bool
    ) -> None:
        """Generates unit test source file

        :param Path input_file_path: Path to src file
        :param Path output_file_path: Path to unit test file
        :param bool overwrite: overwrite if exists
        """
        header_descriptor = parse_file(input_file_path)
        create_file_from_template(
            "ut/ut.cpp.j2",
            output_file_path,
            overwrite=overwrite,
            template_params={"header": header_descriptor},
            config=self._config,
        )

    def _generate_cmake(self, src_dir_path: Path, ut_dir_path: Path) -> None:
        """Generate CMakeLists for unit tests

        :param Path src_dir_path: Source directory for which tests are being generated
        :param Path ut_dir_path: Directory of generated unit tests
        """
        cmake_dir_path = ut_dir_path
        while cmake_dir_path != self._ut_dir:
            add_ut_dir_to_parent_cmake(cmake_dir_path)
            cmake_dir_path = cmake_dir_path.parent

        ut_name = self._get_cmake_tests_name(ut_dir_path)
        ut_files = [
            p.name for p in self._get_paths_with_ext(ut_dir_path, SRC_EXTENSIONS)
        ]

        # Exclude main from srcs to test
        main_cpp = (
            f"{self._config.project.bin_name}.cpp"
            if self._config.project.bin_name
            else None
        )

        src_files = [
            p.relative_to(self._project_path)
            for p in self._get_paths_with_ext(src_dir_path, SRC_EXTENSIONS)
            if p.name != main_cpp
        ]

        create_file_from_template(
            "ut/CMakeLists.txt.j2",
            ut_dir_path / "CMakeLists.txt",
            overwrite=True,
            template_params={
                "src_files": src_files,
                "utest_name": ut_name,
                "ut_files": ut_files,
            },
            config=self._config,
        )

    def _get_unit_test_path(self, input_src_path: Path) -> Path:
        """Return output path for unit test

        :param Path input_src_path: Source path
        :return Path: output path for unit test
        """
        relative_to_src = input_src_path.relative_to(self._config.source_dir_path)
        return Path(self._ut_dir, relative_to_src).with_name(
            f"ut_{input_src_path.stem}.cpp"
        )

    def _get_cmake_tests_name(self, test_dir_path: Path) -> str:
        """Get tests name for cmake

        :param Path test_dir_path: Path to test dir
        :return str: tests name for cmake
        """
        relative_path = test_dir_path.relative_to(self._project_path)
        return "_".join(relative_path.parts)

    @staticmethod
    def _get_paths_with_ext(workdir: Path, extensions: Sequence[str]) -> List[Path]:
        return [child for child in workdir.iterdir() if child.suffix in extensions]


COPYRIGHT = """# #
# Copyright (C) 2022 Spyrosoft Solutions. All rights reserved.
# #\n\n"""


def add_ut_dir_to_parent_cmake(ut_dir_path: Path) -> None:
    # if CMakelists doesn't exist create it in parent dir
    parent_dir = ut_dir_path.parent
    cmake_list_path = parent_dir / "CMakeLists.txt"
    if not cmake_list_path.exists():
        with cmake_list_path.open("w", encoding="utf-8") as file:
            file.write(COPYRIGHT)
    # check if ut_dir_path exists in CMakeLists
    # if not add it
    with cmake_list_path.open("r+", encoding="utf-8") as file:
        cmake_text = file.read()
        add_subdirectory_clause = f"\nadd_subdirectory({ut_dir_path.name})"
        if add_subdirectory_clause not in cmake_text:
            file.write(add_subdirectory_clause)


def generate_ut(input_path: Path, config: Config, force: bool = False) -> None:
    ut_gen = _UnitTestsGen(config)
    ut_gen.generate_tests(input_path, force)
