# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Generate cmake for test dir"""
from pathlib import Path
from shutil import copytree

from scargo.config import Config
from scargo.global_values import SCARGO_PKG_PATH
from scargo.jinja.base_gen import create_file_from_template
from scargo.path_utils import get_project_root


def generate_tests(config: Config) -> None:
    """Generate dirs and files"""
    tests_template_dir = Path(SCARGO_PKG_PATH, "jinja", "templates", "tests")
    project_path = get_project_root()

    # List of files to generate once (template_path, output_path)
    gen_once_file_list = [
        ("tests/CMakeLists-ut.txt.j2", "tests/ut/CMakeLists.txt"),
        ("tests/CMakeLists-it.txt.j2", "tests/it/CMakeLists.txt"),
        ("tests/CMakeLists-mocks.txt.j2", "tests/mocks/CMakeLists.txt"),
    ]

    static_mock_dir = project_path / "tests" / "mocks" / "static_mock"
    if not static_mock_dir.exists():
        copytree(tests_template_dir / "static_mock", static_mock_dir)

    # Update main test cmake on scargo update
    create_file_from_template(
        "tests/CMakeLists-test.txt.j2",
        "tests/CMakeLists.txt",
        overwrite=True,
        template_params={
            "target": config.project.target,
            "tests": config.tests,
        },
        config=config,
    )

    for template, output_path in gen_once_file_list:
        create_file_from_template(
            template,
            output_path,
            overwrite=False,
            template_params={
                "target": config.project.target,
                "tests": config.tests,
            },
            config=config,
        )
