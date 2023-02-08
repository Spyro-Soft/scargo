import os
from pathlib import Path
from shutil import copytree

import pytest
from typer.testing import CliRunner
from utils import assert_str_in_file, get_copyright_text, get_bin_name, add_profile_to_toml

from scargo import cli

TEST_FILES_PATH = Path(pytest.it_path, "test_projects", "test_files", "fix_test_files")



def test_clean_build_check_fix_x86():
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


def test_new_project_x86_dev_flow(capfd):
    # Arrange
    runner = CliRunner()

    # Help
    result_help = runner.invoke(cli, ["-h"])
    assert result_help.exit_code == 0

    # New Help
    result_new_help = runner.invoke(cli, ["new", "-h"])
    assert result_new_help.exit_code == 0

    # New
    result_new_x86 = runner.invoke(
        cli, ["new", pytest.new_test_project_name, "--target=x86"]
    )
    bin_name = get_bin_name()
    expected_bin_file_path = Path("./src/", bin_name.lower() + ".cpp")
    assert expected_bin_file_path.exists()
    assert result_new_x86.exit_code == 0

    # Docker Run
    result_docker_run = runner.invoke(cli, ["docker", "run"])
    assert result_docker_run.exit_code == 0

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

    # Run
    result_run = runner.invoke(cli, ["run"])
    captured = capfd.readouterr()
    assert "Hello World!" in captured.out
    assert result_run.exit_code == 0


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


def test_change_scargo_toml_and_update():
    runner = CliRunner()
    runner.invoke(cli, ["new", pytest.new_test_project_name, "--target=x86"])
    add_profile_to_toml(
        "new",
        "cflags",
        "cxxflags",
        "cflags for new profile",
        "cxxflags for new profile",
    )
    result = runner.invoke(cli, ["update"])
    assert result.exit_code == 0
    cmakelists_lines = [line.strip() for line in open("CMakeLists.txt").readlines()]
    print(cmakelists_lines)
    assert 'set(CMAKE_C_FLAGS_NEW   "cflags for new profile")' in cmakelists_lines
    assert 'set(CMAKE_CXX_FLAGS_NEW "cxxflags for new profile")' in cmakelists_lines
