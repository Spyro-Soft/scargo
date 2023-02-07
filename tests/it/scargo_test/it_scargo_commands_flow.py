import os
from pathlib import Path
from shutil import copytree

import pytest
from typer.testing import CliRunner
from utils import assert_str_in_file, get_copyright_text

from scargo import cli

TEST_FILES_PATH = Path(pytest.it_path, "test_projects", "test_files", "fix_test_files")


def test_clean_build_x86():
    # ARRANGE
    build_dir_path = Path("build")
    debug_project_file_path = Path(
        "build", "Debug", "bin", pytest.new_test_project_name
    )
    release_project_file_path = Path(
        "build", "Release", "bin", pytest.new_test_project_name
    )
    runner = CliRunner()
    runner.invoke(cli, ["new", pytest.new_test_project_name])

    # Build
    result = runner.invoke(cli, ["build"])
    assert result.exit_code == 0
    assert build_dir_path.is_dir()

    # Clean
    result = runner.invoke(cli, ["clean"])
    assert result.exit_code == 0
    assert not build_dir_path.is_dir()

    # Build --profile Debug
    result = runner.invoke(cli, ["build", "--profile", "Debug"])
    assert result.exit_code == 0

    # Build --profile Release
    result = runner.invoke(cli, ["build", "--profile", "Release"])
    assert result.exit_code == 0

    assert debug_project_file_path.is_file()
    assert release_project_file_path.is_file()


def test_check_fix_flow_x86():
    # ARRANGE
    src_dir = "src"
    runner = CliRunner()
    runner.invoke(cli, ["new", pytest.new_test_project_name])
    copytree(TEST_FILES_PATH, Path(os.getcwd(), src_dir), dirs_exist_ok=True)

    # Check
    result = runner.invoke(cli, ["check"])
    assert result.exit_code == 1

    # Fix
    result = runner.invoke(cli, ["fix"])
    assert result.exit_code == 0
    assert assert_str_in_file(Path(src_dir, "fix_test_bin.cpp"), get_copyright_text())
    assert assert_str_in_file(Path(src_dir, "fix_test_lib.cpp"), get_copyright_text())
    assert assert_str_in_file(Path(src_dir, "fix_test_lib.h"), get_copyright_text())
    assert assert_str_in_file(Path(src_dir, "fix_test_lib.h"), "#pragma once")

    # Check
    result = runner.invoke(cli, ["check"])
    assert result.exit_code == 0
