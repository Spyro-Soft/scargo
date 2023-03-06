import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from _pytest.logging import LogCaptureFixture

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
EXAMPLE_URL = "example.com"
REPO_NAME = "repo_name"


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


def test_publish(
    config: Config,
    mock_get_project_root: None,
    mock_subprocess_check_call: MagicMock,
) -> None:
    # ACT
    scargo_publish(REPO_NAME)

    # ASSERT
    project = config
    project_name = project.project.name
    version = project.project.version

    conan_clean_cmd = "conan remote clean"
    conan_add_remote_1_cmd = ["conan", "remote", "add", REMOTE_REPO_NAME_1, EXAMPLE_URL]
    conan_add_remote_2_cmd = ["conan", "remote", "add", REMOTE_REPO_NAME_2, EXAMPLE_URL]
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

    assert mock_subprocess_check_call.mock_calls[0].args[0] == conan_clean_cmd
    assert mock_subprocess_check_call.mock_calls[0].kwargs["shell"] is True
    assert mock_subprocess_check_call.mock_calls[1].args[0] == conan_add_remote_1_cmd
    assert mock_subprocess_check_call.mock_calls[2].args[0] == conan_add_remote_2_cmd
    assert mock_subprocess_check_call.mock_calls[3].args[0] == conan_add_conacenter_cmd
    assert mock_subprocess_check_call.mock_calls[4].args[0] == conan_export_cmd
    assert mock_subprocess_check_call.mock_calls[4].kwargs["shell"] is True
    assert mock_subprocess_check_call.mock_calls[5].args[0] == conan_upload_cmd


def test_conan_add_user(
    mock_subprocess_check_call: MagicMock,
) -> None:
    # ARRANGE
    remote_repo = "repo_name"
    env_conan_user = "mock_user_name"
    env_conan_password = "mock_password"

    # ACT
    with patch.dict(
        os.environ,
        {"CONAN_LOGIN_USERNAME": env_conan_user, "CONAN_PASSWORD": env_conan_password},
    ):
        conan_add_user(remote_repo)

    # ASSERT
    add_user_cmd = [
        "conan",
        "user",
        "-p",
        env_conan_password,
        "-r",
        remote_repo,
        env_conan_user,
    ]

    assert mock_subprocess_check_call.call_args.args[0] == add_user_cmd


def test_conan_add_remote_fail(
    config: Config,
    caplog: pytest.LogCaptureFixture,
) -> None:
    # ARRANGE
    check_call_mock = MagicMock()
    check_call_mock.side_effect = subprocess.CalledProcessError(returncode=1, cmd="")

    # ACT & ASSERT
    with patch("subprocess.check_call", check_call_mock):
        conan_add_remote(Path("some_path"))
        assert "Unable to add remote repository" in caplog.text


def test_conan_add_conancenter_fail(caplog: LogCaptureFixture) -> None:
    # ARRANGE
    check_call_mock = MagicMock()
    check_call_mock.side_effect = subprocess.CalledProcessError(returncode=1, cmd="")

    # ACT & ASSERT
    with patch("subprocess.check_call", check_call_mock):
        conan_add_conancenter()
        assert "Unable to add conancenter remote repository" in caplog.text


def test_conan_clean_remote_fail(caplog: LogCaptureFixture) -> None:
    # ARRANGE
    check_call_mock = MagicMock()
    check_call_mock.side_effect = subprocess.CalledProcessError(returncode=1, cmd="")

    # ACT & ASSERT
    with patch("subprocess.check_call", check_call_mock):
        conan_clean_remote()
        assert "Unable to clean remote repository list" in caplog.text


def test_create_package_fail(
    config: Config,
    mock_get_project_root: None,
    caplog: LogCaptureFixture,
) -> None:
    # ARRANGE
    check_call_mock = MagicMock()
    check_call_mock.side_effect = [
        subprocess.CompletedProcess(args="", returncode=1),  # conan clean
        subprocess.CompletedProcess(args="", returncode=1),  # add remote_1
        subprocess.CompletedProcess(args="", returncode=1),  # add remote_2
        subprocess.CompletedProcess(args="", returncode=1),  # add con center
        subprocess.CalledProcessError(returncode=1, cmd=""),  # create package
        subprocess.CompletedProcess(args="", returncode=1),  # upload package
    ]

    # ACT & ASSERT
    with patch("subprocess.check_call", check_call_mock):
        scargo_publish(REPO_NAME)
        assert "Unable to create package" in caplog.text


def test_upload_package_fail(
    mock_get_project_root: None,
    caplog: LogCaptureFixture,
) -> None:
    # ARRANGE
    check_call_mock = MagicMock()
    check_call_mock.side_effect = [
        subprocess.CompletedProcess(args="", returncode=1),  # conan clean
        subprocess.CompletedProcess(args="", returncode=1),  # add remote 1
        subprocess.CompletedProcess(args="", returncode=1),  # add remote 2
        subprocess.CompletedProcess(args="", returncode=1),  # add con center
        subprocess.CompletedProcess(args="", returncode=1),  # create package
        subprocess.CalledProcessError(returncode=1, cmd=""),  # upload package
    ]

    # ACT & ASSERT
    with patch("subprocess.check_call", check_call_mock):
        with pytest.raises(SystemExit):
            scargo_publish(REPO_NAME)
            assert "Unable to publish package" in caplog.text


def test_conan_add_user_fail(
    caplog: pytest.LogCaptureFixture,
) -> None:
    # ARRANGE
    remote_repo = "repo_name"
    check_call_mock = MagicMock()
    check_call_mock.side_effect = [
        subprocess.CalledProcessError(returncode=1, cmd=""),
    ]

    # ACT & ASSERT
    with patch.dict(os.environ, {"CONAN_LOGIN_USERNAME": "mock-value"}):
        with patch("subprocess.check_call", check_call_mock):
            conan_add_user(remote_repo)
            assert "Unable to add user" in caplog.text
