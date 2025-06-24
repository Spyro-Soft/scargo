import os
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from scargo.config import (
    CheckConfig,
    ChecksConfig,
    ConanConfig,
    Config,
    CppCheckConfig,
    Dependencies,
    DocConfig,
    ProfileConfig,
    ProjectConfig,
    ScargoConfig,
    ScargoTarget,
    TestConfig,
    TodoCheckConfig,
)

TARGET_X86 = ScargoTarget.x86
TARGET_ESP32 = ScargoTarget.esp32
TARGET_STM32 = ScargoTarget.stm32

TEST_PROJECT_NAME = "common_scargo_project"
TEST_PROJECT_STM32_NAME = "common_scargo_project_stm32"
TEST_PROJECT_ESP32_NAME = "common_scargo_project_esp32"
TEST_DATA_PATH = Path(os.path.dirname(os.path.realpath(__file__))).parent / "test_data"
TEST_PROJECT_PATH = Path(TEST_DATA_PATH, "test_projects", TEST_PROJECT_NAME)
TEST_PROJECT_ESP32_PATH = Path(TEST_DATA_PATH, "test_projects", TEST_PROJECT_ESP32_NAME)
TEST_PROJECT_STM32_PATH = Path(TEST_DATA_PATH, "test_projects", TEST_PROJECT_STM32_NAME)


@pytest.fixture()
def config(fs: FakeFilesystem) -> Config:
    return Config(
        project=ProjectConfig(
            **{  # type: ignore
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
            "RelWithDebInfo": ProfileConfig(cflags="-O2 -g -DNDEBUG", cxxflags="-O2 -g -DNDEBUG"),
            "MinSizeRel": ProfileConfig(cflags="-Os -DNDEBUG", cxxflags="-Os -DNDEBUG"),
        },
        check=ChecksConfig(
            **{  # type: ignore
                "exclude": [],
                "pragma": CheckConfig(description=None, exclude=[]),
                "copyright": CheckConfig(description="Copyright", exclude=[]),
                "todo": TodoCheckConfig(description=None, exclude=[], keywords=["TODO", "todo"]),
                "cppcheck": CppCheckConfig(description=None, suppress=[], directories=[]),
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
        dependencies=Dependencies(general=[], build=[], tool=[], test=["gtest/cci.20210126"]),
        conan=ConanConfig(repo={}),
        atsam=None,
        stm32=None,
        esp32=None,
        scargo=ScargoConfig(  # type: ignore
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
