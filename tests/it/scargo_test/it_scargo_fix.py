import os
from pathlib import Path
from shutil import copytree

import pytest
from typer.testing import CliRunner
from utils import assert_str_in_file, get_copyright_text, get_project_target

from scargo import cli
from scargo.scargo_src.sc_config import TARGETS

PRECONDITIONS = [
    "precondition_regression_tests",
    "precondition_regular_tests",
    "precondition_regression_tests_esp32",
    "precondition_regression_tests_stm32",
]
TEST_FILES_PATH = Path(pytest.it_path, "test_projects", "test_files", "fix_test_files")


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_fix_all(precondition, request, caplog):
    # ARRANGE
    request.getfixturevalue(precondition)
    src_dir = TARGETS.get(get_project_target(), "source_dir").source_dir
    runner = CliRunner()

    # ACT
    copytree(TEST_FILES_PATH, Path(os.getcwd(), src_dir), dirs_exist_ok=True)
    result = runner.invoke(cli, ["fix"])

    # ASSERT
    assert result.exit_code == 0
    assert "Finished clang-format check. Fixed problems in 3 files." in caplog.text
    assert "Finished copyright check. Fixed problems in 3 files." in caplog.text
    assert "Finished pragma check. Fixed problems in 1 files." in caplog.text


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_fix_pragma(precondition, request, caplog):
    # ARRANGE
    request.getfixturevalue(precondition)
    src_dir = TARGETS.get(get_project_target(), "source_dir").source_dir
    runner = CliRunner()

    # ACT
    copytree(TEST_FILES_PATH, Path(os.getcwd(), src_dir), dirs_exist_ok=True)
    result = runner.invoke(cli, ["fix", "--pragma"])

    # ASSERT
    assert result.exit_code == 0
    assert assert_str_in_file(Path(src_dir, "fix_test_lib.h"), "#pragma once")
    assert "Finished pragma check. Fixed problems in 1 files." in caplog.text


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_fix_copyright(precondition, request, caplog):
    # ARRANGE
    request.getfixturevalue(precondition)
    src_dir = TARGETS.get(get_project_target(), "source_dir").source_dir
    runner = CliRunner()

    # ACT
    copytree(TEST_FILES_PATH, Path(os.getcwd(), src_dir), dirs_exist_ok=True)
    result = runner.invoke(cli, ["fix", "--copyright"])

    # ASSERT
    assert result.exit_code == 0
    assert assert_str_in_file(Path(src_dir, "fix_test_bin.cpp"), get_copyright_text())
    assert assert_str_in_file(Path(src_dir, "fix_test_lib.cpp"), get_copyright_text())
    assert assert_str_in_file(Path(src_dir, "fix_test_lib.h"), get_copyright_text())
    assert "Finished copyright check. Fixed problems in 3 files." in caplog.text


@pytest.mark.parametrize("precondition", PRECONDITIONS)
def test_fix_clang(precondition, request, caplog):
    # ARRANGE
    request.getfixturevalue(precondition)
    src_dir = TARGETS.get(get_project_target(), "source_dir").source_dir
    runner = CliRunner()

    # ACT
    copytree(TEST_FILES_PATH, Path(os.getcwd(), src_dir), dirs_exist_ok=True)
    result = runner.invoke(cli, ["fix", "--clang-format"])

    # ASSERT
    assert result.exit_code == 0
    assert f"clang-format found error in file {src_dir}/fix_test_bin.cpp" in caplog.text
    assert f"clang-format found error in file {src_dir}/fix_test_lib.cpp" in caplog.text
    assert f"clang-format found error in file {src_dir}/fix_test_lib.h" in caplog.text
    assert "Finished clang-format check. Fixed problems in 3 files." in caplog.text


def test_fix_caps_fail():
    # ARRANGE
    runner = CliRunner()

    # ACT
    result = runner.invoke(cli, ["FIX"])

    # ASSERT
    assert result.exit_code == 2
    assert "Error: No such command" in result.output
