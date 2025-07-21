import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional, Sequence

import pytest
import tomlkit
from pytest import FixtureRequest, TempPathFactory

from scargo.cli import cli
from scargo.config import ScargoTarget
from scargo.config_utils import get_scargo_config_or_exit
from scargo.global_values import SCARGO_UT_COV_FILES_PREFIX
from tests.it.conftest import TEST_DATA_PATH, UT_FILES_PATH
from tests.it.utils import ScargoTestRunner

# List of expected covered files with defined units tests from UT_FILES_PATH
# in relation to source directory
EXPECTED_UT_COVERED_SRC_FILES: Sequence[str] = (
    "pow3.hpp",
    "twice.hpp",
    "square.hpp",
)


@dataclass
class ScargoCommandTestState:
    target_id: ScargoTarget
    proj_name: str
    proj_to_copy_path: Optional[Path] = None
    proj_path: Optional[Path] = None
    src_dir_name: str = "src"

    def __post_init__(self) -> None:
        self.runner = ScargoTestRunner()

        if self.target_id == ScargoTarget.esp32:
            self.src_dir_name = "main"

    def assert_gcov_output_files(self, detailed_coverage: bool = False) -> None:
        config = get_scargo_config_or_exit()
        test_dir_name = "tests"
        project_dir = config.project_root

        test_build_dir = project_dir / "build" / test_dir_name

        errmsg = f"Build directory '{test_build_dir}' does not exist"
        assert test_build_dir.is_dir(), errmsg

        gcov_report_htmlfile = test_build_dir / Path(f"{SCARGO_UT_COV_FILES_PREFIX}.html")

        errmsg = f"File '{gcov_report_htmlfile}' does not exist"
        assert gcov_report_htmlfile.is_file(), errmsg

        if not detailed_coverage:
            return

        gcov_report_htmlfile = test_build_dir / Path(f"{SCARGO_UT_COV_FILES_PREFIX}.details.html")

        errmsg = f"File '{gcov_report_htmlfile}' does not exist"
        assert gcov_report_htmlfile.is_file(), errmsg

        gcov_report_jsonfile = test_build_dir / Path(f"{SCARGO_UT_COV_FILES_PREFIX}.json")

        errmsg = f"File '{gcov_report_jsonfile}' does not exist"
        assert gcov_report_jsonfile.is_file(), errmsg

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

        errmsg = "GCOV coverage: output json file list cannot be empty"
        errmsg += " - expected records for covered files"
        assert bool(covered_files), errmsg

        for expected in expected_files:
            expected_file = config.project_root / Path(self.src_dir_name) / expected

            errmsg = f"GCOV coverage: expected file '{expected_file}' not found"
            errmsg += " in GCOV covered files in JSON"
            assert expected_file in covered_files, errmsg

    def create_dummy_src_files(self, fpaths: Sequence[str]) -> None:
        config = get_scargo_config_or_exit()
        for path in fpaths:
            dummy_file_path = config.project_root / Path(self.src_dir_name) / path
            dummy_file_path.parent.mkdir(parents=True, exist_ok=True)
            dummy_file_path.touch()

    def set_config_src_extensions(self, ext: List[str]) -> None:
        config = get_scargo_config_or_exit()
        config_path = config.project_root / "scargo.toml"

        with open(config_path, encoding="utf-8") as scargo_config_file:
            config_data = tomlkit.load(scargo_config_file)

        config_data["project"]["src_extensions"] = ext  # type: ignore
        with open(config_path, "w", encoding="utf-8") as scargo_lock_file:
            tomlkit.dump(config_data, scargo_lock_file)


@pytest.fixture
def active_state_x86_path() -> ScargoCommandTestState:
    project_path = TEST_DATA_PATH / "test_projects/common_scargo_project"
    return ScargoCommandTestState(
        target_id=ScargoTarget.x86,
        proj_name=project_path.name,
        proj_to_copy_path=project_path,
    )


@pytest.fixture
def active_state_esp32_path() -> ScargoCommandTestState:
    project_path = TEST_DATA_PATH / "test_projects/common_scargo_project_esp32"
    return ScargoCommandTestState(
        target_id=ScargoTarget.esp32,
        proj_name=project_path.name,
        proj_to_copy_path=project_path,
    )


@pytest.fixture
def active_state_atsam_path() -> ScargoCommandTestState:
    project_path = TEST_DATA_PATH / "test_projects/common_scargo_project_atsam"
    return ScargoCommandTestState(
        target_id=ScargoTarget.atsam,
        proj_name=project_path.name,
        proj_to_copy_path=project_path,
    )


@pytest.fixture
def test_state(request: FixtureRequest, tmp_path_factory: TempPathFactory, use_local_scargo: None) -> Any:
    test_state = request.param
    test_state.proj_path = tmp_path_factory.mktemp(test_state.proj_name)
    os.chdir(test_state.proj_path)
    return test_state


@pytest.fixture
def setup_project(test_state: ScargoCommandTestState) -> None:
    """
    Setup new project or copy existing project, chdir into it and run scargo update
    """
    errmsg = f"setup_project(): project in '{test_state.proj_to_copy_path}' "
    errmsg += "does not exists - accepted only existing projects"
    is_valid = test_state.proj_to_copy_path and Path(test_state.proj_to_copy_path).exists()
    assert is_valid, errmsg

    # Copy existing project, backward compatibility tests
    shutil.copytree(
        src=str(test_state.proj_to_copy_path),
        dst=test_state.proj_name,
        dirs_exist_ok=True,
    )

    # Copy fake tests to check GCOV coverage
    dest_test_dir = Path(test_state.proj_name) / "tests/ut"
    shutil.copytree(src=UT_FILES_PATH / "pow3", dst=dest_test_dir / "pow3", dirs_exist_ok=True)
    shutil.copytree(src=UT_FILES_PATH / "square", dst=dest_test_dir / "square", dirs_exist_ok=True)
    shutil.copytree(src=UT_FILES_PATH / "twice", dst=dest_test_dir / "twice", dirs_exist_ok=True)

    # Copy fake sources
    shutil.copytree(
        src=UT_FILES_PATH / "src",
        dst=Path(test_state.proj_name) / test_state.src_dir_name,
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
        pytest.lazy_fixture("active_state_esp32_path"),  # type: ignore
        pytest.lazy_fixture("active_state_atsam_path"),  # type: ignore
    ],
    ids=["copy_project_x86", "copy_project_esp32", "copy_project_atsam"],
    scope="session",
    indirect=True,
)
@pytest.mark.xdist_group(name="TestFlowScargoCommandTest")
class TestFlowScargoCommandTest:
    def _get_fake_src_files(self) -> List[str]:
        expected_files = [
            "echo.c",
            "test/test.cpp",
            "assembly.s",
            "assembly/capital_assembly.S",
            "assembly/asm.asm",
            "cc/cctest.cc",
            "cc/cxxtest.cxx",
        ]
        return expected_files

    def test_cli_basic(self, test_state: ScargoCommandTestState, setup_project: None) -> None:
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

    def test_cli_detailed_coverage(self, test_state: ScargoCommandTestState, setup_project: None) -> None:
        result = test_state.runner.invoke(cli, ["update"])
        assert result.exit_code == 0

        result = test_state.runner.invoke(cli, ["test", "--detailed-coverage"])
        assert result.exit_code == 0
        assert "No tests were found!!!" not in result.output

        # Expected fake unit tests - common
        test_state.assert_gcov_detailed_coverage(EXPECTED_UT_COVERED_SRC_FILES)

        # create dummy fake files and re-run tests
        expected_files = self._get_fake_src_files()
        test_state.create_dummy_src_files(expected_files)
        test_state.runner.invoke(cli, ["test", "--detailed-coverage"])

        expected_files.extend(EXPECTED_UT_COVERED_SRC_FILES)
        test_state.assert_gcov_detailed_coverage(expected_files)

    def test_cli_detailed_coverage_filtering(self, test_state: ScargoCommandTestState, setup_project: None) -> None:
        expected_extensions = [".s", ".cxx"]
        test_state.set_config_src_extensions(expected_extensions)

        result = test_state.runner.invoke(cli, ["update"])
        assert result.exit_code == 0

        # create dummy fake files and re-run tests
        expected_files = self._get_fake_src_files()
        test_state.create_dummy_src_files(expected_files)
        test_state.runner.invoke(cli, ["test", "--detailed-coverage"])

        filtered = []
        for ff in expected_files:
            valid = any([ff.endswith(ext) for ext in expected_extensions])
            if not valid:
                continue
            filtered.append(ff)

        filtered.extend(EXPECTED_UT_COVERED_SRC_FILES)
        test_state.assert_gcov_detailed_coverage(filtered)
