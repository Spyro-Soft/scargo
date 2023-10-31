import os
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
from pytest_subprocess import FakeProcess
from pytest_subprocess.fake_popen import FakePopen

from scargo.conan_utils import conan_add_remote, conan_add_user
from scargo.config import Config
from tests.ut.ut_scargo_publish import (
    ENV_CONAN_PASSWORD,
    ENV_CONAN_USER,
    EXAMPLE_URL,
    REMOTE_REPO_NAME_1,
    REMOTE_REPO_NAME_2,
    REPO_NAME,
    config,
)


def conan_remote_add_error(process: FakePopen, stderr: str) -> None:
    raise subprocess.CalledProcessError(1, process.args, b"", stderr.encode())


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
