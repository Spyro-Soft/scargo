import os
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
from pytest_subprocess import FakeProcess
from pytest_subprocess.fake_popen import FakePopen

from scargo.config import Config
from scargo.utils.conan_utils import conan_add_remote, conan_remote_login, conan_source
from tests.ut.ut_scargo_publish import (
    ENV_CONAN_PASSWORD,
    ENV_CONAN_USER,
    EXAMPLE_URL,
    REMOTE_REPO_NAME_1,
    REMOTE_REPO_NAME_2,
    REPO_NAME,
)
from tests.ut.utils import get_test_project_config


@pytest.fixture
def config(fp: FakeProcess) -> Config:
    test_project_config = get_test_project_config()
    test_project_config.conan.repo[REMOTE_REPO_NAME_1] = EXAMPLE_URL
    test_project_config.conan.repo[REMOTE_REPO_NAME_2] = EXAMPLE_URL

    return test_project_config


def conan_remote_add_error(process: FakePopen, stderr: str = "") -> None:
    raise subprocess.CalledProcessError(1, process.args, b"", stderr.encode())


def test_conan_add_remote_fail(
    config: Config,
    caplog: pytest.LogCaptureFixture,
    fp: FakeProcess,
) -> None:
    # ARRANGE
    fp.register(["conan", "remote", "list-users"])
    fp.register(["conan", "remote", "add", REMOTE_REPO_NAME_1, EXAMPLE_URL])
    fp.register(["conan", "remote", "add", REMOTE_REPO_NAME_2, EXAMPLE_URL], returncode=1)

    # ACT
    conan_add_remote(Path("some_path"), config)

    # ASSERT
    assert "Unable to add remote repository" in caplog.text


def test_conan_add_remote_add_missing_user(
    config: Config,
    caplog: pytest.LogCaptureFixture,
    fp: FakeProcess,
) -> None:
    # ARRANGE
    list_user_stdout = b"""
conancenter:
  No user
remote_repo_name_1:
  No user
remote_repo_name_2:
  Username: env_conan_user_name
  authenticated: True
"""
    fp.register(["conan", "remote", "list-users"], stdout=list_user_stdout)
    fp.register(["conan", "remote", "add", REMOTE_REPO_NAME_1, EXAMPLE_URL])
    fp.register(["conan", "remote", "add", REMOTE_REPO_NAME_2, EXAMPLE_URL])
    fp.register(["conan", "remote", "login", REMOTE_REPO_NAME_1])

    # ACT
    conan_add_remote(Path("some_path"), config)


def test_conan_add_remote_already_exists(
    config: Config,
    caplog: pytest.LogCaptureFixture,
    fp: FakeProcess,
) -> None:
    # ARRANGE
    fp.register(["conan", "remote", "list-users"])
    fp.register(["conan", "remote", "add", REMOTE_REPO_NAME_1, EXAMPLE_URL])
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


def test_conan_remote_login(fp: FakeProcess) -> None:
    # ARRANGE
    add_user_cmd = ["conan", "remote", "login", REPO_NAME]
    fp.register(add_user_cmd)

    # ACT
    conan_remote_login(REPO_NAME)

    assert fp.calls.popleft() == add_user_cmd


def test_conan_remote_login_env_vars(fp: FakeProcess) -> None:
    # ARRANGE
    add_user_cmd = [
        "conan",
        "remote",
        "login",
        REPO_NAME,
    ]
    fp.register(add_user_cmd)

    # ACT
    with patch.dict(
        os.environ,
        {"CONAN_LOGIN_USERNAME": ENV_CONAN_USER, "CONAN_PASSWORD": ENV_CONAN_PASSWORD},
    ):
        conan_remote_login(REPO_NAME)

    assert fp.calls.popleft() == add_user_cmd


def test_conan_remote_login_fail(caplog: pytest.LogCaptureFixture, fp: FakeProcess) -> None:
    # ARRANGE
    add_user_cmd = [
        "conan",
        "remote",
        "login",
        REPO_NAME,
    ]
    fp.register(add_user_cmd, returncode=1)

    # ACT
    with patch.dict(
        os.environ,
        {"CONAN_LOGIN_USERNAME": ENV_CONAN_USER, "CONAN_PASSWORD": ENV_CONAN_PASSWORD},
    ):
        conan_remote_login(REPO_NAME)

    # ASSERT
    assert "Unable to log in to conan remote repo_name" in caplog.text


def test_conan_source_fails(config: Config, caplog: pytest.LogCaptureFixture, fp: FakeProcess) -> None:
    # ARRANGE
    fp.register(["conan", "source", "."], returncode=1)

    # ACT
    conan_source(config.project_root)

    # ASSERT
    assert "Unable to source" in caplog.text
