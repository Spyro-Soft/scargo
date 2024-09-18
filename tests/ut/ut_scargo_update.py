import os
from pathlib import Path
from typing import List, Set

import pytest
from pytest_subprocess import FakeProcess

from scargo.commands.docker import get_docker_compose_command
from scargo.commands.new import scargo_new
from scargo.commands.update import scargo_update
from scargo.config import ScargoTarget
from scargo.global_values import SCARGO_DEFAULT_CONFIG_FILE
from scargo.utils.conan_utils import DEFAULT_PROFILES
from tests.ut.utils import get_all_files_recursively

TEST_PROJECT_NAME = "test_project"


def get_expected_files(target: List[ScargoTarget]) -> Set[str]:
    project_files = {
        "LICENSE",
        "CMakeLists.txt",
        "scargo.toml",
        "scargo.lock",
        ".clang-tidy",
        "conanfile.py",
        ".clang-format",
        "README.md",
        ".gitignore",
        ".gitlab-ci.yml",
        "tests/CMakeLists.txt",
        "tests/conanfile.py",
        "tests/mocks/CMakeLists.txt",
        "tests/mocks/static_mock/CMakeLists.txt",
        "tests/mocks/static_mock/static_mock.h",
        "tests/it/CMakeLists.txt",
        "tests/ut/CMakeLists.txt",
        ".vscode/tasks.json",
        ".devcontainer/.env",
        ".devcontainer/Dockerfile",
        ".devcontainer/.gitlab-ci-custom.yml",
        ".devcontainer/docker-compose.yaml",
        ".devcontainer/devcontainer.json",
        ".devcontainer/Dockerfile-custom",
        ".devcontainer/requirements.txt",
        "src/CMakeLists.txt",
        "src/test_project.cpp",
    }

    for t in target:
        if len(target) > 1:
            project_files.add(f"src/{t.value}-src.cmake")
        for profile in DEFAULT_PROFILES:
            project_files.add(f"config/conan/profiles/{t.value}_{profile}")

    if ScargoTarget.atsam in target:
        project_files.update(
            {
                ".devcontainer/openocd-script.cfg",
                "config/conan/profiles/arm_gcc_toolchain.cmake",
            }
        )

    if ScargoTarget.esp32 in target:
        project_files.update({"version.txt", "partitions.csv"})

    if ScargoTarget.stm32 in target:
        project_files.update(
            {
                ".devcontainer/openocd-script.cfg",
                "config/conan/profiles/stm32_gcc_toolchain.cmake",
            }
        )

    return project_files


@pytest.mark.parametrize(
    "target",
    [ScargoTarget.x86, ScargoTarget.esp32, ScargoTarget.stm32, ScargoTarget.atsam],
)
def test_update_project_content(target: ScargoTarget, tmp_path: Path) -> None:
    os.chdir(tmp_path)
    scargo_new(
        TEST_PROJECT_NAME,
        bin_name=None,
        lib_name=None,
        targets=[target],
        create_docker=False,
        git=False,
        chip=[],
    )
    os.chdir(TEST_PROJECT_NAME)

    scargo_update(Path(SCARGO_DEFAULT_CONFIG_FILE))

    all_files = get_all_files_recursively()
    expected_files = get_expected_files([target])
    assert all_files - expected_files == set()
    assert expected_files - all_files == set()


def test_update_multitarget_project_content(tmp_path: Path) -> None:
    os.chdir(tmp_path)
    targets = [
        ScargoTarget.x86,
        ScargoTarget.esp32,
        ScargoTarget.stm32,
        ScargoTarget.atsam,
    ]
    scargo_new(
        TEST_PROJECT_NAME,
        bin_name=None,
        lib_name=None,
        targets=targets,
        create_docker=False,
        git=False,
        chip=[],
    )
    os.chdir(TEST_PROJECT_NAME)

    scargo_update(Path(SCARGO_DEFAULT_CONFIG_FILE))

    all_files = get_all_files_recursively()
    expected_files = get_expected_files(targets)
    assert all_files - expected_files == set()
    assert expected_files - all_files == set()


def test_update_project_with_docker(tmp_path: Path, fp: FakeProcess) -> None:
    os.chdir(tmp_path)
    scargo_new(TEST_PROJECT_NAME, None, None, [ScargoTarget.x86], True, False, [])
    os.chdir(TEST_PROJECT_NAME)
    called_subprocess_cmd = get_docker_compose_command()
    called_subprocess_cmd.extend(["pull"])
    fp.register(called_subprocess_cmd)
    fp.register(["conan", "profile", "list"])
    fp.register(["conan", "profile", "detect"])
    fp.register(["pip", "show", "scargo"])

    scargo_update(Path(SCARGO_DEFAULT_CONFIG_FILE))


def test_update_project_docker_pull_fails(tmp_path: Path, fp: FakeProcess) -> None:
    os.chdir(tmp_path)
    project_name = "test_project_with_docker"
    scargo_new(project_name, None, None, [ScargoTarget.x86], True, False, [])
    os.chdir(project_name)
    cmd_pull = get_docker_compose_command()
    cmd_pull.extend(["pull"])
    fp.register(cmd_pull, returncode=1)
    cmd_build = get_docker_compose_command()
    fp.register(["conan", "profile", "list"])
    fp.register(["conan", "profile", "detect"])
    fp.register(["pip", "show", "scargo"])

    cmd_build.extend(["build"])
    fp.register(cmd_build)
    scargo_update(Path(SCARGO_DEFAULT_CONFIG_FILE))
