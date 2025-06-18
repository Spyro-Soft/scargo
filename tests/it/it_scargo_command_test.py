import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional, Sequence

import pytest
from pytest import FixtureRequest, TempPathFactory

from scargo.cli import cli
from scargo.config import ScargoTarget
from scargo.config_utils import get_scargo_config_or_exit
from scargo.global_values import SCARGO_UT_COV_FILES_PREFIX
from tests.it.utils import ScargoTestRunner

TEST_DATA_PATH = Path(__file__).parent.parent / "test_data"
FIX_TEST_FILES_PATH = TEST_DATA_PATH / "test_projects/test_files/fix_test_files"
SUBDIRECTORY_TEST_FILES_PATH = (
    TEST_DATA_PATH / "test_projects/test_files/subdirectories_test_files"
)
UT_FILES_PATH = TEST_DATA_PATH / "test_projects/test_files/ut_files"

# List of expected covered files with defined units tests from UT_FILES_PATH
# in relation to source directory
EXPECTED_UT_COVERED_SRC_FILES: Sequence[str] = (
    "src/pow3.hpp",
    "src/twice.hpp",
    "src/square.hpp",
)


@dataclass
class ScargoCommandTestFlow:
    target_id: ScargoTarget
    proj_name: str
    proj_to_copy_path: Optional[Path] = None
    proj_path: Optional[Path] = None

    def __post_init__(self) -> None:
        self.runner = ScargoTestRunner()

    def assert_gcov_output_files(self, detailed_coverage: bool = False) -> None:
        config = get_scargo_config_or_exit()
        test_dir_name = "tests"
        project_dir = config.project_root

        test_build_dir = project_dir / "build" / test_dir_name
        assert (
            test_build_dir.is_dir()
        ), f"Build directory '{test_build_dir}' does not exist"

        gcov_report_htmlfile = test_build_dir / Path(
            f"{SCARGO_UT_COV_FILES_PREFIX}.html"
        )
        assert (
            gcov_report_htmlfile.is_file()
        ), f"File '{gcov_report_htmlfile}' does not exist"

        if not detailed_coverage:
            return

        gcov_report_htmlfile = test_build_dir / Path(
            f"{SCARGO_UT_COV_FILES_PREFIX}.details.html"
        )
        assert (
            gcov_report_htmlfile.is_file()
        ), f"File '{gcov_report_htmlfile}' does not exist"

        gcov_report_jsonfile = test_build_dir / Path(
            f"{SCARGO_UT_COV_FILES_PREFIX}.json"
        )
        assert (
            gcov_report_jsonfile.is_file()
        ), f"File '{gcov_report_jsonfile}' does not exist"

    def assert_gcov_detailed_coverage(self, expected_files: Sequence[str]) -> None:
        config = get_scargo_config_or_exit()
        test_dir_name = "tests"
        project_dir = config.project_root
        test_build_dir = project_dir / "build" / test_dir_name

        gcov_json_file = Path(f"{test_build_dir}/{SCARGO_UT_COV_FILES_PREFIX}.json")
        with open(gcov_json_file, encoding="utf-8") as gcov_json:
            gcov_data = json.load(gcov_json)

        covered_files: List[Path] = []
        for ff in gcov_data["files"]:
            covered_files.append(config.project_root / ff["file"])

        assert bool(
            covered_files
        ), "GCOV coverage: output json file list cannot be empty - expected records for covered files"

        for expected in expected_files:
            expected_file = config.project_root / expected
            assert (
                expected_file in covered_files
            ), f"GCOV coverage: expected file '{expected_file}' not found in GCOV covered files in JSON"

    def create_dummy_src_files(self, fpaths: Sequence[str]) -> None:
        config = get_scargo_config_or_exit()
        for path in fpaths:
            dummy_file_path = config.project_root / path
            dummy_file_path.parent.mkdir(parents=True, exist_ok=True)
            dummy_file_path.touch()


@pytest.fixture
def active_state_x86_path() -> ScargoCommandTestFlow:
    project_path = TEST_DATA_PATH / "test_projects/common_scargo_project"
    return ScargoCommandTestFlow(
        target_id=ScargoTarget.x86,
        proj_name=project_path.name,
        proj_to_copy_path=project_path,
    )


@pytest.fixture
def test_state(request: FixtureRequest, tmp_path_factory: TempPathFactory) -> Any:
    test_state = request.param
    test_state.proj_path = tmp_path_factory.mktemp(test_state.proj_name)
    os.chdir(test_state.proj_path)
    return test_state


@pytest.fixture
def setup_project(test_state: ScargoCommandTestFlow) -> None:
    """
    Setup new project or copy existing project, chdir into it and run scargo update
    """
    assert (
        test_state.proj_to_copy_path and test_state.proj_to_copy_path.exists()
    ), f"setup_project(): project in '{test_state.proj_to_copy_path}' does not exists - accepted only existing projects"

    # Copy existing project, backward compatibility tests
    shutil.copytree(
        src=test_state.proj_to_copy_path, dst=test_state.proj_name, dirs_exist_ok=True
    )

    # Copy fake tests to check GCOV coverage
    dest_test_dir = Path(test_state.proj_name) / "tests/ut"
    shutil.copytree(
        src=UT_FILES_PATH / "pow3", dst=dest_test_dir / "pow3", dirs_exist_ok=True
    )
    shutil.copytree(
        src=UT_FILES_PATH / "square", dst=dest_test_dir / "square", dirs_exist_ok=True
    )
    shutil.copytree(
        src=UT_FILES_PATH / "twice", dst=dest_test_dir / "twice", dirs_exist_ok=True
    )

    # Copy fake sources
    shutil.copytree(
        src=UT_FILES_PATH / "src",
        dst=Path(test_state.proj_name) / "src",
        dirs_exist_ok=True,
    )
    shutil.copy(src=UT_FILES_PATH / "CMakeLists.txt", dst=dest_test_dir)

    os.chdir(test_state.proj_name)
    result = test_state.runner.invoke(cli, ["update"])
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "test_state",
    [
        pytest.lazy_fixture("active_state_x86_path"),  # type: ignore
    ],
    ids=["copy_project_x86"],
    scope="session",
    indirect=True,
)
@pytest.mark.xdist_group(name="TestCommandTestFlow")
class TestCommandTestFlow:
    def test_cli_basic(
        self, test_state: ScargoCommandTestFlow, setup_project: None
    ) -> None:
        result = test_state.runner.invoke(cli, ["update"])
        assert result.exit_code == 0

        result = test_state.runner.invoke(cli, ["test"])
        assert result.exit_code == 0
        assert "No tests were found!!!" not in result.output

        test_state.assert_gcov_output_files()

        result = test_state.runner.invoke(cli, ["test", "--detailed-coverage"])
        assert result.exit_code == 0
        assert "No tests were found!!!" not in result.output

        test_state.assert_gcov_output_files(detailed_coverage=True)

    def test_cli_detailed_coverage(
        self, test_state: ScargoCommandTestFlow, setup_project: None
    ) -> None:
        result = test_state.runner.invoke(cli, ["update"])
        assert result.exit_code == 0

        result = test_state.runner.invoke(cli, ["test", "--detailed-coverage"])
        assert result.exit_code == 0
        assert "No tests were found!!!" not in result.output

        # Expected fake unit tests - common
        test_state.assert_gcov_detailed_coverage(EXPECTED_UT_COVERED_SRC_FILES)

        # create dummy fake files and re-run tests
        expected_files = [
            "src/echo.c",
            "src/test/test.cpp",
            "src/assembly.s",
            "src/assembly/capital_assembly.S",
            "src/assembly/asm.asm",
            "src/cc/cctest.cc",
            "src/cc/cxxtest.cxx",
        ]

        test_state.create_dummy_src_files(expected_files)
        test_state.runner.invoke(cli, ["test", "--detailed-coverage"])

        expected_files.extend(EXPECTED_UT_COVERED_SRC_FILES)
        test_state.assert_gcov_detailed_coverage(expected_files)
