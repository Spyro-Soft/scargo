# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

import re
from pathlib import Path
from typing import List, Sequence

from scargo.jinja.base_gen import BaseGen
from scargo.jinja.mock_utils.cmake_utlis import add_subdirs_to_cmake
from scargo.scargo_src.global_values import SCARGO_PGK_PATH
from scargo.scargo_src.sc_config import Config
from scargo.scargo_src.utils import get_project_root

HEADER_EXTENSIONS = (".h", ".hpp")
SRC_EXTENSIONS = (".c", ".cpp")


class HeaderDescriptor:
    """
    This class is a container for names, includes, classes and namespaces
    which are parsed from the header file. This information is then passed
    to generate unit tests.
    """

    def __init__(self, name, includes, classes, namespaces):
        self.name = name
        self.includes = includes
        self.classes = classes
        self.namespaces = namespaces


class _UnitTestsGen(BaseGen):
    def __init__(self, config: Config):
        template_dir = Path(SCARGO_PGK_PATH, "jinja", "ut_templates")
        BaseGen.__init__(self, template_dir)

        self._config = config
        self._project_path = get_project_root()
        self._ut_dir = self._project_path / "tests/ut"

    def generate_tests(self, input_path: Path, overwrite: bool):
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
            if headers:
                self._generate_cmake(input_path, ut_path.parent)

    def _generate_unit_test(
        self, input_file_path: Path, output_file_path: Path, overwrite: bool
    ):
        """Generates unit test source file

        :param Path input_file_path: Path to src file
        :param Path output_file_path: Path to unit test file
        :param bool overwrite: overwrite if exists
        """
        header_descriptor = self._parse_header_file(input_file_path)
        self.create_file_from_template(
            "ut.cpp.j2",
            output_file_path,
            overwrite,
            header=header_descriptor,
        )

    def _generate_cmake(self, src_dir_path: Path, ut_dir_path: Path):
        """Generate CMakeLists for unit tests

        :param Path src_dir_path: Source directory for which tests are being generated
        :param Path ut_dir_path: Directory of generated unit tests
        """
        add_subdirs_to_cmake(ut_dir_path.relative_to(self._project_path))

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
            p.absolute().relative_to(self._project_path.absolute())
            for p in self._get_paths_with_ext(src_dir_path, SRC_EXTENSIONS)
            if p.name != main_cpp
        ]

        self.create_file_from_template(
            "CMakeLists.txt.j2",
            ut_dir_path / "CMakeLists.txt",
            overwrite=True,
            src_files=src_files,
            utest_name=ut_name,
            ut_files=ut_files,
        )

    def _get_unit_test_path(self, input_src_path: Path) -> Path:
        """Return output path for unit test

        :param Path input_src_path: Source path
        :return Path: output path for unit test
        """
        input_src_path = input_src_path.absolute()
        relative_to_src = input_src_path.relative_to(
            self._project_path.absolute() / self._config.project.target.source_dir
        )
        return Path(self._ut_dir, relative_to_src).with_name(
            f"ut_{input_src_path.stem}.cpp"
        )

    def _get_cmake_tests_name(self, test_dir_path: Path) -> str:
        """Get tests name for cmake

        :param Path test_file_path: Path to test dir
        :return str: tests name for cmake
        """
        test_dir_path = test_dir_path.absolute()
        relative_path = test_dir_path.relative_to(self._project_path.absolute())
        return "_".join(relative_path.parts)

    @staticmethod
    def _get_namespace(line):
        if line.startswith("namespace"):
            namespace = line.split(" ")[1]
        elif line.startswith("using namespace"):
            namespace = line.split(" ")[2]
        else:
            raise "No 'namespace' found in line: '{0}'".format(line)

        last_char = namespace[-1]
        if last_char == "{" or last_char == ";":
            return namespace[0:-1]

        return namespace

    @staticmethod
    def _parse_header_file(header_path: Path) -> HeaderDescriptor:
        namespaces = []
        classes = []
        includes = []

        # open header file to parse the header name and class name
        with open(header_path, "r", encoding="utf-8") as header:
            for line in header:
                line = line.strip()
                if line.startswith("#include"):
                    includes.append(line.split(" ")[1])
                elif line.startswith("namespace") or line.startswith("using namespace"):
                    namespaces.append(_UnitTestsGen._get_namespace(line))
                elif line.startswith("class"):
                    class_regex = re.compile(r"^([a-z]+)(\s[a-zA-Z\d]+)")
                    temp = class_regex.search(line)
                    classes.append(temp.group(2).lstrip())
                elif line.startswith('extern "C"'):
                    class_name = "".join([w.capitalize() for w in header_path.stem])
                    classes.append(class_name)

        return HeaderDescriptor(header_path, namespaces, classes, includes)

    @staticmethod
    def _get_paths_with_ext(workdir: Path, extensions: Sequence[str]) -> List[Path]:
        return [child for child in workdir.iterdir() if child.suffix in extensions]


def generate_ut(input_path: Path, config: Config, force=False):
    ut_gen = _UnitTestsGen(config)
    ut_gen.generate_tests(input_path, force)
