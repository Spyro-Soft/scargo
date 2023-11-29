# #
# @copyright Copyright (C) 2023 SpyroSoft Solutions S.A. All rights reserved.
# #

"""Generate cmake for test dir"""
from pathlib import Path
from shutil import copytree

from scargo.config import Config
from scargo.file_generators.base_gen import create_file_from_template
from scargo.global_values import SCARGO_PKG_PATH


def generate_tests(config: Config) -> None:
    """Generate dirs and files"""
    tests_template_dir = Path(SCARGO_PKG_PATH, "file_generators", "templates", "tests")

    # List of files to generate once (template_path, output_path)
    gen_once_file_list = [
        ("tests/CMakeLists-ut.txt.j2", "tests/ut/CMakeLists.txt"),
        ("tests/CMakeLists-it.txt.j2", "tests/it/CMakeLists.txt"),
        ("tests/CMakeLists-mocks.txt.j2", "tests/mocks/CMakeLists.txt"),
    ]

    static_mock_dir = config.project_root / "tests" / "mocks" / "static_mock"
    if not static_mock_dir.exists():
        copytree(tests_template_dir / "static_mock", static_mock_dir)

    # Update main test cmake on scargo update
    create_file_from_template(
        "tests/CMakeLists-test.txt.j2",
        "tests/CMakeLists.txt",
        overwrite=True,
        template_params={
            "config": config,
        },
        config=config,
    )

    for template, output_path in gen_once_file_list:
        create_file_from_template(
            template,
            output_path,
            overwrite=False,
            template_params={},
            config=config,
        )
