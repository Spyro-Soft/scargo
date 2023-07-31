import os
from pathlib import Path
from shutil import copytree
from typing import Generator, Optional
from unittest.mock import MagicMock, patch

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from pytest import TempdirFactory

from scargo.commands.new import scargo_new
from scargo.commands.update import scargo_update
from scargo.config import (
    CheckConfig,
    ChecksConfig,
    ConanConfig,
    Config,
    Dependencies,
    DocConfig,
    ProfileConfig,
    ProjectConfig,
    ScargoConfig,
    Target,
    TestConfig,
    TodoCheckConfig,
)
from scargo.path_utils import get_project_root_or_none
from tests.it.utils import get_bin_name

TARGET_X86 = Target.get_target_by_id("x86")
TARGET_ESP32 = Target.get_target_by_id("esp32")
TARGET_STM32 = Target.get_target_by_id("stm32")

TEST_PROJECT_NAME = "common_scargo_project"
TEST_PROJECT_STM32_NAME = "common_scargo_project_stm32"
TEST_PROJECT_ESP32_NAME = "common_scargo_project_esp32"
TEST_DATA_PATH = Path(os.path.dirname(os.path.realpath(__file__))).parent / "test_data"
TEST_PROJECT_PATH = Path(TEST_DATA_PATH, "test_projects", TEST_PROJECT_NAME)
TEST_PROJECT_ESP32_PATH = Path(TEST_DATA_PATH, "test_projects", TEST_PROJECT_ESP32_NAME)
TEST_PROJECT_STM32_PATH = Path(TEST_DATA_PATH, "test_projects", TEST_PROJECT_STM32_NAME)


@pytest.fixture()
def config(fs: FakeFilesystem) -> Config:  # type: ignore[no-any-unimported]
    return Config(
        project=ProjectConfig(
            **{
                "name": "test_project",
                "version": "0.1.0",
                "description": "Project description.",
                "homepage_url": "www.example.com",
                "bin_name": "test_project",
                "lib_name": None,
                "target": "x86",
                "build_env": "native",
                "docker-file": Path(".devcontainer/Dockerfile-custom"),
                "docker-image-tag": "test_project-dev:1.0",
                "in-repo-conan-cache": False,
                "cc": "gcc",
                "cxx": "g++",
                "cxxstandard": "17",
                "cflags": "-Wall -Wextra",
                "cxxflags": "-Wall -Wextra",
            }
        ),
        profile={
            "Debug": ProfileConfig(cflags="-g", cxxflags="-g"),
            "Release": ProfileConfig(cflags="-O3 -DNDEBUG", cxxflags="-O3 -DNDEBUG"),
            "RelWithDebInfo": ProfileConfig(
                cflags="-O2 -g -DNDEBUG", cxxflags="-O2 -g -DNDEBUG"
            ),
            "MinSizeRel": ProfileConfig(cflags="-Os -DNDEBUG", cxxflags="-Os -DNDEBUG"),
        },
        check=ChecksConfig(
            **{
                "exclude": [],
                "pragma": CheckConfig(description=None, exclude=[]),
                "copyright": CheckConfig(description="Copyright", exclude=[]),
                "todo": TodoCheckConfig(
                    description=None, exclude=[], keywords=["TODO", "todo"]
                ),
                "clang-format": CheckConfig(description=None, exclude=[]),
                "clang-tidy": CheckConfig(description=None, exclude=[]),
                "cyclomatic": CheckConfig(description=None, exclude=[]),
            }
        ),
        doc=DocConfig(exclude=[]),
        tests=TestConfig(
            **{
                "cc": "gcc",
                "cxx": "g++",
                "cflags": "-Wall -Wextra -Og --coverage -fkeep-inline-functions -fkeep-static-consts",
                "cxxflags": "-Wall -Wextra -Og --coverage -fkeep-inline-functions -fkeep-static-consts",
                "gcov-executable": "",
            }
        ),
        dependencies=Dependencies(
            general=[], build=[], tool=[], test=["gtest/cci.20210126"]
        ),
        conan=ConanConfig(repo={}),
        stm32=None,
        esp32=None,
        scargo=ScargoConfig(
            console_log_level="INFO",
            file_log_level="WARNING",
            update_exclude=[],
            version="1.0.7",
        ),
        project_root=Path(),
    )


@pytest.fixture
def mock_subprocess_run() -> Generator[MagicMock, None, None]:
    with patch("subprocess.run") as mock_subprocess_run:
        yield mock_subprocess_run


@pytest.fixture(scope="session")
def coppy_test_project(tmpdir_factory: TempdirFactory) -> Path:
    """This fixture just copying test project to test backward compatibility"""
    tmp_dir = tmpdir_factory.mktemp("coppy_test_project")
    os.chdir(tmp_dir)
    copytree(TEST_PROJECT_PATH, os.getcwd(), dirs_exist_ok=True)
    project_path = get_project_root_or_none()
    assert project_path is not None
    return project_path


@pytest.fixture(scope="session")
def coppy_test_project_esp32(tmpdir_factory: TempdirFactory) -> Path:
    """This fixture just copying esp32 test project to test backward compatibility"""
    tmp_dir = tmpdir_factory.mktemp("coppy_test_project_esp32")
    os.chdir(tmp_dir)
    copytree(TEST_PROJECT_ESP32_PATH, os.getcwd(), dirs_exist_ok=True)
    project_path = get_project_root_or_none()
    assert project_path is not None
    return project_path


@pytest.fixture(scope="session")
def coppy_test_project_stm32(tmpdir_factory: TempdirFactory) -> Path:
    """This fixture just copying stm32 test project to test backward compatibility"""
    tmp_dir = tmpdir_factory.mktemp("coppy_test_project_stm32")
    os.chdir(tmp_dir)
    copytree(TEST_PROJECT_STM32_PATH, os.getcwd(), dirs_exist_ok=True)
    project_path = get_project_root_or_none()
    assert project_path is not None
    return project_path


@pytest.fixture()
def new_project_x86(tmpdir_factory: TempdirFactory) -> Optional[Path]:
    tmp_path = tmpdir_factory.mktemp("new_test_project_x86")
    os.chdir(tmp_path)
    project_name = "test_project"
    scargo_new(
        project_name,
        bin_name="main",
        lib_name="test_lib",
        target=TARGET_X86,
        create_docker=False,
        git=False,
    )
    os.chdir(project_name)
    # h file for gen tests added
    Path("src/test_lib.h").touch()
    scargo_update(Path(os.getcwd(), "scargo.toml"))
    bin_name = get_bin_name()
    expected_bin_file_path = Path("src", f"{bin_name.lower()}.cpp")
    assert expected_bin_file_path.is_file()
    return get_project_root_or_none()


@pytest.fixture()
def new_project_esp32(tmpdir_factory: TempdirFactory) -> Optional[Path]:
    tmp_path = tmpdir_factory.mktemp("new_test_project_esp32")
    os.chdir(tmp_path)
    project_name = "test_project"
    scargo_new(
        project_name,
        bin_name="test_bin",
        lib_name="test_lib",
        target=TARGET_ESP32,
        create_docker=False,
        git=False,
    )
    os.chdir(project_name)
    # h file for gen tests added
    Path("main/test_lib.h").touch()
    scargo_update(Path(os.getcwd(), "scargo.toml"))
    bin_name = get_bin_name()
    expected_bin_file_path = Path("main", f"{bin_name.lower()}.cpp")
    assert expected_bin_file_path.is_file()
    return get_project_root_or_none()


@pytest.fixture()
def new_project_stm32(tmpdir_factory: TempdirFactory) -> Optional[Path]:
    tmp_path = tmpdir_factory.mktemp("new_test_project_stm32")
    os.chdir(tmp_path)
    project_name = "test_project"
    scargo_new(
        project_name,
        bin_name="test_bin",
        lib_name="test_lib",
        target=TARGET_STM32,
        create_docker=False,
        git=False,
    )
    os.chdir(project_name)
    # h file for gen tests added
    Path("src/test_lib.h").touch()
    scargo_update(Path(os.getcwd(), "scargo.toml"))
    bin_name = get_bin_name()
    expected_bin_file_path = Path("src", f"{bin_name.lower()}.cpp")
    assert expected_bin_file_path.is_file()
    return get_project_root_or_none()
