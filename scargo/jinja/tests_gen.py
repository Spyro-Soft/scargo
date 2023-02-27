# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Generate cmake for test dir"""
from pathlib import Path
from shutil import copytree

from scargo.config import Target, TestConfig
from scargo.global_values import SCARGO_PGK_PATH
from scargo.jinja.base_gen import BaseGen
from scargo.path_utils import get_project_root


class _TestsTemplate(BaseGen):
    """Create cmake template in test dir"""

    def __init__(self) -> None:
        self.tests_template_dir = Path(SCARGO_PGK_PATH, "jinja", "test_templates")
        BaseGen.__init__(self, self.tests_template_dir)
        project_path = get_project_root()
        self.output_dir = project_path / "tests"

        # List of files to generate once (template_path, output_path)
        self._gen_once_file_list = [
            ("CMakeLists-ut.txt.j2", self.output_dir / "ut" / "CMakeLists.txt"),
            ("CMakeLists-it.txt.j2", self.output_dir / "it" / "CMakeLists.txt"),
            ("CMakeLists-mocks.txt.j2", self.output_dir / "mocks" / "CMakeLists.txt"),
        ]

    def generate_test_dirs_and_files(
        self, target: Target, tests_config: TestConfig
    ) -> None:
        """Generate dirs and files"""
        static_mock_dir = self.output_dir / "mocks" / "static_mock"
        if not static_mock_dir.exists():
            copytree(self.tests_template_dir / "static_mock", static_mock_dir)

        # Update main test cmake on scargo update
        self.create_file_from_template(
            "CMakeLists-test.txt.j2",
            self.output_dir / "CMakeLists.txt",
            overwrite=True,
            template_params={
                "target": target,
                "tests": tests_config,
            },
        )

        for template, output_path in self._gen_once_file_list:
            self.create_file_from_template(
                template,
                output_path,
                overwrite=False,
                template_params={
                    "target": target,
                    "tests": tests_config,
                },
            )


def generate_tests(target: Target, tests_config: TestConfig) -> None:
    tests = _TestsTemplate()
    tests.generate_test_dirs_and_files(target, tests_config)
