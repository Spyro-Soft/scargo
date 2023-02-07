import os
from pathlib import Path
from shutil import copytree

import pytest
from typer.testing import CliRunner
from utils import assert_str_in_file, get_copyright_text

from scargo import cli

TEST_FILES_PATH = Path(pytest.it_path, "test_projects", "test_files", "fix_test_files")


def test_check_fix_flow_x86():
    # ARRANGE
    src_dir = "src"
    runner = CliRunner()
    runner.invoke(cli, ["new", pytest.new_test_project_name])
    copytree(TEST_FILES_PATH, Path(os.getcwd(), src_dir), dirs_exist_ok=True)

    # ACT & ASSERT
    result = runner.invoke(cli, ["check"])
    assert result.exit_code == 1

    result = runner.invoke(cli, ["fix"])
    assert result.exit_code == 0
    assert assert_str_in_file(Path(src_dir, "fix_test_bin.cpp"), get_copyright_text())
    assert assert_str_in_file(Path(src_dir, "fix_test_lib.cpp"), get_copyright_text())
    assert assert_str_in_file(Path(src_dir, "fix_test_lib.h"), get_copyright_text())
    assert assert_str_in_file(Path(src_dir, "fix_test_lib.h"), "#pragma once")

    result = runner.invoke(cli, ["check"])
    assert result.exit_code == 0
