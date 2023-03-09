import os
from pathlib import Path
from unittest.mock import patch

import pytest
from _pytest.logging import LogCaptureFixture
from pytest_subprocess import FakeProcess

from scargo.commands.publish import (
    conan_add_conancenter,
    conan_add_remote,
    conan_add_user,
    conan_clean_remote,
    scargo_publish,
)
from scargo.config import Config
from tests.ut.utils import get_test_project_config

REMOTE_REPO_NAME_1 = "remote_repo_name_1"
REMOTE_REPO_NAME_2 = "remote_repo_name_2"
EXAMPLE_URL = "https://example.com"
REPO_NAME = "repo_name"
ENV_CONAN_USER = "env_conan_user_name"
ENV_CONAN_PASSWORD = "env_conan_password"


@pytest.fixture
def mock_get_project_root(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "scargo.commands.publish.get_project_root", lambda: Path("some_path")
    )


@pytest.fixture
def config(monkeypatch: pytest.MonkeyPatch) -> Config:
    test_project_config = get_test_project_config()
    test_project_config.conan.repo[REMOTE_REPO_NAME_1] = EXAMPLE_URL
    test_project_config.conan.repo[REMOTE_REPO_NAME_2] = EXAMPLE_URL

    monkeypatch.setattr(
        "scargo.commands.publish.prepare_config",
        lambda: test_project_config,
    )

    return test_project_config


def test_publish(config: Config, mock_get_project_root: None, fp: FakeProcess) -> None:
    # ARRANGE
    fp.keep_last_process(True)
    fp.register([fp.any()])

    # ACT
    scargo_publish(REPO_NAME)

    # ASSERT
    project_name = config.project.name
    version = config.project.version

    conan_clean_cmd = "conan remote clean"
    conan_add_remote_1_cmd = ["conan", "remote", "add", REMOTE_REPO_NAME_1, EXAMPLE_URL]
    conan_add_remote_2_cmd = ["conan", "remote", "add", REMOTE_REPO_NAME_2, EXAMPLE_URL]
    conan_user_cmd = "conan user"
    conan_add_conacenter_cmd = "conan remote add conancenter https://center.conan.io"
    conan_export_cmd = "conan export-pkg . -f"
    conan_upload_cmd = [
        "conan",
        "upload",
        f"{project_name}/{version}",
        "-r",
        REPO_NAME,
        "--all",
        "--confirm",
    ]

    assert fp.calls[0] == conan_clean_cmd
    assert fp.calls[1] == conan_add_remote_1_cmd
    assert fp.calls[2] == conan_user_cmd
    assert fp.calls[3] == conan_add_remote_2_cmd
    assert fp.calls[4] == conan_user_cmd
    assert fp.calls[5] == conan_add_conacenter_cmd
    assert fp.calls[6] == conan_export_cmd
    assert fp.calls[7] == conan_upload_cmd
    assert len(fp.calls) == 8


def test_conan_add_user(fp: FakeProcess) -> None:
    # ARRANGE
    fp.keep_last_process(True)
    fp.register([fp.any()])

    # ACT
    with patch.dict(
        os.environ,
        {"CONAN_LOGIN_USERNAME": ENV_CONAN_USER, "CONAN_PASSWORD": ENV_CONAN_PASSWORD},
    ):
        conan_add_user(REPO_NAME)

    # ASSERT
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
    fp.register(
        ["conan", "remote", "add", REMOTE_REPO_NAME_2, EXAMPLE_URL], returncode=1
    )

    # ACT
    with pytest.raises(fp.exceptions.ProcessNotRegisteredError):
        conan_add_remote(Path("some_path"))

        # ASSERT
        assert "Unable to add remote repository" in caplog.text


def test_conan_add_conancenter_fail(caplog: LogCaptureFixture, fp: FakeProcess) -> None:
    # ARRANGE
    cmd = "conan remote add conancenter https://center.conan.io"
    fp.register(cmd, returncode=1)

    # ACT
    conan_add_conancenter()

    # ASSERT
    assert "Unable to add conancenter remote repository" in caplog.text


def test_conan_clean_remote_fail(caplog: LogCaptureFixture, fp: FakeProcess) -> None:
    # ARRANGE
    cmd = "conan remote clean"
    fp.register(cmd, returncode=1)

    # ACT
    conan_clean_remote()

    # ASSERT
    assert "Unable to clean remote repository list" in caplog.text


def test_create_package_fail(
    config: Config,
    mock_get_project_root: None,
    caplog: LogCaptureFixture,
    fp: FakeProcess,
) -> None:
    # ARRANGE
    cmd = "conan export-pkg . -f"
    fp.register(cmd, returncode=1)

    # ACT
    with pytest.raises(fp.exceptions.ProcessNotRegisteredError):
        scargo_publish(REPO_NAME)

        # ASSERT
        assert "Unable to create package" in caplog.text


def test_upload_package_fail(
    config: Config,
    mock_get_project_root: None,
    caplog: LogCaptureFixture,
    fp: FakeProcess,
) -> None:
    # ARRANGE
    project_name = config.project.name
    version = config.project.version
    cmd = [
        "conan",
        "upload",
        f"{project_name}/{version}",
        "-r",
        REPO_NAME,
        "--all",
        "--confirm",
    ]
    fp.register(cmd, returncode=1)

    # ACT
    with pytest.raises(fp.exceptions.ProcessNotRegisteredError):
        with pytest.raises(SystemExit) as error:
            scargo_publish(REPO_NAME)

            # ASSERT
            assert "Unable to publish package" in caplog.text
            assert error.value.code == 1


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
