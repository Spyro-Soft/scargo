import os
from pathlib import Path
from shutil import copytree

import pytest
from typer.testing import CliRunner
from utils import (
    add_profile_to_toml,
    assert_str_in_CMakeLists,
    assert_str_in_file,
    get_bin_name,
    get_copyright_text,
    get_project_name,
)

from scargo import cli

TEST_FILES_PATH = Path(pytest.it_path, "test_projects", "test_files", "fix_test_files")

PROJECT_CREATION_x86 = [
    "new_project_x86",
    "copy_project_x86",
]


@pytest.fixture()
def new_project_x86():
    # Arrange
    runner = CliRunner()

    # New Help
    result = runner.invoke(cli, ["new", "-h"])
    assert result.exit_code == 0

    # New
    result = runner.invoke(cli, ["new", pytest.new_test_project_name, "--target=x86"])
    bin_name = get_bin_name()
    expected_bin_file_path = Path("./src/", bin_name.lower() + ".cpp")
    assert expected_bin_file_path.exists()
    assert result.exit_code == 0


@pytest.fixture()
def copy_project_x86():

    copytree(pytest.predefined_test_project_path, os.getcwd(), dirs_exist_ok=True)


@pytest.fixture()
def copy_project_esp32():

    copytree(pytest.predefined_test_project_esp32_path, os.getcwd(), dirs_exist_ok=True)


@pytest.fixture()
def copy_project_stm32():

    copytree(pytest.predefined_test_project_stm32_path, os.getcwd(), dirs_exist_ok=True)


@pytest.mark.parametrize("project_creation", PROJECT_CREATION_x86)
def test_project_x86_dev_flow(project_creation, request, capfd):
    # Arrange
    build_dir_path = Path("build")
    src_dir = "src"
    runner = CliRunner()

    # Help
    result = runner.invoke(cli, ["-h"])
    assert result.exit_code == 0

    # New Help, New or copy existing project for regression tests
    request.getfixturevalue(project_creation)
    project_name = get_project_name()

    # Docker Run
    result = runner.invoke(cli, ["docker", "run"])
    assert result.exit_code == 0

    # Build
    result = runner.invoke(cli, ["build"])
    assert result.exit_code == 0
    assert build_dir_path.is_dir()

    # Clean
    result = runner.invoke(cli, ["clean"])
    assert result.exit_code == 0
    assert not build_dir_path.is_dir()

    # Build --profile Debug
    debug_project_file_path = Path("build", "Debug", "bin", project_name)

    result = runner.invoke(cli, ["build", "--profile", "Debug"])
    assert result.exit_code == 0
    assert debug_project_file_path.is_file()

    # Build --profile Release
    release_project_file_path = Path("build", "Release", "bin", project_name)

    result = runner.invoke(cli, ["build", "--profile", "Release"])
    assert result.exit_code == 0
    assert release_project_file_path.is_file()

    # Test
    # result = runner.invoke(cli, ["test"])
    # assert result.exit_code == 0

    # Run
    result = runner.invoke(cli, ["run"])
    captured = capfd.readouterr()
    assert "Hello World!" in captured.out
    assert result.exit_code == 0

    # Check fail
    copytree(TEST_FILES_PATH, Path(os.getcwd(), src_dir), dirs_exist_ok=True)
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

    # Update
    add_profile_to_toml(
        "new",
        "cflags",
        "cxxflags",
        "cflags for new profile",
        "cxxflags for new profile",
    )
    result = runner.invoke(cli, ["update"])
    assert result.exit_code == 0
    assert assert_str_in_CMakeLists('set(CMAKE_C_FLAGS_NEW   "cflags for new profile")')
    assert assert_str_in_CMakeLists(
        'set(CMAKE_CXX_FLAGS_NEW "cxxflags for new profile")'
    )


def test_new_project_esp32_dev_flow():
    # ARRANGE
    runner = CliRunner()

    # Help
    result_help = runner.invoke(cli, ["-h"])
    assert result_help.exit_code == 0

    # New Help
    result_new_help = runner.invoke(cli, ["new", "-h"])
    assert result_new_help.exit_code == 0

    # New
    result_new_esp32 = runner.invoke(
        cli, ["new", pytest.new_test_project_name, "--target=esp32"]
    )
    bin_name = get_bin_name()
    expected_bin_file_path = Path("./main/", bin_name.lower() + ".cpp")
    assert expected_bin_file_path.exists()
    assert result_new_esp32.exit_code == 0

    # Docker Run
    result_docker_run = runner.invoke(cli, ["docker", "run"])
    assert result_docker_run.exit_code == 0

    # IDF.py
    # Build
    result_build = runner.invoke(cli, ["build"])
    build_path = Path("build/Debug")
    assert build_path.is_dir()
    assert result_build.exit_code == 0

    # Gen --fs
    result_gen_fs = runner.invoke(cli, ["gen", "--fs"])
    spiffs_file_path = Path("build", "spiffs.bin")
    assert result_gen_fs.exit_code == 0
    assert spiffs_file_path.is_file()

    # Check
    result_check = runner.invoke(cli, ["check"])
    assert result_check.exit_code == 0

    # Test
    result_test = runner.invoke(cli, ["test"])
    assert result_test.exit_code == 0

    # idf.py -B build/Debug monitor
    # CTRL+]
    # exit


def test_new_project_stm32_dev_flow():
    # Arrange
    runner = CliRunner()

    # Help
    result_help = runner.invoke(cli, ["-h"])
    assert result_help.exit_code == 0

    # New Help
    result_new_help = runner.invoke(cli, ["new", "-h"])
    assert result_new_help.exit_code == 0

    # New
    result_new_stm32 = runner.invoke(
        cli, ["new", pytest.new_test_project_name, "--target=stm32"]
    )
    bin_name = get_bin_name()
    expected_bin_file_path = Path("./src/", bin_name.lower() + ".cpp")
    assert expected_bin_file_path.exists()
    assert result_new_stm32.exit_code == 0

    # Docker Run
    result_docker_run = runner.invoke(cli, ["docker", "run"])
    assert result_docker_run.exit_code == 0

    # IDF.py
    # Build
    result_build = runner.invoke(cli, ["build"])
    build_path = Path("build/Debug")
    assert build_path.is_dir()
    assert result_build.exit_code == 0

    # Check
    result_check = runner.invoke(cli, ["check"])
    assert result_check.exit_code == 0

    # Test
    result_test = runner.invoke(cli, ["test"])
    assert result_test.exit_code == 0
    # exit
