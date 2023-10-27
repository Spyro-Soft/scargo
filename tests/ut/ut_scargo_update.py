import os
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
from pytest_subprocess import FakeProcess
from pytest_subprocess.fake_popen import FakePopen

from scargo.commands.docker import get_docker_compose_command
from scargo.commands.new import scargo_new
from scargo.commands.update import conan_add_remote, conan_add_user, scargo_update
from scargo.config import Config, Target
from tests.ut.ut_scargo_publish import (
    ENV_CONAN_PASSWORD,
    ENV_CONAN_USER,
    EXAMPLE_URL,
    REMOTE_REPO_NAME_1,
    REMOTE_REPO_NAME_2,
    REPO_NAME,
    config,
)

EXPECTED_FILES_AND_DIRS = [
    ".clang-format",
    ".clang-tidy",
    ".vscode",
    ".devcontainer",
    ".gitignore",
    ".gitlab-ci.yml",
    "CMakeLists.txt",
    "conanfile.py",
    "LICENSE",
    "README.md",
    "scargo.lock",
    "scargo.log",
    "scargo.toml",
    "src",
    "tests",
    "config",
]

TARGET_X86 = Target.get_target_by_id("x86")


def conan_remote_add_error(process: FakePopen, stderr: str) -> None:
    raise subprocess.CalledProcessError(1, process.args, b"", stderr.encode())


def test_update_project_content_without_docker(tmp_path: Path) -> None:
    os.chdir(tmp_path)
    project_name = "test_project"
    scargo_new(
        project_name,
        bin_name=None,
        lib_name=None,
        target=TARGET_X86,
        create_docker=False,
        git=False,
        chip=None,
    )
    os.chdir(tmp_path / project_name)
    scargo_update(Path("scargo.toml"))


def test_update_project_content_with_docker(tmp_path: Path, fp: FakeProcess) -> None:
    conan_add_remote_1_cmd = ["conan", "remote", "add", REMOTE_REPO_NAME_1, EXAMPLE_URL]
    conan_add_remote_2_cmd = ["conan", "remote", "add", REMOTE_REPO_NAME_2, EXAMPLE_URL]
    conan_user_cmd = "conan user"
    conan_source_cmd = [
        "conan",
        "source",
        ".",
    ]

    fp.register(conan_add_remote_1_cmd)
    fp.register(conan_add_remote_2_cmd)
    fp.register(conan_user_cmd, occurrences=2)
    fp.register(conan_source_cmd)
    os.chdir(tmp_path)
    project_name = "test_project_with_docker"
    scargo_new(project_name, None, None, TARGET_X86, True, False, None)
    os.chdir(project_name)
    called_subprocess_cmd = get_docker_compose_command()
    called_subprocess_cmd.extend(["pull"])
    fp.register(called_subprocess_cmd)
    fp.register(["conan", "profile", "list"])
    fp.register(["conan", "profile", "detect"])
    scargo_update(Path("scargo.toml"))
    for path in Path().iterdir():
        assert path.name in EXPECTED_FILES_AND_DIRS


def test_update_project_content_with_docker__build(
    tmp_path: Path, fp: FakeProcess
) -> None:
    conan_add_remote_1_cmd = ["conan", "remote", "add", REMOTE_REPO_NAME_1, EXAMPLE_URL]
    conan_add_remote_2_cmd = ["conan", "remote", "add", REMOTE_REPO_NAME_2, EXAMPLE_URL]
    conan_user_cmd = "conan user"
    conan_source_cmd = [
        "conan",
        "source",
        ".",
    ]

    fp.register(conan_add_remote_1_cmd)
    fp.register(conan_add_remote_2_cmd)
    fp.register(conan_user_cmd, occurrences=2)
    fp.register(conan_source_cmd)
    os.chdir(tmp_path)
    project_name = "test_project_with_docker"
    scargo_new(project_name, None, None, TARGET_X86, True, False, None)
    os.chdir(project_name)
    cmd_pull = get_docker_compose_command()
    cmd_pull.extend(["pull"])
    fp.register(cmd_pull, returncode=1)
    cmd_build = get_docker_compose_command()
    fp.register(["conan", "profile", "list"])
    fp.register(["conan", "profile", "detect"])
    cmd_build.extend(["build"])
    fp.register(cmd_build)
    scargo_update(Path("scargo.toml"))
    assert fp.call_count(cmd_build) == 1
    for path in Path().iterdir():
        assert path.name in EXPECTED_FILES_AND_DIRS


def test_conan_add_user(fp: FakeProcess) -> None:
    # ARRANGE
    conan_user_cmd = "conan user"
    add_user_cmd = [
        "conan",
        "user",
        "-p",
        ENV_CONAN_PASSWORD,
        "-r",
        REPO_NAME,
        ENV_CONAN_USER,
    ]
    fp.register(conan_user_cmd, occurrences=2)
    fp.register(add_user_cmd)

    # ACT
    with patch.dict(
        os.environ,
        {"CONAN_LOGIN_USERNAME": ENV_CONAN_USER, "CONAN_PASSWORD": ENV_CONAN_PASSWORD},
    ):
        conan_add_user(REPO_NAME)

    assert fp.calls[0] == conan_user_cmd
    assert fp.calls[1] == add_user_cmd
    assert len(fp.calls) == 2


def test_conan_add_remote_fail(
    config: Config,
    caplog: pytest.LogCaptureFixture,
    fp: FakeProcess,
) -> None:
    # ARRANGE
    fp.register(["conan", "remote", "add", REMOTE_REPO_NAME_1, EXAMPLE_URL])
    fp.register("conan user", occurrences=2)
    fp.register(
        ["conan", "remote", "add", REMOTE_REPO_NAME_2, EXAMPLE_URL], returncode=1
    )

    # ACT
    conan_add_remote(Path("some_path"), config)

    # ASSERT
    assert "Unable to add remote repository" in caplog.text


def test_conan_add_user_fail(caplog: pytest.LogCaptureFixture, fp: FakeProcess) -> None:
    # ARRANGE
    cmd = ["conan", "user", "-p", ENV_CONAN_PASSWORD, "-r", REPO_NAME, ENV_CONAN_USER]
    fp.register(cmd, returncode=1)
    fp.register("conan user", stdout="user_name")

    # ACT
    with patch.dict(
        os.environ,
        {"CONAN_LOGIN_USERNAME": ENV_CONAN_USER, "CONAN_PASSWORD": ENV_CONAN_PASSWORD},
    ):
        conan_add_user(REPO_NAME)

    # ASSERT
    assert "Unable to add user" in caplog.text


def test_conan_add_remote_already_exists(
    config: Config,
    caplog: pytest.LogCaptureFixture,
    fp: FakeProcess,
) -> None:
    # ARRANGE
    fp.register(["conan", "remote", "add", REMOTE_REPO_NAME_1, EXAMPLE_URL])
    fp.register("conan user", occurrences=2)
    error = f"ERROR: Remote '{REMOTE_REPO_NAME_2}' already exists in remotes (use --force to continue)"
    fp.register(
        ["conan", "remote", "add", REMOTE_REPO_NAME_2, EXAMPLE_URL],
        callback=conan_remote_add_error,
        callback_kwargs={"stderr": error},
    )

    # ACT
    conan_add_remote(Path("some_path"), config)

    # ASSERT
    assert "Unable to add remote repository" not in caplog.text
