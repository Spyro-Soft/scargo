import os
from pathlib import Path
from shutil import copy, copytree

import pytest
from utils import (  # type: ignore[import]
    ScargoTestRunner,
    add_profile_to_toml,
    assert_str_in_CMakeLists,
    assert_str_in_file,
    get_bin_name,
    get_copyright_text,
    get_project_name,
)

from scargo.cli import cli
from scargo.jinja.env_gen import generate_env
from scargo.scargo_src.utils import get_project_root

TEST_PROJECT_NAME = "common_scargo_project"
TEST_PROJECT_ESP32_NAME = "common_scargo_project_esp32"
TEST_PROJECT_STM32_NAME = "common_scargo_project_stm32"
NEW_TEST_PROJECT_NAME = "test_new_project"
IT_PATH = Path("tests", "it").absolute()
TEST_PROJECT_PATH = Path(IT_PATH, "test_projects", TEST_PROJECT_NAME)
TEST_LIBS_PATH = Path(IT_PATH, "test_projects", "test_files", "test_libs")
ESP_32_BUILD_PATH = Path(IT_PATH, "test_projects", "test_files", "esp_32_build")
TEST_PROJECT_ESP32_PATH = Path(IT_PATH, "test_projects", TEST_PROJECT_ESP32_NAME)
TEST_PROJECT_STM32_PATH = Path(IT_PATH, "test_projects", TEST_PROJECT_STM32_NAME)


FIX_TEST_FILES_PATH = Path(IT_PATH, "test_projects", "test_files", "fix_test_files")

IDF_SDKCONFIG_FILE_PATH = Path(
    IT_PATH, "test_projects", "test_files", "esp_32_idf_config", "sdkconfig"
)

PROJECT_CREATION_x86 = [
    "new_project_x86",
    "copy_project_x86",
]

PROJECT_CREATION_esp32 = [
    "new_project_esp32",
    "copy_project_esp32",
]

PROJECT_CREATION_stm32 = [
    "new_project_stm32",
    "copy_project_stm32",
]


@pytest.fixture()
def new_project_x86() -> None:
    # Arrange
    runner = ScargoTestRunner()

    # New Help
    result = runner.invoke(cli, ["new", "-h"])
    assert result.exit_code == 0

    # New
    result = runner.invoke(cli, ["new", NEW_TEST_PROJECT_NAME, "--target=x86"])
    bin_name = get_bin_name()
    expected_bin_file_path = Path("src", f"{bin_name.lower()}.cpp")
    assert result.exit_code == 0
    assert expected_bin_file_path.is_file()


@pytest.fixture()
def new_project_esp32() -> None:
    # Arrange
    runner = ScargoTestRunner()

    # New
    result_new_esp32 = runner.invoke(
        cli, ["new", NEW_TEST_PROJECT_NAME, "--target=esp32"]
    )
    bin_name = get_bin_name()
    expected_bin_file_path = Path("main", f"{bin_name.lower()}.cpp")
    assert result_new_esp32.exit_code == 0
    assert expected_bin_file_path.is_file()


@pytest.fixture()
def new_project_stm32() -> None:
    # Arrange
    runner = ScargoTestRunner()

    # New
    result_new_stm32 = runner.invoke(
        cli, ["new", NEW_TEST_PROJECT_NAME, "--target=stm32"]
    )
    bin_name = get_bin_name()
    expected_bin_file_path = Path("src", f"{bin_name.lower()}.cpp")
    assert result_new_stm32.exit_code == 0
    assert expected_bin_file_path.is_file()


@pytest.fixture()
def copy_project_x86() -> None:
    copytree(TEST_PROJECT_PATH, os.getcwd(), dirs_exist_ok=True)
    project_path = get_project_root()
    docker_path = Path(project_path, ".devcontainer")
    generate_env(docker_path)


@pytest.fixture()
def copy_project_esp32() -> None:
    copytree(TEST_PROJECT_ESP32_PATH, os.getcwd(), dirs_exist_ok=True)
    project_path = get_project_root()
    docker_path = Path(project_path, ".devcontainer")
    generate_env(docker_path)


@pytest.fixture()
def copy_project_stm32() -> None:
    copytree(TEST_PROJECT_STM32_PATH, os.getcwd(), dirs_exist_ok=True)
    project_path = get_project_root()
    docker_path = Path(project_path, ".devcontainer")
    generate_env(docker_path)


@pytest.mark.parametrize("project_creation", PROJECT_CREATION_x86)
def test_project_x86_dev_flow(
    project_creation: str, request: pytest.FixtureRequest
) -> None:
    # Arrange
    build_dir_path = Path("build")
    src_dir = "src"
    runner = ScargoTestRunner()

    # Help
    result = runner.invoke(cli, ["-h"])
    assert result.exit_code == 0

    # New Help, New or copy existing project for regression tests
    request.getfixturevalue(project_creation)

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
    project_name = get_project_name()
    debug_project_file_path = Path("build", "Debug", "bin", project_name)

    result = runner.invoke(cli, ["build", "--profile", "Debug"])
    assert result.exit_code == 0
    assert debug_project_file_path.is_file()

    # Build --profile Release
    release_project_file_path = Path("build", "Release", "bin", project_name)

    result = runner.invoke(cli, ["build", "--profile", "Release"])
    assert result.exit_code == 0
    assert release_project_file_path.is_file()

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

    # Gen -u
    result = runner.invoke(cli, ["gen", "-u", src_dir])
    assert result.exit_code == 0

    # Test
    result = runner.invoke(cli, ["test"])
    assert result.exit_code == 0

    # Run
    result = runner.invoke(cli, ["run"])
    assert "Hello World!" in result.output
    assert result.exit_code == 0

    # Check fail
    copytree(FIX_TEST_FILES_PATH, Path(os.getcwd(), src_dir), dirs_exist_ok=True)
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


@pytest.mark.parametrize("project_creation", PROJECT_CREATION_esp32)
def test_project_esp32_dev_flow(
    project_creation: str, request: pytest.FixtureRequest
) -> None:
    # ARRANGE
    runner = ScargoTestRunner()

    # New or copy existing project for regression tests
    request.getfixturevalue(project_creation)

    # Docker Run
    result_docker_run = runner.invoke(cli, ["docker", "run"])
    assert result_docker_run.exit_code == 0

    # IDF.py
    copy(IDF_SDKCONFIG_FILE_PATH, Path(os.getcwd()))

    # Update
    result = runner.invoke(cli, ["update"])
    assert result.exit_code == 0

    # Build
    build_path = Path("build/Debug")
    result = runner.invoke(cli, ["build"])
    assert build_path.is_dir()
    assert result.exit_code == 0

    # Gen --fs
    result = runner.invoke(cli, ["gen", "--fs"])
    spiffs_file_path = Path("build", "spiffs.bin")
    assert result.exit_code == 0
    assert spiffs_file_path.is_file()

    # Check
    result = runner.invoke(cli, ["check"])
    assert result.exit_code == 0

    # Test
    result = runner.invoke(cli, ["test"])
    assert result.exit_code == 0


@pytest.mark.parametrize("project_creation", PROJECT_CREATION_stm32)
def test_project_stm32_dev_flow(
    project_creation: str, request: pytest.FixtureRequest
) -> None:
    # Arrange
    runner = ScargoTestRunner()

    # New or copy existing project for regression tests
    request.getfixturevalue(project_creation)

    # Docker Run
    result = runner.invoke(cli, ["docker", "run"])
    assert result.exit_code == 0

    # Update
    result = runner.invoke(cli, ["update"])
    assert result.exit_code == 0

    # Build
    build_path = Path("build/Debug")
    result = runner.invoke(cli, ["build"])
    assert build_path.is_dir()
    assert result.exit_code == 0

    # Check
    result = runner.invoke(cli, ["check"])
    assert result.exit_code == 0

    # Test
    result = runner.invoke(cli, ["test"])
    assert result.exit_code == 0
